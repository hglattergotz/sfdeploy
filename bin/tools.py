# -*- coding: utf-8 -*-
# tools.py
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

# tools.py - Collection of configuration tasks for fabric
#
# To include it in the fabfile.py add this near the top
#
# import sys
# import tools

import os
from fabric.api import *
from fabric.colors import red, green

@task
def loc():
    """
    Run phploc on the project
    """
    if (fabtools.pear_detect('phploc')):
        local('phploc --exclude plugins --exclude lib/model --exclude lib/form --exclude lib/filter --exclude lib/vendor --exclude web .')
    else:
        print(red('The PEAR package phploc is not installed.', True) + '\nInstall it as follows (first command as root)\n  pear config-set auto_discover 1\n  pear install pear.phpunit.de/phploc')


@task
def messdetector():
    """
    Run messdetector on the project
    """
    if (fabtools.pear_detect('PHP_PMD')):
        with settings(warn_only=True):
            result = local('phpmd . html codesize,unusedcode,design --reportfile ../messdetector.html --exclude cache,log,lib/model,lib/form,lib/filter,lib/fabtools,plugins,apps/automation/lib/SeminarSync', capture=True)
        if result.return_code == 0 or result.return_code == 2:
            local('open ../messdetector.html');
        else:
            abort(result)
    else:
        print(red('The PEAR package phploc is not installed.', True) + '\nInstall it as follows (first command as root)\n  pear config-set auto_discover 1\n  pear install pear.phpunit.de/phploc')


@task
def ct(sf='n'):
    """
    Build the ctags file for this project (for vim use). fab ct:sf=y/n
    """
    if (sf == 'y'):
        local("/usr/local/bin/ctags -R --exclude=.svn --tag-relative=yes --PHP-kinds=+cf-v --regex-PHP='/abstract\s+class\s+([^ ]+)/\1/c/' --regex-PHP='/interface\s+([^ ]+)/\1/c/' --regex-PHP='/(public\s+|static\s+|abstract\s+|protected\s+|private\s+)function\s+\&?\s*([^ (]+)/\2/f/' . /usr/local/share/symfony1.4.17/lib")
    else:
        local("/usr/local/bin/ctags -R --exclude=.svn --tag-relative=yes --PHP-kinds=+cf-v --regex-PHP='/abstract\s+class\s+([^ ]+)/\1/c/' --regex-PHP='/interface\s+([^ ]+)/\1/c/' --regex-PHP='/(public\s+|static\s+|abstract\s+|protected\s+|private\s+)function\s+\&?\s*([^ (]+)/\2/f/'")

