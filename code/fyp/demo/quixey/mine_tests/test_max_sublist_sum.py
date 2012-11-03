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
        self.module = __import__('max_sublist_sum')
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

    def test_max_sublist_sum_all_None(self): 
        self.assertRaises(TypeError, self.module.max_sublist_sum, *[None])

    def test_max_sublist_sum_all_attr_None_wdef(self): 
        self.assertRaises(TypeError, self.module.max_sublist_sum, *[None])

    def test_max_sublist_sum_all_attr_MetaParam_wdef(self): 
        self.assertRaises(TypeError, self.module.max_sublist_sum, *[None])

    def test_max_sublist_sum_5ec27ef40b424dd8a351df325ab0a68b(self): 
        Param1 = type('',(object,), {})()
        self.assertRaises(TypeError, self.module.max_sublist_sum, *[Param1])

    def test_max_sublist_sum_ee2c6df3436c4c1fae79343f0434678d(self): 
        self.assertNotRaises(self.module.max_sublist_sum, *[()])
        self.assertEqual(self.module.max_sublist_sum(*[()]), 0, 'incorrect function return value encountered')

    def test_max_sublist_sum_7794de64cf09493b993bb0009e0b8cd7(self): 
        self.assertNotRaises(self.module.max_sublist_sum, *[()])
        self.assertEqual(self.module.max_sublist_sum(*[()]), 0, 'incorrect function return value encountered')

    def test_max_sublist_sum_ada928bdd5df47879641fb2f0d760b74(self): 
        self.assertNotRaises(self.module.max_sublist_sum, *[(566,)])
        self.assertEqual(self.module.max_sublist_sum(*[(566,)]), 566, 'incorrect function return value encountered')

    def test_max_sublist_sum_ba6dfdfae79147c6804a6acadbe046a0(self): 
        self.assertNotRaises(self.module.max_sublist_sum, *[(6293634267175511825, 5361191959523010245)])
        self.assertEqual(self.module.max_sublist_sum(*[(6293634267175511825, 5361191959523010245)]), 11654826226698522070L, 'incorrect function return value encountered')

    def test_max_sublist_sum_0fd5c195d8474a3288afaf12edccfa27(self): 
        self.assertNotRaises(self.module.max_sublist_sum, *[(7128359841165267673, 7555282960853503650, 7177237911764244618)])
        self.assertEqual(self.module.max_sublist_sum(*[(7128359841165267673, 7555282960853503650, 7177237911764244618)]), 21860880713783015941L, 'incorrect function return value encountered')

    def test_max_sublist_sum_793fecf8a2424e71a8a5b890354997fd(self): 
        self.assertNotRaises(self.module.max_sublist_sum, *[(888, 1016, 991, 893)])
        self.assertEqual(self.module.max_sublist_sum(*[(888, 1016, 991, 893)]), 3788, 'incorrect function return value encountered')

    def test_max_sublist_sum_b83492182eae4e9e9281989803c20468(self): 
        self.assertNotRaises(self.module.max_sublist_sum, *[(-408510380006951514, -2719381258784219339, -3609314548029048618, -2281897032238002282, -4485287994799647027)])
        self.assertEqual(self.module.max_sublist_sum(*[(-408510380006951514, -2719381258784219339, -3609314548029048618, -2281897032238002282, -4485287994799647027)]), 0, 'incorrect function return value encountered')


if __name__ == '__main__':
    unittest.main()
