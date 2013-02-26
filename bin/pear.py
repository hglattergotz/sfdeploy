# -*- coding: utf-8 -*-
# config.py
#
# Copyright (c) 2012-2013 Henning Glatter-Götz
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

# pear.py - Collection of pear related tasks for fabric
#
# To include it in the fabfile.py add this near the top
#
# import sys
# import pear

import os
from fabric.api import *
from fabric.colors import red, green

def pear_detect(package):
    """
    Detect if a pear package is installed.
    """
    if which('pear'):
        pear_out = local('pear list -a', True)
        if pear_out.find(package) == -1:
            return False
        else:
            return True
    else:
        print(red('pear is not installed', True))
        return False
