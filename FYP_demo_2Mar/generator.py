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
from header   import *  # enable colors

from template_writer import *   # submodule support

MAX_ITERATIONS = 2 ** 10

#############################################################################
class Generator(object):
    def __init__(self, target):
        self.target = target

    def run(self):
        print ">> Testing top-level functions in '%s'..." \
            % self.target.__name__
        functions = inspect.getmembers(self.target, inspect.isfunction)
        all_tests = []
        for name,function in functions:
            all_tests.extend(self.test_function(function))
        #pprint.pprint(all_tests)
        tmpl_writer = TemplateWriter(self.target)
        tmpl_writer.run(all_tests)

    def test_function(self, function):
        assert hasattr(function, '__call__')

        print "\t'%s': %s..." % \
            (function.__name__, inspect.getargspec(function))
        args, varargs, keywords, defaults = inspect.getargspec(function)
        tests = []
        # case 1: Nones
        print "Testing with all parameters = 'None'..."
        arglist = [None] * len(args)    # correct number of arguments supplied
        assert len(arglist) == len(args)
        try:
            return_value = function(*arglist)
        except AttributeError as e:
            print OKGREEN + 'Error' + ':' + ENDC, e
            assert isinstance(e, Exception)
            tests.append(UnitTestObject(
                function.__name__, "all_Nones", None,
                [ "self.assertRaises(%s, %s, *%s)" % \
                    (e.__class__.__name__, function.__name__, arglist) ]
            ))
        else:
            # function executed succesfully with Nones supplied
            # assert that return value is equal (also if None)
            statements = []
            statements.append("self.assertNotRaised(%s, *%s)" % \
                (function.__name__, arglist))
            if return_value is None:
                statements.append("self.assertIsNone(%s(*%s))" % (function.__name__, arglist))
            else:
                statements.append("self.assertEqual(%s(*%s), %r, 'function return value not equal')" % (function.__name__, arglist, return_value))
            tests.append(UnitTestObject(
                function.__name__, "all_Nones", None, statements))
        return tests

#############################################################################
@aspect_import_mut
@aspect_timer
def run(*vargs, **kwargs):
    generator = Generator(kwargs['module'])
    generator.run()

if __name__ == "__main__":
    run()
    sys.exit(0)

