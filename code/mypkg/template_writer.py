#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement
import os
import sys
import simplejson
import jsonpickle
import pyparsing    # S-Expr
import pystache
import codecs
import markupsafe
from settings import *
from collections import defaultdict

# Generator - template writer submodule #
# Features:
#    - given function, test name, & statements
#      generate unit test suite

TEMPLATE_FILENAME = "test_template_py.mustache"

class UnitTestObject(object):
    def __init__(self, fn_name, test_name, stmts, add_params=None):
        self.prefix     = ' '*4  # prepend unit test definition
        self.fn_name    = fn_name
        self.test_name  = test_name
        self.add_params = None
        if add_params is not None:
            self.add_params = ', ' + add_params
        self.stmts      = ''.join(map(lambda l: '\n'+(' '*8) + l, stmts)) + '\n'
        self.stmts_list = stmts
    def __str__(self):
        return self.__repr__()
    def __repr__(self):
        return "%s(%s,%s,%s,%s)" % \
            (self.__class__.__name__, self.fn_name, self.test_name, self.add_params, self.stmts)

class TemplateWriter(object):
    def run(self, GLOBALS, basedir, module_path, module_name, rel_path,
        basename, test_objects):
        assert isinstance(test_objects, list)
        if len(test_objects) <= 0:  return
        assert isinstance(test_objects[0], UnitTestObject)
        template = self.read(os.path.join( \
            os.path.dirname(os.path.realpath(__file__)), TEMPLATE_FILENAME))
        context = {
            'module_name': basename,
            'base_import_path': GLOBALS['base_import_dir'],
            'module_path': os.path.join(module_path, rel_path),
            'all_imports': None,
            'all_tests':   test_objects
        }
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
        output_filename = os.path.join(basedir, "test_%s" % module_name)
        self.write(pystache.render(template, context), basedir, output_filename+".py")
        self.write(pickled, basedir, output_filename+".json")
    def read(self, template_file):
        """ Read in template test py file to populate """
        with open(template_file, "rU") as template:
            return template.read()
    def write(self, data, basedir, filename):
        """ Write out unit test suite into test_* py file """
        if not os.path.exists(basedir):
            os.makedirs(basedir)
        with codecs.open(filename, "w", "utf-8") as fout:
            if isinstance(data, markupsafe.Markup):
                print >> fout, data.unescape() \
                    .replace("&#34;",'"').replace("&#39;","'")
            else:
                print >> fout, data

def main(GLOBALS):
    unit_test_objects = defaultdict(list)
    for function_name, values in GLOBALS['unittest_cache'].iteritems():
        # basedir/relative module path/module name
        module_name = values['module']
        if module_name.startswith('/'):
            module_name = module_name[1:]
        basename, rel_path = '/'.join(module_name.rstrip('/') \
            .split('/')[::-1]).partition('/')[::2]
        unit_test_objects[(basename, rel_path)].extend(values['testcases'])

    if GLOBALS['pkg_type'] == 'bytecode':
        module_path = os.path.dirname(GLOBALS['pkg_path'])
    elif GLOBALS['pkg_type'] == 'directory':
        module_path = GLOBALS['pkg_path']
    basedir = os.path.join(module_path, '%s-tests'%GLOBALS['pkg_name'])

    for (basename, rel_path), testcases in unit_test_objects.iteritems():
        module_name = os.path.join(rel_path, basename).replace('/', '_')
        TemplateWriter().run(GLOBALS, basedir, module_path, module_name,
            rel_path, basename, testcases)

    print 'Unit test suite written to:', basedir
