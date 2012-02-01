#!/usr/bin/env python
# -*- coding: utf-8 -*-
''' introspection.py '''
import sys
import re
import IPython
import lazy_test
import dis
import inspect
import types
import py

print "Disassembling Python module 'lazy_test'..."
sys.stdout = sys.__stderr__
dis.dis(lazy_test)
sys.stdout = sys.__stdout__

# get classes
classes = inspect.getmembers(lazy_test, inspect.isclass)
functions = inspect.getmembers(lazy_test, inspect.isfunction)
print "Searching for class definitions in bytecode..."
print >> sys.stderr, classes
del lazy_test

module_name = 'lazy_test'
module = __import__(module_name)
context = []
for class_name, fragment in classes:
    # issubclass
    print type(class_name), type(fragment), isinstance(fragment, type)
    if type(fragment) is types.ClassType:
        print fragment()
    try:
        instance = getattr(module, class_name)()
    except TypeError, e:
        _, expected, actual, _ = re.split('^.*takes exactly (\d)+ arguments \((\d)+ given\)$', e.message)
        assert (expected > actual), ('Constructor args: %s ≤ %s' %(expected,actual))
        expected = int(expected)
        actual = int(actual)
        arglist = [ None for arg in range(expected - actual) ]
#        IPython.embed()
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
