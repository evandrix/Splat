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
        self.module = __import__('lis')
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

    def test_lis_all_None(self): 
        self.assertRaises(TypeError, self.module.lis, *[None])

    def test_lis_all_attr_None_wdef(self): 
        self.assertRaises(TypeError, self.module.lis, *[None])

    def test_lis_all_attr_MetaParam_wdef(self): 
        self.assertRaises(TypeError, self.module.lis, *[None])

    def test_lis_b368d5e7ad1c4558b1a3c392b950a3ae(self): 
        Param1 = type('',(object,), {})()
        self.assertRaises(TypeError, self.module.lis, *[Param1])

    def test_lis_e0b3b9fe7fde46e58011348bd18f3986(self): 
        self.assertNotRaises(self.module.lis, *[()])
        self.assertEqual(self.module.lis(*[()]), 0, 'incorrect function return value encountered')

    def test_lis_195b16a462984237b7674332ab631c04(self): 
        self.assertNotRaises(self.module.lis, *[()])
        self.assertEqual(self.module.lis(*[()]), 0, 'incorrect function return value encountered')

    def test_lis_83c7f2a6ee6d4264864307ed621067d4(self): 
        self.assertNotRaises(self.module.lis, *[(0,)])
        self.assertEqual(self.module.lis(*[(0,)]), 1, 'incorrect function return value encountered')

    def test_lis_048c8cb1eb8945a79e9d31e9e81dbebe(self): 
        self.assertNotRaises(self.module.lis, *[(-577245221895551140, -3824200884398223295)])
        self.assertEqual(self.module.lis(*[(-577245221895551140, -3824200884398223295)]), 1, 'incorrect function return value encountered')

    def test_lis_b25c7c44ce664f2a963623be60523f49(self): 
        self.assertNotRaises(self.module.lis, *[(8685739528358633916, 6940970953117365031, 6666440127884224804)])
        self.assertEqual(self.module.lis(*[(8685739528358633916, 6940970953117365031, 6666440127884224804)]), 1, 'incorrect function return value encountered')

    def test_lis_b63b200a985a446ea6a9f0805823765a(self): 
        self.assertNotRaises(self.module.lis, *[(-315, -829, -772, -715)])
        self.assertEqual(self.module.lis(*[(-315, -829, -772, -715)]), 3, 'incorrect function return value encountered')

    def test_lis_a15fded7e046401b911002fc0dc2223a(self): 
        self.assertNotRaises(self.module.lis, *[(6180960439341623574, 6782358740266430055, 5370222243179824010, 4662927160217473603, 7288769043185720720)])
        self.assertEqual(self.module.lis(*[(6180960439341623574, 6782358740266430055, 5370222243179824010, 4662927160217473603, 7288769043185720720)]), 3, 'incorrect function return value encountered')

    def test_lis_187eca995d6d43e294d6f8798715c2f3(self): 
        self.assertNotRaises(self.module.lis, *[(461481341511480054, 3387618358463501922, 1497060318446378925, 824559258531871896, 772854680295914467, 3144710507877647112)])
        self.assertEqual(self.module.lis(*[(461481341511480054, 3387618358463501922, 1497060318446378925, 824559258531871896, 772854680295914467, 3144710507877647112)]), 3, 'incorrect function return value encountered')

    def test_lis_821ae0af42c14af3ac9635f62c522579(self): 
        self.assertNotRaises(self.module.lis, *[(-607, -949, -512, -950, -492, -584, -17)])
        self.assertEqual(self.module.lis(*[(-607, -949, -512, -950, -492, -584, -17)]), 4, 'incorrect function return value encountered')

    def test_lis_cbb0da148fcf4d9cb41cfa36e29fc0b3(self): 
        self.assertNotRaises(self.module.lis, *[(-945, -838, -108, -902, -663, -678, -567, -691)])
        self.assertEqual(self.module.lis(*[(-945, -838, -108, -902, -663, -678, -567, -691)]), 4, 'incorrect function return value encountered')

    def test_lis_3b1ee6a10d224b9abfcb4c293ff674bc(self): 
        self.assertNotRaises(self.module.lis, *[(-4186610645230580080, -2864274059781918243, -2747100661649043340, -2890457382549994898, -1497071809933715545, -1633073520371508444, -2371709132455902750, -1667306954150455211, -4504143519630081732)])
        self.assertEqual(self.module.lis(*[(-4186610645230580080, -2864274059781918243, -2747100661649043340, -2890457382549994898, -1497071809933715545, -1633073520371508444, -2371709132455902750, -1667306954150455211, -4504143519630081732)]), 5, 'incorrect function return value encountered')

    def test_lis_6f2ac8e741794e01876664ada1e75214(self): 
        self.assertNotRaises(self.module.lis, *[(0, 0, 0, 0, 0, 0, 0, 0, 0, 0)])
        self.assertEqual(self.module.lis(*[(0, 0, 0, 0, 0, 0, 0, 0, 0, 0)]), 1, 'incorrect function return value encountered')

    def test_lis_1ffd7e9f8d454008b8cbf6ad7d330434(self): 
        self.assertNotRaises(self.module.lis, *[(-3353421000387375360, -2977021533327801925, -2129978196347035200, -1285213092146702619, -3645236470896782542, -4280285011272571897, -1513937214405843399, -4466810930346886526, -1171064601205866928, -3102767905263634, -4601513633445821499)])
        self.assertEqual(self.module.lis(*[(-3353421000387375360, -2977021533327801925, -2129978196347035200, -1285213092146702619, -3645236470896782542, -4280285011272571897, -1513937214405843399, -4466810930346886526, -1171064601205866928, -3102767905263634, -4601513633445821499)]), 6, 'incorrect function return value encountered')

    def test_lis_c8b79f6cec1b44f39dc94ec703b61c00(self): 
        self.assertNotRaises(self.module.lis, *[(-2878290740272272315, -297835996345602415, -3628629295401005296, -36967137474130416, -983445431702198864, -3618661521812579332, -3935405084995954977, -3100915211303293694, -1630788533928089003, -1445610028791169334, -697625686802580436, -2050987582241741115)])
        self.assertEqual(self.module.lis(*[(-2878290740272272315, -297835996345602415, -3628629295401005296, -36967137474130416, -983445431702198864, -3618661521812579332, -3935405084995954977, -3100915211303293694, -1630788533928089003, -1445610028791169334, -697625686802580436, -2050987582241741115)]), 6, 'incorrect function return value encountered')


if __name__ == '__main__':
    unittest.main()
