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
        sys.path.append('/Users/lwy08/Downloads/pyutilib.math-3.3')
        sys.path.append('/Users/lwy08/Downloads/pyutilib.math-3.3/pyutilib/math/')
        # reference module under test
        self.module = __import__('util')
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

    def test_as_number_all_None(self): 
        self.assertNotRaises(self.module.as_number, *[None])
        self.assertIsNone(self.module.as_number(*[None]))

    def test_as_number_all_attr_None_wdef(self): 
        self.assertNotRaises(self.module.as_number, *[None])
        self.assertIsNone(self.module.as_number(*[None]))

    def test_as_number_all_attr_MetaParam_wdef(self): 
        self.assertNotRaises(self.module.as_number, *[None])
        self.assertIsNone(self.module.as_number(*[None]))

    def test_argmin_all_None(self): 
        self.assertRaises(TypeError, self.module.argmin, *[None])

    def test_argmin_all_attr_None_wdef(self): 
        self.assertRaises(TypeError, self.module.argmin, *[None])

    def test_argmin_all_attr_MetaParam_wdef(self): 
        self.assertRaises(TypeError, self.module.argmin, *[None])

    def test_argmin_ad4efc0a06c14ec7a1df5cf0d8155530(self): 
        Param1 = type('',(object,), {})()
        self.assertRaises(TypeError, self.module.argmin, *[Param1])

    def test_argmin_4ed680dcd03e480c9e3eee2150fa705c(self): 
        Param1 = type('',(object,), {})()
        self.assertRaises(TypeError, self.module.argmin, *[Param1])

    def test_argmin_30d973a6ece64248948dc7ad199f7ac3(self): 
        Param1 = type('',(object,), {})()
        self.assertRaises(TypeError, self.module.argmin, *[Param1])

    def test_isint_all_None(self): 
        self.assertNotRaises(self.module.isint, *[None])
        self.assertEqual(self.module.isint(*[None]), False, 'incorrect function return value encountered')

    def test_isint_all_attr_None_wdef(self): 
        self.assertNotRaises(self.module.isint, *[None])
        self.assertEqual(self.module.isint(*[None]), False, 'incorrect function return value encountered')

    def test_isint_all_attr_MetaParam_wdef(self): 
        self.assertNotRaises(self.module.isint, *[None])
        self.assertEqual(self.module.isint(*[None]), False, 'incorrect function return value encountered')

    def test_isint_caf54bb775384cec8b5835fa675dcc63(self): 
        Param1 = type('',(object,), {})()
        self.assertNotRaises(self.module.isint, *[Param1])
        self.assertEqual(self.module.isint(*[Param1]), False, 'incorrect function return value encountered')

    def test_factorial_all_None(self): 
        self.assertRaises(ArithmeticError, self.module.factorial, *[None])

    def test_factorial_all_attr_None_wdef(self): 
        self.assertRaises(ArithmeticError, self.module.factorial, *[None])

    def test_factorial_all_attr_MetaParam_wdef(self): 
        self.assertRaises(ArithmeticError, self.module.factorial, *[None])

    def test_factorial_01b0d3dfcbfb45179f727d45af77c8b4(self): 
        Param1 = type('',(object,), {})()
        self.assertRaises(TypeError, self.module.factorial, *[Param1])

    def test_factorial_8d7ff0c9efc147a88fedb9b1f2c1faec(self): 
        self.assertNotRaises(self.module.factorial, *[0])
        self.assertEqual(self.module.factorial(*[0]), 1, 'incorrect function return value encountered')

    def test_factorial_4340135040(self): 
        self.assertEqual(479001600, self.module.factorial(12))

    def test_factorial_4340135232(self): 
        self.assertEqual(24, self.module.factorial(4))

    def test_factorial_4340135304(self): 
        self.assertEqual(1, self.module.factorial(1))

    def test_factorial_4340135184(self): 
        self.assertEqual(720, self.module.factorial(6))

    def test_factorial_4340134800(self): 
        self.assertEqual(1124000727777607680000L, self.module.factorial(22))

    def test_factorial_4340135256(self): 
        self.assertEqual(6, self.module.factorial(3))

    def test_factorial_4340134920(self): 
        self.assertEqual(355687428096000, self.module.factorial(17))

    def test_factorial_4340135064(self): 
        self.assertEqual(39916800, self.module.factorial(11))

    def test_factorial_4340134728(self): 
        self.assertEqual(15511210043330985984000000L, self.module.factorial(25))

    def test_factorial_4340134656(self): 
        self.assertEqual(304888344611713860501504000000L, self.module.factorial(28))

    def test_factorial_4340134944(self): 
        self.assertEqual(20922789888000, self.module.factorial(16))

    def test_factorial_4340134704(self): 
        self.assertEqual(403291461126605635584000000L, self.module.factorial(26))

    def test_factorial_4340134824(self): 
        self.assertEqual(51090942171709440000L, self.module.factorial(21))

    def test_factorial_4340135088(self): 
        self.assertEqual(3628800, self.module.factorial(10))

    def test_factorial_4340134536(self): 
        self.assertEqual(8683317618811886495518194401280000000L, self.module.factorial(33))

    def test_factorial_4340134584(self): 
        self.assertEqual(8222838654177922817725562880000000L, self.module.factorial(31))

    def test_factorial_4340135160(self): 
        self.assertEqual(5040, self.module.factorial(7))

    def test_factorial_4340134848(self): 
        self.assertEqual(2432902008176640000, self.module.factorial(20))

    def test_factorial_4340135328(self): 
        self.assertEqual(1, self.module.factorial(0))

    def test_factorial_4340134896(self): 
        self.assertEqual(6402373705728000, self.module.factorial(18))

    def test_factorial_4340135112(self): 
        self.assertEqual(362880, self.module.factorial(9))

    def test_factorial_4340134992(self): 
        self.assertEqual(87178291200, self.module.factorial(14))

    def test_factorial_4340134968(self): 
        self.assertEqual(1307674368000, self.module.factorial(15))

    def test_factorial_4340134488(self): 
        self.assertEqual(10333147966386144929666651337523200000000L, self.module.factorial(35))

    def test_factorial_4340134560(self): 
        self.assertEqual(263130836933693530167218012160000000L, self.module.factorial(32))

    def test_factorial_4340135208(self): 
        self.assertEqual(120, self.module.factorial(5))

    def test_factorial_4340136416(self): 
        self.assertEqual(13763753091226345046315979581580902400000000L, self.module.factorial(37))

    def test_factorial_4340134752(self): 
        self.assertEqual(620448401733239439360000L, self.module.factorial(24))

    def test_factorial_4340135280(self): 
        self.assertEqual(2, self.module.factorial(2))

    def test_factorial_4340136440(self): 
        self.assertEqual(371993326789901217467999448150835200000000L, self.module.factorial(36))

    def test_factorial_4340134632(self): 
        self.assertEqual(8841761993739701954543616000000L, self.module.factorial(29))

    def test_factorial_4340135136(self): 
        self.assertEqual(40320, self.module.factorial(8))

    def test_factorial_4340134680(self): 
        self.assertEqual(10888869450418352160768000000L, self.module.factorial(27))

    def test_factorial_4340134512(self): 
        self.assertEqual(295232799039604140847618609643520000000L, self.module.factorial(34))

    def test_factorial_4340135016(self): 
        self.assertEqual(6227020800, self.module.factorial(13))

    def test_factorial_4340134872(self): 
        self.assertEqual(121645100408832000, self.module.factorial(19))

    def test_factorial_4340134776(self): 
        self.assertEqual(25852016738884976640000L, self.module.factorial(23))

    def test_factorial_4340134608(self): 
        self.assertEqual(265252859812191058636308480000000L, self.module.factorial(30))

    def test_approx_equal_all_None(self): 
        self.assertRaises(TypeError, self.module.approx_equal, *[None, None, None, None])

    def test_approx_equal_all_attr_None_wdef(self): 
        self.assertRaises(TypeError, self.module.approx_equal, *[None, None, None, None])

    def test_approx_equal_all_attr_MetaParam_wdef(self): 
        self.assertRaises(TypeError, self.module.approx_equal, *[None, None, None, None])

    def test_approx_equal_2146bade19504f498c783c5a8683c15c(self): 
        Param1 = type('',(object,), {})()
        Param2 = type('',(object,), {})()
        Param3 = type('',(object,), {})()
        Param4 = type('',(object,), {})()
        self.assertRaises(TypeError, self.module.approx_equal, *[Param1, Param2, Param3, Param4])

    def test_approx_equal_265fbaa69c67493491ecf4ad4a815af8(self): 
        Param2 = type('',(object,), {})()
        Param3 = type('',(object,), {})()
        Param4 = type('',(object,), {})()
        self.assertRaises(TypeError, self.module.approx_equal, *[0, Param2, Param3, Param4])

    def test_approx_equal_7ca9cc0d97a642cc867f78b9209493d3(self): 
        Param3 = type('',(object,), {})()
        Param4 = type('',(object,), {})()
        self.assertNotRaises(self.module.approx_equal, *[0, 0, Param3, Param4])
        self.assertEqual(self.module.approx_equal(*[0, 0, Param3, Param4]), True, 'incorrect function return value encountered')

    def test_approx_equal_494f01ec03334a448e889a47110c7a3f(self): 
        Param3 = type('',(object,), {})()
        Param4 = type('',(object,), {})()
        self.assertNotRaises(self.module.approx_equal, *[-4655114418234116396, 0, Param3, Param4])
        self.assertEqual(self.module.approx_equal(*[-4655114418234116396, 0, Param3, Param4]), True, 'incorrect function return value encountered')

    def test_approx_equal_e16ffff2da044d2b964631dc136a02f2(self): 
        Param3 = type('',(object,), {})()
        Param4 = type('',(object,), {})()
        self.assertNotRaises(self.module.approx_equal, *[-6131897808919339136, 0, Param3, Param4])
        self.assertEqual(self.module.approx_equal(*[-6131897808919339136, 0, Param3, Param4]), True, 'incorrect function return value encountered')

    def test_approx_equal_7611746f797649c081a9aeec5ff9f37d(self): 
        Param3 = type('',(object,), {})()
        Param4 = type('',(object,), {})()
        self.assertNotRaises(self.module.approx_equal, *[-6125374539477339154, 0, Param3, Param4])
        self.assertEqual(self.module.approx_equal(*[-6125374539477339154, 0, Param3, Param4]), True, 'incorrect function return value encountered')

    def test_approx_equal_9566e0c92ca645df899ba326536be2f3(self): 
        Param3 = type('',(object,), {})()
        Param4 = type('',(object,), {})()
        self.assertNotRaises(self.module.approx_equal, *[-2636873581161505499, 0, Param3, Param4])
        self.assertEqual(self.module.approx_equal(*[-2636873581161505499, 0, Param3, Param4]), True, 'incorrect function return value encountered')

    def test_approx_equal_f5d5a33386c040d8b272f067c21cb99e(self): 
        Param3 = type('',(object,), {})()
        Param4 = type('',(object,), {})()
        self.assertNotRaises(self.module.approx_equal, *[-2420807821085804151, 0, Param3, Param4])
        self.assertEqual(self.module.approx_equal(*[-2420807821085804151, 0, Param3, Param4]), True, 'incorrect function return value encountered')

    def test_approx_equal_b4f731f2232843228fbb8a80669f5d6f(self): 
        Param3 = type('',(object,), {})()
        Param4 = type('',(object,), {})()
        self.assertNotRaises(self.module.approx_equal, *[-3409018997018743123, 0, Param3, Param4])
        self.assertEqual(self.module.approx_equal(*[-3409018997018743123, 0, Param3, Param4]), True, 'incorrect function return value encountered')

    def test_approx_equal_2b3701d80de34b40b176c7e62aabd25f(self): 
        Param3 = type('',(object,), {})()
        Param4 = type('',(object,), {})()
        self.assertNotRaises(self.module.approx_equal, *[-180, 0, Param3, Param4])
        self.assertEqual(self.module.approx_equal(*[-180, 0, Param3, Param4]), True, 'incorrect function return value encountered')

    def test_approx_equal_45818dc9e91e41c391fa3047dca9e474(self): 
        Param3 = type('',(object,), {})()
        Param4 = type('',(object,), {})()
        self.assertNotRaises(self.module.approx_equal, *[-330, 0, Param3, Param4])
        self.assertEqual(self.module.approx_equal(*[-330, 0, Param3, Param4]), True, 'incorrect function return value encountered')

    def test_approx_equal_dabfaa6cf7b94610b81262c7f9894fef(self): 
        Param3 = type('',(object,), {})()
        Param4 = type('',(object,), {})()
        self.assertNotRaises(self.module.approx_equal, *[-421, 0, Param3, Param4])
        self.assertEqual(self.module.approx_equal(*[-421, 0, Param3, Param4]), True, 'incorrect function return value encountered')

    def test_approx_equal_28fbe40318ce42a7a5fd1ee28e14458d(self): 
        Param3 = type('',(object,), {})()
        Param4 = type('',(object,), {})()
        self.assertNotRaises(self.module.approx_equal, *[0, 0, Param3, Param4])
        self.assertEqual(self.module.approx_equal(*[0, 0, Param3, Param4]), True, 'incorrect function return value encountered')

    def test_approx_equal_279532e93ae84bd9bed1bf90f4428941(self): 
        Param3 = type('',(object,), {})()
        Param4 = type('',(object,), {})()
        self.assertNotRaises(self.module.approx_equal, *[0, 0, Param3, Param4])
        self.assertEqual(self.module.approx_equal(*[0, 0, Param3, Param4]), True, 'incorrect function return value encountered')

    def test_approx_equal_7d897a945669483eaf9014b505499792(self): 
        Param3 = type('',(object,), {})()
        Param4 = type('',(object,), {})()
        self.assertNotRaises(self.module.approx_equal, *[0, 0, Param3, Param4])
        self.assertEqual(self.module.approx_equal(*[0, 0, Param3, Param4]), True, 'incorrect function return value encountered')

    def test_approx_equal_db2798d8e21d42b286eda749dc3c90a0(self): 
        Param3 = type('',(object,), {})()
        Param4 = type('',(object,), {})()
        self.assertNotRaises(self.module.approx_equal, *[1461055374234865915, 0, Param3, Param4])
        self.assertEqual(self.module.approx_equal(*[1461055374234865915, 0, Param3, Param4]), True, 'incorrect function return value encountered')

    def test_approx_equal_9ccca1aefaf043609f7c0708e9a6578e(self): 
        Param3 = type('',(object,), {})()
        Param4 = type('',(object,), {})()
        self.assertNotRaises(self.module.approx_equal, *[2335276838901610646, 0, Param3, Param4])
        self.assertEqual(self.module.approx_equal(*[2335276838901610646, 0, Param3, Param4]), True, 'incorrect function return value encountered')

    def test_approx_equal_dae1ff1641fb49548f30b26f54c47566(self): 
        Param3 = type('',(object,), {})()
        Param4 = type('',(object,), {})()
        self.assertNotRaises(self.module.approx_equal, *[570933242364456186, 0, Param3, Param4])
        self.assertEqual(self.module.approx_equal(*[570933242364456186, 0, Param3, Param4]), True, 'incorrect function return value encountered')

    def test_approx_equal_42c9a9e6dc2442af971d7d2278bf7400(self): 
        Param3 = type('',(object,), {})()
        Param4 = type('',(object,), {})()
        self.assertNotRaises(self.module.approx_equal, *[994, 0, Param3, Param4])
        self.assertEqual(self.module.approx_equal(*[994, 0, Param3, Param4]), True, 'incorrect function return value encountered')

    def test_approx_equal_f2ec09d613b146e48a487485c1b90e8e(self): 
        Param3 = type('',(object,), {})()
        Param4 = type('',(object,), {})()
        self.assertNotRaises(self.module.approx_equal, *[943, 0, Param3, Param4])
        self.assertEqual(self.module.approx_equal(*[943, 0, Param3, Param4]), True, 'incorrect function return value encountered')

    def test_approx_equal_11724f3966f947f8b3eda44d1d22324c(self): 
        Param3 = type('',(object,), {})()
        Param4 = type('',(object,), {})()
        self.assertNotRaises(self.module.approx_equal, *[199, 0, Param3, Param4])
        self.assertEqual(self.module.approx_equal(*[199, 0, Param3, Param4]), True, 'incorrect function return value encountered')

    def test_approx_equal_6389de1635ad4681bc8f70fc0eee1a27(self): 
        Param3 = type('',(object,), {})()
        Param4 = type('',(object,), {})()
        self.assertNotRaises(self.module.approx_equal, *[8526227503029157372, 0, Param3, Param4])
        self.assertEqual(self.module.approx_equal(*[8526227503029157372, 0, Param3, Param4]), True, 'incorrect function return value encountered')

    def test_approx_equal_c2061993b6404830bf7f44b70b66133d(self): 
        Param3 = type('',(object,), {})()
        Param4 = type('',(object,), {})()
        self.assertNotRaises(self.module.approx_equal, *[7084305517131841305, 0, Param3, Param4])
        self.assertEqual(self.module.approx_equal(*[7084305517131841305, 0, Param3, Param4]), True, 'incorrect function return value encountered')

    def test_approx_equal_5931703f73b043a09fa6fd7897df5a45(self): 
        Param3 = type('',(object,), {})()
        Param4 = type('',(object,), {})()
        self.assertNotRaises(self.module.approx_equal, *[6508623219935938797, 0, Param3, Param4])
        self.assertEqual(self.module.approx_equal(*[6508623219935938797, 0, Param3, Param4]), True, 'incorrect function return value encountered')

    def test_approx_equal_c8abae97e7c24627b26ca40cf7fccba4(self): 
        Param3 = type('',(object,), {})()
        Param4 = type('',(object,), {})()
        self.assertNotRaises(self.module.approx_equal, *[6508623219935938797, -8736418112569525826, Param3, Param4])
        self.assertEqual(self.module.approx_equal(*[6508623219935938797, -8736418112569525826, Param3, Param4]), True, 'incorrect function return value encountered')

    def test_approx_equal_bdb9cad9a3824a24b4a71b9a550e5623(self): 
        Param3 = type('',(object,), {})()
        Param4 = type('',(object,), {})()
        self.assertNotRaises(self.module.approx_equal, *[6508623219935938797, -7462078265811997708, Param3, Param4])
        self.assertEqual(self.module.approx_equal(*[6508623219935938797, -7462078265811997708, Param3, Param4]), True, 'incorrect function return value encountered')

    def test_approx_equal_0467fe21c54e477fa9eee3ae0faf96b9(self): 
        Param3 = type('',(object,), {})()
        Param4 = type('',(object,), {})()
        self.assertNotRaises(self.module.approx_equal, *[6508623219935938797, -7639708591453651354, Param3, Param4])
        self.assertEqual(self.module.approx_equal(*[6508623219935938797, -7639708591453651354, Param3, Param4]), True, 'incorrect function return value encountered')

    def test_approx_equal_a101114c4a604f94827ca235691bbd82(self): 
        Param3 = type('',(object,), {})()
        Param4 = type('',(object,), {})()
        self.assertNotRaises(self.module.approx_equal, *[6508623219935938797, -4449899796604440793, Param3, Param4])
        self.assertEqual(self.module.approx_equal(*[6508623219935938797, -4449899796604440793, Param3, Param4]), True, 'incorrect function return value encountered')

    def test_approx_equal_5749b95df7db47299d86cd617c92b208(self): 
        Param3 = type('',(object,), {})()
        Param4 = type('',(object,), {})()
        self.assertNotRaises(self.module.approx_equal, *[6508623219935938797, -481283442090188829, Param3, Param4])
        self.assertEqual(self.module.approx_equal(*[6508623219935938797, -481283442090188829, Param3, Param4]), True, 'incorrect function return value encountered')

    def test_approx_equal_a335fadb1fc841e5961e5191ece775ff(self): 
        Param3 = type('',(object,), {})()
        Param4 = type('',(object,), {})()
        self.assertNotRaises(self.module.approx_equal, *[6508623219935938797, -3826906411031990765, Param3, Param4])
        self.assertEqual(self.module.approx_equal(*[6508623219935938797, -3826906411031990765, Param3, Param4]), True, 'incorrect function return value encountered')

    def test_approx_equal_cb9ba04e1346493da5d6c15c943fc630(self): 
        Param3 = type('',(object,), {})()
        Param4 = type('',(object,), {})()
        self.assertNotRaises(self.module.approx_equal, *[6508623219935938797, -175, Param3, Param4])
        self.assertEqual(self.module.approx_equal(*[6508623219935938797, -175, Param3, Param4]), True, 'incorrect function return value encountered')

    def test_approx_equal_70b1615fc064437ab7fa8f78533100f6(self): 
        Param3 = type('',(object,), {})()
        Param4 = type('',(object,), {})()
        self.assertNotRaises(self.module.approx_equal, *[6508623219935938797, -974, Param3, Param4])
        self.assertEqual(self.module.approx_equal(*[6508623219935938797, -974, Param3, Param4]), True, 'incorrect function return value encountered')

    def test_approx_equal_0c03cdfb07ad496298bac507593d7f90(self): 
        Param3 = type('',(object,), {})()
        Param4 = type('',(object,), {})()
        self.assertNotRaises(self.module.approx_equal, *[6508623219935938797, -929, Param3, Param4])
        self.assertEqual(self.module.approx_equal(*[6508623219935938797, -929, Param3, Param4]), True, 'incorrect function return value encountered')

    def test_approx_equal_c2201b8f95fe4edea529318e0110f414(self): 
        Param3 = type('',(object,), {})()
        Param4 = type('',(object,), {})()
        self.assertNotRaises(self.module.approx_equal, *[6508623219935938797, 0, Param3, Param4])
        self.assertEqual(self.module.approx_equal(*[6508623219935938797, 0, Param3, Param4]), True, 'incorrect function return value encountered')

    def test_approx_equal_c9971c2475ff4ba3bfc4666c0ede86ea(self): 
        Param3 = type('',(object,), {})()
        Param4 = type('',(object,), {})()
        self.assertNotRaises(self.module.approx_equal, *[6508623219935938797, 0, Param3, Param4])
        self.assertEqual(self.module.approx_equal(*[6508623219935938797, 0, Param3, Param4]), True, 'incorrect function return value encountered')

    def test_approx_equal_966ebc90a8c7450ca5b6fbf527db8cd2(self): 
        Param3 = type('',(object,), {})()
        Param4 = type('',(object,), {})()
        self.assertNotRaises(self.module.approx_equal, *[6508623219935938797, 0, Param3, Param4])
        self.assertEqual(self.module.approx_equal(*[6508623219935938797, 0, Param3, Param4]), True, 'incorrect function return value encountered')

    def test_approx_equal_76c4dca96b474d52baac0504640b7ee5(self): 
        Param3 = type('',(object,), {})()
        Param4 = type('',(object,), {})()
        self.assertNotRaises(self.module.approx_equal, *[6508623219935938797, 2299004351204935507, Param3, Param4])
        self.assertEqual(self.module.approx_equal(*[6508623219935938797, 2299004351204935507, Param3, Param4]), True, 'incorrect function return value encountered')

    def test_approx_equal_79101415071941d5be7a87449e1c3859(self): 
        Param3 = type('',(object,), {})()
        Param4 = type('',(object,), {})()
        self.assertNotRaises(self.module.approx_equal, *[6508623219935938797, 718409013508866449, Param3, Param4])
        self.assertEqual(self.module.approx_equal(*[6508623219935938797, 718409013508866449, Param3, Param4]), True, 'incorrect function return value encountered')

    def test_approx_equal_5822eeaf63ff404b9090b69882f3ff21(self): 
        Param3 = type('',(object,), {})()
        Param4 = type('',(object,), {})()
        self.assertNotRaises(self.module.approx_equal, *[6508623219935938797, 3855680292900019305, Param3, Param4])
        self.assertEqual(self.module.approx_equal(*[6508623219935938797, 3855680292900019305, Param3, Param4]), True, 'incorrect function return value encountered')

    def test_approx_equal_3dc79d78883a4e56870b4da91d853236(self): 
        Param3 = type('',(object,), {})()
        Param4 = type('',(object,), {})()
        self.assertNotRaises(self.module.approx_equal, *[6508623219935938797, 223, Param3, Param4])
        self.assertEqual(self.module.approx_equal(*[6508623219935938797, 223, Param3, Param4]), True, 'incorrect function return value encountered')

    def test_approx_equal_589eab1d6e6f4f62af6b4ef499706a48(self): 
        Param3 = type('',(object,), {})()
        Param4 = type('',(object,), {})()
        self.assertNotRaises(self.module.approx_equal, *[6508623219935938797, 126, Param3, Param4])
        self.assertEqual(self.module.approx_equal(*[6508623219935938797, 126, Param3, Param4]), True, 'incorrect function return value encountered')

    def test_approx_equal_a8b65acefb91484f8ed93be6c78ea673(self): 
        Param3 = type('',(object,), {})()
        Param4 = type('',(object,), {})()
        self.assertNotRaises(self.module.approx_equal, *[6508623219935938797, 218, Param3, Param4])
        self.assertEqual(self.module.approx_equal(*[6508623219935938797, 218, Param3, Param4]), True, 'incorrect function return value encountered')

    def test_approx_equal_149d9192aa214c28b89f56dbaa2852c9(self): 
        Param3 = type('',(object,), {})()
        Param4 = type('',(object,), {})()
        self.assertNotRaises(self.module.approx_equal, *[6508623219935938797, 8031884445174416923, Param3, Param4])
        self.assertEqual(self.module.approx_equal(*[6508623219935938797, 8031884445174416923, Param3, Param4]), True, 'incorrect function return value encountered')

    def test_approx_equal_a57773f9b7b9462d94598f67052896cc(self): 
        Param3 = type('',(object,), {})()
        Param4 = type('',(object,), {})()
        self.assertNotRaises(self.module.approx_equal, *[6508623219935938797, 8194069775094425622, Param3, Param4])
        self.assertEqual(self.module.approx_equal(*[6508623219935938797, 8194069775094425622, Param3, Param4]), True, 'incorrect function return value encountered')

    def test_approx_equal_cde3abc933664290be3613fb861bd201(self): 
        Param3 = type('',(object,), {})()
        Param4 = type('',(object,), {})()
        self.assertNotRaises(self.module.approx_equal, *[6508623219935938797, 8404225380505660358, Param3, Param4])
        self.assertEqual(self.module.approx_equal(*[6508623219935938797, 8404225380505660358, Param3, Param4]), True, 'incorrect function return value encountered')

    def test_perm_all_None(self): 
        self.assertRaises(TypeError, self.module.perm, *[None, None])

    def test_perm_all_attr_None_wdef(self): 
        self.assertRaises(TypeError, self.module.perm, *[None, None])

    def test_perm_all_attr_MetaParam_wdef(self): 
        self.assertRaises(TypeError, self.module.perm, *[None, None])

    def test_perm_6c92bb388a07410fb605972dff0127c4(self): 
        Param1 = type('',(object,), {})()
        Param2 = type('',(object,), {})()
        self.assertRaises(TypeError, self.module.perm, *[Param1, Param2])

    def test_perm_2e6abcc574504c39850f2bac58dd6bf3(self): 
        Param1 = type('',(object,), {})()
        self.assertRaises(TypeError, self.module.perm, *[Param1, 0])

    def test_perm_3a325e3a4e60413bb13eca033b1553a9(self): 
        self.assertNotRaises(self.module.perm, *[0, 0])
        self.assertEqual(self.module.perm(*[0, 0]), 1, 'incorrect function return value encountered')

    def test_perm_fd60de189d8f44099d9a481566f4d148(self): 
        self.assertNotRaises(self.module.perm, *[1, 0])
        self.assertEqual(self.module.perm(*[1, 0]), 1, 'incorrect function return value encountered')

    def test_perm_b5cd59159f1946f589f1d0e3728b533c(self): 
        self.assertNotRaises(self.module.perm, *[0, 0])
        self.assertEqual(self.module.perm(*[0, 0]), 1, 'incorrect function return value encountered')

    def test_perm_fe8eec8e76c54ec389f8b3093d6a0019(self): 
        self.assertNotRaises(self.module.perm, *[0, 0])
        self.assertEqual(self.module.perm(*[0, 0]), 1, 'incorrect function return value encountered')

    def test_perm_c04700ba307e451296848d6ef3d3a935(self): 
        self.assertNotRaises(self.module.perm, *[0, 0])
        self.assertEqual(self.module.perm(*[0, 0]), 1, 'incorrect function return value encountered')

    def test_perm_5fd15087f9854ab58bfa58ec67b59a65(self): 
        self.assertNotRaises(self.module.perm, *[757, 0])
        self.assertEqual(self.module.perm(*[757, 0]), 1L, 'incorrect function return value encountered')

    def test_perm_7017f5a4c4e745e3b8bbbaca3b2bbb44(self): 
        self.assertNotRaises(self.module.perm, *[465, 0])
        self.assertEqual(self.module.perm(*[465, 0]), 1L, 'incorrect function return value encountered')

    def test_perm_372ab171a348497b8035515f12b2f321(self): 
        self.assertNotRaises(self.module.perm, *[793, 0])
        self.assertEqual(self.module.perm(*[793, 0]), 1L, 'incorrect function return value encountered')

    def test_argmax_all_None(self): 
        self.assertRaises(TypeError, self.module.argmax, *[None])

    def test_argmax_all_attr_None_wdef(self): 
        self.assertRaises(TypeError, self.module.argmax, *[None])

    def test_argmax_all_attr_MetaParam_wdef(self): 
        self.assertRaises(TypeError, self.module.argmax, *[None])

    def test_argmax_5fe63084cde8447f8311ce3d42c7049a(self): 
        Param1 = type('',(object,), {})()
        self.assertRaises(TypeError, self.module.argmax, *[Param1])

    def test_argmax_b267d6b7aff44a30806ed9988fc6b85b(self): 
        Param1 = type('',(object,), {})()
        self.assertRaises(TypeError, self.module.argmax, *[Param1])

    def test_argmax_90eec8ae2a2a431eb81304d53a3dae25(self): 
        Param1 = type('',(object,), {})()
        self.assertRaises(TypeError, self.module.argmax, *[Param1])

    def test_mean_all_None(self): 
        self.assertRaises(TypeError, self.module.mean, *[None])

    def test_mean_all_attr_None_wdef(self): 
        self.assertRaises(TypeError, self.module.mean, *[None])

    def test_mean_all_attr_MetaParam_wdef(self): 
        self.assertRaises(TypeError, self.module.mean, *[None])

    def test_mean_3f5e12f197c14380b0a51e60e4118d19(self): 
        Param1 = type('',(object,), {})()
        self.assertRaises(TypeError, self.module.mean, *[Param1])

    def test_mean_c2a640b8ae1e48e1a110391a15a533d8(self): 
        Param1 = type('',(object,), {})()
        self.assertRaises(TypeError, self.module.mean, *[Param1])

    def test_mean_45e29a753ace4029a4542c8f50ee3ce9(self): 
        Param1 = type('',(object,), {})()
        self.assertRaises(TypeError, self.module.mean, *[Param1])


if __name__ == '__main__':
    unittest.main()
