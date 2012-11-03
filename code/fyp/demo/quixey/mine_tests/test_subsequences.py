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
        self.module = __import__('subsequences')
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

    def test_subsequences_all_None(self): 
        self.assertRaises(TypeError, self.module.subsequences, *[None, None, None])

    def test_subsequences_all_attr_None_wdef(self): 
        self.assertRaises(TypeError, self.module.subsequences, *[None, None, None])

    def test_subsequences_all_attr_MetaParam_wdef(self): 
        self.assertRaises(TypeError, self.module.subsequences, *[None, None, None])

    def test_subsequences_2b2a3e0438904416afaee7ca43b470b5(self): 
        Param1 = type('',(object,), {})()
        Param2 = type('',(object,), {})()
        Param3 = type('',(object,), {})()
        self.assertRaises(TypeError, self.module.subsequences, *[Param1, Param2, Param3])

    def test_subsequences_db45c59984cc423d8a263cfc3f2cade7(self): 
        Param1 = type('',(object,), {})()
        Param3 = type('',(object,), {})()
        self.assertRaises(TypeError, self.module.subsequences, *[Param1, 0, Param3])

    def test_subsequences_84fb3989aa6c4a73a504a63d7271b3a9(self): 
        Param1 = type('',(object,), {})()
        self.assertNotRaises(self.module.subsequences, *[Param1, 0, 0])
        self.assertEqual(self.module.subsequences(*[Param1, 0, 0]), [[]], 'incorrect function return value encountered')

    def test_subsequences_2cfa08b0f4ae49a88e39552ba4b44190(self): 
        Param1 = type('',(object,), {})()
        self.assertNotRaises(self.module.subsequences, *[Param1, 1, 0])
        self.assertEqual(self.module.subsequences(*[Param1, 1, 0]), [[]], 'incorrect function return value encountered')

    def test_subsequences_5ac0993375c5496180b7443bc9b05175(self): 
        Param1 = type('',(object,), {})()
        self.assertNotRaises(self.module.subsequences, *[Param1, -7070089453654809380, 0])
        self.assertEqual(self.module.subsequences(*[Param1, -7070089453654809380, 0]), [[]], 'incorrect function return value encountered')

    def test_subsequences_ccf69b171e9d45228d398b5999d3ff85(self): 
        Param1 = type('',(object,), {})()
        self.assertNotRaises(self.module.subsequences, *[Param1, -4855725619510551760, 0])
        self.assertEqual(self.module.subsequences(*[Param1, -4855725619510551760, 0]), [[]], 'incorrect function return value encountered')

    def test_subsequences_7a88ae3fec84488081db93090b6b76ce(self): 
        Param1 = type('',(object,), {})()
        self.assertNotRaises(self.module.subsequences, *[Param1, -6673508855836340420, 0])
        self.assertEqual(self.module.subsequences(*[Param1, -6673508855836340420, 0]), [[]], 'incorrect function return value encountered')

    def test_subsequences_fdf7aad40bb94a268f149f9095fb7f88(self): 
        Param1 = type('',(object,), {})()
        self.assertNotRaises(self.module.subsequences, *[Param1, -1814147055746782354, 0])
        self.assertEqual(self.module.subsequences(*[Param1, -1814147055746782354, 0]), [[]], 'incorrect function return value encountered')

    def test_subsequences_35c213db12204970acba403765b43706(self): 
        Param1 = type('',(object,), {})()
        self.assertNotRaises(self.module.subsequences, *[Param1, -2262356656390433084, 0])
        self.assertEqual(self.module.subsequences(*[Param1, -2262356656390433084, 0]), [[]], 'incorrect function return value encountered')

    def test_subsequences_e636fe80be2a41eca7e26f25cec916fb(self): 
        Param1 = type('',(object,), {})()
        self.assertNotRaises(self.module.subsequences, *[Param1, -517890502629620839, 0])
        self.assertEqual(self.module.subsequences(*[Param1, -517890502629620839, 0]), [[]], 'incorrect function return value encountered')

    def test_subsequences_a0d12fe0ac9d4ce6b0b876fc3e0c0716(self): 
        Param1 = type('',(object,), {})()
        self.assertNotRaises(self.module.subsequences, *[Param1, -444, 0])
        self.assertEqual(self.module.subsequences(*[Param1, -444, 0]), [[]], 'incorrect function return value encountered')

    def test_subsequences_0e89bcc3a82348989a0dfab94b0ad740(self): 
        Param1 = type('',(object,), {})()
        self.assertNotRaises(self.module.subsequences, *[Param1, -531, 0])
        self.assertEqual(self.module.subsequences(*[Param1, -531, 0]), [[]], 'incorrect function return value encountered')

    def test_subsequences_6df919fe127d481aaa81203e60fb039f(self): 
        Param1 = type('',(object,), {})()
        self.assertNotRaises(self.module.subsequences, *[Param1, -627, 0])
        self.assertEqual(self.module.subsequences(*[Param1, -627, 0]), [[]], 'incorrect function return value encountered')

    def test_subsequences_021ef1dfe4804213a2282d2cc59b024f(self): 
        Param1 = type('',(object,), {})()
        self.assertNotRaises(self.module.subsequences, *[Param1, 0, 0])
        self.assertEqual(self.module.subsequences(*[Param1, 0, 0]), [[]], 'incorrect function return value encountered')

    def test_subsequences_b6617149762b42d59ba1ac57143532b8(self): 
        Param1 = type('',(object,), {})()
        self.assertNotRaises(self.module.subsequences, *[Param1, 0, 0])
        self.assertEqual(self.module.subsequences(*[Param1, 0, 0]), [[]], 'incorrect function return value encountered')

    def test_subsequences_404a38e9c0f347f68e44b619e8c18e66(self): 
        Param1 = type('',(object,), {})()
        self.assertNotRaises(self.module.subsequences, *[Param1, 0, 0])
        self.assertEqual(self.module.subsequences(*[Param1, 0, 0]), [[]], 'incorrect function return value encountered')

    def test_subsequences_7b89fbb50e804bae94608a9ac5e3028e(self): 
        Param1 = type('',(object,), {})()
        self.assertNotRaises(self.module.subsequences, *[Param1, 981819820360712466, 0])
        self.assertEqual(self.module.subsequences(*[Param1, 981819820360712466, 0]), [[]], 'incorrect function return value encountered')

    def test_subsequences_67f77b68e4ec4163b088225c3b54eebd(self): 
        Param1 = type('',(object,), {})()
        self.assertNotRaises(self.module.subsequences, *[Param1, 3549206202212888516, 0])
        self.assertEqual(self.module.subsequences(*[Param1, 3549206202212888516, 0]), [[]], 'incorrect function return value encountered')

    def test_subsequences_35b082f7648e4622801f29bdd3a65a12(self): 
        Param1 = type('',(object,), {})()
        self.assertNotRaises(self.module.subsequences, *[Param1, 559960619412446467, 0])
        self.assertEqual(self.module.subsequences(*[Param1, 559960619412446467, 0]), [[]], 'incorrect function return value encountered')

    def test_subsequences_3c12ef6e821d472192b047d57ee79877(self): 
        Param1 = type('',(object,), {})()
        self.assertNotRaises(self.module.subsequences, *[Param1, 766, 0])
        self.assertEqual(self.module.subsequences(*[Param1, 766, 0]), [[]], 'incorrect function return value encountered')

    def test_subsequences_05ca9bcaaa344a7aa294aa7f567bf19e(self): 
        Param1 = type('',(object,), {})()
        self.assertNotRaises(self.module.subsequences, *[Param1, 660, 0])
        self.assertEqual(self.module.subsequences(*[Param1, 660, 0]), [[]], 'incorrect function return value encountered')

    def test_subsequences_d61cec35b9f744b588b0e09ddb69a2f5(self): 
        Param1 = type('',(object,), {})()
        self.assertNotRaises(self.module.subsequences, *[Param1, 309, 0])
        self.assertEqual(self.module.subsequences(*[Param1, 309, 0]), [[]], 'incorrect function return value encountered')

    def test_subsequences_2c14ff9c12aa4419a7c02d8ef5cccb8b(self): 
        Param1 = type('',(object,), {})()
        self.assertNotRaises(self.module.subsequences, *[Param1, 6432772509554301912, 0])
        self.assertEqual(self.module.subsequences(*[Param1, 6432772509554301912, 0]), [[]], 'incorrect function return value encountered')

    def test_subsequences_6a4f13ae4f734763bec184b1ce2ea616(self): 
        Param1 = type('',(object,), {})()
        self.assertNotRaises(self.module.subsequences, *[Param1, 5815621685105373381, 0])
        self.assertEqual(self.module.subsequences(*[Param1, 5815621685105373381, 0]), [[]], 'incorrect function return value encountered')

    def test_subsequences_648241ce72ba4cce83d13387c54af1e1(self): 
        Param1 = type('',(object,), {})()
        self.assertNotRaises(self.module.subsequences, *[Param1, 5477200603875284408, 0])
        self.assertEqual(self.module.subsequences(*[Param1, 5477200603875284408, 0]), [[]], 'incorrect function return value encountered')

    def test_subsequences_9395ad2d147748d19806676761024aef(self): 
        Param1 = type('',(object,), {})()
        self.assertNotRaises(self.module.subsequences, *[Param1, 5477200603875284408, 0])
        self.assertEqual(self.module.subsequences(*[Param1, 5477200603875284408, 0]), [[]], 'incorrect function return value encountered')

    def test_subsequences_e25229c9cfe44022a8b317dbe518f3e4(self): 
        Param1 = type('',(object,), {})()
        self.assertNotRaises(self.module.subsequences, *[Param1, 5477200603875284408, 0])
        self.assertEqual(self.module.subsequences(*[Param1, 5477200603875284408, 0]), [[]], 'incorrect function return value encountered')

    def test_subsequences_a182cbe689bf4d2695bfb78a84624bd9(self): 
        Param1 = type('',(object,), {})()
        self.assertNotRaises(self.module.subsequences, *[Param1, 5477200603875284408, 0])
        self.assertEqual(self.module.subsequences(*[Param1, 5477200603875284408, 0]), [[]], 'incorrect function return value encountered')


if __name__ == '__main__':
    unittest.main()
