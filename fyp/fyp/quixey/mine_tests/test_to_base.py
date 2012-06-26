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
        self.module = __import__('to_base')
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

    def test_to_base_all_None(self): 
        self.assertNotRaises(self.module.to_base, *[None, None])
        self.assertEqual(self.module.to_base(*[None, None]), '', 'incorrect function return value encountered')

    def test_to_base_all_attr_None_wdef(self): 
        self.assertNotRaises(self.module.to_base, *[None, None])
        self.assertEqual(self.module.to_base(*[None, None]), '', 'incorrect function return value encountered')

    def test_to_base_all_attr_MetaParam_wdef(self): 
        self.assertNotRaises(self.module.to_base, *[None, None])
        self.assertEqual(self.module.to_base(*[None, None]), '', 'incorrect function return value encountered')

    def test_to_base_71f87d4761944adcb0d25f5eab6fd69f(self): 
        Param1 = type('',(object,), {})()
        Param2 = type('',(object,), {})()
        self.assertRaises(TypeError, self.module.to_base, *[Param1, Param2])

    def test_to_base_e89689defa5948508a42d1ec46bee488(self): 
        Param2 = type('',(object,), {})()
        self.assertNotRaises(self.module.to_base, *[0, Param2])
        self.assertEqual(self.module.to_base(*[0, Param2]), '', 'incorrect function return value encountered')

    def test_to_base_f3e3350297cc4c02b1ebe493f1fd1e32(self): 
        Param2 = type('',(object,), {})()
        self.assertNotRaises(self.module.to_base, *[-1, Param2])
        self.assertEqual(self.module.to_base(*[-1, Param2]), '', 'incorrect function return value encountered')

    def test_to_base_a821b82efa9148a2badfc9263e7c7c2f(self): 
        Param2 = type('',(object,), {})()
        self.assertNotRaises(self.module.to_base, *[-5023432220746140167, Param2])
        self.assertEqual(self.module.to_base(*[-5023432220746140167, Param2]), '', 'incorrect function return value encountered')

    def test_to_base_fc515b779f00487c95b426bd7c45ca2f(self): 
        Param2 = type('',(object,), {})()
        self.assertNotRaises(self.module.to_base, *[-7577355511772500766, Param2])
        self.assertEqual(self.module.to_base(*[-7577355511772500766, Param2]), '', 'incorrect function return value encountered')

    def test_to_base_721d92e4c1ef4910b5beb9fb95bb3932(self): 
        Param2 = type('',(object,), {})()
        self.assertNotRaises(self.module.to_base, *[-7000422558840710914, Param2])
        self.assertEqual(self.module.to_base(*[-7000422558840710914, Param2]), '', 'incorrect function return value encountered')

    def test_to_base_9d2a61ac30ee414e9cd3edb3b93f0773(self): 
        Param2 = type('',(object,), {})()
        self.assertNotRaises(self.module.to_base, *[-803191160365812776, Param2])
        self.assertEqual(self.module.to_base(*[-803191160365812776, Param2]), '', 'incorrect function return value encountered')

    def test_to_base_e08ad42d76cd4295a47ed66cda02170a(self): 
        Param2 = type('',(object,), {})()
        self.assertNotRaises(self.module.to_base, *[-1548349315154523096, Param2])
        self.assertEqual(self.module.to_base(*[-1548349315154523096, Param2]), '', 'incorrect function return value encountered')

    def test_to_base_65d5270e53a048779a66c05306407083(self): 
        Param2 = type('',(object,), {})()
        self.assertNotRaises(self.module.to_base, *[-2679134794659684595, Param2])
        self.assertEqual(self.module.to_base(*[-2679134794659684595, Param2]), '', 'incorrect function return value encountered')

    def test_to_base_472e13bd6645404ba1a9071122dbbd5d(self): 
        Param2 = type('',(object,), {})()
        self.assertNotRaises(self.module.to_base, *[-330, Param2])
        self.assertEqual(self.module.to_base(*[-330, Param2]), '', 'incorrect function return value encountered')

    def test_to_base_8afd0fd9289b4b8c86208006975b4365(self): 
        Param2 = type('',(object,), {})()
        self.assertNotRaises(self.module.to_base, *[-298, Param2])
        self.assertEqual(self.module.to_base(*[-298, Param2]), '', 'incorrect function return value encountered')

    def test_to_base_fb849d4886de48fdbb7713afff783646(self): 
        Param2 = type('',(object,), {})()
        self.assertNotRaises(self.module.to_base, *[-30, Param2])
        self.assertEqual(self.module.to_base(*[-30, Param2]), '', 'incorrect function return value encountered')

    def test_to_base_88febad97ce14f94a6ee993b2cceff41(self): 
        Param2 = type('',(object,), {})()
        self.assertNotRaises(self.module.to_base, *[0, Param2])
        self.assertEqual(self.module.to_base(*[0, Param2]), '', 'incorrect function return value encountered')

    def test_to_base_82d7192fa17545bc9785186a290abc53(self): 
        Param2 = type('',(object,), {})()
        self.assertNotRaises(self.module.to_base, *[0, Param2])
        self.assertEqual(self.module.to_base(*[0, Param2]), '', 'incorrect function return value encountered')

    def test_to_base_c08cae50720145bdb39e38cb01b1a09f(self): 
        Param2 = type('',(object,), {})()
        self.assertNotRaises(self.module.to_base, *[0, Param2])
        self.assertEqual(self.module.to_base(*[0, Param2]), '', 'incorrect function return value encountered')


if __name__ == '__main__':
    unittest.main()
