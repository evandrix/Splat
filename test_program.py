#!/usr/bin/env python
# -*- coding: utf-8 -*-
# run nosetests for an entire directory of tests: `nosetests -v -s -w tests`

class TestProgram:
    def setUp(self):
        print "setup"

    def tearDown(self):
        print "teardown"

    def test_case_1(self):
        assert 'c' == 'c'
        print 'some value'
        print '0'
        print '1'
        print '2'

#from unittest import TestCase
#class TestProgramAlt(TestCase):
#    def test_case_2(self):
#        self.assert_(1 == 1)
#        self.assertEquals(1,1)
