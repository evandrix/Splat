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
        self.module = __import__('fib')
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

    def test_fib_recursive_all_None(self): 
        self.assertRaises(TypeError, self.module.fib_recursive, *[None])

    def test_fib_recursive_all_attr_None_wdef(self): 
        self.assertRaises(TypeError, self.module.fib_recursive, *[None])

    def test_fib_recursive_all_attr_MetaParam_wdef(self): 
        self.assertRaises(TypeError, self.module.fib_recursive, *[None])

    def test_fib_recursive_0a604a3a399f477d8d806d36641d9f41(self): 
        Param1 = type('',(object,), {})()
        self.assertRaises(TypeError, self.module.fib_recursive, *[Param1])

    def test_fib_recursive_58584817a07a42038b6455d65d2c6480(self): 
        self.assertNotRaises(self.module.fib_recursive, *[0])
        self.assertEqual(self.module.fib_recursive(*[0]), 0, 'incorrect function return value encountered')

    def test_fib_recursive_4372640288(self): 
        self.assertEqual(0, self.module.fib_recursive(0))

    def test_fib_recursive_4372640192(self): 
        self.assertEqual(3, self.module.fib_recursive(4))

    def test_fib_recursive_4372640096(self): 
        self.assertEqual(21, self.module.fib_recursive(8))

    def test_fib_recursive_4372640264(self): 
        self.assertEqual(1, self.module.fib_recursive(1))

    def test_fib_recursive_4372640168(self): 
        self.assertEqual(5, self.module.fib_recursive(5))

    def test_fib_recursive_4372640048(self): 
        self.assertEqual(55, self.module.fib_recursive(10))

    def test_fib_recursive_4372640072(self): 
        self.assertEqual(34, self.module.fib_recursive(9))

    def test_fib_recursive_4372640144(self): 
        self.assertEqual(8, self.module.fib_recursive(6))

    def test_fib_recursive_4372640240(self): 
        self.assertEqual(1, self.module.fib_recursive(2))

    def test_fib_recursive_4372640216(self): 
        self.assertEqual(2, self.module.fib_recursive(3))

    def test_fib_recursive_4372640120(self): 
        self.assertEqual(13, self.module.fib_recursive(7))

    def test_fib_recursive_4372640024(self): 
        self.assertEqual(89, self.module.fib_recursive(11))


if __name__ == '__main__':
    unittest.main()
