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
        self.module = __import__('median2')
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

    def test_median_226ae155ca4f41809eecc12dd2c586da(self): 
        Param1 = type('',(object,), {})()
        Param1_sort = type('',(object,), {})()
        Param1.sort = Param1_sort
        self.assertRaises(TypeError, self.module.median, *[Param1])

    def test_median_4845d0f5604f45acb8765351814c661e(self): 
        self.assertRaises(ArithmeticError, self.module.median, *[()])

    def test_median_63cae9fe99334e8c96079c1369e72cb5(self): 
        self.assertNotRaises(self.module.median, *[(663,)])
        self.assertEqual(self.module.median(*[(663,)]), 663, 'incorrect function return value encountered')

    def test_median_7e9877d8b0fb4c62b5fca93812ebbb88(self): 
        self.assertNotRaises(self.module.median, *[(6040511590601481453,)])
        self.assertEqual(self.module.median(*[(6040511590601481453,)]), 6040511590601481453, 'incorrect function return value encountered')

    def test_median_5ca93ab8c3974c22aeda4a505f39cf33(self): 
        self.assertNotRaises(self.module.median, *[(2203715661962684802, 1752513644035367621)])
        self.assertEqual(self.module.median(*[(2203715661962684802, 1752513644035367621)]), 1.9781146529990262e+18, 'incorrect function return value encountered')

    def test_median_9ce7a9e9c5ee478584d256169df3e6fa(self): 
        self.assertNotRaises(self.module.median, *[(-866, -429, -349)])
        self.assertEqual(self.module.median(*[(-866, -429, -349)]), -429, 'incorrect function return value encountered')

    def test_median_75ae7412bdb143a59943e2af0d49dd3a(self): 
        self.assertNotRaises(self.module.median, *[(0, 0, 0, 0)])
        self.assertEqual(self.module.median(*[(0, 0, 0, 0)]), 0.0, 'incorrect function return value encountered')

    def test_median_eff375bd513948279777dedda2c85eba(self): 
        self.assertNotRaises(self.module.median, *[(8910976753704474463, 5328488970213496862, 5176864687829489842, 7087501662058721504, 7413561733179009339)])
        self.assertEqual(self.module.median(*[(8910976753704474463, 5328488970213496862, 5176864687829489842, 7087501662058721504, 7413561733179009339)]), 7087501662058721504, 'incorrect function return value encountered')


if __name__ == '__main__':
    unittest.main()
