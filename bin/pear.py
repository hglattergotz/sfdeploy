"""
PEAR task

A task to detect whether a specific PEAR package is installed or not

"""
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
