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

    def test_classify_triangle_e73c22d6bdb24d7fbcce054f9d62af73(self): 
        Param1 = type('',(object,), {})()
        Param2 = type('',(object,), {})()
        Param3 = type('',(object,), {})()
        self.assertRaises(TypeError, self.module.classify_triangle, *[Param1, Param2, Param3])

    def test_classify_triangle_91d87cd8d026489aac6c08ec50854166(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[0, 0, Param3])
        self.assertEqual(self.module.classify_triangle(*[0, 0, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_b43290cb3e8b4be2b4e905e4777ea5e7(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[-9098266836481939088, 0, Param3])
        self.assertEqual(self.module.classify_triangle(*[-9098266836481939088, 0, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_8331d054cca147ad9a67a7a706a13973(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[-7776628870325070877, 0, Param3])
        self.assertEqual(self.module.classify_triangle(*[-7776628870325070877, 0, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_e55e0efdb666458bb296a408b6bdc9ac(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[-8055282179576096984, 0, Param3])
        self.assertEqual(self.module.classify_triangle(*[-8055282179576096984, 0, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_5740330b2ee84953876c6bae98814e54(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[-970945443572754518, 0, Param3])
        self.assertEqual(self.module.classify_triangle(*[-970945443572754518, 0, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_445ff8da770a4726aec15a1dd3171299(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[-1461237147600852090, 0, Param3])
        self.assertEqual(self.module.classify_triangle(*[-1461237147600852090, 0, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_47e8e81b6e914a72894dc69391e844e2(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[-4425664766222593202, 0, Param3])
        self.assertEqual(self.module.classify_triangle(*[-4425664766222593202, 0, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_9cb55ab187074615abdc9e94669fcb1d(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[-1009, 0, Param3])
        self.assertEqual(self.module.classify_triangle(*[-1009, 0, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_6bbafba9a16b42b6888162e0861597ea(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[-766, 0, Param3])
        self.assertEqual(self.module.classify_triangle(*[-766, 0, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_0da8eb49adf54b6989c7ac7b460ac734(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[-864, 0, Param3])
        self.assertEqual(self.module.classify_triangle(*[-864, 0, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_a14176ef61f141fbb18c760050d0bd89(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[0, 0, Param3])
        self.assertEqual(self.module.classify_triangle(*[0, 0, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_533c67d49aeb46b2ac3eb4fd3a765679(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[0, 0, Param3])
        self.assertEqual(self.module.classify_triangle(*[0, 0, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_d3584373132c40c3a67019a3b93e3a9d(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[0, 0, Param3])
        self.assertEqual(self.module.classify_triangle(*[0, 0, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_feea8fce171947368a094fbc5299f443(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[44949353439603663, 0, Param3])
        self.assertEqual(self.module.classify_triangle(*[44949353439603663, 0, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_cbb4c069c5944985bb05a00e08ce0fd0(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[2363597385455211445, 0, Param3])
        self.assertEqual(self.module.classify_triangle(*[2363597385455211445, 0, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_94eddfdf1bb248139370e3c23e1bb5c8(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[583669195290464833, 0, Param3])
        self.assertEqual(self.module.classify_triangle(*[583669195290464833, 0, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_bf5c1585e8dc445f92572d1dad738a57(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[305, 0, Param3])
        self.assertEqual(self.module.classify_triangle(*[305, 0, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_dbafe9a119fc428abacfc57a07f798e3(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[291, 0, Param3])
        self.assertEqual(self.module.classify_triangle(*[291, 0, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_d9118bae74b449988796688c5372716c(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[38, 0, Param3])
        self.assertEqual(self.module.classify_triangle(*[38, 0, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_ec3d123093534b029ee4afec92fe23ed(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[6907401966550559642, 0, Param3])
        self.assertEqual(self.module.classify_triangle(*[6907401966550559642, 0, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_3ee03904ed094c58bd16e64e776ba7f8(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[6694881956192058422, 0, Param3])
        self.assertEqual(self.module.classify_triangle(*[6694881956192058422, 0, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_16c3a387c3f14a368510e08028aec9dc(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[7092161432345273898, 0, Param3])
        self.assertEqual(self.module.classify_triangle(*[7092161432345273898, 0, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_802993e8a27942c398e89cec004bbf92(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[7092161432345273898, -8359135771300741740, Param3])
        self.assertEqual(self.module.classify_triangle(*[7092161432345273898, -8359135771300741740, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_133fb7fd59b94d2a89b33ca0353027d2(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[7092161432345273898, -5153202965759438073, Param3])
        self.assertEqual(self.module.classify_triangle(*[7092161432345273898, -5153202965759438073, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_1d1e7b74ded44eae8014562254776a2a(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[7092161432345273898, -7455004510357419174, Param3])
        self.assertEqual(self.module.classify_triangle(*[7092161432345273898, -7455004510357419174, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_5643c602005f401bbfea5d473142b819(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[7092161432345273898, -4346943506381233164, Param3])
        self.assertEqual(self.module.classify_triangle(*[7092161432345273898, -4346943506381233164, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_b6e5d2f9bc5140e3a7d37659eb570ee3(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[7092161432345273898, -151166311180607018, Param3])
        self.assertEqual(self.module.classify_triangle(*[7092161432345273898, -151166311180607018, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_84eda74c81e0481c8eaee1f756c9bb20(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[7092161432345273898, -641929050485586731, Param3])
        self.assertEqual(self.module.classify_triangle(*[7092161432345273898, -641929050485586731, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_2c0bc089b11648b58cc6b2a9dab471d7(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[7092161432345273898, -876, Param3])
        self.assertEqual(self.module.classify_triangle(*[7092161432345273898, -876, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_fc8c2263fa2d4bccb7f885e8edb502fe(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[7092161432345273898, -641, Param3])
        self.assertEqual(self.module.classify_triangle(*[7092161432345273898, -641, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_277f35cb56d94bb59e8670e714764598(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[7092161432345273898, -575, Param3])
        self.assertEqual(self.module.classify_triangle(*[7092161432345273898, -575, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_f00e2eb8da294869949674cc8b9bef53(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[7092161432345273898, 0, Param3])
        self.assertEqual(self.module.classify_triangle(*[7092161432345273898, 0, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_2286aa4d17a04be6942f8a05bcd16e12(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[7092161432345273898, 0, Param3])
        self.assertEqual(self.module.classify_triangle(*[7092161432345273898, 0, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_1cc81f27dfd349dcaf9eb2f82ae2a3be(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[7092161432345273898, 0, Param3])
        self.assertEqual(self.module.classify_triangle(*[7092161432345273898, 0, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_38ff1c6414da4f5a867e4e80aab0c84b(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[7092161432345273898, 2671615764116305031, Param3])
        self.assertEqual(self.module.classify_triangle(*[7092161432345273898, 2671615764116305031, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_f5fb3951aca54016abb1755aaf3b3d00(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[7092161432345273898, 1076279294251032554, Param3])
        self.assertEqual(self.module.classify_triangle(*[7092161432345273898, 1076279294251032554, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_7ddc662a21c94f98bf065821df552b17(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[7092161432345273898, 3653157459329182906, Param3])
        self.assertEqual(self.module.classify_triangle(*[7092161432345273898, 3653157459329182906, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_b59aa28d8aa3425184d997ba53521513(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[7092161432345273898, 521, Param3])
        self.assertEqual(self.module.classify_triangle(*[7092161432345273898, 521, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_eb709224445e4efc8d00d163078137ba(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[7092161432345273898, 641, Param3])
        self.assertEqual(self.module.classify_triangle(*[7092161432345273898, 641, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_71c1f19ac78546edaf2d8f5c51a0f2e8(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[7092161432345273898, 521, Param3])
        self.assertEqual(self.module.classify_triangle(*[7092161432345273898, 521, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_dfdf0f05cb5d493c8f6a160f42f50cbd(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[7092161432345273898, 8855937244593114916, Param3])
        self.assertEqual(self.module.classify_triangle(*[7092161432345273898, 8855937244593114916, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_70f986ee10bd452799430116d4841054(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[7092161432345273898, 7005917874193542379, Param3])
        self.assertEqual(self.module.classify_triangle(*[7092161432345273898, 7005917874193542379, Param3]), 'notvalid', 'incorrect function return value encountered')

    def test_classify_triangle_cc7617314f924ec286026f1a87b18c35(self): 
        Param3 = type('',(object,), {})()
        self.assertNotRaises(self.module.classify_triangle, *[7092161432345273898, 5967288242350414670, Param3])
        self.assertEqual(self.module.classify_triangle(*[7092161432345273898, 5967288242350414670, Param3]), 'notvalid', 'incorrect function return value encountered')


if __name__ == '__main__':
    unittest.main()
