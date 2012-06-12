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
        self.module = __import__('readwrite.markup')
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

    def test_write_all_Nones(self): 
        self.assertRaises(InvalidGraphType, self.module.write, *[None])

    def test_write_hypergraph_all_Nones(self): 
        self.assertRaises(AttributeError, self.module.write_hypergraph, *[None])

    def test_read_all_Nones(self): 
        self.assertRaises(TypeError, self.module.read, *[None])

    def test_read_hypergraph_all_Nones(self): 
        self.assertRaises(TypeError, self.module.read_hypergraph, *[None])


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestProgram))
    return suite
if __name__ == '__main__':
    unittest.main()
    #unittest.TextTestRunner(verbosity=2).run(suite())


