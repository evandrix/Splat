import os
import sys
import time
import re
import pprint
import random
import types
import unittest
import imp
import jsonpickle

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
        sys.path.append('/Users/lwy08/Dropbox/FYP/fyp/fyp')
        sys.path.append('/Users/lwy08/Dropbox/FYP/fyp/fyp/trivial/')
        # reference module under test
        self.module = __import__('bank_account')
    def tearDown(self):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        del self.module
    def assertRaisesException(self, expected_e, function, *args, **kwargs):
        try:
            function(*args, **kwargs)
        except Exception as actual_e:
            assert actual_e.__class__.__name__ == expected_e.__name__
    def assertEqualClassName(self, function, expected, *args, **kwargs):
        return_value = function
        assert return_value.__class__.__name__ == expected
    def assertEqualAttrs(self, function, expected, *args, **kwargs):
        return_value = function
        unpickled = jsonpickle.decode(expected)
        assert isinstance(unpickled, dict)
        for key, value in unpickled.iteritems():
            assert return_value.__dict__[key] == value
    def assertNotRaises(self, function, *args, **kwargs):
        with self.assertRaises(Exception):
            try:
                function(*args, **kwargs)
            except:
                pass
            else:
                raise Exception

    def test_main_all_None(self): 
        self.assertNotRaises(self.module.main, *[])
        self.assertEqual(self.module.main(*[]), 10, 'incorrect function return value encountered')

    def test_main_all_attr_None_wdef(self): 
        self.assertNotRaises(self.module.main, *[])
        self.assertEqual(self.module.main(*[]), 10, 'incorrect function return value encountered')

    def test_main_all_attr_MetaParam_wdef(self): 
        self.assertNotRaises(self.module.main, *[])
        self.assertEqual(self.module.main(*[]), 10, 'incorrect function return value encountered')

    def test_main_77b94f81ab2340c88876006cab767671(self): 
        self.assertNotRaises(self.module.main, *[])
        self.assertEqual(self.module.main(*[]), 10, 'incorrect function return value encountered')


if __name__ == '__main__':
    unittest.main()
