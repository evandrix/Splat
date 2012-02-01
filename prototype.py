#!/usr/bin/env python
# -*- coding: utf-8 -*-
''' Prototype '''
import os
import sys
import time
import re
import IPython
import dis
import types
import py
from inspect import *
from pprint import pprint
#print "Disassembling Python module 'lazy_test'..."
#sys.stdout = sys.__stderr__
#dis.dis(lazy_test)
#sys.stdout = sys.__stdout__

# Colors
HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
colors = [ HEADER, OKBLUE, OKGREEN, WARNING, FAIL ]
#for c in colors:
#    print c + "test" + ENDC
    
# Redirect output streams
class writer :
    def __init__(self, *writers):
        self.writers = writers

    def write(self, text):
        for w in self.writers:
            if text.startswith(">>"):
                w.write(WARNING + text + ENDC)
            else:
                w.write(OKBLUE + text + ENDC)
sys.stdout = writer(sys.stdout)
#############################################################################
MODULE_UNDER_TEST='lazy_test' if len(sys.argv) < 2 else sys.argv[1]
#############################################################################
# Import Python module bytecode
try:
    MODULE_UNDER_TEST = __import__(MODULE_UNDER_TEST)
except ImportError, ie:
    print >> sys.stderr, "Module cannot be imported"
    sys.exit(0)
#############################################################################
# Top level functions
functions = getmembers(MODULE_UNDER_TEST, isfunction)
print ">> Scanning for top level functions..."
print "\t",
pprint(functions)
print
#############################################################################
# Class definitions
print ">> Scanning for class definitions..."
classes = getmembers(MODULE_UNDER_TEST, isclass)
# methods within classes
for label, klass in classes:
    print "\t", label, klass
    print "\t\t", getmembers(klass, ismethod)
print
#############################################################################
class TestObject():
    pass

def get_user_attributes(cls):
    boring = dir(type('dummy', (object,), {}))
    return [item for item in getmembers(cls) if item[0] not in boring]

# unwraps a list of arguments to function
def wrapper(func, args):
    return func(*args)

# Collect minimal (lazy) object instantiation into a list
print ">> Generating test context..."
context = []
for label, klass in classes:
    obj = params = None
    while True:
        if obj:
            # store complete object
            tobj = TestObject()
            tobj.ref_object      = obj
            tobj.num_ctor_params = len(params)
            context.append(tobj)
            break
        # try the empty class constructor first
        # then augment with None's
        if params is None:
            params = []
        else:
            params.append(None)
        try:
            obj = wrapper(klass, params)
        except TypeError, te:
            pass
assert len(context) == len(classes), "Not all classes instantiated (lazily)!"
for c in context:
    print "\t", get_user_attributes(c)
print
#############################################################################
# Type sanity checking
print ">> Verifying class types..."
for label, klass in classes:
    if type(klass) is types.TypeType:
        print "\tNew user-defined class:", klass
    elif type(klass) is types.ClassType:
        print "\tUser-defined old-style classes:", klass
print

#############################################################################
# Generating unit test suite
print ">> Writing out tests to file..."
fout = open("%s_unittest.py" % MODULE_UNDER_TEST.__name__, "w")

print >> fout, MODULE_UNDER_TEST

fout.close()
del fout
#############################################################################
# Unused functions
"""
    isinstance()
    issubclass()
    IPython.embed()
"""
#############################################################################
del MODULE_UNDER_TEST   # cleanup
sys.exit(0)
"""
    try:
        instance = getattr(module, class_name)()
    except TypeError, e:
        _, expected, actual, _ = re.split('^.*takes exactly (\d)+ arguments \((\d)+ given\)$', e.message)
        assert (expected > actual), ('Constructor args: %s ≤ %s' %(expected,actual))
        expected = int(expected)
        actual = int(actual)
        arglist = [ None for arg in range(expected - actual) ]
        instance = getattr(module, class_name)(*arglist)
        test_dict = {'name':None,'age':None,'address':None}
        instance = getattr(module, class_name)(**test_dict)
    context.append(instance)
print >> sys.stderr, '[',
for obj in context:
    if hasattr(obj, '__str__'):
        print >> sys.stderr, obj.__str__(),
    else:
        print >> sys.stderr, obj,
print >> sys.stderr, ']'
for name, fn in functions:
    if name == 'foo':
        print 'Executing function lazy_test.%s()...' % name
        print '\t', inspect.getargspec(fn)
        args, varargs, keywords, defaults = inspect.getargspec(fn)
        context.append('5')
        arglist = []
        while True:
            try:
                apply(fn, arglist)
                break
            except TypeError, e:
                _, _, expected, actual, _ = re.split('^.*takes (exactly|at least) (\d)+ arguments \((\d)+ given\)$', e.message)
                expected = int(expected)
                actual = int(actual)
                print >> sys.stderr, 'expected = %d; actual = %d' % (expected, actual)
                # initially all NoneType arguments
                if not len(arglist):
                    arglist = [ None for arg in range(expected - actual) ]
            except AttributeError, e:
                # failed: have to initialise one of them (lazily)
                _, _, fn_name, _ = re.split('^\'([^\']+)\' object has no attribute \'([^\']+)\'$', e.message)
                _, _, tb = sys.exc_info()

                t = py.code.Traceback(tb)
                code = str(t[-1].statement).strip()
                keywords = re.split('\.', code)
                arg = None
                for idx, keyword in enumerate(keywords):
                    if fn_name in keyword:
                        arg = keywords[idx-1]
                pos = [ i for i,x in enumerate(args) if x == arg ][0]
                for name, fragment in classes:
                    if hasattr(fragment, fn_name):
                        for class_name in context:
                            if isinstance(class_name, fragment):
                                arglist[pos] = class_name
print "Instantiated argument list:", arglist
"""
