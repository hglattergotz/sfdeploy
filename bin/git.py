# -*- coding: utf-8 -*-
# git.py
#
# Copyright (c) 2012-2013 Henning Glatter-Götz
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# git.py - Collection of git tasks for fabric
#
# To include it in the fabfile.py add this near the top
#
# import sys
# import git

import os
from fabric.api import *
from fabric.colors import red, green


def git_archive_all(path, archive_file_name):
    """
    Creates a gzipped tar file as git-archive would, but includes all the
    submodules if any exist.

     --path The path where the achrive is created
     --archive_file_name The file name of the archive

    Original source from https://github.com/ikame/fabric-git-archive-all
    """
    import os
    import tarfile

    def ls_files(prefix=''):
        """
        Does a `git ls-files` on every git repository (eg: submodules)
        found in the working git repository and returns a list with all the
        filenames returned by each `git ls-files`

         --full-name Forces paths to be output relative to the project top
           directory
         --exclude-standard adds standard git exclusions
           (.git/info/exclude, .gitignore, ...)
        """
        cmd = 'git ls-files --full-name --exclude-standard'
        raw_files = local(cmd, capture=True)
        files = []

        for filename in raw_files.split('\n'):
            if (os.path.isdir(filename) and
                os.path.exists(os.path.join(filename, '.git'))):
                os.chdir(filename)
                files.extend(ls_files(prefix=filename))
            else:
                files.append(os.path.join(prefix, filename))

        return files

    cwd = os.getcwd()
    os.chdir(path)
    files = ls_files()
    os.chdir(path)
    project_tar = tarfile.open(archive_file_name, 'w:gz')

    for filename in files:
        project_tar.add(filename)

    project_tar.close()
    os.chdir(cwd)

    print(green('Archive created at %s/%s' % (path, archive_file_name)))


def is_git_dirty():
    """
    Determine if the current working copy is dirty - have files been modified
    or are there untracked files.
    """
    dirty_status = local('git diff --quiet || echo "*"', capture=True)
    if dirty_status == '*':
        return True

    untracked_count = int(local('git status --porcelain 2>/dev/null| grep "^??" | wc -l', capture=True))
    if untracked_count > 0:
        return True

    return False


def git_sha1_commit():
    """
    Get the commit SHA1 (short) of the current branch.
    """
    return local('git rev-parse --short HEAD', capture=True)
