#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import re
import dis
import types
import py
from common   import *
from inspect  import *
from pprint   import pprint
from byteplay import Code

t0 = time.time()

# Colors
FAIL = '\033[91m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
OKBLUE = '\033[94m'
HEADER = '\033[95m'
ENDC = '\033[0m'
colors = [ HEADER, OKBLUE, OKGREEN, WARNING, FAIL ]
#for c in colors:
#    print c + "test" + ENDC

MODULE_UNDER_TEST='program' if len(sys.argv) < 2 else sys.argv[1]

#print "Disassembling Python module '%s'..." % MODULE_UNDER_TEST
#sys.stdout = sys.__stderr__
#dis.dis(MODULE_UNDER_TEST)
#sys.stdout = sys.__stdout__
# Redirect output streams
class writer :
    def __init__(self, *writers):
        self.writers = writers
    def write(self, text):
        for w in self.writers:
            if text.startswith(">>"):
                w.write(WARNING + text + ENDC)
            elif text.startswith("**"):
                w.write(HEADER + text + ENDC)
            else:
                w.write(OKBLUE + text + ENDC)
sys.stdout = writer(sys.stdout)
