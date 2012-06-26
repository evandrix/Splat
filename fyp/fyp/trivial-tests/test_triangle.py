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
        sys.path.append('/Users/lwy08/Dropbox/FYP/fyp/fyp/trivial/')
        # reference module under test
        self.module = __import__('triangle')
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

    def test_classify_triangle_all_None(self): 
        self.assertRaises(TypeError, self.module.classify_triangle, *[None, None, None])

    def test_classify_triangle_all_attr_None_wdef(self): 
        self.assertRaises(TypeError, self.module.classify_triangle, *[None, None, None])

    def test_classify_triangle_all_attr_MetaParam_wdef(self): 
        self.assertRaises(TypeError, self.module.classify_triangle, *[None, None, None])

    def test_classify_triangle_67eb5876c91447e88d9153736f9a1077(self): 
        Param1 = type('',(object,), {})()
        Param2 = type('',(object,), {})()
        Param3 = type('',(object,), {})()
        self.assertRaises(TypeError, self.module.classify_triangle, *[Param1, Param2, Param3])

    def test_classify_triangle_208af87ad8834101b37a736e405da722(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[0, 0, Param3])
        self.assertEqual(self.module.classify_triangle(*[0, 0, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_b54d6c4620a240f2a646abcde9bf52aa(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[-5385852856656963197, 0, Param3])
        self.assertEqual(self.module.classify_triangle(*[-5385852856656963197, 0, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_b5c36e9c28b9427ea4640196c1aca1d7(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[-6809951951096240627, 0, Param3])
        self.assertEqual(self.module.classify_triangle(*[-6809951951096240627, 0, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_0ac6705dde69426e92d2364fe77e60e3(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[-7462921287611520563, 0, Param3])
        self.assertEqual(self.module.classify_triangle(*[-7462921287611520563, 0, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_276451700d9b4a4daad177e012f5b8c1(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[-3700875811614281776, 0, Param3])
        self.assertEqual(self.module.classify_triangle(*[-3700875811614281776, 0, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_0e9707d3ebb5450cbf8922dcbd59bb6d(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[-3784587203926556620, 0, Param3])
        self.assertEqual(self.module.classify_triangle(*[-3784587203926556620, 0, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_5427d382cb6a4c699fea8bd5d94004c7(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[-2938136369776137995, 0, Param3])
        self.assertEqual(self.module.classify_triangle(*[-2938136369776137995, 0, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_e189dcca085f4c348604a7e50ed3d493(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[-469, 0, Param3])
        self.assertEqual(self.module.classify_triangle(*[-469, 0, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_a00f646a01e040c09acdf848231d3b17(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[-944, 0, Param3])
        self.assertEqual(self.module.classify_triangle(*[-944, 0, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_5a6c9ff662424f77823fe2a15e52890d(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[-701, 0, Param3])
        self.assertEqual(self.module.classify_triangle(*[-701, 0, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_a44286f2e81d4a85b07107c1a1b69f68(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[0, 0, Param3])
        self.assertEqual(self.module.classify_triangle(*[0, 0, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_f90b6cf9f1704f4ea6a96d9b32ebc29f(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[0, 0, Param3])
        self.assertEqual(self.module.classify_triangle(*[0, 0, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_7f8141bfbf514ea7b91c9e175a4772aa(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[0, 0, Param3])
        self.assertEqual(self.module.classify_triangle(*[0, 0, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_13376f9ec57749ffae6ead8ccf48c4d9(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[4283312769081439286, 0, Param3])
        self.assertEqual(self.module.classify_triangle(*[4283312769081439286, 0, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_d41705aa1ce84b21a2158bb1669f7b4c(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[538524519001625494, 0, Param3])
        self.assertEqual(self.module.classify_triangle(*[538524519001625494, 0, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_d7b7d46bd8b44a7abf1e2cca31dea849(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[1004626203598924839, 0, Param3])
        self.assertEqual(self.module.classify_triangle(*[1004626203598924839, 0, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_e708d4009ced4316884dcc2e4ea76a04(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[919, 0, Param3])
        self.assertEqual(self.module.classify_triangle(*[919, 0, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_a95bfc0eef2449908d23144453de1b22(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[91, 0, Param3])
        self.assertEqual(self.module.classify_triangle(*[91, 0, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_cef61830a4dc4866ba41750938dc66f6(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[82, 0, Param3])
        self.assertEqual(self.module.classify_triangle(*[82, 0, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_6622ab789cb747088e06dfa503e06827(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[7774058870576908452, 0, Param3])
        self.assertEqual(self.module.classify_triangle(*[7774058870576908452, 0, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_7e585b457fb7478a96577e9dda45be2f(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[5170858206915932572, 0, Param3])
        self.assertEqual(self.module.classify_triangle(*[5170858206915932572, 0, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_2f078dce48564ab7b21827478102392d(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[8948516607368931863, 0, Param3])
        self.assertEqual(self.module.classify_triangle(*[8948516607368931863, 0, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_469dd52752b24ea88447bb2f7442a24e(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[8948516607368931863, -6665445894585184477, Param3])
        self.assertEqual(self.module.classify_triangle(*[8948516607368931863, -6665445894585184477, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_2aeff1c7db094d15be86f0e8e5d941df(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[8948516607368931863, -5074391951703945484, Param3])
        self.assertEqual(self.module.classify_triangle(*[8948516607368931863, -5074391951703945484, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_9945da8bd85d434c8433d720e9a7fafc(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[8948516607368931863, -7569639963602890986, Param3])
        self.assertEqual(self.module.classify_triangle(*[8948516607368931863, -7569639963602890986, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_dce443ec6f2f401cb70208688fa052de(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[8948516607368931863, -3620381872143335971, Param3])
        self.assertEqual(self.module.classify_triangle(*[8948516607368931863, -3620381872143335971, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_87d34fc7e42a43e88ab3cdbd555f6cd9(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[8948516607368931863, -2545710340054348386, Param3])
        self.assertEqual(self.module.classify_triangle(*[8948516607368931863, -2545710340054348386, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_04bc6c6cce7742bfba0340fb350ae411(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[8948516607368931863, -3988476991517147117, Param3])
        self.assertEqual(self.module.classify_triangle(*[8948516607368931863, -3988476991517147117, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_93c1a2ae72504c17aafb8f47084021b9(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[8948516607368931863, -546, Param3])
        self.assertEqual(self.module.classify_triangle(*[8948516607368931863, -546, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_5a945321b6824b8e8b16bd0ffeab7839(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[8948516607368931863, -247, Param3])
        self.assertEqual(self.module.classify_triangle(*[8948516607368931863, -247, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_f39ee695fc26492f9364b7ad607ab60d(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[8948516607368931863, -457, Param3])
        self.assertEqual(self.module.classify_triangle(*[8948516607368931863, -457, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_b3757ddba13f40b6971cf3ca656c3e42(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[8948516607368931863, 0, Param3])
        self.assertEqual(self.module.classify_triangle(*[8948516607368931863, 0, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_44ebe6b984674224a9c92935050664c4(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[8948516607368931863, 0, Param3])
        self.assertEqual(self.module.classify_triangle(*[8948516607368931863, 0, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_1053ad8734d34b64bf2bcff872c2a334(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[8948516607368931863, 0, Param3])
        self.assertEqual(self.module.classify_triangle(*[8948516607368931863, 0, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_1ddfeea00f744ceb9045b5a234c8c67a(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[8948516607368931863, 1091897349682880348, Param3])
        self.assertEqual(self.module.classify_triangle(*[8948516607368931863, 1091897349682880348, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_b64064bcafc942a29c2d629ac7a181a5(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[8948516607368931863, 2361775118441719978, Param3])
        self.assertEqual(self.module.classify_triangle(*[8948516607368931863, 2361775118441719978, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_bda5acc4a8bf4b31859a14ca820e6564(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[8948516607368931863, 1811346471742534802, Param3])
        self.assertEqual(self.module.classify_triangle(*[8948516607368931863, 1811346471742534802, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_36102187dbdb46ee8d24707d061e0b67(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[8948516607368931863, 842, Param3])
        self.assertEqual(self.module.classify_triangle(*[8948516607368931863, 842, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_da4cd4f411c84381a89396a291a6d726(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[8948516607368931863, 126, Param3])
        self.assertEqual(self.module.classify_triangle(*[8948516607368931863, 126, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_24958749789441a3a4ac980e74348b84(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[8948516607368931863, 705, Param3])
        self.assertEqual(self.module.classify_triangle(*[8948516607368931863, 705, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_4caf666f2c494fc4a9aaaf6a97b007e6(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[8948516607368931863, 4735365713558046225, Param3])
        self.assertEqual(self.module.classify_triangle(*[8948516607368931863, 4735365713558046225, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_31b6b80ad9854c5fab48efb629ea3df8(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[8948516607368931863, 6215585535532202818, Param3])
        self.assertEqual(self.module.classify_triangle(*[8948516607368931863, 6215585535532202818, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_3c22915f86a940aa994890f68156fec8(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[8948516607368931863, 6590435082477003741, Param3])
        self.assertEqual(self.module.classify_triangle(*[8948516607368931863, 6590435082477003741, Param3]), 'notvalid', 'incorrect function return value encountered')


if __name__ == '__main__':
    unittest.main()
