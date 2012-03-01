#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

# Colors
FAIL    = '\033[91m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
OKBLUE  = '\033[94m'
HEADER  = '\033[95m'
ENDC    = '\033[0m'
colors  = [ HEADER, OKBLUE, OKGREEN, WARNING, FAIL ]

# Redirect streams
class Writer(object):
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
sys.stdout = Writer(sys.stdout)
#sys.stdout = sys.__stdout__
sys.stderr = sys.__stderr__

