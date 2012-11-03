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
        self.module = __import__('bucket_sort')
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

    def test_bucketsort_all_None(self): 
        self.assertRaises(TypeError, self.module.bucketsort, *[None, None])

    def test_bucketsort_all_attr_None_wdef(self): 
        self.assertRaises(TypeError, self.module.bucketsort, *[None, None])

    def test_bucketsort_all_attr_MetaParam_wdef(self): 
        self.assertRaises(TypeError, self.module.bucketsort, *[None, None])

    def test_bucketsort_8eb42d9d642e43bf9fc9f98e21819c36(self): 
        Param1 = type('',(object,), {})()
        Param2 = type('',(object,), {})()
        self.assertRaises(TypeError, self.module.bucketsort, *[Param1, Param2])

    def test_bucketsort_124ea31c8c2949e09903c52d1783379b(self): 
        Param1 = type('',(object,), {})()
        self.assertRaises(TypeError, self.module.bucketsort, *[Param1, -1023])

    def test_bucketsort_c68126a7fdfb4305ac7254049bf4feba(self): 
        self.assertNotRaises(self.module.bucketsort, *[(), -1023])
        self.assertEqual(self.module.bucketsort(*[(), -1023]), [], 'incorrect function return value encountered')

    def test_bucketsort_1fcb61f2ab91461c97f285096f817609(self): 
        self.assertNotRaises(self.module.bucketsort, *[(), -1023])
        self.assertEqual(self.module.bucketsort(*[(), -1023]), [], 'incorrect function return value encountered')

    def test_bucketsort_e86a8586f18040dcaaffb862b7b9a050(self): 
        self.assertNotRaises(self.module.bucketsort, *[(-937, -935, -313, -824, -171, -982, -662, -892, -612, -971), 1021])
        self.assertEqual(self.module.bucketsort(*[(-937, -935, -313, -824, -171, -982, -662, -892, -612, -971), 1021]), [39, 50, 84, 86, 129, 197, 359, 409, 708, 850], 'incorrect function return value encountered')


if __name__ == '__main__':
    unittest.main()
