#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import re
import dis
import types
import py
import inspect
import pprint
import byteplay
from common   import *  # AOP
from header   import *  # color output stream

MAX_ITERATIONS = 2 ** 10

#############################################################################
class Generator(object):
    def __init__(self, target):
        self.target = target

    def run(self):
        print ">> Testing top-level functions..."
        functions = inspect.getmembers(self.target, inspect.isfunction)
        for name,function in functions:
            self.test_function(function)

    def test_function(self, function):
        print ">> Testing function '%s'..." % function.__name__

#############################################################################
@aspect_import_mut
@aspect_timer
def run(*vargs, **kwargs):
    generator = Generator(kwargs['module'])
    generator.run()

if __name__ == "__main__":
    run()
    sys.exit(0)

