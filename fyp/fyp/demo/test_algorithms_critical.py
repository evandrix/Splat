import os
import sys
import time
import re
import pprint
import random
import types
import unittest
import imp

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
        #sys.stdout = DevNull(sys.stdout)
        sys.stderr = DevNull(sys.stderr)
        sys.path.append('/Users/lwy08/Dropbox/FYP/benchmarks')
        # reference module under test
        self.module = __import__('pygraph.algorithms.critical')
    def tearDown(self):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        del self.module
    def assertRaisesException(self, expected_e, function, *args, **kwargs):
        try:
            function(*args, **kwargs)
        except Exception as actual_e:
            if actual_e.__class__.__name__ != expected_e.__name__:
                raise Exception
    def assertEqualClassName(self, function, expected, *args, **kwargs):
        return_value = function
        if return_value.__class__.__name__ != expected:
            raise Exception
    def assertNotRaises(self, function, *args, **kwargs):
        with self.assertRaises(Exception):
            try:
                function(*args, **kwargs)
            except:
                pass
            else:
                raise Exception

    def test_transitive_edges_all_Nones(self):
        exception_module = imp.load_compiled('exceptions', '/Users/lwy08/Dropbox/FYP/benchmarks/pygraph/classes/exceptions.pyc')
        self.assertRaisesException(exception_module.InvalidGraphType, self.module.algorithms.critical.transitive_edges, *[None])

    def test_critical_path_all_Nones(self): 
        exception_module = imp.load_compiled('exceptions', '/Users/lwy08/Dropbox/FYP/benchmarks/pygraph/classes/exceptions.pyc')
        self.assertRaisesException(exception_module.InvalidGraphType, self.module.algorithms.critical.critical_path, *[None])


if __name__ == '__main__':
    unittest.main()
