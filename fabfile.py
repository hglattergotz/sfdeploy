from __future__ import with_statement

from fabric.api import *
from fabric.contrib.files import *
from sys import exit
from datetime import date, timedelta
from fabric.contrib.console import confirm
from fabric.colors import red, green
import time


@task
def ct(sf='n'):
    """
    Build the ctags file for this project (for vim use). fab ct:sf=y/n
    """
    if (sf == 'y'):
        local("/usr/local/bin/ctags -R --exclude=.svn --tag-relative=yes --PHP-kinds=+cf-v --regex-PHP='/abstract\s+class\s+([^ ]+)/\1/c/' --regex-PHP='/interface\s+([^ ]+)/\1/c/' --regex-PHP='/(public\s+|static\s+|abstract\s+|protected\s+|private\s+)function\s+\&?\s*([^ (]+)/\2/f/' . /usr/local/share/symfony1.4.17/lib")
    else:
        local("/usr/local/bin/ctags -R --exclude=.svn --tag-relative=yes --PHP-kinds=+cf-v --regex-PHP='/abstract\s+class\s+([^ ]+)/\1/c/' --regex-PHP='/interface\s+([^ ]+)/\1/c/' --regex-PHP='/(public\s+|static\s+|abstract\s+|protected\s+|private\s+)function\s+\&?\s*([^ (]+)/\2/f/'")


