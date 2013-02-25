# -*- coding: utf-8 -*-
# pear.py
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
