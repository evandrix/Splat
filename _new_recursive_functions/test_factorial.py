#!/usr/bin/env python
# -*- coding: utf-8 -*-
# run nosetests for directory 'tests': `nosetests -vsw tests`
import os
import sys
import time
import re
import pprint
import random
import types
import unittest
from factorial import *

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
        sys.stdout = DevNull(sys.stdout)
        sys.stderr = DevNull(sys.stderr)
        # reference module under test
        self.factorial = __import__('factorial')
    def tearDown(self):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        del self.factorial
    def assertNotRaises(self, function, *args, **kwargs):
        with self.assertRaises(Exception):
            try:
                function(*args, **kwargs)
            except:
                pass
            else:
                raise Exception

    def test_all(self):
        self.assertEquals(1, factorial(0))
        self.assertEquals(1, factorial(1))
        self.assertEquals(2, factorial(2))
        self.assertEquals(6, factorial(3))
        self.assertEquals(24, factorial(4))
        self.assertEquals(120, factorial(5))
        self.assertEquals(720, factorial(6))
        self.assertEquals(5040, factorial(7))
        self.assertEquals(40320, factorial(8))
        self.assertEquals(362880, factorial(9))
        self.assertEquals(3628800, factorial(10))
        self.assertEquals(39916800, factorial(11))
        self.assertEquals(479001600, factorial(12))
        self.assertEquals(6227020800, factorial(13))
        self.assertEquals(87178291200, factorial(14))
        self.assertEquals(1307674368000, factorial(15))
        self.assertEquals(20922789888000, factorial(16))
        self.assertEquals(355687428096000, factorial(17))
        self.assertEquals(6402373705728000, factorial(18))
        self.assertEquals(121645100408832000, factorial(19))
        self.assertEquals(2432902008176640000, factorial(20))
        self.assertEquals(51090942171709440000L, factorial(21))
        self.assertEquals(1124000727777607680000L, factorial(22))
        self.assertEquals(25852016738884976640000L, factorial(23))
        self.assertEquals(620448401733239439360000L, factorial(24))
        self.assertEquals(15511210043330985984000000L, factorial(25))
        self.assertEquals(403291461126605635584000000L, factorial(26))
        self.assertEquals(10888869450418352160768000000L, factorial(27))
        self.assertEquals(304888344611713860501504000000L, factorial(28))
        self.assertEquals(8841761993739701954543616000000L, factorial(29))
        self.assertEquals(265252859812191058636308480000000L, factorial(30))
        self.assertEquals(8222838654177922817725562880000000L, factorial(31))
        self.assertEquals(263130836933693530167218012160000000L, factorial(32))
        self.assertEquals(8683317618811886495518194401280000000L, factorial(33))
        self.assertEquals(295232799039604140847618609643520000000L, factorial(34))
        self.assertEquals(10333147966386144929666651337523200000000L, factorial(35))
        self.assertEquals(371993326789901217467999448150835200000000L, factorial(36))
        self.assertEquals(13763753091226345046315979581580902400000000L, factorial(37))
        self.assertEquals(523022617466601111760007224100074291200000000L, factorial(38))
        self.assertEquals(20397882081197443358640281739902897356800000000L, factorial(39))
        self.assertEquals(815915283247897734345611269596115894272000000000L, factorial(40))
        self.assertEquals(33452526613163807108170062053440751665152000000000L, factorial(41))
        self.assertEquals(1405006117752879898543142606244511569936384000000000L, factorial(42))
        self.assertEquals(60415263063373835637355132068513997507264512000000000L, factorial(43))
        self.assertEquals(2658271574788448768043625811014615890319638528000000000L, factorial(44))
        self.assertEquals(119622220865480194561963161495657715064383733760000000000L, factorial(45))
        self.assertEquals(5502622159812088949850305428800254892961651752960000000000L, factorial(46))
        self.assertEquals(258623241511168180642964355153611979969197632389120000000000L, factorial(47))
        self.assertEquals(12413915592536072670862289047373375038521486354677760000000000L, factorial(48))
        self.assertEquals(608281864034267560872252163321295376887552831379210240000000000L, factorial(49))
        self.assertEquals(30414093201713378043612608166064768844377641568960512000000000000L, factorial(50))
        self.assertEquals(1551118753287382280224243016469303211063259720016986112000000000000L, factorial(51))
        self.assertEquals(80658175170943878571660636856403766975289505440883277824000000000000L, factorial(52))
        self.assertEquals(4274883284060025564298013753389399649690343788366813724672000000000000L, factorial(53))
        self.assertEquals(230843697339241380472092742683027581083278564571807941132288000000000000L, factorial(54))
        self.assertEquals(12696403353658275925965100847566516959580321051449436762275840000000000000L, factorial(55))
        self.assertEquals(710998587804863451854045647463724949736497978881168458687447040000000000000L, factorial(56))
        self.assertEquals(40526919504877216755680601905432322134980384796226602145184481280000000000000L, factorial(57))
        self.assertEquals(2350561331282878571829474910515074683828862318181142924420699914240000000000000L, factorial(58))
        self.assertEquals(138683118545689835737939019720389406345902876772687432540821294940160000000000000L, factorial(59))
        self.assertEquals(8320987112741390144276341183223364380754172606361245952449277696409600000000000000L, factorial(60))
        self.assertEquals(507580213877224798800856812176625227226004528988036003099405939480985600000000000000L, factorial(61))
        self.assertEquals(31469973260387937525653122354950764088012280797258232192163168247821107200000000000000L, factorial(62))
        self.assertEquals(1982608315404440064116146708361898137544773690227268628106279599612729753600000000000000L, factorial(63))
        self.assertEquals(126886932185884164103433389335161480802865516174545192198801894375214704230400000000000000L, factorial(64))
        self.assertEquals(8247650592082470666723170306785496252186258551345437492922123134388955774976000000000000000L, factorial(65))
        self.assertEquals(544344939077443064003729240247842752644293064388798874532860126869671081148416000000000000000L, factorial(66))
        self.assertEquals(36471110918188685288249859096605464427167635314049524593701628500267962436943872000000000000000L, factorial(67))
        self.assertEquals(2480035542436830599600990418569171581047399201355367672371710738018221445712183296000000000000000L, factorial(68))
        self.assertEquals(171122452428141311372468338881272839092270544893520369393648040923257279754140647424000000000000000L, factorial(69))

if __name__ == '__main__':
    unittest.main()
