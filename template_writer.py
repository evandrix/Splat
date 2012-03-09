#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement
import simplejson
import jsonpickle
import pyparsing    # S-Expr
import pystache
import codecs
import markupsafe
from settings import *

# Generator - template writer submodule #
#
# Features:
#    - given function, test name, & statements, generate unit test suite
#
TEMPLATE_FILENAME = "test_template.mustache"

class UnitTestObject(object):
    def __init__(self, fn_name, test_name, stmts, add_params=None):
        self.prefix     = '\t'  # prepend unit test definition
        self.fn_name    = fn_name
        self.test_name  = test_name
        self.add_params = None
        if add_params is not None:
            self.add_params = ', ' + add_params
        self.stmts      = ''.join(map(lambda l: '\n\t\t' + l, stmts)) + '\n'
        self.stmts_list = stmts
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

        attr_excluded = [ 'stmts', 'prefix' ]
        json_test_objects = []
        for obj in test_objects:
            json_obj = {}
            for attr in obj.__dict__:
                if attr not in attr_excluded:
                    json_obj[attr] = obj.__dict__[attr]
            json_test_objects.append(json_obj)
        pickled = jsonpickle.encode(json_test_objects, unpicklable=False)
        unpickled = jsonpickle.decode(pickled)
        assert isinstance(unpickled, list)
        if len(unpickled) > 0:
            assert isinstance(unpickled[0], dict)

        output_filename = "test_%s" % self.target.__name__
        self.write(pystache.render(template, context), output_filename+".py")
        self.write(pickled, output_filename+".json")

    def read(self, template_file):
        """ Read in template test py file to populate """

        with open(template_file, "rU") as template:
            return template.read()

    def write(self, data, filename):
        """ Write out unit test suite into test_* py file """

        with codecs.open(filename, "w", "utf-8") as fout:
            if isinstance(data, markupsafe.Markup):
                print >> fout, data.unescape().replace("&#39;","'")
            else: #isinstance(data, 'unicode')
                print >> fout, data
