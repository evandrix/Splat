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
        self.module = __import__('sieve_of_eratosthenes')
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

    def test_sieve_all_None(self): 
        self.assertRaises(TypeError, self.module.sieve, *[None])

    def test_sieve_all_attr_None_wdef(self): 
        self.assertRaises(TypeError, self.module.sieve, *[None])

    def test_sieve_all_attr_MetaParam_wdef(self): 
        self.assertRaises(TypeError, self.module.sieve, *[None])

    def test_sieve_ccb25474be2d455ba20a9f041fa995f8(self): 
        Param1 = type('',(object,), {})()
        self.assertRaises(TypeError, self.module.sieve, *[Param1])

    def test_sieve_62ff2414b0c04a4d8608e2a3e3efaa3d(self): 
        self.assertNotRaises(self.module.sieve, *[0])
        self.assertEqual(self.module.sieve(*[0]), [], 'incorrect function return value encountered')

    def test_sieve_0129c69577f044e897a74672c7d10325(self): 
        self.assertNotRaises(self.module.sieve, *[2])
        self.assertEqual(self.module.sieve(*[2]), [2], 'incorrect function return value encountered')

    def test_sieve_c85cc36a5ae54a078020c6761d593031(self): 
        self.assertNotRaises(self.module.sieve, *[1])
        self.assertEqual(self.module.sieve(*[1]), [], 'incorrect function return value encountered')

    def test_sieve_16caa8a854dc4403af9eadd6c61be658(self): 
        self.assertNotRaises(self.module.sieve, *[-4712845034287957590])
        self.assertEqual(self.module.sieve(*[-4712845034287957590]), [], 'incorrect function return value encountered')

    def test_sieve_44a460dbc3dc443899cd6f240bd567ec(self): 
        self.assertNotRaises(self.module.sieve, *[-8064919278631114303])
        self.assertEqual(self.module.sieve(*[-8064919278631114303]), [], 'incorrect function return value encountered')

    def test_sieve_df3560d4fca7453fa6ecfb539c3399bf(self): 
        self.assertNotRaises(self.module.sieve, *[-5564640025494606668])
        self.assertEqual(self.module.sieve(*[-5564640025494606668]), [], 'incorrect function return value encountered')

    def test_sieve_73474d4d026748b1af2061e42a8fece6(self): 
        self.assertNotRaises(self.module.sieve, *[-2312374537089860189])
        self.assertEqual(self.module.sieve(*[-2312374537089860189]), [], 'incorrect function return value encountered')

    def test_sieve_d260c79ab61746e0a8e790989b5e3e39(self): 
        self.assertNotRaises(self.module.sieve, *[-4336012212480301380])
        self.assertEqual(self.module.sieve(*[-4336012212480301380]), [], 'incorrect function return value encountered')

    def test_sieve_c975d85cc7c44d4c9a578e50698d95ad(self): 
        self.assertNotRaises(self.module.sieve, *[-1355146120626863948])
        self.assertEqual(self.module.sieve(*[-1355146120626863948]), [], 'incorrect function return value encountered')

    def test_sieve_8407860793104b0fb89100c33bcc48f0(self): 
        self.assertNotRaises(self.module.sieve, *[-496])
        self.assertEqual(self.module.sieve(*[-496]), [], 'incorrect function return value encountered')

    def test_sieve_626187a8efd04e2f896b963faf6de719(self): 
        self.assertNotRaises(self.module.sieve, *[-595])
        self.assertEqual(self.module.sieve(*[-595]), [], 'incorrect function return value encountered')

    def test_sieve_121d3ed881dc45d0b492024cf6c87015(self): 
        self.assertNotRaises(self.module.sieve, *[-362])
        self.assertEqual(self.module.sieve(*[-362]), [], 'incorrect function return value encountered')

    def test_sieve_d7f95632e16b414a849e86098df7f64b(self): 
        self.assertNotRaises(self.module.sieve, *[0])
        self.assertEqual(self.module.sieve(*[0]), [], 'incorrect function return value encountered')

    def test_sieve_05922cfe82d04b589eb90c0419543cd7(self): 
        self.assertNotRaises(self.module.sieve, *[0])
        self.assertEqual(self.module.sieve(*[0]), [], 'incorrect function return value encountered')

    def test_sieve_22620cebb9154c0496a1a755b7736ede(self): 
        self.assertNotRaises(self.module.sieve, *[0])
        self.assertEqual(self.module.sieve(*[0]), [], 'incorrect function return value encountered')

    def test_sieve_694ea2e5bd5c4f039c1e6c82e47d92af(self): 
        self.assertNotRaises(self.module.sieve, *[111])
        self.assertEqual(self.module.sieve(*[111]), [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109], 'incorrect function return value encountered')

    def test_sieve_25456a5c29fd4f37a4ee4e5c1f0db45c(self): 
        self.assertNotRaises(self.module.sieve, *[522])
        self.assertEqual(self.module.sieve(*[522]), [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521], 'incorrect function return value encountered')

    def test_sieve_9ef3e48e646340eebfd8913f74bd280b(self): 
        self.assertNotRaises(self.module.sieve, *[244])
        self.assertEqual(self.module.sieve(*[244]), [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241], 'incorrect function return value encountered')


if __name__ == '__main__':
    unittest.main()
