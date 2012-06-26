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
        self.module = __import__('factorial')
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

    def test_factorial_all_None(self): 
        self.assertRaises(TypeError, self.module.factorial, *[None])

    def test_factorial_all_attr_None_wdef(self): 
        self.assertRaises(TypeError, self.module.factorial, *[None])

    def test_factorial_all_attr_MetaParam_wdef(self): 
        self.assertRaises(TypeError, self.module.factorial, *[None])

    def test_factorial_d0c14d4cdd1b4018acd6cbaa74b4622b(self): 
        Param1 = type('',(object,), {})()
        self.assertRaises(TypeError, self.module.factorial, *[Param1])

    def test_factorial_ac07ae2c8cb445cfa037bade81ddc454(self): 
        self.assertNotRaises(self.module.factorial, *[0])
        self.assertEqual(self.module.factorial(*[0]), 1, 'incorrect function return value encountered')

    def test_factorial_140323707760896(self): 
        self.assertEqual(479001600, self.module.factorial(12))

    def test_factorial_140323707760512(self): 
        self.assertEqual(304888344611713860501504000000L, self.module.factorial(28))

    def test_factorial_140323707761160(self): 
        self.assertEqual(1, self.module.factorial(1))

    def test_factorial_140323707761040(self): 
        self.assertEqual(720, self.module.factorial(6))

    def test_factorial_140323707760728(self): 
        self.assertEqual(121645100408832000, self.module.factorial(19))

    def test_factorial_140323707760536(self): 
        self.assertEqual(10888869450418352160768000000L, self.module.factorial(27))

    def test_factorial_140323707760368(self): 
        self.assertEqual(295232799039604140847618609643520000000L, self.module.factorial(34))

    def test_factorial_140323707760800(self): 
        self.assertEqual(20922789888000, self.module.factorial(16))

    def test_factorial_140323707760560(self): 
        self.assertEqual(403291461126605635584000000L, self.module.factorial(26))

    def test_factorial_140323707761064(self): 
        self.assertEqual(120, self.module.factorial(5))

    def test_factorial_140323707760944(self): 
        self.assertEqual(3628800, self.module.factorial(10))

    def test_factorial_140323707760776(self): 
        self.assertEqual(355687428096000, self.module.factorial(17))

    def test_factorial_140323707761136(self): 
        self.assertEqual(2, self.module.factorial(2))

    def test_factorial_140323707760824(self): 
        self.assertEqual(1307674368000, self.module.factorial(15))

    def test_factorial_140323707760416(self): 
        self.assertEqual(263130836933693530167218012160000000L, self.module.factorial(32))

    def test_factorial_140323707761088(self): 
        self.assertEqual(24, self.module.factorial(4))

    def test_factorial_140323707761184(self): 
        self.assertEqual(1, self.module.factorial(0))

    def test_factorial_140323707760968(self): 
        self.assertEqual(362880, self.module.factorial(9))

    def test_factorial_140323707762296(self): 
        self.assertEqual(371993326789901217467999448150835200000000L, self.module.factorial(36))

    def test_factorial_140323707760704(self): 
        self.assertEqual(2432902008176640000, self.module.factorial(20))

    def test_factorial_140323707760848(self): 
        self.assertEqual(87178291200, self.module.factorial(14))

    def test_factorial_140323707760440(self): 
        self.assertEqual(8222838654177922817725562880000000L, self.module.factorial(31))

    def test_factorial_140323707760344(self): 
        self.assertEqual(10333147966386144929666651337523200000000L, self.module.factorial(35))

    def test_factorial_140323707760920(self): 
        self.assertEqual(39916800, self.module.factorial(11))

    def test_factorial_140323707760608(self): 
        self.assertEqual(620448401733239439360000L, self.module.factorial(24))

    def test_factorial_140323707760464(self): 
        self.assertEqual(265252859812191058636308480000000L, self.module.factorial(30))

    def test_factorial_140323707760992(self): 
        self.assertEqual(40320, self.module.factorial(8))

    def test_factorial_140323707761112(self): 
        self.assertEqual(6, self.module.factorial(3))

    def test_factorial_140323707760656(self): 
        self.assertEqual(1124000727777607680000L, self.module.factorial(22))

    def test_factorial_140323707760872(self): 
        self.assertEqual(6227020800, self.module.factorial(13))

    def test_factorial_140323707760392(self): 
        self.assertEqual(8683317618811886495518194401280000000L, self.module.factorial(33))

    def test_factorial_140323707760752(self): 
        self.assertEqual(6402373705728000, self.module.factorial(18))

    def test_factorial_140323707760680(self): 
        self.assertEqual(51090942171709440000L, self.module.factorial(21))

    def test_factorial_140323707761016(self): 
        self.assertEqual(5040, self.module.factorial(7))

    def test_factorial_140323707760584(self): 
        self.assertEqual(15511210043330985984000000L, self.module.factorial(25))

    def test_factorial_140323707760488(self): 
        self.assertEqual(8841761993739701954543616000000L, self.module.factorial(29))

    def test_factorial_140323707760632(self): 
        self.assertEqual(25852016738884976640000L, self.module.factorial(23))

    def test_factorial_140323707762272(self): 
        self.assertEqual(13763753091226345046315979581580902400000000L, self.module.factorial(37))


if __name__ == '__main__':
    unittest.main()
