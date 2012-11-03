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
        self.module = __import__('bitcount')
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

    def test_bitcount_all_None(self): 
        self.assertNotRaises(self.module.bitcount, *[None])
        self.assertEqual(self.module.bitcount(*[None]), 0, 'incorrect function return value encountered')

    def test_bitcount_all_attr_None_wdef(self): 
        self.assertNotRaises(self.module.bitcount, *[None])
        self.assertEqual(self.module.bitcount(*[None]), 0, 'incorrect function return value encountered')

    def test_bitcount_all_attr_MetaParam_wdef(self): 
        self.assertNotRaises(self.module.bitcount, *[None])
        self.assertEqual(self.module.bitcount(*[None]), 0, 'incorrect function return value encountered')

    def test_bitcount_b6e27973918649ab887bf84ee087b940(self): 
        Param1 = type('',(object,), {})()
        self.assertRaises(TypeError, self.module.bitcount, *[Param1])

    def test_bitcount_8210a80fdf064dc88174592106183793(self): 
        self.assertNotRaises(self.module.bitcount, *[0])
        self.assertEqual(self.module.bitcount(*[0]), 0, 'incorrect function return value encountered')

    def test_bitcount_72561c8fafd74fb8bd4e17ae1623fbb1(self): 
        self.assertNotRaises(self.module.bitcount, *[1])
        self.assertEqual(self.module.bitcount(*[1]), 1, 'incorrect function return value encountered')

    def test_bitcount_82f7044e40eb491d97848740148bd39e(self): 
        self.assertNotRaises(self.module.bitcount, *[0])
        self.assertEqual(self.module.bitcount(*[0]), 0, 'incorrect function return value encountered')

    def test_bitcount_3fb9460de45b42b89291b9e582c597ae(self): 
        self.assertNotRaises(self.module.bitcount, *[0])
        self.assertEqual(self.module.bitcount(*[0]), 0, 'incorrect function return value encountered')

    def test_bitcount_23b67cbbcc0041f2947a8f484d455fff(self): 
        self.assertNotRaises(self.module.bitcount, *[0])
        self.assertEqual(self.module.bitcount(*[0]), 0, 'incorrect function return value encountered')

    def test_bitcount_e082e7e6d1114ec39144cdcb8096077e(self): 
        self.assertNotRaises(self.module.bitcount, *[889005278810437270])
        self.assertEqual(self.module.bitcount(*[889005278810437270]), 31, 'incorrect function return value encountered')

    def test_bitcount_d2dd940300ca43a7aeed6257b4917d3b(self): 
        self.assertNotRaises(self.module.bitcount, *[1056529059130503180])
        self.assertEqual(self.module.bitcount(*[1056529059130503180]), 27, 'incorrect function return value encountered')

    def test_bitcount_5232ef7820bb4de7a06400dc28aacebc(self): 
        self.assertNotRaises(self.module.bitcount, *[1721735051828196619])
        self.assertEqual(self.module.bitcount(*[1721735051828196619]), 32, 'incorrect function return value encountered')

    def test_bitcount_13e5cd2453ed4bbfbdb9de752cc7233a(self): 
        self.assertNotRaises(self.module.bitcount, *[830])
        self.assertEqual(self.module.bitcount(*[830]), 7, 'incorrect function return value encountered')

    def test_bitcount_7831a8906ee5437595733c23a97d1de4(self): 
        self.assertNotRaises(self.module.bitcount, *[993])
        self.assertEqual(self.module.bitcount(*[993]), 6, 'incorrect function return value encountered')

    def test_bitcount_c2689e80beed4bfb81d0661d9c2bbf00(self): 
        self.assertNotRaises(self.module.bitcount, *[123])
        self.assertEqual(self.module.bitcount(*[123]), 6, 'incorrect function return value encountered')

    def test_bitcount_aad7a2c47db04faab37ba40b39ece1a2(self): 
        self.assertNotRaises(self.module.bitcount, *[9194380262245548427])
        self.assertEqual(self.module.bitcount(*[9194380262245548427]), 25, 'incorrect function return value encountered')

    def test_bitcount_12b28f6e85f546aeb4ac6ce0eeaf4531(self): 
        self.assertNotRaises(self.module.bitcount, *[8870994521099122006])
        self.assertEqual(self.module.bitcount(*[8870994521099122006]), 29, 'incorrect function return value encountered')

    def test_bitcount_78f6f83bfb3a4ba78ac962436759928d(self): 
        self.assertNotRaises(self.module.bitcount, *[7068870795393364737])
        self.assertEqual(self.module.bitcount(*[7068870795393364737]), 27, 'incorrect function return value encountered')


if __name__ == '__main__':
    unittest.main()
