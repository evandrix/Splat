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

t0 = time.time()
#print "Disassembling Python module 'program'..."
#sys.stdout = sys.__stderr__
#dis.dis(program)
#sys.stdout = sys.__stdout__

# Colors
FAIL = '\033[91m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
OKBLUE = '\033[94m'
HEADER = '\033[95m'
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
MODULE_UNDER_TEST='program' if len(sys.argv) < 2 else sys.argv[1]
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

# Collect minimal (lazy) object instantiation into a list
print ">> Generating test context..."
context = []
for label, klass in classes:
    obj = params = None
    while True:
        try:
            obj = apply(klass, params)
        except TypeError, te:
            # try the empty class constructor first
            # then augment with None's
            if params is None:
                params = []
            else:
                params.append(None)
        else:
            # store complete object
            tobj = TestObject()
            tobj.ref_object      = obj
            tobj.num_ctor_params = len(params)
            context.append(tobj)
            break

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
print ">> Writing out unit test suite to file..."
import simplejson
import pyparsing    # S-Expr
import pystache

def todict(obj, classkey=None):
    """ Serialise object to dictionary for template rendering """

    if isinstance(obj, dict):
        for k in obj.keys():
            obj[k] = todict(obj[k], classkey)
        return obj
    elif hasattr(obj, "__iter__"):
        return [todict(v, classkey) for v in obj]
    elif hasattr(obj, "__dict__"):
        data = dict([(key, todict(value, classkey)) 
            for key, value in obj.__dict__.iteritems() 
            if not callable(value) and not key.startswith('_')])
        if classkey is not None and hasattr(obj, "__class__"):
            data[classkey] = obj.__class__.__name__
        return data
    else:
        return obj

class tmplObj:
    def __init__(self, idx):
        self.n = idx
objs = [ todict(tmplObj(i)) for i in xrange(3) ]
tmpl_context = {
    'a': context[0].ref_object,
    'b': objs
}
template_file = open("test_template.mustache", "r")
tmpl = template_file.read()
template_file.close()
rendered = pystache.render(tmpl, tmpl_context)
print rendered

fout = open("test_%s.py" % MODULE_UNDER_TEST.__name__, "w")
print >> fout, rendered
fout.close()
del fout
print ">> ...done!"
#############################################################################
print ">> Testing global functions..."

for name, fn in functions:
    if name == 'foo':
        print '\tExecuting function %s.%s()...' % (MODULE_UNDER_TEST.__name__,name)
        print '\tFound function definition:', getargspec(fn)
        args, varargs, keywords, defaults = getargspec(fn)
        
        # incrementally instantiating function arguments
        arglist = None
        i = 0
        while True:
            encountered_errors = False

            try:
                apply(fn, arglist)
            except AttributeError as ae:
                print 'AttributeError encountered:', ae
                # arguments cannot be NoneType
                encountered_errors = True
                print ae.args
            except TypeError, te:
                print 'TypeError encountered:', te
                # insufficient no. of arguments
                encountered_errors = True
                if arglist is None:
                    arglist = []
                else:
                    arglist.append(None)
            except:
                print "WARN: Uncaught Exception!"
            else:
                break
            finally:
                pass
            
            if not encountered_errors or i > 5:
                break
            i+=1
# print "Instantiated argument list:", arglist
#############################################################################
# User-defined Exceptions
class MyError(Exception):
     def __init__(self, value):
         self.value = value
     def __str__(self):
         return repr(self.value)
try:
    raise MyError(2*2)
except MyError as e:
    print 'Custom exception, value =', e.value
#############################################################################
# Unused functions
"""
    isinstance()
    issubclass()
"""
#############################################################################
print >> sys.stderr, "*** Total time: %.3f seconds ***" % (time.time() - t0)
del MODULE_UNDER_TEST   # cleanup
sys.exit(0)
#############################################################################
"""
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
"""
