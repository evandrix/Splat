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
        sys.path.append('/Users/lwy08/Dropbox/FYP/fyp/fyp/quixey/')
        # reference module under test
        self.module = __import__('gcd')
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

    def test_lcm_all_None(self): 
        self.assertRaises(TypeError, self.module.lcm, *[None, None])

    def test_lcm_all_attr_None_wdef(self): 
        self.assertRaises(TypeError, self.module.lcm, *[None, None])

    def test_lcm_all_attr_MetaParam_wdef(self): 
        self.assertRaises(TypeError, self.module.lcm, *[None, None])

    def test_lcm_8f79fa99cf8040248ea170799226c7fd(self): 
        Param1 = type('',(object,), {})()
        Param2 = type('',(object,), {})()
        self.assertRaises(TypeError, self.module.lcm, *[Param1, Param2])

    def test_lcm_fdfaa4672c99487f8fddd7181e583bfc(self): 
        Param2 = type('',(object,), {})()
        self.assertRaises(TypeError, self.module.lcm, *[0, Param2])

    def test_lcm_c90fe362593d4d45991b6ff544de6f19(self): 
        self.assertRaises(ZeroDivisionError, self.module.lcm, *[0, 0])

    def test_gcd_all_None(self): 
        self.assertRaises(TypeError, self.module.gcd, *[None, None])

    def test_gcd_all_attr_None_wdef(self): 
        self.assertRaises(TypeError, self.module.gcd, *[None, None])

    def test_gcd_all_attr_MetaParam_wdef(self): 
        self.assertRaises(TypeError, self.module.gcd, *[None, None])

    def test_gcd_604b42cbb4164237b1770e2b863f1734(self): 
        Param1 = type('',(object,), {})()
        Param2 = type('',(object,), {})()
        self.assertRaises(TypeError, self.module.gcd, *[Param1, Param2])

    def test_gcd_a445f4a1ff4243ec9058bc3a4e272e69(self): 
        Param2 = type('',(object,), {})()
        self.assertRaises(TypeError, self.module.gcd, *[0, Param2])

    def test_gcd_572639ff8e9e4cdda7fc4157f65270a4(self): 
        self.assertNotRaises(self.module.gcd, *[0, 0])
        self.assertEqual(self.module.gcd(*[0, 0]), 0, 'incorrect function return value encountered')


if __name__ == '__main__':
    unittest.main()
