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
        self.module = __import__('algorithms.minmax')
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

    def test_maximum_flow_all_Nones(self): 
        self.assertRaises(AttributeError, self.module.maximum_flow, *[None, None, None, None])

    def test_cut_value_all_Nones(self): 
        self.assertRaises(AttributeError, self.module.cut_value, *[None, None, None])

    def test_minimal_spanning_tree_all_Nones(self): 
        self.assertRaises(TypeError, self.module.minimal_spanning_tree, *[None, None])

    def test_self.module.heuristic_search_all_Nones(self): 
        self.assertNotRaises(self.module.heuristic_search, *[None, None, None, None])
        self.assertEqual(self.module.heuristic_search(*[None, None, None, None]), [None], function return value not equal)

    def test_cut_tree_all_Nones(self): 
        self.assertRaises(AttributeError, self.module.cut_tree, *[None, None])

    def test_shortest_path_bellman_ford_all_Nones(self): 
        self.assertRaises(AttributeError, self.module.shortest_path_bellman_ford, *[None, None])

    def test_shortest_path_all_Nones(self): 
        self.assertRaises(TypeError, self.module.shortest_path, *[None, None])


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestProgram))
    return suite
if __name__ == '__main__':
    unittest.main()
    #unittest.TextTestRunner(verbosity=2).run(suite())


