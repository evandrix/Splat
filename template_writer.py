#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement
import simplejson
import pyparsing    # S-Expr
import pystache
import inspect
from settings import *

# Generator - template writer submodule #
#
# Features:
#    - given function, test name, & statements, generate unit test suite
#
TEMPLATE_FILENAME = "test_template.mustache"

class UnitTestObject(object):
    def __init__(self, fn_name, test_name, stmts, add_params=None):
        self.fn_name    = fn_name
        self.test_name  = test_name
        self.add_params = None
        if add_params is not None:
            self.add_params = ', ' + add_params
        self.stmts      = ''.join(map(lambda l: '\n\t\t' + l, stmts)) + '\n'
    def __str__(self):
        return self.__repr__()
    def __repr__(self):
        return "%s(%s,%s,%s,%s)" % \
            (self.__class__.__name__, self.fn_name, self.test_name, self.add_params, self.stmts)

class TemplateWriter(object):
    def __init__(self, target):
        self.target = target

    def create_context(self, test_objects):
        context = {
            'module_name': self.target.__name__,
            'all_imports': None,
            'all_tests':   test_objects
        }
        return context

    def run(self, test_objects):
        template = self.read(TEMPLATE_FILENAME)
        context = self.create_context(test_objects)
        self.write(pystache.render(template, context))

    def read(self, template_file):
        """ Read in template test py file to populate """
        with open(template_file, "r") as template:
            return template.read()

    def write(self, data):
        """ Write out unit test suite into test_* py file """
        with open("test_%s.py" % self.target.__name__, "w") as fout:
            print >> fout, data
