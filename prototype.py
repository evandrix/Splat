#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import time
import re
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
            elif text.startswith("**"):
                w.write(HEADER + text + ENDC)
            else:
                w.write(OKBLUE + text + ENDC)
sys.stdout = writer(sys.stdout)

MODULE_UNDER_TEST='program' if len(sys.argv) < 2 else sys.argv[1]
#############################################################################
class MyType(type): pass
class MyParam(object):
    __metaclass__ = MyType
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return 'param%d' % self.value
    def __repr__(self):
        return 'param%d' % self.value
    def __getttr__(self, name):
        raise AttributeError, name
def repr(arg):
    return arg.__class__.__name__
def getattr(self, name):
    print self, 'tried to get attribute:', name
    if name == '__call__':
        return lambda:None
    if name == 'func2':
        return lambda:None
    if name == 'func3':
        return lambda:None
    #raise AttributeError,name

def create_function(name, args):
    def y(): pass
    y_code = types.CodeType(args, \
            y.func_code.co_nlocals, \
            y.func_code.co_stacksize, \
            y.func_code.co_flags, \
            y.func_code.co_code, \
            y.func_code.co_consts, \
            y.func_code.co_names, \
            y.func_code.co_varnames, \
            y.func_code.co_filename, \
            name, \
            y.func_code.co_firstlineno, \
            y.func_code.co_lnotab)
    return types.FunctionType(y_code, y.func_globals, name)

def run(functions):
    print ">> Testing global functions..."
    for name, fn in functions:
        if name == 'foo':   # TODO: remove target function name here
            print '\t%s.%s()...' % (MODULE_UNDER_TEST.__name__,name)
            print '\t', getargspec(fn)
            args, varargs, keywords, defaults = getargspec(fn)

            # instantiate argument list according to argspec
            arglist = [] if len(args) else None

            for i in xrange(len(args)):
                param_obj = MyParam(i)
                param_obj.__class__ = type(
                    "param%d" % (i),        #name
                    (object,),              #bases
                    {                       #attrs
                        '__repr__':repr,
                        '__getattr__':getattr
                    }
                )
                arglist.append(param_obj)

            while True:
                try:
                    apply(fn, arglist)
                except AttributeError as ae:
                    print OKGREEN + 'AttributeError' + ENDC + ':', ae
                    _, param, _, missing_fn, _ = re.split('^\'?([^\']+)\'? (instance|object) has no attribute \'([^\']+)\'$', ae.message)

                    exception_type, exception_value, tb = sys.exc_info()
                    code = py.code.Traceback(tb)[-1]
                    fn_name = code.name
                    fn_frame = code.frame
                    fn_code = fn_frame.code
                    fn_lineno = code.lineno + 1
                    code.getfirstlinesource()
                    code.locals
                    code.relline

                    _, idx, _ = re.split('param([0-9]+)', param)
                    idx = int(idx)
                    if hasattr(arglist[idx], missing_fn):
                        param = arglist[idx].__dict__[missing_fn]
                        if param is None:
                            arglist[idx].__dict__[missing_fn] = 0
                        elif isinstance(param, int):
                            arglist[idx].__dict__[missing_fn] = 0.0
                        elif isinstance(param, float):
                            arglist[idx].__dict__[missing_fn] = ''
                        elif isinstance(param, str):
                            setattr(arglist[idx], missing_fn, lambda:None)
                    else:
                        arglist[idx].__dict__[missing_fn] = None

                    continue
                    
                    tb = sys.exc_info()[2]
                    stack = []

                    while tb:
                        stack.append(tb.tb_frame)
                        tb = tb.tb_next

                    traceback.print_exc()
                    print "Locals by frame, innermost last"
                    
                    from byteplay import Code
                    from pprint import pprint
                    code = Code.from_code(arglist[idx].__dict__[missing_fn].func_code)
                    pprint(code.code)
                    code = Code.from_code(MyObject.func3.func_code)
                    pprint(code.code)
                    #import IPython
                    #IPython.embed()
                except TypeError, te:
                    print OKGREEN + 'TypeError' + ENDC + ':', te
                    try:
                        _, _, _ = re.split("^\'(.*)\' object is not callable$", te.message)
                        if not hasattr(arglist[1], '__call__'):
                            arglist[1].__dict__['func2'] = create_function(missing_fn, 0)
                        if not hasattr(arglist[0], '__call__'):
                                arglist[0].__dict__['func3'] = create_function(missing_fn, 0)

#if hasattr(param, '__call__'): #function
#args = []
#the_args, _, _, _ = getargspec(param)
#num_args = int(len(the_args))
#arglist[idx].__dict__[missing_fn] = create_function(missing_fn, num_args+1)

                    except ValueError, ve:
                        _, param, _ = re.split("^%d format: a number is required, not (.*)$", te.message)
                        _, idx, _ = re.split('param([0-9]+)', param)
                        idx = int(idx)
                        arglist[idx] = 0
                except:
                    print "WARN: Uncaught Exception!"
                else:   # Successfully invoked fn()
                    break
                finally:
                    pass
            print "Instantiated argument list:", arglist

def unused():
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
    print ">> ...done!" #############################################################################
    print ">> Testing global functions..."
    run(functions)
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
            - works on old-style classes
            - need to know type before calling
            - legit type-checking against a known class
        __class__
            - works on old-style classes
            - no need to know type before calling
            - use for debugging: no idea what class the instance is
        issubclass()
    """
    """
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

if __name__ == "__main__":
    # Import Python module bytecode
    try:
        MODULE_UNDER_TEST = __import__(MODULE_UNDER_TEST)
    except ImportError, ie:
        print >> sys.stderr, "Module cannot be imported"
        sys.exit(0)

#    unused()
    functions = getmembers(MODULE_UNDER_TEST, isfunction)
    run(functions)

    print >> sys.stderr, FAIL + \
        ("*** Total time: %.3f seconds ***" % (time.time() - t0)) + ENDC
    del MODULE_UNDER_TEST   # cleanup
    sys.exit(0)
