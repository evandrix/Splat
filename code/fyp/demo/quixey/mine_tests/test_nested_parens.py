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
        self.module = __import__('nested_parens')
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

    def test_is_valid_parenthesization_all_None(self): 
        self.assertRaises(TypeError, self.module.is_valid_parenthesization, *[None])

    def test_is_valid_parenthesization_all_attr_None_wdef(self): 
        self.assertRaises(TypeError, self.module.is_valid_parenthesization, *[None])

    def test_is_valid_parenthesization_all_attr_MetaParam_wdef(self): 
        self.assertRaises(TypeError, self.module.is_valid_parenthesization, *[None])

    def test_is_valid_parenthesization_442b4f624122497b89cbf2cbb951fdb9(self): 
        Param1 = type('',(object,), {})()
        self.assertRaises(TypeError, self.module.is_valid_parenthesization, *[Param1])

    def test_is_valid_parenthesization_479021aa540648c6ac0de2a56a7b1cd9(self): 
        self.assertNotRaises(self.module.is_valid_parenthesization, *[()])
        self.assertEqual(self.module.is_valid_parenthesization(*[()]), True, 'incorrect function return value encountered')

    def test_is_valid_parenthesization_87391b55e7ac4a1da92ae09b6a9c628e(self): 
        self.assertNotRaises(self.module.is_valid_parenthesization, *[()])
        self.assertEqual(self.module.is_valid_parenthesization(*[()]), True, 'incorrect function return value encountered')

    def test_is_valid_parenthesization_42ffd74349eb4590b36d0bd2e28ddbf4(self): 
        self.assertNotRaises(self.module.is_valid_parenthesization, *[(-596,)])
        self.assertEqual(self.module.is_valid_parenthesization(*[(-596,)]), False, 'incorrect function return value encountered')

    def test_is_valid_parenthesization_09720ac920c842e88e0b74249b740c40(self): 
        self.assertNotRaises(self.module.is_valid_parenthesization, *[(-3935197669140691210, -438014187441103657)])
        self.assertEqual(self.module.is_valid_parenthesization(*[(-3935197669140691210, -438014187441103657)]), False, 'incorrect function return value encountered')

    def test_is_valid_parenthesization_71d290e6e3db4374bf153c3e03c96487(self): 
        self.assertNotRaises(self.module.is_valid_parenthesization, *[(0, 0, 0)])
        self.assertEqual(self.module.is_valid_parenthesization(*[(0, 0, 0)]), False, 'incorrect function return value encountered')

    def test_is_valid_parenthesization_10b0fe81f438491b948576c1657ef9b7(self): 
        self.assertNotRaises(self.module.is_valid_parenthesization, *[(-2654776536999009788, -421483899870453449, -616978710250790731, -3300587204165786271)])
        self.assertEqual(self.module.is_valid_parenthesization(*[(-2654776536999009788, -421483899870453449, -616978710250790731, -3300587204165786271)]), False, 'incorrect function return value encountered')

    def test_is_valid_parenthesization_0fcdac64980442d7815680296186b2eb(self): 
        self.assertNotRaises(self.module.is_valid_parenthesization, *[(-8323293884479745930, -8120537248255704381, -7449197611837682790, -8328176407763732370, -6504410429045518369)])
        self.assertEqual(self.module.is_valid_parenthesization(*[(-8323293884479745930, -8120537248255704381, -7449197611837682790, -8328176407763732370, -6504410429045518369)]), False, 'incorrect function return value encountered')

    def test_is_valid_parenthesization_6471e16d27f344f2b7ee1f22f34d9165(self): 
        self.assertNotRaises(self.module.is_valid_parenthesization, *[(-7242572002504979143, -8376994950490136336, -5078143269007821074, -5877889100464121379, -4702280649891157478, -5541547734372343134)])
        self.assertEqual(self.module.is_valid_parenthesization(*[(-7242572002504979143, -8376994950490136336, -5078143269007821074, -5877889100464121379, -4702280649891157478, -5541547734372343134)]), False, 'incorrect function return value encountered')


if __name__ == '__main__':
    unittest.main()
