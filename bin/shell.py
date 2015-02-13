"""
Shell module

"""
import os
from fabric.api import *
from fabric.colors import red, green

def which(program):
    """
    Return the path of an executable file.
    Borrowed from http://stackoverflow.com/a/377028/250780
    """
    import os
    def is_exe(fpath):
        return os.path.exists(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)

    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def archive_all(archive_path, archive_file_name, ignore = []):
    """
    Create a tar archive from a list of files build by the find command.
    This is a bit messy because it forces the user to manually exclude all
    undesired paths. An alternative would be to combine some form of
    git ls-files for the main project and an iterator that does the same for all
    vendors (This could be a problem if some vendors are not sourced from git).
    """
    import tarfile
    params = []
    params.append('find .')
    params.append('-type f')
    params.append('! -path "./.git"')
    params.append('! -path "*/.git/*"')
    params.append('! -iname "*.pyc"')
    params.append('! -iname ".gitignore"')
    params.append('! -iname "tags"')

    for path in ignore:
        params.append(''.join(['! -path "*', path, '/*"']))

    params.append('-print')
    cmd = ' '.join(params)

    files = local(cmd, capture=True).split('\n')
    cwd = os.getcwd()
    os.chdir(archive_path)
    project_tar = tarfile.open(archive_file_name, 'w:gz')

    for filename in files:
        project_tar.add(filename)

    project_tar.close()
    os.chdir(cwd)

    print(green('Archive created at %s/%s' % (path, archive_file_name)))
