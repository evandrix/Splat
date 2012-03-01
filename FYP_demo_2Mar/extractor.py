#!/usr/bin/env python
# -*- coding: utf-8 -*-

import inspect
import types
import time
import sys
import pprint
from common import *

# Bytecode extractor module #
#
# Features:
#   - Scans for the following information in bytecode using 'inspect' module:
#       * class definitions (w/ class types, ie. {old|new}-style
#       * top-level functions
#     ...used for targeting unit tests later as candidates
#

class Extractor(object):
    """
        Input: 	<target>.pyc
        Output: Scan results >> sys.stdout
    """

    def __init__(self, target):
        self.target = target

    def run(self):
        # scan for top-level functions
        functions = inspect.getmembers(self.target, inspect.isfunction)
        print ">> Scanning for top level functions..."
        for function in functions:
            name, fn = function
            print "\t", name, "\t", inspect.getargspec(fn)
        print

        # scan for class definitions
        print ">> Scanning for class definitions (& methods within)..."
        classes = inspect.getmembers(self.target, inspect.isclass)
        for label, klass in classes:
            if type(klass) is types.TypeType:
                print "\t(New-Style)", label, klass
            elif type(klass) is types.ClassType:
                print "\t(Old-Style)", label, klass
            else:
                print "\t", label, klass

            # methods within classes
            for item in inspect.getmembers(klass, inspect.ismethod):
                name, method = item
                print "\t\t", name, "\t", inspect.getargspec(method)
        print

@aspect_import_mut
@aspect_timer
def run(*vargs, **kwargs):
    extractor = Extractor(kwargs['module'])
    extractor.run()

if __name__ == "__main__":
    run()
    sys.exit(0)

