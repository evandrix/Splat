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
        self.module = __import__('median3')
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

    def test_median_all_None(self): 
        self.assertRaises(TypeError, self.module.median, *[None])

    def test_median_all_attr_None_wdef(self): 
        self.assertNotRaises(self.module.median, *[{'sort': None}])
        self.assertEqual(self.module.median(*[{'sort': None}]), 'sort', 'incorrect function return value encountered')

    def test_median_all_attr_MetaParam_wdef(self): 
        Param1 = type('',(object,), {})()
        Param1_sort = type('',(object,), {})()
        Param1.sort = Param1_sort
        self.assertRaises(TypeError, self.module.median, *[Param1])

    def test_median_be42a443781b4c11a3271e4640fc0245(self): 
        Param1 = type('',(object,), {})()
        Param1_sort = type('',(object,), {})()
        Param1.sort = Param1_sort
        self.assertRaises(TypeError, self.module.median, *[Param1])

    def test_median_a3028104e19b4eedb6803c5a8a9453b1(self): 
        self.assertRaises(ArithmeticError, self.module.median, *[()])

    def test_median_3fbec70ed75f4301814ad715d05f713a(self): 
        self.assertNotRaises(self.module.median, *[(-663,)])
        self.assertEqual(self.module.median(*[(-663,)]), -663, 'incorrect function return value encountered')

    def test_median_6b2b67cbfb874e29a160db7ed1600480(self): 
        self.assertNotRaises(self.module.median, *[(-179,)])
        self.assertEqual(self.module.median(*[(-179,)]), -179, 'incorrect function return value encountered')

    def test_median_59187225faf24738a7a56f370c697fbc(self): 
        self.assertNotRaises(self.module.median, *[(1638917825854042004, 3917868969821641529)])
        self.assertEqual(self.module.median(*[(1638917825854042004, 3917868969821641529)]), 2.778393397837842e+18, 'incorrect function return value encountered')

    def test_median_a7bd91e802e4401491f4d3a10305e642(self): 
        self.assertNotRaises(self.module.median, *[(0, 0, 0)])
        self.assertEqual(self.module.median(*[(0, 0, 0)]), 0, 'incorrect function return value encountered')

    def test_median_832b6f20a9024607acdafc39615b9b4a(self): 
        self.assertNotRaises(self.module.median, *[(-677, -19, -302, -568)])
        self.assertEqual(self.module.median(*[(-677, -19, -302, -568)]), -435.0, 'incorrect function return value encountered')


if __name__ == '__main__':
    unittest.main()
