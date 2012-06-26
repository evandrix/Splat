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
        sys.path.append('/Users/lwy08/Dropbox/FYP/fyp/fyp/')
        # reference module under test
        self.module = __import__('absolute')
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

    def test_absolute_all_None(self): 
        self.assertRaises(TypeError, self.module.absolute, *[None])

    def test_absolute_all_attr_None_wdef(self): 
        self.assertRaises(TypeError, self.module.absolute, *[None])

    def test_absolute_all_attr_MetaParam_wdef(self): 
        self.assertRaises(TypeError, self.module.absolute, *[None])

    def test_absolute_42ee5f0179d440269fe1f349af6ff4f7(self): 
        Param1 = type('',(object,), {})()
        self.assertNotRaises(self.module.absolute, *[Param1])
        self.assertEqualClassName(self.module.absolute(*[Param1]), 'Param1', 'incorrect class name for return value encountered')
        self.assertEqualAttrs(self.module.absolute(*[Param1]), '{"index": 1, "dct": {}, "attr": null}', 'incorrect attributes for return value encountered')


if __name__ == '__main__':
    unittest.main()
