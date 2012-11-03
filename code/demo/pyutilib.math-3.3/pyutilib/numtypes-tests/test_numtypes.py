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
        sys.path.append('/Users/lwy08/Downloads/pyutilib.math-3.3/pyutilib/math/')
        # reference module under test
        self.module = __import__('numtypes')
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

    def test_is_nan_all_None(self): 
        self.assertNotRaises(self.module.is_nan, *[None])
        self.assertEqual(self.module.is_nan(*[None]), False, 'incorrect function return value encountered')

    def test_is_nan_all_attr_None_wdef(self): 
        self.assertNotRaises(self.module.is_nan, *[None])
        self.assertEqual(self.module.is_nan(*[None]), False, 'incorrect function return value encountered')

    def test_is_nan_all_attr_MetaParam_wdef(self): 
        self.assertNotRaises(self.module.is_nan, *[None])
        self.assertEqual(self.module.is_nan(*[None]), False, 'incorrect function return value encountered')

    def test_is_nan_fa31d8123a454fd3a44df6f92c63bc1c(self): 
        Param1 = type('',(object,), {})()
        self.assertNotRaises(self.module.is_nan, *[Param1])
        self.assertEqual(self.module.is_nan(*[Param1]), False, 'incorrect function return value encountered')

    def test_is_finite_all_None(self): 
        self.assertNotRaises(self.module.is_finite, *[None])
        self.assertEqual(self.module.is_finite(*[None]), False, 'incorrect function return value encountered')

    def test_is_finite_all_attr_None_wdef(self): 
        self.assertNotRaises(self.module.is_finite, *[None])
        self.assertEqual(self.module.is_finite(*[None]), False, 'incorrect function return value encountered')

    def test_is_finite_all_attr_MetaParam_wdef(self): 
        self.assertNotRaises(self.module.is_finite, *[None])
        self.assertEqual(self.module.is_finite(*[None]), False, 'incorrect function return value encountered')

    def test_is_finite_db3b22fb424b4e57b9771ae17e97c865(self): 
        Param1 = type('',(object,), {})()
        self.assertNotRaises(self.module.is_finite, *[Param1])
        self.assertEqual(self.module.is_finite(*[Param1]), False, 'incorrect function return value encountered')


if __name__ == '__main__':
    unittest.main()
