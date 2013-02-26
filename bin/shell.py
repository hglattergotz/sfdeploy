# -*- coding: utf-8 -*-
# config.py
#
# Copyright (c) 2012-2013 Henning Glatter-Götz
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.

# fabtools.py - Collection of shell tasks for fabric
#
# To include it in the fabfile.py add this near the top
#
# import sys
# import shell

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
