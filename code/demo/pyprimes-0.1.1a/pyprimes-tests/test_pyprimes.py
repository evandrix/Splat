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
        sys.path.append('/Users/lwy08/Downloads/pyprimes-0.1.1a/src/')
        # reference module under test
        self.module = __import__('pyprimes')
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

    def test_trial_division_all_None(self): 
        self.assertNotRaises(self.module.trial_division, *[])
        self.assertEqualClassName(self.module.trial_division(*[]), 'generator', 'incorrect class name for return value encountered')

    def test_trial_division_all_attr_None_wdef(self): 
        self.assertNotRaises(self.module.trial_division, *[])
        self.assertEqualClassName(self.module.trial_division(*[]), 'generator', 'incorrect class name for return value encountered')

    def test_trial_division_all_attr_MetaParam_wdef(self): 
        self.assertNotRaises(self.module.trial_division, *[])
        self.assertEqualClassName(self.module.trial_division(*[]), 'generator', 'incorrect class name for return value encountered')

    def test_trial_division_e804bca6c22c47b7bf447a7527578b59(self): 
        self.assertNotRaises(self.module.trial_division, *[])
        self.assertEqualClassName(self.module.trial_division(*[]), 'generator', 'incorrect class name for return value encountered')

    def test_isprime_naive_all_None(self): 
        self.assertRaises(TypeError, self.module.isprime_naive, *[None])

    def test_isprime_naive_all_attr_None_wdef(self): 
        self.assertRaises(TypeError, self.module.isprime_naive, *[None])

    def test_isprime_naive_all_attr_MetaParam_wdef(self): 
        self.assertRaises(TypeError, self.module.isprime_naive, *[None])

    def test_isprime_naive_12223d7189c84aea9df3661afd084f98(self): 
        Param1 = type('',(object,), {})()
        self.assertRaises(TypeError, self.module.isprime_naive, *[Param1])

    def test_isprime_naive_6c9ea0d48be842b591955ccac9842df7(self): 
        self.assertNotRaises(self.module.isprime_naive, *[0])
        self.assertEqual(self.module.isprime_naive(*[0]), False, 'incorrect function return value encountered')

    def test_isprime_naive_c3180837d69142a7a15c627f12230140(self): 
        self.assertNotRaises(self.module.isprime_naive, *[2])
        self.assertEqual(self.module.isprime_naive(*[2]), True, 'incorrect function return value encountered')

    def test_isprime_naive_616ab14dd0a84b32a8faad6adc9651b9(self): 
        self.assertNotRaises(self.module.isprime_naive, *[3])
        self.assertEqual(self.module.isprime_naive(*[3]), True, 'incorrect function return value encountered')

    def test_isprime_naive_8e5744795b3b4cb2a7788ecb454e79ba(self): 
        self.assertNotRaises(self.module.isprime_naive, *[1])
        self.assertEqual(self.module.isprime_naive(*[1]), False, 'incorrect function return value encountered')

    def test_isprime_naive_433c0ba20afe4f3e8760ca2c41a0ad10(self): 
        self.assertNotRaises(self.module.isprime_naive, *[-8873894904541875077])
        self.assertEqual(self.module.isprime_naive(*[-8873894904541875077]), False, 'incorrect function return value encountered')

    def test_isprime_naive_5a8fceb433854716accf4a929652b4c5(self): 
        self.assertNotRaises(self.module.isprime_naive, *[-6942836223953790679])
        self.assertEqual(self.module.isprime_naive(*[-6942836223953790679]), False, 'incorrect function return value encountered')

    def test_isprime_naive_f108361bb5c34f2398c821a5ed835fc9(self): 
        self.assertNotRaises(self.module.isprime_naive, *[-8841717298371345354])
        self.assertEqual(self.module.isprime_naive(*[-8841717298371345354]), False, 'incorrect function return value encountered')

    def test_isprime_naive_10d7e9c301454ea5aa7e3c6e24baf4fa(self): 
        self.assertNotRaises(self.module.isprime_naive, *[-3956683108301849755])
        self.assertEqual(self.module.isprime_naive(*[-3956683108301849755]), False, 'incorrect function return value encountered')

    def test_isprime_naive_4652e2a9f09b46d990e890afafb7c1b2(self): 
        self.assertNotRaises(self.module.isprime_naive, *[-1692902973401755902])
        self.assertEqual(self.module.isprime_naive(*[-1692902973401755902]), False, 'incorrect function return value encountered')

    def test_isprime_naive_527905d7f27743a599ad7c51883c3675(self): 
        self.assertNotRaises(self.module.isprime_naive, *[-3482617539724162082])
        self.assertEqual(self.module.isprime_naive(*[-3482617539724162082]), False, 'incorrect function return value encountered')

    def test_isprime_naive_6cbe9393a0b7498b9cfac9b99e722f85(self): 
        self.assertNotRaises(self.module.isprime_naive, *[-381])
        self.assertEqual(self.module.isprime_naive(*[-381]), False, 'incorrect function return value encountered')

    def test_isprime_naive_08cae2419c1f481d85243427ecd2cf38(self): 
        self.assertNotRaises(self.module.isprime_naive, *[-977])
        self.assertEqual(self.module.isprime_naive(*[-977]), False, 'incorrect function return value encountered')

    def test_isprime_naive_1755dad9b9ed47d0a28eaeeb1541bbe9(self): 
        self.assertNotRaises(self.module.isprime_naive, *[-209])
        self.assertEqual(self.module.isprime_naive(*[-209]), False, 'incorrect function return value encountered')

    def test_isprime_naive_9c6f5b1e09b4414f85af854515830410(self): 
        self.assertNotRaises(self.module.isprime_naive, *[0])
        self.assertEqual(self.module.isprime_naive(*[0]), False, 'incorrect function return value encountered')

    def test_isprime_naive_982adaa44175407fb74be4c3bbdefdc9(self): 
        self.assertNotRaises(self.module.isprime_naive, *[0])
        self.assertEqual(self.module.isprime_naive(*[0]), False, 'incorrect function return value encountered')

    def test_isprime_naive_86ec0ebf07c84d20ac68181ba8344cc1(self): 
        self.assertNotRaises(self.module.isprime_naive, *[0])
        self.assertEqual(self.module.isprime_naive(*[0]), False, 'incorrect function return value encountered')

    def test_isprime_naive_1e8a58534de648e4a5d7d36b8e4db980(self): 
        self.assertNotRaises(self.module.isprime_naive, *[4065219231595422342])
        self.assertEqual(self.module.isprime_naive(*[4065219231595422342]), False, 'incorrect function return value encountered')

    def test_isprime_naive_944106bf494a4b89b824ab5433284f53(self): 
        self.assertNotRaises(self.module.isprime_naive, *[1929749951946685114])
        self.assertEqual(self.module.isprime_naive(*[1929749951946685114]), False, 'incorrect function return value encountered')

    def test_isprime_naive_d039d33f05354e79ba3fe77f3c08120e(self): 
        self.assertNotRaises(self.module.isprime_naive, *[1735688022166422787])
        self.assertEqual(self.module.isprime_naive(*[1735688022166422787]), False, 'incorrect function return value encountered')

    def test_isprime_naive_2e669cf6a977484b97cdc54e017de020(self): 
        self.assertNotRaises(self.module.isprime_naive, *[464])
        self.assertEqual(self.module.isprime_naive(*[464]), False, 'incorrect function return value encountered')

    def test_isprime_naive_bab48caa9fb149e0b6be54939be5e512(self): 
        self.assertNotRaises(self.module.isprime_naive, *[128])
        self.assertEqual(self.module.isprime_naive(*[128]), False, 'incorrect function return value encountered')

    def test_isprime_naive_dab87f595b7245658295921d0a400597(self): 
        self.assertNotRaises(self.module.isprime_naive, *[93])
        self.assertEqual(self.module.isprime_naive(*[93]), False, 'incorrect function return value encountered')

    def test_isprime_naive_a587a4866a424dafa84e2c6e8b09aa4e(self): 
        self.assertNotRaises(self.module.isprime_naive, *[6447392333538164671])
        self.assertEqual(self.module.isprime_naive(*[6447392333538164671]), False, 'incorrect function return value encountered')

    def test_isprime_naive_229e9da6939247f691269dc6df62f767(self): 
        self.assertNotRaises(self.module.isprime_naive, *[5659379163776986245])
        self.assertEqual(self.module.isprime_naive(*[5659379163776986245]), False, 'incorrect function return value encountered')

    def test_isprime_naive_1ee71d403f2d4cdf8149067e2e385d53(self): 
        self.assertNotRaises(self.module.isprime_naive, *[6703742255790722554])
        self.assertEqual(self.module.isprime_naive(*[6703742255790722554]), False, 'incorrect function return value encountered')

    def test_primesums_all_None(self): 
        self.assertNotRaises(self.module.primesums, *[])
        self.assertEqualClassName(self.module.primesums(*[]), 'generator', 'incorrect class name for return value encountered')

    def test_primesums_all_attr_None_wdef(self): 
        self.assertNotRaises(self.module.primesums, *[])
        self.assertEqualClassName(self.module.primesums(*[]), 'generator', 'incorrect class name for return value encountered')

    def test_primesums_all_attr_MetaParam_wdef(self): 
        self.assertNotRaises(self.module.primesums, *[])
        self.assertEqualClassName(self.module.primesums(*[]), 'generator', 'incorrect class name for return value encountered')

    def test_primesums_f3d3305ea3b04925bea9765647694117(self): 
        self.assertNotRaises(self.module.primesums, *[])
        self.assertEqualClassName(self.module.primesums(*[]), 'generator', 'incorrect class name for return value encountered')

    def test_erat_all_None(self): 
        self.assertRaises(TypeError, self.module.erat, *[None])

    def test_erat_all_attr_None_wdef(self): 
        self.assertRaises(TypeError, self.module.erat, *[None])

    def test_erat_all_attr_MetaParam_wdef(self): 
        self.assertRaises(TypeError, self.module.erat, *[None])

    def test_erat_04bfd81367364ad296f919bbe0727048(self): 
        Param1 = type('',(object,), {})()
        self.assertRaises(TypeError, self.module.erat, *[Param1])

    def test_erat_39e6f0560144414393458bdb0db31c09(self): 
        self.assertRaises(IndexError, self.module.erat, *[0])

    def test_erat_8c4820d8858740c7adc3fc89a392d0be(self): 
        self.assertRaises(IndexError, self.module.erat, *[0])

    def test_primes_above_all_None(self): 
        self.assertNotRaises(self.module.primes_above, *[None])
        self.assertEqualClassName(self.module.primes_above(*[None]), 'generator', 'incorrect class name for return value encountered')

    def test_primes_above_all_attr_None_wdef(self): 
        self.assertNotRaises(self.module.primes_above, *[None])
        self.assertEqualClassName(self.module.primes_above(*[None]), 'generator', 'incorrect class name for return value encountered')

    def test_primes_above_all_attr_MetaParam_wdef(self): 
        self.assertNotRaises(self.module.primes_above, *[None])
        self.assertEqualClassName(self.module.primes_above(*[None]), 'generator', 'incorrect class name for return value encountered')

    def test_primes_above_100c7764f9bc4cf3b6524aed4c5424b5(self): 
        Param1 = type('',(object,), {})()
        self.assertNotRaises(self.module.primes_above, *[Param1])
        self.assertEqualClassName(self.module.primes_above(*[Param1]), 'generator', 'incorrect class name for return value encountered')

    def test_turner_all_None(self): 
        self.assertNotRaises(self.module.turner, *[])
        self.assertEqualClassName(self.module.turner(*[]), 'generator', 'incorrect class name for return value encountered')

    def test_turner_all_attr_None_wdef(self): 
        self.assertNotRaises(self.module.turner, *[])
        self.assertEqualClassName(self.module.turner(*[]), 'generator', 'incorrect class name for return value encountered')

    def test_turner_all_attr_MetaParam_wdef(self): 
        self.assertNotRaises(self.module.turner, *[])
        self.assertEqualClassName(self.module.turner(*[]), 'generator', 'incorrect class name for return value encountered')

    def test_turner_f1a42ba1aae94ab0ab3e3c73f9a94e12(self): 
        self.assertNotRaises(self.module.turner, *[])
        self.assertEqualClassName(self.module.turner(*[]), 'generator', 'incorrect class name for return value encountered')

    def test_croft_all_None(self): 
        self.assertNotRaises(self.module.croft, *[])
        self.assertEqualClassName(self.module.croft(*[]), 'generator', 'incorrect class name for return value encountered')

    def test_croft_all_attr_None_wdef(self): 
        self.assertNotRaises(self.module.croft, *[])
        self.assertEqualClassName(self.module.croft(*[]), 'generator', 'incorrect class name for return value encountered')

    def test_croft_all_attr_MetaParam_wdef(self): 
        self.assertNotRaises(self.module.croft, *[])
        self.assertEqualClassName(self.module.croft(*[]), 'generator', 'incorrect class name for return value encountered')

    def test_croft_cc2cddb193d5407f8e5f1039ad40cec9(self): 
        self.assertNotRaises(self.module.croft, *[])
        self.assertEqualClassName(self.module.croft(*[]), 'generator', 'incorrect class name for return value encountered')

    def test_factors_all_None(self): 
        self.assertRaises(TypeError, self.module.factors, *[None])

    def test_factors_all_attr_None_wdef(self): 
        self.assertRaises(TypeError, self.module.factors, *[None])

    def test_factors_all_attr_MetaParam_wdef(self): 
        self.assertRaises(TypeError, self.module.factors, *[None])

    def test_factors_9f7c38e8ca3b48b4b5d8dc8929e89c4b(self): 
        Param1 = type('',(object,), {})()
        self.assertRaises(TypeError, self.module.factors, *[Param1])

    def test_factors_272b3eaa43a34d0a88bb4b55d908ce71(self): 
        self.assertNotRaises(self.module.factors, *[0])
        self.assertEqual(self.module.factors(*[0]), [0], 'incorrect function return value encountered')

    def test_factors_9cbee65123a848278964f09a125c8ac8(self): 
        self.assertNotRaises(self.module.factors, *[1])
        self.assertEqual(self.module.factors(*[1]), [1], 'incorrect function return value encountered')

    def test_factors_e6fef54ce5eb445f9154e5b4f496e637(self): 
        self.assertNotRaises(self.module.factors, *[-6838818771331499353])
        self.assertEqual(self.module.factors(*[-6838818771331499353]), [-1, 59, 25357, 4571210417831], 'incorrect function return value encountered')

    def test_factors_874dcd6189884377b742cc68dd65b8fb(self): 
        self.assertNotRaises(self.module.factors, *[-4848501088708453838])
        self.assertEqual(self.module.factors(*[-4848501088708453838]), [-1, 2, 962671, 2518254465289], 'incorrect function return value encountered')

    def test_factors_16c8d06cdeed45598b7a73a346f2beda(self): 
        self.assertNotRaises(self.module.factors, *[-2008626517041462702])
        self.assertEqual(self.module.factors(*[-2008626517041462702]), [-1, 2, 3, 3, 56503, 1974945791513], 'incorrect function return value encountered')

    def test_factors_b9165f1db4974dfeae01e9a470a1498a(self): 
        self.assertNotRaises(self.module.factors, *[-2084768798621869895])
        self.assertEqual(self.module.factors(*[-2084768798621869895]), [-1, 5, 17, 6679, 132173, 27783361], 'incorrect function return value encountered')

    def test_factors_8765eb602b5c49cb947485c632b13f52(self): 
        self.assertNotRaises(self.module.factors, *[-24181174471044032])
        self.assertEqual(self.module.factors(*[-24181174471044032]), [-1, 2, 2, 2, 2, 2, 2, 13, 13, 9133, 244792019], 'incorrect function return value encountered')

    def test_factors_31d62bddd7db4586a8a7940aa2aa16a2(self): 
        self.assertNotRaises(self.module.factors, *[-941])
        self.assertEqual(self.module.factors(*[-941]), [-1, 941], 'incorrect function return value encountered')

    def test_factors_6656c016b255412692724a644ae3c721(self): 
        self.assertNotRaises(self.module.factors, *[-547])
        self.assertEqual(self.module.factors(*[-547]), [-1, 547], 'incorrect function return value encountered')

    def test_factors_415c05fcac5843488ad051236715ba8c(self): 
        self.assertNotRaises(self.module.factors, *[-795])
        self.assertEqual(self.module.factors(*[-795]), [-1, 3, 5, 53], 'incorrect function return value encountered')

    def test_factors_0f9b7ffb34a1475bb38b785ef557827b(self): 
        self.assertNotRaises(self.module.factors, *[0])
        self.assertEqual(self.module.factors(*[0]), [0], 'incorrect function return value encountered')

    def test_factors_864bc0eb46394b8cb7b31bb2360459cb(self): 
        self.assertNotRaises(self.module.factors, *[0])
        self.assertEqual(self.module.factors(*[0]), [0], 'incorrect function return value encountered')

    def test_factors_894deab3d66e4d40b125a340e31fd6e3(self): 
        self.assertNotRaises(self.module.factors, *[0])
        self.assertEqual(self.module.factors(*[0]), [0], 'incorrect function return value encountered')

    def test_factors_9a62c9d8efbd46409759bd1998316748(self): 
        self.assertNotRaises(self.module.factors, *[4586974206669369841])
        self.assertEqual(self.module.factors(*[4586974206669369841]), [43, 173, 35111, 17561780329], 'incorrect function return value encountered')

    def test_factors_4c803f9a17894b27981ec8d673b18c1f(self): 
        self.assertNotRaises(self.module.factors, *[603])
        self.assertEqual(self.module.factors(*[603]), [3, 3, 67], 'incorrect function return value encountered')

    def test_factors_0208e4c78bad4a03b8944dfcaffe37b5(self): 
        self.assertNotRaises(self.module.factors, *[833])
        self.assertEqual(self.module.factors(*[833]), [7, 7, 17], 'incorrect function return value encountered')

    def test_factors_ebecc4be546c4d3fb73052cbf8f53951(self): 
        self.assertNotRaises(self.module.factors, *[580])
        self.assertEqual(self.module.factors(*[580]), [2, 2, 5, 29], 'incorrect function return value encountered')

    def test_factors_bebdfeb53471456c89d5f8fe69307f47(self): 
        self.assertNotRaises(self.module.factors, *[8483727225802548648])
        self.assertEqual(self.module.factors(*[8483727225802548648]), [2, 2, 2, 3, 37, 127, 1987, 37859261879], 'incorrect function return value encountered')

    def test_factors_71b81530d4d94e26a14bdb6c50d9f54b(self): 
        self.assertNotRaises(self.module.factors, *[8766858584698797363])
        self.assertEqual(self.module.factors(*[8766858584698797363]), [3, 11, 12289, 330703, 65369533], 'incorrect function return value encountered')

    def test_isprime_division_all_None(self): 
        self.assertRaises(TypeError, self.module.isprime_division, *[None])

    def test_isprime_division_all_attr_None_wdef(self): 
        self.assertRaises(TypeError, self.module.isprime_division, *[None])

    def test_isprime_division_all_attr_MetaParam_wdef(self): 
        self.assertRaises(TypeError, self.module.isprime_division, *[None])

    def test_isprime_division_0092dc7019b240f1b81dd56df118d106(self): 
        Param1 = type('',(object,), {})()
        self.assertRaises(TypeError, self.module.isprime_division, *[Param1])

    def test_isprime_division_4afb25246ad947719f1cad0214803723(self): 
        self.assertNotRaises(self.module.isprime_division, *[0])
        self.assertEqual(self.module.isprime_division(*[0]), False, 'incorrect function return value encountered')

    def test_isprime_division_844541c8716c4e139080dbb1e0163bb5(self): 
        self.assertNotRaises(self.module.isprime_division, *[2])
        self.assertEqual(self.module.isprime_division(*[2]), True, 'incorrect function return value encountered')

    def test_isprime_division_3ff83840051f4d58b8df377711147417(self): 
        self.assertNotRaises(self.module.isprime_division, *[-4612001783903172207])
        self.assertEqual(self.module.isprime_division(*[-4612001783903172207]), False, 'incorrect function return value encountered')

    def test_isprime_division_4ff72f29b21d4d8984417c91e555b11b(self): 
        self.assertNotRaises(self.module.isprime_division, *[-4640582219593000956])
        self.assertEqual(self.module.isprime_division(*[-4640582219593000956]), False, 'incorrect function return value encountered')

    def test_isprime_division_a86d90f7281e40b998174471deb18817(self): 
        self.assertNotRaises(self.module.isprime_division, *[-9043580183395281008])
        self.assertEqual(self.module.isprime_division(*[-9043580183395281008]), False, 'incorrect function return value encountered')

    def test_isprime_division_a51414b79bdf41a199ecb9403a721400(self): 
        self.assertNotRaises(self.module.isprime_division, *[-2082812727490864665])
        self.assertEqual(self.module.isprime_division(*[-2082812727490864665]), False, 'incorrect function return value encountered')

    def test_isprime_division_762612ce07b740dc883d0b234aac5e48(self): 
        self.assertNotRaises(self.module.isprime_division, *[-115266406413589433])
        self.assertEqual(self.module.isprime_division(*[-115266406413589433]), False, 'incorrect function return value encountered')

    def test_isprime_division_4a870753a8d84426a50fc5ee4c51694c(self): 
        self.assertNotRaises(self.module.isprime_division, *[-3142852208306177746])
        self.assertEqual(self.module.isprime_division(*[-3142852208306177746]), False, 'incorrect function return value encountered')

    def test_isprime_division_f57f7063c7094169af0275bd36c493a3(self): 
        self.assertNotRaises(self.module.isprime_division, *[-49])
        self.assertEqual(self.module.isprime_division(*[-49]), False, 'incorrect function return value encountered')

    def test_isprime_division_685724ac36e64630a2ed7bc7f6b0235e(self): 
        self.assertNotRaises(self.module.isprime_division, *[-313])
        self.assertEqual(self.module.isprime_division(*[-313]), False, 'incorrect function return value encountered')

    def test_isprime_division_1d101504f69b4cd5954f86e9d797905e(self): 
        self.assertNotRaises(self.module.isprime_division, *[-502])
        self.assertEqual(self.module.isprime_division(*[-502]), False, 'incorrect function return value encountered')

    def test_isprime_division_93f6525cf9d5443e9eaac07d96e85123(self): 
        self.assertNotRaises(self.module.isprime_division, *[0])
        self.assertEqual(self.module.isprime_division(*[0]), False, 'incorrect function return value encountered')

    def test_isprime_division_c1cf6a57197d4f16b7b9e63b7eb01462(self): 
        self.assertNotRaises(self.module.isprime_division, *[0])
        self.assertEqual(self.module.isprime_division(*[0]), False, 'incorrect function return value encountered')

    def test_isprime_division_5f19ac8e13884a0c8f49758ec58f0218(self): 
        self.assertNotRaises(self.module.isprime_division, *[0])
        self.assertEqual(self.module.isprime_division(*[0]), False, 'incorrect function return value encountered')

    def test_isprime_division_87f58b6f409841f287cf8069bbd8f3c9(self): 
        self.assertNotRaises(self.module.isprime_division, *[462819544582706203])
        self.assertEqual(self.module.isprime_division(*[462819544582706203]), False, 'incorrect function return value encountered')

    def test_isprime_division_5e20426d494b49d4ba3d66c27cacef16(self): 
        self.assertNotRaises(self.module.isprime_division, *[1963489041711912540])
        self.assertEqual(self.module.isprime_division(*[1963489041711912540]), False, 'incorrect function return value encountered')

    def test_isprime_division_68bb7b1f1ccf49f29883afcdd69a3d2d(self): 
        self.assertNotRaises(self.module.isprime_division, *[447628188893537331])
        self.assertEqual(self.module.isprime_division(*[447628188893537331]), False, 'incorrect function return value encountered')

    def test_isprime_division_72fa30cd8aed40b1a9421ad93f0bb7a2(self): 
        self.assertNotRaises(self.module.isprime_division, *[114])
        self.assertEqual(self.module.isprime_division(*[114]), False, 'incorrect function return value encountered')

    def test_isprime_division_05491d5e24b142fb8386d3b67476a99f(self): 
        self.assertNotRaises(self.module.isprime_division, *[407])
        self.assertEqual(self.module.isprime_division(*[407]), False, 'incorrect function return value encountered')

    def test_isprime_division_4e1b89bc520c4f9bb43927de69d5ee1f(self): 
        self.assertNotRaises(self.module.isprime_division, *[839])
        self.assertEqual(self.module.isprime_division(*[839]), True, 'incorrect function return value encountered')

    def test_isprime_division_e9773b91ca434f65af0127d4f3cc0ddb(self): 
        self.assertNotRaises(self.module.isprime_division, *[6077997195964628165])
        self.assertEqual(self.module.isprime_division(*[6077997195964628165]), False, 'incorrect function return value encountered')

    def test_isprime_division_0038fd3a29274fbeade223790425afbd(self): 
        self.assertNotRaises(self.module.isprime_division, *[7203317477251428920])
        self.assertEqual(self.module.isprime_division(*[7203317477251428920]), False, 'incorrect function return value encountered')

    def test_isprime_division_2a11f7c5410c41d6aecaffcee333acfc(self): 
        self.assertNotRaises(self.module.isprime_division, *[7560250739908606631])
        self.assertEqual(self.module.isprime_division(*[7560250739908606631]), False, 'incorrect function return value encountered')

    def test_checked_ints_all_None(self): 
        self.assertNotRaises(self.module.checked_ints, *[])
        self.assertEqualClassName(self.module.checked_ints(*[]), 'generator', 'incorrect class name for return value encountered')

    def test_checked_ints_all_attr_None_wdef(self): 
        self.assertNotRaises(self.module.checked_ints, *[])
        self.assertEqualClassName(self.module.checked_ints(*[]), 'generator', 'incorrect class name for return value encountered')

    def test_checked_ints_all_attr_MetaParam_wdef(self): 
        self.assertNotRaises(self.module.checked_ints, *[])
        self.assertEqualClassName(self.module.checked_ints(*[]), 'generator', 'incorrect class name for return value encountered')

    def test_checked_ints_c70ba8bfeeb34069b2c313067fd801c6(self): 
        self.assertNotRaises(self.module.checked_ints, *[])
        self.assertEqualClassName(self.module.checked_ints(*[]), 'generator', 'incorrect class name for return value encountered')

    def test_factorise_all_None(self): 
        self.assertNotRaises(self.module.factorise, *[None])
        self.assertEqualClassName(self.module.factorise(*[None]), 'generator', 'incorrect class name for return value encountered')

    def test_factorise_all_attr_None_wdef(self): 
        self.assertNotRaises(self.module.factorise, *[None])
        self.assertEqualClassName(self.module.factorise(*[None]), 'generator', 'incorrect class name for return value encountered')

    def test_factorise_all_attr_MetaParam_wdef(self): 
        self.assertNotRaises(self.module.factorise, *[None])
        self.assertEqualClassName(self.module.factorise(*[None]), 'generator', 'incorrect class name for return value encountered')

    def test_factorise_f4bcf1bc33a542719e1926984c5a2a53(self): 
        Param1 = type('',(object,), {})()
        self.assertNotRaises(self.module.factorise, *[Param1])
        self.assertEqualClassName(self.module.factorise(*[Param1]), 'generator', 'incorrect class name for return value encountered')

    def test_primes_below_all_None(self): 
        self.assertNotRaises(self.module.primes_below, *[None])
        self.assertEqualClassName(self.module.primes_below(*[None]), 'generator', 'incorrect class name for return value encountered')

    def test_primes_below_all_attr_None_wdef(self): 
        self.assertNotRaises(self.module.primes_below, *[None])
        self.assertEqualClassName(self.module.primes_below(*[None]), 'generator', 'incorrect class name for return value encountered')

    def test_primes_below_all_attr_MetaParam_wdef(self): 
        self.assertNotRaises(self.module.primes_below, *[None])
        self.assertEqualClassName(self.module.primes_below(*[None]), 'generator', 'incorrect class name for return value encountered')

    def test_primes_below_d6b28a99471843229c4771a5e163cb1e(self): 
        Param1 = type('',(object,), {})()
        self.assertNotRaises(self.module.primes_below, *[Param1])
        self.assertEqualClassName(self.module.primes_below(*[Param1]), 'generator', 'incorrect class name for return value encountered')

    def test_wheel_all_None(self): 
        self.assertNotRaises(self.module.wheel, *[])
        self.assertEqualClassName(self.module.wheel(*[]), 'generator', 'incorrect class name for return value encountered')

    def test_wheel_all_attr_None_wdef(self): 
        self.assertNotRaises(self.module.wheel, *[])
        self.assertEqualClassName(self.module.wheel(*[]), 'generator', 'incorrect class name for return value encountered')

    def test_wheel_all_attr_MetaParam_wdef(self): 
        self.assertNotRaises(self.module.wheel, *[])
        self.assertEqualClassName(self.module.wheel(*[]), 'generator', 'incorrect class name for return value encountered')

    def test_wheel_6664ad8990ae49f0ae69bea0d2754559(self): 
        self.assertNotRaises(self.module.wheel, *[])
        self.assertEqualClassName(self.module.wheel(*[]), 'generator', 'incorrect class name for return value encountered')

    def test_primesum_all_None(self): 
        self.assertRaises(TypeError, self.module.primesum, *[None])

    def test_primesum_all_attr_None_wdef(self): 
        self.assertRaises(TypeError, self.module.primesum, *[None])

    def test_primesum_all_attr_MetaParam_wdef(self): 
        self.assertRaises(TypeError, self.module.primesum, *[None])

    def test_primesum_92694196f3d047578f6fd2a5cc0c7bd3(self): 
        Param1 = type('',(object,), {})()
        self.assertRaises(TypeError, self.module.primesum, *[Param1])

    def test_primesum_b5a6eec447e84206bcf27ce020b498bb(self): 
        self.assertNotRaises(self.module.primesum, *[0])
        self.assertEqual(self.module.primesum(*[0]), 0, 'incorrect function return value encountered')

    def test_primesum_2e4ffd3847ad4bc989704058872b8f3d(self): 
        self.assertRaises(ValueError, self.module.primesum, *[-7066676192016951898])

    def test_primesum_f9acd5188d6e469bad7d09b9a702730e(self): 
        self.assertRaises(ValueError, self.module.primesum, *[-9142189203468175716])

    def test_primesum_94cda709dff94a96a25aab04b39373e4(self): 
        self.assertRaises(ValueError, self.module.primesum, *[-8927861737264962242])

    def test_primesum_3c2bef4e1ba2425fb2e445ebef733649(self): 
        self.assertRaises(ValueError, self.module.primesum, *[-2547701290206992107])

    def test_primesum_2497c8cd14dd4000a512b85659625377(self): 
        self.assertRaises(ValueError, self.module.primesum, *[-1593073840560805566])

    def test_primesum_eec9c88e1c74426c9302e5be6720bea5(self): 
        self.assertRaises(ValueError, self.module.primesum, *[-3576325266072301177])

    def test_primesum_15c1159e1598416daf323eb4108f720e(self): 
        self.assertRaises(ValueError, self.module.primesum, *[-954])

    def test_primesum_9bf04390c09d439faa91e4d64bc2d535(self): 
        self.assertRaises(ValueError, self.module.primesum, *[-893])

    def test_primesum_56be58b5b246477da6ecd0e8686ec033(self): 
        self.assertRaises(ValueError, self.module.primesum, *[-347])

    def test_primesum_08a9a52f488a4cb68105a364feb3eeaa(self): 
        self.assertNotRaises(self.module.primesum, *[0])
        self.assertEqual(self.module.primesum(*[0]), 0, 'incorrect function return value encountered')

    def test_primesum_9c8b0da36f144a7a8cb7dcefa2da18ae(self): 
        self.assertNotRaises(self.module.primesum, *[0])
        self.assertEqual(self.module.primesum(*[0]), 0, 'incorrect function return value encountered')

    def test_primesum_81f6ec5b3a6e419fb4ac7f392a402f7b(self): 
        self.assertNotRaises(self.module.primesum, *[0])
        self.assertEqual(self.module.primesum(*[0]), 0, 'incorrect function return value encountered')

    def test_primesum_f647310ae8144d6a9c68e5873469dbb7(self): 
        self.assertNotRaises(self.module.primesum, *[875])
        self.assertEqual(self.module.primesum(*[875]), 2762836, 'incorrect function return value encountered')

    def test_primesum_8323b909454f4d319656541d0ca88bb1(self): 
        self.assertNotRaises(self.module.primesum, *[760])
        self.assertEqual(self.module.primesum(*[760]), 2039559, 'incorrect function return value encountered')

    def test_primesum_344b6c706d95438a83f60a56da938bfb(self): 
        self.assertNotRaises(self.module.primesum, *[495])
        self.assertEqual(self.module.primesum(*[495]), 806918, 'incorrect function return value encountered')

    def test_awful_primes_all_None(self): 
        self.assertNotRaises(self.module.awful_primes, *[])
        self.assertEqualClassName(self.module.awful_primes(*[]), 'generator', 'incorrect class name for return value encountered')

    def test_awful_primes_all_attr_None_wdef(self): 
        self.assertNotRaises(self.module.awful_primes, *[])
        self.assertEqualClassName(self.module.awful_primes(*[]), 'generator', 'incorrect class name for return value encountered')

    def test_awful_primes_all_attr_MetaParam_wdef(self): 
        self.assertNotRaises(self.module.awful_primes, *[])
        self.assertEqualClassName(self.module.awful_primes(*[]), 'generator', 'incorrect class name for return value encountered')

    def test_awful_primes_3d5e20c3084c4aebb0febcdf05db4ddf(self): 
        self.assertNotRaises(self.module.awful_primes, *[])
        self.assertEqualClassName(self.module.awful_primes(*[]), 'generator', 'incorrect class name for return value encountered')

    def test_miller_rabin_all_None(self): 
        self.assertRaises(TypeError, self.module.miller_rabin, *[None, None])

    def test_miller_rabin_all_attr_None_wdef(self): 
        self.assertRaises(TypeError, self.module.miller_rabin, *[None, 2])

    def test_miller_rabin_all_attr_MetaParam_wdef(self): 
        self.assertRaises(TypeError, self.module.miller_rabin, *[None, 2])

    def test_miller_rabin_15d1b60282c049f5912577f421486a17(self): 
        Param1 = type('',(object,), {})()
        self.assertRaises(TypeError, self.module.miller_rabin, *[Param1, 2])

    def test_miller_rabin_3446d8879aa342eaaa264aefc7a21eaf(self): 
        self.assertRaises(ValueError, self.module.miller_rabin, *[0, 2])

    def test_miller_rabin_aed710ffd8324ed9b3e561dc79665b4f(self): 
        self.assertRaises(ValueError, self.module.miller_rabin, *[0, 2])

    def test_fermat_all_None(self): 
        self.assertRaises(TypeError, self.module.fermat, *[None, None])

    def test_fermat_all_attr_None_wdef(self): 
        self.assertRaises(TypeError, self.module.fermat, *[None, 2])

    def test_fermat_all_attr_MetaParam_wdef(self): 
        self.assertRaises(TypeError, self.module.fermat, *[None, 2])

    def test_fermat_554db7893ebf4fc4acc3a3706a984f31(self): 
        Param1 = type('',(object,), {})()
        self.assertRaises(TypeError, self.module.fermat, *[Param1, 2])

    def test_fermat_b4942420964d4ebdb112faad9c52d462(self): 
        self.assertRaises(ValueError, self.module.fermat, *[0, 2])

    def test_fermat_8506ccbc40194420a4fa12404c6e6fed(self): 
        self.assertRaises(ValueError, self.module.fermat, *[0, 2])

    def test_cookbook_all_None(self): 
        self.assertNotRaises(self.module.cookbook, *[])
        self.assertEqualClassName(self.module.cookbook(*[]), 'generator', 'incorrect class name for return value encountered')

    def test_cookbook_all_attr_None_wdef(self): 
        self.assertNotRaises(self.module.cookbook, *[])
        self.assertEqualClassName(self.module.cookbook(*[]), 'generator', 'incorrect class name for return value encountered')

    def test_cookbook_all_attr_MetaParam_wdef(self): 
        self.assertNotRaises(self.module.cookbook, *[])
        self.assertEqualClassName(self.module.cookbook(*[]), 'generator', 'incorrect class name for return value encountered')

    def test_cookbook_305a5258649448b9bdc4c041cfd3dd43(self): 
        self.assertNotRaises(self.module.cookbook, *[])
        self.assertEqualClassName(self.module.cookbook(*[]), 'generator', 'incorrect class name for return value encountered')

    def test_naive_primes2_all_None(self): 
        self.assertNotRaises(self.module.naive_primes2, *[])
        self.assertEqualClassName(self.module.naive_primes2(*[]), 'generator', 'incorrect class name for return value encountered')

    def test_naive_primes2_all_attr_None_wdef(self): 
        self.assertNotRaises(self.module.naive_primes2, *[])
        self.assertEqualClassName(self.module.naive_primes2(*[]), 'generator', 'incorrect class name for return value encountered')

    def test_naive_primes2_all_attr_MetaParam_wdef(self): 
        self.assertNotRaises(self.module.naive_primes2, *[])
        self.assertEqualClassName(self.module.naive_primes2(*[]), 'generator', 'incorrect class name for return value encountered')

    def test_naive_primes2_cfdd06e9d4fd4b8bac3ad59d58461c4b(self): 
        self.assertNotRaises(self.module.naive_primes2, *[])
        self.assertEqualClassName(self.module.naive_primes2(*[]), 'generator', 'incorrect class name for return value encountered')

    def test_naive_primes1_all_None(self): 
        self.assertNotRaises(self.module.naive_primes1, *[])
        self.assertEqualClassName(self.module.naive_primes1(*[]), 'generator', 'incorrect class name for return value encountered')

    def test_naive_primes1_all_attr_None_wdef(self): 
        self.assertNotRaises(self.module.naive_primes1, *[])
        self.assertEqualClassName(self.module.naive_primes1(*[]), 'generator', 'incorrect class name for return value encountered')

    def test_naive_primes1_all_attr_MetaParam_wdef(self): 
        self.assertNotRaises(self.module.naive_primes1, *[])
        self.assertEqualClassName(self.module.naive_primes1(*[]), 'generator', 'incorrect class name for return value encountered')

    def test_naive_primes1_6623735e32ed4ad69fcc9d796f0c62bb(self): 
        self.assertNotRaises(self.module.naive_primes1, *[])
        self.assertEqualClassName(self.module.naive_primes1(*[]), 'generator', 'incorrect class name for return value encountered')

    def test_checked_oddints_all_None(self): 
        self.assertNotRaises(self.module.checked_oddints, *[])
        self.assertEqualClassName(self.module.checked_oddints(*[]), 'generator', 'incorrect class name for return value encountered')

    def test_checked_oddints_all_attr_None_wdef(self): 
        self.assertNotRaises(self.module.checked_oddints, *[])
        self.assertEqualClassName(self.module.checked_oddints(*[]), 'generator', 'incorrect class name for return value encountered')

    def test_checked_oddints_all_attr_MetaParam_wdef(self): 
        self.assertNotRaises(self.module.checked_oddints, *[])
        self.assertEqualClassName(self.module.checked_oddints(*[]), 'generator', 'incorrect class name for return value encountered')

    def test_checked_oddints_ad36f3eab0e64847a70a11a31fd530ec(self): 
        self.assertNotRaises(self.module.checked_oddints, *[])
        self.assertEqualClassName(self.module.checked_oddints(*[]), 'generator', 'incorrect class name for return value encountered')

    def test_nprimes_all_None(self): 
        self.assertRaises(TypeError, self.module.nprimes, *[None])

    def test_nprimes_all_attr_None_wdef(self): 
        self.assertRaises(TypeError, self.module.nprimes, *[None])

    def test_nprimes_all_attr_MetaParam_wdef(self): 
        self.assertRaises(TypeError, self.module.nprimes, *[None])

    def test_nprimes_ffd8b2a83d0d4e9ab9dbde8aaf71e4cb(self): 
        Param1 = type('',(object,), {})()
        self.assertRaises(TypeError, self.module.nprimes, *[Param1])

    def test_nprimes_2221fc50a01d4a98b91c0aef265c5287(self): 
        self.assertNotRaises(self.module.nprimes, *[0])
        self.assertEqualClassName(self.module.nprimes(*[0]), 'islice', 'incorrect class name for return value encountered')
        self.assertEqualAttrs(self.module.nprimes(*[0]), 'null', 'incorrect attributes for return value encountered')

    def test_nprimes_5b78cd8541474ada95314421261f220b(self): 
        self.assertRaises(ValueError, self.module.nprimes, *[-8432526776627525013])

    def test_nprimes_afa434b2c35a46c9b1f0397e024d4248(self): 
        self.assertRaises(ValueError, self.module.nprimes, *[-7744033180567595554])

    def test_nprimes_174ccf5f57434e4fb5904a34bb99c678(self): 
        self.assertRaises(ValueError, self.module.nprimes, *[-5602974007384457345])

    def test_nprimes_57adc78bbfc64425a08dd4a48f149411(self): 
        self.assertRaises(ValueError, self.module.nprimes, *[-1242282416504010923])

    def test_nprimes_05462b06bfd2483d977ad0423be5c561(self): 
        self.assertRaises(ValueError, self.module.nprimes, *[-605376607423395778])

    def test_nprimes_28b2d46434e445d98f65e25fc7014498(self): 
        self.assertRaises(ValueError, self.module.nprimes, *[-1707480619799234835])

    def test_nprimes_311bd55d3ca7489ca4fc0847106ff6c9(self): 
        self.assertRaises(ValueError, self.module.nprimes, *[-72])

    def test_nprimes_14a1ff013e4147539500b74d4a090636(self): 
        self.assertRaises(ValueError, self.module.nprimes, *[-920])

    def test_nprimes_571ca08f0d8441c093d6c4ccf6a004f0(self): 
        self.assertRaises(ValueError, self.module.nprimes, *[-996])

    def test_nprimes_cad7dfcd6c2c4ec9ac6baeae39205249(self): 
        self.assertNotRaises(self.module.nprimes, *[0])
        self.assertEqualClassName(self.module.nprimes(*[0]), 'islice', 'incorrect class name for return value encountered')
        self.assertEqualAttrs(self.module.nprimes(*[0]), 'null', 'incorrect attributes for return value encountered')

    def test_nprimes_f066eb202a9b4490923239f886b2506e(self): 
        self.assertNotRaises(self.module.nprimes, *[0])
        self.assertEqualClassName(self.module.nprimes(*[0]), 'islice', 'incorrect class name for return value encountered')
        self.assertEqualAttrs(self.module.nprimes(*[0]), 'null', 'incorrect attributes for return value encountered')

    def test_nprimes_7b1050214dac4369b29a4456e70ce105(self): 
        self.assertNotRaises(self.module.nprimes, *[0])
        self.assertEqualClassName(self.module.nprimes(*[0]), 'islice', 'incorrect class name for return value encountered')
        self.assertEqualAttrs(self.module.nprimes(*[0]), 'null', 'incorrect attributes for return value encountered')

    def test_nprimes_c214bc65108343e5b7d9cd7af14d613a(self): 
        self.assertNotRaises(self.module.nprimes, *[4244540345722047101])
        self.assertEqualClassName(self.module.nprimes(*[4244540345722047101]), 'islice', 'incorrect class name for return value encountered')
        self.assertEqualAttrs(self.module.nprimes(*[4244540345722047101]), 'null', 'incorrect attributes for return value encountered')

    def test_nprimes_1782557943b6402f8a63428bbf4ed747(self): 
        self.assertNotRaises(self.module.nprimes, *[2212925397429142645])
        self.assertEqualClassName(self.module.nprimes(*[2212925397429142645]), 'islice', 'incorrect class name for return value encountered')
        self.assertEqualAttrs(self.module.nprimes(*[2212925397429142645]), 'null', 'incorrect attributes for return value encountered')

    def test_nprimes_a962f9cbdc574340aca89e254c260132(self): 
        self.assertNotRaises(self.module.nprimes, *[2290307774239876271])
        self.assertEqualClassName(self.module.nprimes(*[2290307774239876271]), 'islice', 'incorrect class name for return value encountered')
        self.assertEqualAttrs(self.module.nprimes(*[2290307774239876271]), 'null', 'incorrect attributes for return value encountered')

    def test_nprimes_cfa75b0c96f64ebbb55bee262a7afc1a(self): 
        self.assertNotRaises(self.module.nprimes, *[12])
        self.assertEqualClassName(self.module.nprimes(*[12]), 'islice', 'incorrect class name for return value encountered')
        self.assertEqualAttrs(self.module.nprimes(*[12]), 'null', 'incorrect attributes for return value encountered')

    def test_nprimes_9e553eca8394411a8e9e76fae8fc149b(self): 
        self.assertNotRaises(self.module.nprimes, *[821])
        self.assertEqualClassName(self.module.nprimes(*[821]), 'islice', 'incorrect class name for return value encountered')
        self.assertEqualAttrs(self.module.nprimes(*[821]), 'null', 'incorrect attributes for return value encountered')

    def test_nprimes_b4abd34de4904f5e90b063196e94c7fa(self): 
        self.assertNotRaises(self.module.nprimes, *[976])
        self.assertEqualClassName(self.module.nprimes(*[976]), 'islice', 'incorrect class name for return value encountered')
        self.assertEqualAttrs(self.module.nprimes(*[976]), 'null', 'incorrect attributes for return value encountered')

    def test_nprimes_d731cd4808004bc09e03161f33acdf3e(self): 
        self.assertNotRaises(self.module.nprimes, *[9058649468608610603])
        self.assertEqualClassName(self.module.nprimes(*[9058649468608610603]), 'islice', 'incorrect class name for return value encountered')
        self.assertEqualAttrs(self.module.nprimes(*[9058649468608610603]), 'null', 'incorrect attributes for return value encountered')

    def test_nprimes_a042c5e6321040afa684fc2f0a277446(self): 
        self.assertNotRaises(self.module.nprimes, *[5709481193068930917])
        self.assertEqualClassName(self.module.nprimes(*[5709481193068930917]), 'islice', 'incorrect class name for return value encountered')
        self.assertEqualAttrs(self.module.nprimes(*[5709481193068930917]), 'null', 'incorrect attributes for return value encountered')

    def test_nprimes_7d7cd6c2877c4557b72206862943cc5e(self): 
        self.assertNotRaises(self.module.nprimes, *[5931738492665625571])
        self.assertEqualClassName(self.module.nprimes(*[5931738492665625571]), 'islice', 'incorrect class name for return value encountered')
        self.assertEqualAttrs(self.module.nprimes(*[5931738492665625571]), 'null', 'incorrect attributes for return value encountered')

    def test_isprime_all_None(self): 
        self.assertRaises(TypeError, self.module.isprime, *[None])

    def test_isprime_all_attr_None_wdef(self): 
        self.assertRaises(TypeError, self.module.isprime, *[None])

    def test_isprime_all_attr_MetaParam_wdef(self): 
        self.assertRaises(TypeError, self.module.isprime, *[None])

    def test_isprime_a963d161f2224876afe4257fc06e519a(self): 
        Param1 = type('',(object,), {})()
        self.assertRaises(TypeError, self.module.isprime, *[Param1])

    def test_isprime_f1486a4124fa4305bf4083b922d365e5(self): 
        self.assertNotRaises(self.module.isprime, *[0])
        self.assertEqual(self.module.isprime(*[0]), False, 'incorrect function return value encountered')

    def test_isprime_5da2c9d1ed224e21a7d0b2caf5b55fb7(self): 
        self.assertNotRaises(self.module.isprime, *[2])
        self.assertEqual(self.module.isprime(*[2]), True, 'incorrect function return value encountered')

    def test_isprime_8d1071d9cc8b421692140b25d7db6866(self): 
        self.assertNotRaises(self.module.isprime, *[7])
        self.assertEqual(self.module.isprime(*[7]), True, 'incorrect function return value encountered')

    def test_isprime_da078e950f6446bebaa01b0f47d94909(self): 
        self.assertNotRaises(self.module.isprime, *[-1])
        self.assertEqual(self.module.isprime(*[-1]), False, 'incorrect function return value encountered')

    def test_isprime_c40700c385584caaa2977920fef7f89e(self): 
        self.assertNotRaises(self.module.isprime, *[-5749933004837450512])
        self.assertEqual(self.module.isprime(*[-5749933004837450512]), False, 'incorrect function return value encountered')

    def test_isprime_49b6f0df2c064642b08ed4180106619d(self): 
        self.assertNotRaises(self.module.isprime, *[-8965690059771660566])
        self.assertEqual(self.module.isprime(*[-8965690059771660566]), False, 'incorrect function return value encountered')

    def test_isprime_14d2bd79a69545d49b5fbbbfe922dfc5(self): 
        self.assertNotRaises(self.module.isprime, *[-7685856947944713416])
        self.assertEqual(self.module.isprime(*[-7685856947944713416]), False, 'incorrect function return value encountered')

    def test_isprime_8b0d8d63ac9c447b9f705378f5e9988a(self): 
        self.assertNotRaises(self.module.isprime, *[-1979984358984976233])
        self.assertEqual(self.module.isprime(*[-1979984358984976233]), False, 'incorrect function return value encountered')

    def test_isprime_fb724dd623bc455182bcb36cce4159bf(self): 
        self.assertNotRaises(self.module.isprime, *[-1779279984675296683])
        self.assertEqual(self.module.isprime(*[-1779279984675296683]), False, 'incorrect function return value encountered')

    def test_isprime_ee142d21e78d4acd82d3d1db2b60244d(self): 
        self.assertNotRaises(self.module.isprime, *[-2802762862888773775])
        self.assertEqual(self.module.isprime(*[-2802762862888773775]), False, 'incorrect function return value encountered')

    def test_isprime_77f07e22b98740e6b133e4914e3f8697(self): 
        self.assertNotRaises(self.module.isprime, *[-672])
        self.assertEqual(self.module.isprime(*[-672]), False, 'incorrect function return value encountered')

    def test_isprime_b0a450c5ba5f4f26a6753c2922c9888a(self): 
        self.assertNotRaises(self.module.isprime, *[-761])
        self.assertEqual(self.module.isprime(*[-761]), False, 'incorrect function return value encountered')

    def test_isprime_6bec9a030cfb497a82116dba6902653c(self): 
        self.assertNotRaises(self.module.isprime, *[-324])
        self.assertEqual(self.module.isprime(*[-324]), False, 'incorrect function return value encountered')

    def test_isprime_88428026c48d433398c6f912fe134d0a(self): 
        self.assertNotRaises(self.module.isprime, *[0])
        self.assertEqual(self.module.isprime(*[0]), False, 'incorrect function return value encountered')

    def test_isprime_e0f15fc174ec40ebafd6303c92822ac0(self): 
        self.assertNotRaises(self.module.isprime, *[0])
        self.assertEqual(self.module.isprime(*[0]), False, 'incorrect function return value encountered')

    def test_isprime_bf14cb39ef1f45b281864fac144fb76e(self): 
        self.assertNotRaises(self.module.isprime, *[0])
        self.assertEqual(self.module.isprime(*[0]), False, 'incorrect function return value encountered')

    def test_isprime_b3c3b033a184409facfa206c7fbb0ca3(self): 
        self.assertNotRaises(self.module.isprime, *[1467590942794259174])
        self.assertEqual(self.module.isprime(*[1467590942794259174]), False, 'incorrect function return value encountered')

    def test_isprime_7b9bf1091d7649f98de3bfcd44877375(self): 
        self.assertNotRaises(self.module.isprime, *[3214182706091540711])
        self.assertEqual(self.module.isprime(*[3214182706091540711]), False, 'incorrect function return value encountered')

    def test_isprime_ab049cd6fceb4b0099655f754b45ebf4(self): 
        self.assertNotRaises(self.module.isprime, *[1994060996972820645])
        self.assertEqual(self.module.isprime(*[1994060996972820645]), False, 'incorrect function return value encountered')

    def test_isprime_7c2a32965c8e490ca9c19f5cf3ecf123(self): 
        self.assertNotRaises(self.module.isprime, *[760])
        self.assertEqual(self.module.isprime(*[760]), False, 'incorrect function return value encountered')

    def test_isprime_d99c107c3bc34e4295242dc62638aaa0(self): 
        self.assertNotRaises(self.module.isprime, *[554])
        self.assertEqual(self.module.isprime(*[554]), False, 'incorrect function return value encountered')

    def test_isprime_b3523cf895574e3586a5d3a8e7bd1416(self): 
        self.assertNotRaises(self.module.isprime, *[805])
        self.assertEqual(self.module.isprime(*[805]), False, 'incorrect function return value encountered')

    def test_isprime_2db39f6682f048dbaf7b6615054e56ce(self): 
        self.assertNotRaises(self.module.isprime, *[5115790157702286729])
        self.assertEqual(self.module.isprime(*[5115790157702286729]), False, 'incorrect function return value encountered')

    def test_isprime_98e422c7412847419ecb424b9a7c1114(self): 
        self.assertNotRaises(self.module.isprime, *[9023431607803533592])
        self.assertEqual(self.module.isprime(*[9023431607803533592]), False, 'incorrect function return value encountered')

    def test_isprime_085b67587d1f4700900258bcd73ccef1(self): 
        self.assertNotRaises(self.module.isprime, *[6552878918466187172])
        self.assertEqual(self.module.isprime(*[6552878918466187172]), False, 'incorrect function return value encountered')

    def test_nth_prime_all_None(self): 
        self.assertRaises(TypeError, self.module.nth_prime, *[None])

    def test_nth_prime_all_attr_None_wdef(self): 
        self.assertRaises(TypeError, self.module.nth_prime, *[None])

    def test_nth_prime_all_attr_MetaParam_wdef(self): 
        self.assertRaises(TypeError, self.module.nth_prime, *[None])

    def test_nth_prime_0cdabfb42c9449538498b0832c8263b4(self): 
        Param1 = type('',(object,), {})()
        self.assertRaises(TypeError, self.module.nth_prime, *[Param1])

    def test_nth_prime_f3717413663e48e298d143ec585f3683(self): 
        self.assertRaises(ValueError, self.module.nth_prime, *[0])

    def test_nth_prime_795230d01d8c459ca3b841d9e4b66a2d(self): 
        self.assertRaises(ValueError, self.module.nth_prime, *[0])

    def test_isfinite_all_None(self): 
        self.assertRaises(TypeError, self.module.isfinite, *[None])

    def test_isfinite_all_attr_None_wdef(self): 
        self.assertRaises(TypeError, self.module.isfinite, *[None])

    def test_isfinite_all_attr_MetaParam_wdef(self): 
        self.assertRaises(TypeError, self.module.isfinite, *[None])

    def test_isfinite_1b0f71f78f4741de9da8b056fce2ffe4(self): 
        Param1 = type('',(object,), {})()
        self.assertRaises(TypeError, self.module.isfinite, *[Param1])

    def test_isfinite_124262eb6fa947488eb6fd92b0536c55(self): 
        Param1 = type('',(object,), {})()
        self.assertRaises(TypeError, self.module.isfinite, *[Param1])

    def test_isfinite_da1a10eb574e448fab852858bc523892(self): 
        Param1 = type('',(object,), {})()
        self.assertRaises(TypeError, self.module.isfinite, *[Param1])

    def test_prime_count_all_None(self): 
        self.assertRaises(TypeError, self.module.prime_count, *[None])

    def test_prime_count_all_attr_None_wdef(self): 
        self.assertRaises(TypeError, self.module.prime_count, *[None])

    def test_prime_count_all_attr_MetaParam_wdef(self): 
        self.assertRaises(TypeError, self.module.prime_count, *[None])

    def test_prime_count_8353abbf7c2d467f8bf1d1411627e445(self): 
        Param1 = type('',(object,), {})()
        self.assertRaises(TypeError, self.module.prime_count, *[Param1])

    def test_prime_count_07e5bd6b1edb4408ac55337d41c2d741(self): 
        self.assertNotRaises(self.module.prime_count, *[0])
        self.assertEqual(self.module.prime_count(*[0]), 0, 'incorrect function return value encountered')

    def test_prime_count_9f012df492964fc5bae4cbf902df74ee(self): 
        self.assertNotRaises(self.module.prime_count, *[-6463760784422426822])
        self.assertEqual(self.module.prime_count(*[-6463760784422426822]), 0, 'incorrect function return value encountered')

    def test_prime_count_8510cac90c194883ae24dabbca34b738(self): 
        self.assertNotRaises(self.module.prime_count, *[-7261419247807804108])
        self.assertEqual(self.module.prime_count(*[-7261419247807804108]), 0, 'incorrect function return value encountered')

    def test_prime_count_c64ad89e5efc472c90ec7bd89ac1c67b(self): 
        self.assertNotRaises(self.module.prime_count, *[-5172379062552783417])
        self.assertEqual(self.module.prime_count(*[-5172379062552783417]), 0, 'incorrect function return value encountered')

    def test_prime_count_19d9833b02794a1cbc8c74a01c363b10(self): 
        self.assertNotRaises(self.module.prime_count, *[-3221800977478096043])
        self.assertEqual(self.module.prime_count(*[-3221800977478096043]), 0, 'incorrect function return value encountered')

    def test_prime_count_b38e4721eae9454eb86eab37b15ef86b(self): 
        self.assertNotRaises(self.module.prime_count, *[-728071084028245456])
        self.assertEqual(self.module.prime_count(*[-728071084028245456]), 0, 'incorrect function return value encountered')

    def test_prime_count_c924e1b94bf34bd79f32671f33010baa(self): 
        self.assertNotRaises(self.module.prime_count, *[-4379455409848132596])
        self.assertEqual(self.module.prime_count(*[-4379455409848132596]), 0, 'incorrect function return value encountered')

    def test_prime_count_34b59a5ca3a743d5a42a470eebd6fa7e(self): 
        self.assertNotRaises(self.module.prime_count, *[-445])
        self.assertEqual(self.module.prime_count(*[-445]), 0, 'incorrect function return value encountered')

    def test_prime_count_583f2068c32245a8a9848511d02087e0(self): 
        self.assertNotRaises(self.module.prime_count, *[-488])
        self.assertEqual(self.module.prime_count(*[-488]), 0, 'incorrect function return value encountered')

    def test_prime_count_1c795413bec34475a106b40ad74291f3(self): 
        self.assertNotRaises(self.module.prime_count, *[-517])
        self.assertEqual(self.module.prime_count(*[-517]), 0, 'incorrect function return value encountered')

    def test_prime_count_073fa13338b545dab0dbc00f4529fb37(self): 
        self.assertNotRaises(self.module.prime_count, *[0])
        self.assertEqual(self.module.prime_count(*[0]), 0, 'incorrect function return value encountered')

    def test_prime_count_ab0c7e5cb116434da13bc1d6523ed496(self): 
        self.assertNotRaises(self.module.prime_count, *[0])
        self.assertEqual(self.module.prime_count(*[0]), 0, 'incorrect function return value encountered')

    def test_prime_count_ba691a982a484b50aebffea333856b39(self): 
        self.assertNotRaises(self.module.prime_count, *[0])
        self.assertEqual(self.module.prime_count(*[0]), 0, 'incorrect function return value encountered')

    def test_prime_count_1fdae13a3ef24c7a8082a6df8b6371f0(self): 
        self.assertNotRaises(self.module.prime_count, *[376])
        self.assertEqual(self.module.prime_count(*[376]), 74, 'incorrect function return value encountered')

    def test_prime_count_c955bc7f69c043c1a579b1fa2f6e22f1(self): 
        self.assertNotRaises(self.module.prime_count, *[835])
        self.assertEqual(self.module.prime_count(*[835]), 145, 'incorrect function return value encountered')

    def test_prime_count_dfa15f96b9f6487d96f02bfa27697dbe(self): 
        self.assertNotRaises(self.module.prime_count, *[483])
        self.assertEqual(self.module.prime_count(*[483]), 92, 'incorrect function return value encountered')


if __name__ == '__main__':
    unittest.main()
