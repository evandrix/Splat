#!/usr/bin/env python
# -*- coding: utf-8 -*-
# run nosetests for directory 'tests': `nosetests -vsw tests`
import os
import sys
import time
import re
import pprint
import random
import types
import unittest


class DevNull(object):
    def __init__(self, *writers):
        self.writers = writers
    def write(self, text):
       return
def f_noarg(self):
   return
def f_varg(self, *args, **kwargs):
   return
class TestProgram(unittest.TestCase):
    def setUp(self):
        # suppress program output streams
        sys.stdout = DevNull(sys.stdout)
        sys.stderr = DevNull(sys.stderr)
        sys.path.append('/Users/lwy08/Dropbox/FYP/benchmarks/pygraph')
        # reference module under test
        self.module = __import__('algorithms.accessibility')
        print self.module, dir(self.module)
    def tearDown(self):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        del self.module
    def assertNotRaises(self, function, *args, **kwargs):
        with self.assertRaises(Exception):
            try:
                function(*args, **kwargs)
            except:
                pass
            else:
                raise Exception

    def test_connected_components_all_Nones(self): 
        self.assertRaises(AttributeError, self.module.connected_components, *[None])

    def test_accessibility_all_Nones(self): 
        self.assertRaises(AttributeError, self.module.accessibility, *[None])

    def test_mutual_accessibility_all_Nones(self): 
        self.assertRaises(AttributeError, self.module.mutual_accessibility, *[None])

    def test_cut_edges_all_Nones(self): 
        self.assertRaises(AttributeError, self.module.cut_edges, *[None])

    def test_cut_nodes_all_Nones(self): 
        self.assertRaises(AttributeError, self.module.cut_nodes, *[None])


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestProgram))
    return suite
if __name__ == '__main__':
    sys.path.append('/Users/lwy08/Dropbox/FYP/benchmarks/pygraph')
    # reference module under test
    module = __import__('algorithms.accessibility')
    print module, dir(module), dir(module.accessibility)
    #unittest.TextTestRunner(verbosity=2).run(suite())


