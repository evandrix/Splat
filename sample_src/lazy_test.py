#!/usr/bin/env python
# -*- coding: utf-8 -*-

class MyObject(object):
    """ Example for dis. """
    CLASS_ATTRIBUTE = 'some value'
    def __init__(self, name, age, address):
        self.name = name
    def __str__(self):
        return 'MyObject(%s)' % self.name

class clazz1:
    def func1(self):
        print 'class#1', self

class clazz2:
    def func2(self, a, b, c, d=None):
        x = a + b + c + 60
        print 'class#2', self, x

def foo(myobj, klass1, klass2, n):
    klass1.func1()
    klass2.func2(1, 2, 3, 4)    
    print "myobj:", myobj.__str__(), "n:", n
