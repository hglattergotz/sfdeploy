# -*- coding: utf-8 -*-
# config.py
#
# Copyright (c) 2012-2013 Henning Glatter-Götz
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

# tools.py - Collection of configuration tasks for fabric
#
# To include it in the fabfile.py add this near the top
#
# import sys
# import tools

import os
from fabric.api import *
from fabric.colors import red, green
import pear

@task
def loc():
    """
    Run phploc on the project
    """
    if (pear.pear_detect('phploc')):
        local('phploc --exclude app/cache,app/logs/vendor')
    else:
        print(red('The PEAR package phploc is not installed.', True) + '\nInstall it as follows (first command as root)\n  pear config-set auto_discover 1\n  pear install pear.phpunit.de/phploc')


@task
def messdetector():
    """
    Run messdetector on the project
    """
    if (pear.pear_detect('PHP_PMD')):
        with settings(warn_only=True):
            result = local('phpmd . html codesize,unusedcode,design --reportfile ../messdetector.html --exclude app/cache,app/logs,vendor', capture=True)
        if result.return_code == 0 or result.return_code == 2:
            local('open ../messdetector.html');
        else:
            abort(result)
    else:
        print(red('The PEAR package phploc is not installed.', True) + '\nInstall it as follows (first command as root)\n  pear config-set auto_discover 1\n  pear install pear.phpunit.de/phploc')


@task
def ct():
    """
    Build the ctags file for this project (for vim use)
    """
    local("/usr/local/bin/ctags -R --exclude=.svn --tag-relative=yes --PHP-kinds=+cf-v --regex-PHP='/abstract\s+class\s+([^ ]+)/\1/c/' --regex-PHP='/interface\s+([^ ]+)/\1/c/' --regex-PHP='/(public\s+|static\s+|abstract\s+|protected\s+|private\s+)function\s+\&?\s*([^ (]+)/\2/f/'")

