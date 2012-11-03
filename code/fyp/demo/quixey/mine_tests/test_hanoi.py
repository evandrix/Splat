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
        self.module = __import__('hanoi')
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

    def test_hanoi_all_None(self): 
        self.assertNotRaises(self.module.hanoi, *[None, None, None])
        self.assertEqual(self.module.hanoi(*[None, None, None]), [], 'incorrect function return value encountered')

    def test_hanoi_all_attr_None_wdef(self): 
        self.assertNotRaises(self.module.hanoi, *[None, 1, 3])
        self.assertEqual(self.module.hanoi(*[None, 1, 3]), [], 'incorrect function return value encountered')

    def test_hanoi_all_attr_MetaParam_wdef(self): 
        self.assertNotRaises(self.module.hanoi, *[None, 1, 3])
        self.assertEqual(self.module.hanoi(*[None, 1, 3]), [], 'incorrect function return value encountered')

    def test_hanoi_0b63271647c14c87ab22afaf823e1e49(self): 
        Param1 = type('',(object,), {})()
        self.assertRaises(TypeError, self.module.hanoi, *[Param1, 1, 3])

    def test_hanoi_d1bc47e057f0444fbc01712142f2b28a(self): 
        self.assertNotRaises(self.module.hanoi, *[0, 1, 3])
        self.assertEqual(self.module.hanoi(*[0, 1, 3]), [], 'incorrect function return value encountered')

    def test_hanoi_ceb8fcecda194d59a618669795cc749e(self): 
        self.assertNotRaises(self.module.hanoi, *[1, 1, 3])
        self.assertEqual(self.module.hanoi(*[1, 1, 3]), [(1, 3)], 'incorrect function return value encountered')

    def test_hanoi_c338439d5c894ade871999a24d8ef896(self): 
        self.assertNotRaises(self.module.hanoi, *[2, 1, 3])
        self.assertEqual(self.module.hanoi(*[2, 1, 3]), [(1, 2), (1, 3), (2, 3)], 'incorrect function return value encountered')

    def test_hanoi_56208f7bcec743268b9be8a325e37b0b(self): 
        self.assertNotRaises(self.module.hanoi, *[3, 1, 3])
        self.assertEqual(self.module.hanoi(*[3, 1, 3]), [(1, 3), (1, 2), (3, 2), (1, 3), (2, 1), (2, 3), (1, 3)], 'incorrect function return value encountered')

    def test_hanoi_66b9a73f52044f6eadd6049cd74a56b7(self): 
        self.assertNotRaises(self.module.hanoi, *[-5128545559296686203, 1, 3])
        self.assertEqual(self.module.hanoi(*[-5128545559296686203, 1, 3]), [], 'incorrect function return value encountered')

    def test_hanoi_94909523aadc4ed2a1fe3de31dc8b316(self): 
        self.assertNotRaises(self.module.hanoi, *[-4976984656924790665, 1, 3])
        self.assertEqual(self.module.hanoi(*[-4976984656924790665, 1, 3]), [], 'incorrect function return value encountered')

    def test_hanoi_863280977f9749c6a5a70872b236586e(self): 
        self.assertNotRaises(self.module.hanoi, *[-8295385784921821185, 1, 3])
        self.assertEqual(self.module.hanoi(*[-8295385784921821185, 1, 3]), [], 'incorrect function return value encountered')

    def test_hanoi_021021e2c86b43b89f63fa9bd2ecc769(self): 
        self.assertNotRaises(self.module.hanoi, *[-3500611111582276530, 1, 3])
        self.assertEqual(self.module.hanoi(*[-3500611111582276530, 1, 3]), [], 'incorrect function return value encountered')

    def test_hanoi_b25c1688bee94ce59cc4c52b872d1b49(self): 
        self.assertNotRaises(self.module.hanoi, *[-938799931236625225, 1, 3])
        self.assertEqual(self.module.hanoi(*[-938799931236625225, 1, 3]), [], 'incorrect function return value encountered')

    def test_hanoi_b3b2c9d77b14433794a98767bb9d2670(self): 
        self.assertNotRaises(self.module.hanoi, *[-3487361269994774902, 1, 3])
        self.assertEqual(self.module.hanoi(*[-3487361269994774902, 1, 3]), [], 'incorrect function return value encountered')

    def test_hanoi_58e2d07ccbce4d88ad7cb382b7383ba2(self): 
        self.assertNotRaises(self.module.hanoi, *[-149, 1, 3])
        self.assertEqual(self.module.hanoi(*[-149, 1, 3]), [], 'incorrect function return value encountered')

    def test_hanoi_218b1f4a1c01411f8f452869e7553e46(self): 
        self.assertNotRaises(self.module.hanoi, *[-169, 1, 3])
        self.assertEqual(self.module.hanoi(*[-169, 1, 3]), [], 'incorrect function return value encountered')

    def test_hanoi_b244132442bd49bfb54ec921de77eaf9(self): 
        self.assertNotRaises(self.module.hanoi, *[-219, 1, 3])
        self.assertEqual(self.module.hanoi(*[-219, 1, 3]), [], 'incorrect function return value encountered')

    def test_hanoi_c447ec50a03a4f7aabc76a02a255f818(self): 
        self.assertNotRaises(self.module.hanoi, *[0, 1, 3])
        self.assertEqual(self.module.hanoi(*[0, 1, 3]), [], 'incorrect function return value encountered')

    def test_hanoi_1473176dfe924ad7bc62e8a4dce700a2(self): 
        self.assertNotRaises(self.module.hanoi, *[0, 1, 3])
        self.assertEqual(self.module.hanoi(*[0, 1, 3]), [], 'incorrect function return value encountered')

    def test_hanoi_bffad8bf7bec4aa68515b5a1d22474d8(self): 
        self.assertNotRaises(self.module.hanoi, *[0, 1, 3])
        self.assertEqual(self.module.hanoi(*[0, 1, 3]), [], 'incorrect function return value encountered')


if __name__ == '__main__':
    unittest.main()
