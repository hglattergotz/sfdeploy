"""
Symfony 2 deployment

"""
from __future__ import with_statement

# Add install directory to the beginning of the include path
import sys
import os

if os.path.exists("app/config/deployment/custom.py"):
    sys.path[:0] = ["app/config/deployment"]

sys.path[:0] = ["vendor/hgg/sfdeploy/bin"]

from fabric.api import *
from fabric.contrib.files import *
from fabric.contrib.console import confirm
from fabric.colors import red, green
from datetime import date, timedelta
import time
import config
import git
import pear
import shell
import tools

try:
    import custom
except ImportError:
    print(red('Cannot import custom. Any custom fabric task will not be available.'))

def load_config():
    """
    Load the yaml configuration file into the env dictionary.
    This depends on the deployment_target being set and should typically get
    called from either dev() or prod().
    """
    env.update(config.load_yaml_config('app/config/deployment/config.yml',
               env.deployment_target))

@task
def dev():
    """
    Set the target to be the development environment and load the configuration
    for that environment.
    """
    env.deployment_target = 'dev'
    load_config()


@task
def prod():
    """
    Set the target to be the production environment and load the configuration
    for that environment.
    """
    env.deployment_target = 'prod'
    load_config()


@task
def deploy(force = False):
    """
    Deploy to project to target server(s)
    """
    if not force:
        if git.is_git_dirty():
            print(red('Your working copy is dirty! Commit or stash files first and checkout the commit you want to deploy.', bold=True))
            exit(1)

    if not confirm(red('You are about to deploy the commit "%s" copy to target "%s". Continue?' %
                   (git.git_sha1_commit(), env.deployment_target),
                   bold=True)):
      return

    deploy_rev = git.git_sha1_commit()
    set_source_dir(deploy_rev)
    set_tmp_dir(deploy_rev)

    print(green('Deploying revision %s to "%s"' %
          (deploy_rev, env.deployment_target), bold=True))
    make_folders()
    mkdir(env.source_dir, 755)
    upload_source(deploy_rev, env.directories['packages']['dir'], env.source_dir)
    mkdir('%s/app/cache' % (env.source_dir), 777)
    mkdir('%s/app/logs' % (env.source_dir), 777)
    sf_permissions()
    stop()
    link_folders()
    start()
    print(green('Successfully deployed revision %s to %s' %
          (deploy_rev, env.deployment_target), bold=True))


@task
def installed_rev():
    """
    Get the installed revision on the target server
    """
    print(green('Installed revision on %s: %s' %
          (env.deployment_target, get_installed_revision())))


def get_installed_revision():
    """
    Not sure if this will work too well anymore until the actual git revision
    is used.
    """
    parts = get_current_physical_dir().split('/')

    return parts.pop()


def sf_permissions():
    print('You might want to do something here')
    #sudo('cd %s && ./symfony project:permissions' % (env.source_dir))


def make_folders():
    """
    Create the folder structure on the deployment target
    """
    print(green('Creating remote folders'))
    sorted = []

    for dir, values in env.directories.iteritems():
        sorted.append(values)

    sorted.sort(key=operator.itemgetter('order'))

    for values in sorted:
        mkdir(values['dir'], values['perms'])


def mkdir(path, mod):
    if not exists('%s' % (path)):
        sudo('mkdir %s' % (path))
        sudo('chmod %s %s' % (mod, path))


def set_source_dir(deploy_rev = ''):
    if deploy_rev != '':
        env.source_dir = "%s/%s" % (env.directories['sources']['dir'], deploy_rev)
    else:
        env.source_dir = get_current_physical_dir()


def set_tmp_dir(deploy_rev):
    env.tmp_dir = '%s/%s' % (tempfile.gettempdir(), deploy_rev)


def get_current_physical_dir():
    if exists(env.symlinks['current']['path']):
        return sudo('cd %s && pwd -P' % (env.symlinks['current']['path']))
    else:
        print(red('Directory %s does not exist.' % env.symlinks['current']['path'], bold=True))
        raise Exception('Directory %s does not exist' % (env.symlinks['current']['path']))


def upload_source(deploy_revision, package_dir, source_dir):
    """
    Upload the project source code to the target server

    Suggested folder structure on the deployment target:

      project_dir
        |-current (symlink to source_dir/<deploy_revision>)
        |-previous (symlink to previous source_dir/<deploy_revision>)
        |-package_dir
        |   |-<deploy_revision>.tar.gz
        |
        |-source_dir
        |   |-<deploy_revision>
        |   |    |-the project source

    Steps taken by this task:

      * Create an archive of the source code
      * Upload it to the package folder
      * Unpack it in a versioned release directory
      * Remove the archive on the local system
    """
    print(green('Creating source archive'))
    archive_name = '%s.tar.gz' % (deploy_revision)
    shell.archive_all(os.getcwd(), archive_name, env.ignore_on_deploy)
    print(green('Uploading archive to target'))
    put('%s' % (archive_name), '%s/'  % (package_dir), True)
    sudo('cd %s && tar zxf %s/%s' % (source_dir, package_dir, archive_name))
    local('rm %s' % archive_name)


def link_folders():
    """
    Link package folder to current and the previous folder to the previously
    installed package folder.
    """
    print(green('Linking folders', bold=True))
    if exists(env.symlinks['current']['path']):
        sudo('rm -rf %s' % (env.symlinks['current']['path']))

    sudo('ln -s %s %s' % (env.source_dir, env.symlinks['current']['path']))


@task
def start():
    """
    Start all cron jobs
    """
    print(green('Starting cron jobs', bold=True))
    try:
        physical_dir = get_current_physical_dir()

        if env.symlinks['current']['path']!= physical_dir:
            cron = load_cron_config()
            for job in cron['cron']['jobs']:
                install_sf_cron_job(job, cron['cron']['runhour'][env.deployment_target], physical_dir)
        else:
            print(red('No cron jobs to start'))
    except Exception as inst:
        print(red('Cron jobs not started. Exception: %s' % inst, bold=True))


@task
def stop():
    """
    Stop all cron jobs
    """
    print(green('Stopping cron jobs', bold=True))
    try:
        physical_dir = get_current_physical_dir()

        if env.symlinks['current']['path']!= physical_dir:
            cron = load_cron_config()
            with settings(warn_only=True):
                sudo('rm %s/%s*' % (cron['cron']['cron_dir'], cron['cron']['cron_job_prefix']))
        else:
            print(red('No cron jobs to stop', bold=True))
    except Exception as inst:
        print(red('Cron jobs not stopped (There might not be any installed). Exception: %s' % inst, bold=True))


def load_cron_config():
    cron = config.load_yaml('config/deployment/cron.yml')

    return cron


def install_sf_cron_job(job, hour, install_dir):
    """
    Install a symfony cron job
    """
    if env.deployment_target in job['targets']:
        print(green('Installing cron job %s:%s' %
              (job['namespace'], job['name']), bold=True))
        options = ' '

        for index, object in enumerate(job['options']):
            if '##cron-hour##' in object:
                job['options'][index] = object.replace('##cron-hour##', str(hour))

        if not '--install' in job['options']:
            job['options'].insert(0, '--install')
        options = options.join(job['options'])
        cmd = ("%s/symfony %s:%s %s" %
               (install_dir, job['namespace'], job['name'], options))
        sudo(cmd)
    else:
        print(green('Skipped %s:%s' %
              (job['namespace'], job['name']), bold=True))
