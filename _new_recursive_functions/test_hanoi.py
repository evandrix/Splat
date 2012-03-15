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
from hanoi import *

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
        self.hanoi = __import__('hanoi')
    def tearDown(self):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        del self.hanoi
    def assertNotRaises(self, function, *args, **kwargs):
        with self.assertRaises(Exception):
            try:
                function(*args, **kwargs)
            except:
                pass
            else:
                raise Exception

    def test_all(self):
        h = Hanoi()
        self.assertEquals([], hanoi(0))
        self.assertEquals([], hanoi(0))
        self.assertEquals([(1, 3)], hanoi(1))
        self.assertEquals([], hanoi(0))
        self.assertEquals([], hanoi(0))
        self.assertEquals([(3, 2)], hanoi(1))
        self.assertEquals([(1, 3), (1, 2), (3, 2)], hanoi(2))
        self.assertEquals([], hanoi(0))
        self.assertEquals([], hanoi(0))
        self.assertEquals([(2, 1)], hanoi(1))
        self.assertEquals([], hanoi(0))
        self.assertEquals([], hanoi(0))
        self.assertEquals([(1, 3)], hanoi(1))
        self.assertEquals([(2, 1), (2, 3), (1, 3)], hanoi(2))
        self.assertEquals([(1, 3), (1, 2), (3, 2), (1, 3), (2, 1), (2, 3), (1, 3)], hanoi(3))

if __name__ == '__main__':
    unittest.main()
