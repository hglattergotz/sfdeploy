from __future__ import with_statement

# Import the fabtools module by adding it to the beginning of the path
import sys
sys.path[:0] = ["./"]
print(os.getcwd())
#sys.exit(0)
import config
import git
import pear
import shell
import tools

from fabric.api import *
from fabric.contrib.files import *
#from sys import exit
from datetime import date, timedelta
from fabric.contrib.console import confirm
from fabric.colors import red, green
import time


def load_config():
    """
    Load the yaml configuration file into the env dictionary.
    This depends on the deployment_target being set and should typically get
    called from either dev() or prod().
    """
    env.update(fabtools.load_yaml_config('config/deployment/config.yml',
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
def deploy(skip_cron='n'):
    """
    Deploy to project to target server(s), example: fab prod deploy:skip_cron=y/n
    """
    if fabtools.is_git_dirty():
        print(red('Your working copy is dirty! Commit or stash files first and checkout the commit you want to deploy.', bold=True))
        exit(1)

    if not confirm(red('You are about to deploy the commit "%s" copy to target "%s". Continue?' %
                   (fabtools.git_sha1_commit(), env.deployment_target),
                   bold=True)):
      return

    deploy_rev = fabtools.git_sha1_commit()
    set_source_dir(deploy_rev)

    print(green('Deploying revision %s to "%s"' %
          (deploy_rev, env.deployment_target), bold=True))
    make_folders()
    upload_source(deploy_rev, env.packages_dir, env.source_dir)
    sf_permissions()

    stop()
    link_folders()

    if (skip_cron == 'n'):
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


def sf_permissions():
    sudo('cd %s && ./symfony project:permissions' % (env.source_dir))


def get_installed_revision():
    """
    Not sure if this will work too well anymore until the actual git revision
    is used.
    """
    parts = get_current_physical_dir().split('/')

    return parts.pop()


def make_folders():
    """
    Create the folder structure on the deployment target
    """
    print(green('Creating remote folders'))
    if not exists('%(project_dir)s' % (env)):
      sudo('mkdir %(project_dir)s' % (env))

    if not exists('%(sources_dir)s' % (env)):
      sudo('mkdir %(sources_dir)s' % (env))

    if not exists('%(source_dir)s' % (env)):
      sudo('mkdir %(source_dir)s' % (env))

    if not exists('%(source_dir)s/cache' % (env)):
      sudo('mkdir %(source_dir)s/cache' % (env))

    if not exists('%(source_dir)s/log' % (env)):
      sudo('mkdir %(source_dir)s/log' % (env))

    if not exists('%(packages_dir)s' % (env)):
      sudo('mkdir %(packages_dir)s' % (env))

    if not exists('%(reports_dir)s' % (env)):
      sudo('mkdir %(reports_dir)s' % (env))


def set_source_dir(deploy_rev = ''):
    if deploy_rev != '':
        env.source_dir = "%s/%s" % (env.sources_dir, deploy_rev)
    else:
        env.source_dir = get_current_physical_dir()


def get_current_physical_dir():
    if exists(env.current_dir):
        return sudo('cd %s && pwd -P' % (env.current_dir))
    else:
        print(red('Directory %s does not exist.' % env.current_dir, bold=True))
        raise Exception('Directory env.current_dir does not exist')


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
    print(green('Uploading source to target'))
    archive_name = '%s.tar.gz' % (deploy_revision)
    fabtools.git_archive_all(os.getcwd(), archive_name)
    put('%s' % (archive_name), '%s/'  % (package_dir), True)
    sudo('cd %s && tar zxf %s/%s' % (source_dir, package_dir, archive_name))
    local('rm %s' % archive_name)


def link_folders():
    """
    Link package folder to current and the previous folder to the previously
    installed package folder.
    """
    print(green('Linking folders', bold=True))
    if exists(env.current_dir):
        sudo('rm -rf %s' % (env.current_dir))

    sudo('ln -s %s %s' % (env.source_dir, env.current_dir))


@task
def start():
    """
    Start all cron jobs
    """
    print(green('Starting cron jobs', bold=True))
    try:
        physical_dir = get_current_physical_dir()

        if env.current_dir != physical_dir:
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

        if env.current_dir != physical_dir:
            cron = load_cron_config()
            with settings(warn_only=True):
                sudo('rm %s/%s*' % (cron['cron']['cron_dir'], cron['cron']['cron_job_prefix']))
        else:
            print(red('No cron jobs to stop', bold=True))
    except Exception as inst:
        print(red('Cron jobs not stopped (There might not be any installed). Exception: %s' % inst, bold=True))


def load_cron_config():
    cron = fabtools.load_yaml('config/deployment/cron.yml')

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
