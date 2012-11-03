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
        self.module = __import__('shortest_paths')
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

    def test_shortest_paths_all_None(self): 
        self.assertRaises(TypeError, self.module.shortest_paths, *[None, None])

    def test_shortest_paths_all_attr_None_wdef(self): 
        self.assertRaises(ValueError, self.module.shortest_paths, *[None, {'items': None}])

    def test_shortest_paths_all_attr_MetaParam_wdef(self): 
        Param2 = type('',(object,), {})()
        Param2_items = type('',(object,), {})()
        Param2.items = Param2_items
        self.assertRaises(TypeError, self.module.shortest_paths, *[None, Param2])

    def test_shortest_paths_d8afc2a3785b46ab8c543044d4f3e337(self): 
        Param1 = type('',(object,), {})()
        Param2 = type('',(object,), {})()
        Param2_items = type('',(object,), {})()
        Param2.items = Param2_items
        self.assertRaises(TypeError, self.module.shortest_paths, *[Param1, Param2])

    def test_shortest_paths_8af9247df6c44f5dba7875ec8ed8429d(self): 
        Param1 = type('',(object,), {})()
        self.assertNotRaises(self.module.shortest_paths, *[Param1, ()])
        self.assertEqual(self.module.shortest_paths(*[Param1, ()]), {Param1: 0}, 'incorrect function return value encountered')

    def test_shortest_paths_5aefbd323caa4acaa1e502979c42af62(self): 
        Param1 = type('',(object,), {})()
        self.assertNotRaises(self.module.shortest_paths, *[Param1, ()])
        self.assertEqual(self.module.shortest_paths(*[Param1, ()]), {Param1: 0}, 'incorrect function return value encountered')


if __name__ == '__main__':
    unittest.main()
