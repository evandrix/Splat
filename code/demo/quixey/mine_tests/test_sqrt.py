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
        self.module = __import__('sqrt')
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

    def test_sqrt_all_None(self): 
        self.assertRaises(TypeError, self.module.sqrt, *[None, None])

    def test_sqrt_all_attr_None_wdef(self): 
        self.assertRaises(TypeError, self.module.sqrt, *[None, None])

    def test_sqrt_all_attr_MetaParam_wdef(self): 
        self.assertRaises(TypeError, self.module.sqrt, *[None, None])

    def test_sqrt_d57034ce4d494cf3852639034fbc95e9(self): 
        Param1 = type('',(object,), {})()
        Param2 = type('',(object,), {})()
        self.assertRaises(TypeError, self.module.sqrt, *[Param1, Param2])

    def test_sqrt_d104cb8833d84edf83deac5b71a19bfe(self): 
        Param2 = type('',(object,), {})()
        self.assertNotRaises(self.module.sqrt, *[0, Param2])
        self.assertEqual(self.module.sqrt(*[0, Param2]), 0, 'incorrect function return value encountered')

    def test_sqrt_b78231ba32314517a75e6a4361e7710f(self): 
        Param2 = type('',(object,), {})()
        self.assertNotRaises(self.module.sqrt, *[2, Param2])
        self.assertEqual(self.module.sqrt(*[2, Param2]), 1, 'incorrect function return value encountered')

    def test_sqrt_716a7b76ab454afb92cb560a6528452a(self): 
        Param2 = type('',(object,), {})()
        self.assertNotRaises(self.module.sqrt, *[-6475311238485395723, Param2])
        self.assertEqual(self.module.sqrt(*[-6475311238485395723, Param2]), -3237655619242697862, 'incorrect function return value encountered')

    def test_sqrt_17c5117f091346899ddf61eb510b5c9c(self): 
        Param2 = type('',(object,), {})()
        self.assertNotRaises(self.module.sqrt, *[-7104629630854491654, Param2])
        self.assertEqual(self.module.sqrt(*[-7104629630854491654, Param2]), -3552314815427245827, 'incorrect function return value encountered')

    def test_sqrt_1bb3960cd3264b0bb45eff3ba31af0bd(self): 
        Param2 = type('',(object,), {})()
        self.assertNotRaises(self.module.sqrt, *[-9114422441613373097, Param2])
        self.assertEqual(self.module.sqrt(*[-9114422441613373097, Param2]), -4557211220806686549, 'incorrect function return value encountered')

    def test_sqrt_8c8f1eaffe6b4d93849d5a5320b952d4(self): 
        Param2 = type('',(object,), {})()
        self.assertNotRaises(self.module.sqrt, *[-2545806423944103120, Param2])
        self.assertEqual(self.module.sqrt(*[-2545806423944103120, Param2]), -1272903211972051560, 'incorrect function return value encountered')

    def test_sqrt_ffb6f44eeb7440ec815be47a64a07e2c(self): 
        Param2 = type('',(object,), {})()
        self.assertNotRaises(self.module.sqrt, *[-2537854860753931133, Param2])
        self.assertEqual(self.module.sqrt(*[-2537854860753931133, Param2]), -1268927430376965567, 'incorrect function return value encountered')

    def test_sqrt_47474bb924d14ca18467f2765de4a513(self): 
        Param2 = type('',(object,), {})()
        self.assertNotRaises(self.module.sqrt, *[-104054748580964746, Param2])
        self.assertEqual(self.module.sqrt(*[-104054748580964746, Param2]), -52027374290482373, 'incorrect function return value encountered')

    def test_sqrt_4fac19b900004e20b41594d5da5bc359(self): 
        Param2 = type('',(object,), {})()
        self.assertNotRaises(self.module.sqrt, *[-801, Param2])
        self.assertEqual(self.module.sqrt(*[-801, Param2]), -401, 'incorrect function return value encountered')

    def test_sqrt_b14b99c3bb794fb8b527b454ff28fb6f(self): 
        Param2 = type('',(object,), {})()
        self.assertNotRaises(self.module.sqrt, *[-294, Param2])
        self.assertEqual(self.module.sqrt(*[-294, Param2]), -147, 'incorrect function return value encountered')

    def test_sqrt_8999a3b0f0d5414f9b248538320c5d4d(self): 
        Param2 = type('',(object,), {})()
        self.assertNotRaises(self.module.sqrt, *[-406, Param2])
        self.assertEqual(self.module.sqrt(*[-406, Param2]), -203, 'incorrect function return value encountered')

    def test_sqrt_42824aabd4384b49b3973ea49e0b9c57(self): 
        Param2 = type('',(object,), {})()
        self.assertNotRaises(self.module.sqrt, *[0, Param2])
        self.assertEqual(self.module.sqrt(*[0, Param2]), 0, 'incorrect function return value encountered')

    def test_sqrt_a65c4591bdb2465590edbea4a498c1e8(self): 
        Param2 = type('',(object,), {})()
        self.assertNotRaises(self.module.sqrt, *[0, Param2])
        self.assertEqual(self.module.sqrt(*[0, Param2]), 0, 'incorrect function return value encountered')

    def test_sqrt_d30950561c934da6ad6f78aa700c8981(self): 
        Param2 = type('',(object,), {})()
        self.assertNotRaises(self.module.sqrt, *[0, Param2])
        self.assertEqual(self.module.sqrt(*[0, Param2]), 0, 'incorrect function return value encountered')

    def test_sqrt_e34ef9f3256246ceaeb8cc320d1884db(self): 
        Param2 = type('',(object,), {})()
        self.assertNotRaises(self.module.sqrt, *[4257219998233686503, Param2])
        self.assertEqual(self.module.sqrt(*[4257219998233686503, Param2]), 2128609999116843251, 'incorrect function return value encountered')

    def test_sqrt_34564f95b5254960acb7fa419476a690(self): 
        Param2 = type('',(object,), {})()
        self.assertNotRaises(self.module.sqrt, *[4258015124872130863, Param2])
        self.assertEqual(self.module.sqrt(*[4258015124872130863, Param2]), 2129007562436065431, 'incorrect function return value encountered')

    def test_sqrt_2d8b9a1d35a4486296a12afa60274dea(self): 
        Param2 = type('',(object,), {})()
        self.assertNotRaises(self.module.sqrt, *[3726399790450133121, Param2])
        self.assertEqual(self.module.sqrt(*[3726399790450133121, Param2]), 1863199895225066560, 'incorrect function return value encountered')

    def test_sqrt_ee611b25e8e347ca96509ae48bd676cd(self): 
        Param2 = type('',(object,), {})()
        self.assertNotRaises(self.module.sqrt, *[281, Param2])
        self.assertEqual(self.module.sqrt(*[281, Param2]), 140, 'incorrect function return value encountered')

    def test_sqrt_7ee39a1bb24c4657a352ac17568817bf(self): 
        Param2 = type('',(object,), {})()
        self.assertNotRaises(self.module.sqrt, *[493, Param2])
        self.assertEqual(self.module.sqrt(*[493, Param2]), 246, 'incorrect function return value encountered')

    def test_sqrt_671fcdecc18c45c0af25faa8f19815f9(self): 
        Param2 = type('',(object,), {})()
        self.assertNotRaises(self.module.sqrt, *[706, Param2])
        self.assertEqual(self.module.sqrt(*[706, Param2]), 353, 'incorrect function return value encountered')

    def test_sqrt_67f634c4c7474f53990287afa7d4ed17(self): 
        Param2 = type('',(object,), {})()
        self.assertNotRaises(self.module.sqrt, *[5574667725761928877, Param2])
        self.assertEqual(self.module.sqrt(*[5574667725761928877, Param2]), 2787333862880964438, 'incorrect function return value encountered')

    def test_sqrt_6f530493d28c44e39ed6bacd90ed745b(self): 
        Param2 = type('',(object,), {})()
        self.assertNotRaises(self.module.sqrt, *[5113539389512822649, Param2])
        self.assertEqual(self.module.sqrt(*[5113539389512822649, Param2]), 2556769694756411324, 'incorrect function return value encountered')

    def test_sqrt_363e57453243486f812b657f30b54913(self): 
        Param2 = type('',(object,), {})()
        self.assertNotRaises(self.module.sqrt, *[7707977529837403030, Param2])
        self.assertEqual(self.module.sqrt(*[7707977529837403030, Param2]), 3853988764918701515, 'incorrect function return value encountered')


if __name__ == '__main__':
    unittest.main()
