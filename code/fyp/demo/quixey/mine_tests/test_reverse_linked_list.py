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
        self.module = __import__('reverse_linked_list')
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

    def test_reverse_linked_list_all_None(self): 
        self.assertNotRaises(self.module.reverse_linked_list, *[None])
        self.assertIsNone(self.module.reverse_linked_list(*[None]))

    def test_reverse_linked_list_all_attr_None_wdef(self): 
        self.assertRaises(AttributeError, self.module.reverse_linked_list, *[{'successor': None}])

    def test_reverse_linked_list_all_attr_MetaParam_wdef(self): 
        Param1 = type('',(object,), {})()
        Param1.successor = None
        self.assertRaises(AttributeError, self.module.reverse_linked_list, *[Param1])

    def test_reverse_linked_list_78e83babee124dc78d85cf99b13ab47c(self): 
        Param1 = type('',(object,), {})()
        Param1.successor = None
        self.assertNotRaises(self.module.reverse_linked_list, *[Param1])
        self.assertEqualClassName(self.module.reverse_linked_list(*[Param1]), 'Param1', 'incorrect class name for return value encountered')
        self.assertEqualAttrs(self.module.reverse_linked_list(*[Param1]), '{"index": 1, "dct": {"successor": {"index": 1, "dct": {}, "attr": "successor"}}, "attr": null, "successor": null}', 'incorrect attributes for return value encountered')


if __name__ == '__main__':
    unittest.main()
