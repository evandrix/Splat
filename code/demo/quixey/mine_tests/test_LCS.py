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
        self.module = __import__('LCS_b')
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

    def test_LongestCommonSubsequence_all_None(self): 
        self.assertRaises(TypeError, self.module.LongestCommonSubsequence, *[None, None])

    def test_LongestCommonSubsequence_all_attr_None_wdef(self): 
        self.assertRaises(TypeError, self.module.LongestCommonSubsequence, *[None, None])

    def test_LongestCommonSubsequence_all_attr_MetaParam_wdef(self): 
        self.assertRaises(TypeError, self.module.LongestCommonSubsequence, *[None, None])

    def test_LongestCommonSubsequence_bf89c1b7d5584dd29cb46c321235a215(self): 
        Param1 = type('',(object,), {})()
        Param2 = type('',(object,), {})()
        self.assertRaises(TypeError, self.module.LongestCommonSubsequence, *[Param1, Param2])

    def test_LongestCommonSubsequence_7c1d2404edaf4c04a2a734f266b4fb1e(self): 
        Param2 = type('',(object,), {})()
        self.assertRaises(TypeError, self.module.LongestCommonSubsequence, *[(), Param2])

    def test_LongestCommonSubsequence_a342ba0271c1458aa0bfde4c20a226b6(self): 
        self.assertNotRaises(self.module.LongestCommonSubsequence, *[(), ()])
        self.assertEqual(self.module.LongestCommonSubsequence(*[(), ()]), [], 'incorrect function return value encountered')

    def test_LongestCommonSubsequence_3672c5b20cb248f3a31a1c2350758e79(self): 
        self.assertNotRaises(self.module.LongestCommonSubsequence, *[(), ()])
        self.assertEqual(self.module.LongestCommonSubsequence(*[(), ()]), [], 'incorrect function return value encountered')

    def test_LongestCommonSubsequence_dfefd0913c6e4ae0bed1cdb250e59556(self): 
        self.assertNotRaises(self.module.LongestCommonSubsequence, *[(1548057758841140840,), ()])
        self.assertEqual(self.module.LongestCommonSubsequence(*[(1548057758841140840,), ()]), [], 'incorrect function return value encountered')

    def test_LongestCommonSubsequence_ae6a08d5e6ed49deb06bc17ce1709816(self): 
        self.assertNotRaises(self.module.LongestCommonSubsequence, *[(1214592314326688180, 3122688670431758032), ()])
        self.assertEqual(self.module.LongestCommonSubsequence(*[(1214592314326688180, 3122688670431758032), ()]), [], 'incorrect function return value encountered')

    def test_LongestCommonSubsequence_eb41cdcf0a2a4f8890b1e5b0b84e2918(self): 
        self.assertNotRaises(self.module.LongestCommonSubsequence, *[(-3337047813136428758, -2861095063565209478, -2136802574485530429), ()])
        self.assertEqual(self.module.LongestCommonSubsequence(*[(-3337047813136428758, -2861095063565209478, -2136802574485530429), ()]), [], 'incorrect function return value encountered')

    def test_LongestCommonSubsequence_f7d0ba25217b47c09df1c49173c8b0aa(self): 
        self.assertNotRaises(self.module.LongestCommonSubsequence, *[(868, 321, 202, 274), ()])
        self.assertEqual(self.module.LongestCommonSubsequence(*[(868, 321, 202, 274), ()]), [], 'incorrect function return value encountered')

    def test_LongestCommonSubsequence_d0be9d0b34784be99f40def79a6a8301(self): 
        self.assertNotRaises(self.module.LongestCommonSubsequence, *[(-7789465692662498625, -8808417288531218459, -6145141295346887518, -5143888918576463084, -4852891012845230557), ()])
        self.assertEqual(self.module.LongestCommonSubsequence(*[(-7789465692662498625, -8808417288531218459, -6145141295346887518, -5143888918576463084, -4852891012845230557), ()]), [], 'incorrect function return value encountered')

    def test_LongestCommonSubsequence_ee1a4fb946cd4b8795de12b898735d66(self): 
        self.assertNotRaises(self.module.LongestCommonSubsequence, *[(-7789465692662498625, -8808417288531218459, -6145141295346887518, -5143888918576463084, -4852891012845230557), ()])
        self.assertEqual(self.module.LongestCommonSubsequence(*[(-7789465692662498625, -8808417288531218459, -6145141295346887518, -5143888918576463084, -4852891012845230557), ()]), [], 'incorrect function return value encountered')

    def test_LongestCommonSubsequence_1bc132971b04475e87439ac6140dc274(self): 
        self.assertNotRaises(self.module.LongestCommonSubsequence, *[(-7789465692662498625, -8808417288531218459, -6145141295346887518, -5143888918576463084, -4852891012845230557), (7368664165227234818,)])
        self.assertEqual(self.module.LongestCommonSubsequence(*[(-7789465692662498625, -8808417288531218459, -6145141295346887518, -5143888918576463084, -4852891012845230557), (7368664165227234818,)]), [], 'incorrect function return value encountered')

    def test_LongestCommonSubsequence_5ec45cfc8a0c492d952eacb7d560702b(self): 
        self.assertNotRaises(self.module.LongestCommonSubsequence, *[(-7789465692662498625, -8808417288531218459, -6145141295346887518, -5143888918576463084, -4852891012845230557), (1018029720600481376, 2621260310529761131)])
        self.assertEqual(self.module.LongestCommonSubsequence(*[(-7789465692662498625, -8808417288531218459, -6145141295346887518, -5143888918576463084, -4852891012845230557), (1018029720600481376, 2621260310529761131)]), [], 'incorrect function return value encountered')

    def test_LongestCommonSubsequence_0e6aa89960324530b7fd3e63acc59e99(self): 
        self.assertNotRaises(self.module.LongestCommonSubsequence, *[(-7789465692662498625, -8808417288531218459, -6145141295346887518, -5143888918576463084, -4852891012845230557), (8254303248769287078, 6351213767193850952, 7690360522254302504)])
        self.assertEqual(self.module.LongestCommonSubsequence(*[(-7789465692662498625, -8808417288531218459, -6145141295346887518, -5143888918576463084, -4852891012845230557), (8254303248769287078, 6351213767193850952, 7690360522254302504)]), [], 'incorrect function return value encountered')

    def test_LongestCommonSubsequence_fed0012567084bb1ad919f69c7c91fc2(self): 
        self.assertNotRaises(self.module.LongestCommonSubsequence, *[(-7789465692662498625, -8808417288531218459, -6145141295346887518, -5143888918576463084, -4852891012845230557), (480, 388, 420, 984)])
        self.assertEqual(self.module.LongestCommonSubsequence(*[(-7789465692662498625, -8808417288531218459, -6145141295346887518, -5143888918576463084, -4852891012845230557), (480, 388, 420, 984)]), [], 'incorrect function return value encountered')

    def test_LongestCommonSubsequence_da81a5b950bc4a94815ac55cb205a75d(self): 
        self.assertNotRaises(self.module.LongestCommonSubsequence, *[(-7789465692662498625, -8808417288531218459, -6145141295346887518, -5143888918576463084, -4852891012845230557), (-8141644271244833768, -7290940727667797151, -8412990906528899965, -8158061153527272148, -8102949908028770318)])
        self.assertEqual(self.module.LongestCommonSubsequence(*[(-7789465692662498625, -8808417288531218459, -6145141295346887518, -5143888918576463084, -4852891012845230557), (-8141644271244833768, -7290940727667797151, -8412990906528899965, -8158061153527272148, -8102949908028770318)]), [], 'incorrect function return value encountered')

    def test_LongestCommonSubsequence_3fdca7ed5b0a478588b155d6a8cd2a24(self): 
        self.assertNotRaises(self.module.LongestCommonSubsequence, *[(-7789465692662498625, -8808417288531218459, -6145141295346887518, -5143888918576463084, -4852891012845230557), (-8686280255779133823, -4980621298094720476, -8282122315798290247, -6621273532971502798, -7078459186229094805, -8162639474115514431)])
        self.assertEqual(self.module.LongestCommonSubsequence(*[(-7789465692662498625, -8808417288531218459, -6145141295346887518, -5143888918576463084, -4852891012845230557), (-8686280255779133823, -4980621298094720476, -8282122315798290247, -6621273532971502798, -7078459186229094805, -8162639474115514431)]), [], 'incorrect function return value encountered')

    def test_LongestCommonSubsequence_9f849830a5074ed19d5454b85d8abdba(self): 
        self.assertNotRaises(self.module.LongestCommonSubsequence, *[(-7789465692662498625, -8808417288531218459, -6145141295346887518, -5143888918576463084, -4852891012845230557), (0, 0, 0, 0, 0, 0, 0)])
        self.assertEqual(self.module.LongestCommonSubsequence(*[(-7789465692662498625, -8808417288531218459, -6145141295346887518, -5143888918576463084, -4852891012845230557), (0, 0, 0, 0, 0, 0, 0)]), [], 'incorrect function return value encountered')

    def test_LongestCommonSubsequence_326fbbc5df4d4d508abca14bfe88a301(self): 
        self.assertNotRaises(self.module.LongestCommonSubsequence, *[(-7789465692662498625, -8808417288531218459, -6145141295346887518, -5143888918576463084, -4852891012845230557), (-458, -52, -360, -297, -779, -434, -602, -477)])
        self.assertEqual(self.module.LongestCommonSubsequence(*[(-7789465692662498625, -8808417288531218459, -6145141295346887518, -5143888918576463084, -4852891012845230557), (-458, -52, -360, -297, -779, -434, -602, -477)]), [], 'incorrect function return value encountered')

    def test_LongestCommonSubsequence_215fef0dccb047de810df73ddf11bac6(self): 
        self.assertNotRaises(self.module.LongestCommonSubsequence, *[(-7789465692662498625, -8808417288531218459, -6145141295346887518, -5143888918576463084, -4852891012845230557), (6127431208441898454, 6283165516938534331, 8939718827017257723, 5298414595762255389, 9204748364157825266, 6936528087473055990, 8621980513826578518, 6734195493794071154, 5030482623696751865)])
        self.assertEqual(self.module.LongestCommonSubsequence(*[(-7789465692662498625, -8808417288531218459, -6145141295346887518, -5143888918576463084, -4852891012845230557), (6127431208441898454, 6283165516938534331, 8939718827017257723, 5298414595762255389, 9204748364157825266, 6936528087473055990, 8621980513826578518, 6734195493794071154, 5030482623696751865)]), [], 'incorrect function return value encountered')

    def test_LongestCommonSubsequence_407cf38e51894b2da1b7a32408efee1e(self): 
        self.assertNotRaises(self.module.LongestCommonSubsequence, *[(-7789465692662498625, -8808417288531218459, -6145141295346887518, -5143888918576463084, -4852891012845230557), (0, 0, 0, 0, 0, 0, 0, 0, 0, 0)])
        self.assertEqual(self.module.LongestCommonSubsequence(*[(-7789465692662498625, -8808417288531218459, -6145141295346887518, -5143888918576463084, -4852891012845230557), (0, 0, 0, 0, 0, 0, 0, 0, 0, 0)]), [], 'incorrect function return value encountered')

    def test_LongestCommonSubsequence_990fa5e71dcb49578dd91372d7f6ff48(self): 
        self.assertNotRaises(self.module.LongestCommonSubsequence, *[(-7789465692662498625, -8808417288531218459, -6145141295346887518, -5143888918576463084, -4852891012845230557), (-7557583987957642326, -7596963855873977569, -5808867453317961940, -8761128753817111864, -6159633042469851607, -8419010071112156074, -6152066300566920091, -6340812495775524085, -7148924458409497678, -5189413826488320963, -4968500053443679970)])
        self.assertEqual(self.module.LongestCommonSubsequence(*[(-7789465692662498625, -8808417288531218459, -6145141295346887518, -5143888918576463084, -4852891012845230557), (-7557583987957642326, -7596963855873977569, -5808867453317961940, -8761128753817111864, -6159633042469851607, -8419010071112156074, -6152066300566920091, -6340812495775524085, -7148924458409497678, -5189413826488320963, -4968500053443679970)]), [], 'incorrect function return value encountered')

    def test_LongestCommonSubsequence_202fd774fadf4b0ab13781eb725596b7(self): 
        self.assertNotRaises(self.module.LongestCommonSubsequence, *[(-7789465692662498625, -8808417288531218459, -6145141295346887518, -5143888918576463084, -4852891012845230557), (-8, -575, -101, -946, -264, -295, -256, -299, -28, -1022, -780, -191)])
        self.assertEqual(self.module.LongestCommonSubsequence(*[(-7789465692662498625, -8808417288531218459, -6145141295346887518, -5143888918576463084, -4852891012845230557), (-8, -575, -101, -946, -264, -295, -256, -299, -28, -1022, -780, -191)]), [], 'incorrect function return value encountered')


if __name__ == '__main__':
    unittest.main()
