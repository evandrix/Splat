#!/usr/bin/env python
# -*- coding: utf-8 -*-

from headers import *

class AttrError(Exception):
    target_object = missing_attr = None
    def __init__(self, target_object, missing_attr):
        self.target_object = target_object
        self.missing_attr  = missing_attr
    def __str__(self):
        return repr(self)
    def __repr__(self):
        return str(self.target_object) + '_' + str(self.missing_attr)

def create_param_obj(value):
    class MyMeta(type):
        __repr__ = lambda c: c.__name__

        def __new__(meta, name, bases, dct):
            """__new__ should be implemented when you want to control the
            creation of a new object (class in our case)"""

    #        print '-----------------------------------'
    #        print "Allocating memory for class", name
    #        print meta
    #        print bases
    #        pprint(dct)
            #print "meta __new__ called"
            return super(MyMeta, meta).__new__(meta, name, bases, dct)
        def __init__(cls, name, bases, dct):
            """
            __init__ will happen when the metaclass is constructed: 
            the class object itself (not the instance of the class)
        
            __init__ should be implemented when you want to control
            the initialization of the new object after it has been created
            """

    #        print '-----------------------------------'
    #        print "Initializing class", name
    #        print cls
    #        print bases
    #        pprint(dct)
            #print "meta __init__ called"
            super(MyMeta, cls).__init__(name, bases, dct)
        def __call__(cls, *args, **kwds):
            """
            __call__ will happen when an instance of the class (NOT metaclass)
            is instantiated. For example, We can add instance methods here and 
            they will be added to the instance of our class and NOT as a class 
            method (aka: a method applied to our instance of object).

            Or, if this metaclass is used as a factory, we can return a whole 
            different classes' instance
            """

    #        print '__call__ of ', str(cls)
    #        print '__call__ *args=', str(args)
            #print "meta __call__ called"
            return type.__call__(cls, *args, **kwds)
    class MyParam(object):
        __metaclass__ = MyMeta

        def __new__(cls, *args):
            """
            Use __new__ when you need to control the creation of a new instance.
            __new__ is the first step of instance creation.
            It's called first, and is responsible for returning a new instance
            of your class.
            Generally used for subclassing an immutable type, like str, int,
            unicode or tuple.
            """
            #print "param __new__ called"
            return super(MyParam, cls).__new__(cls, args)
        def __init__(self, value):
            """
            Use __init__ when you need to control initialization of a
            new instance.
            __init__ doesn't return anything; it's only responsible
            for initializing the instance after it's been created.
            """
            self.value = value + 1
            #print "param __init__ called - %d" % self.value
            self.__class__.__name__ = "MyParam%d" % self.value
        def __getattr__(self, name):
            raise AttrError(self, name)
        def __str__(self):
            return repr(self)
        def __repr__(self):
            return self.__class__.__name__ #+ str(self.value)
    return MyParam(value)

#############################################################################
# Generating unit test suite
def generate_tests(testname, function, arglist, result, *vargs, **kwargs):
    
    # sanity check on number of arguments
    args, varargs, keywords, defaults = getargspec(function)
    assert len(arglist) == len(args)

    stmt = ""
    if isinstance(result, Exception):
        result = result.__class__.__name__

        assert hasattr(function, '__call__')
        function = function.func_name
        
        stmt = "self.assertRaises(%s, %s, *%s)" % (result,function,arglist)

    print ">> UNITTEST: *%s => %s" % (arglist, result)
    print ">> Writing out unit test suite to file...",

    import simplejson
    import pyparsing    # S-Expr
    import pystache

    class ImportObject(object):
        def __init__(self, module):
            self.module = module
    class UnitTestObject(object):
        def __init__(self, function_name, name, params, stmts):
            self.function_name = function_name
            self.name = name
            self.params = None if params is None else (', ' + params)
            self.stmts = '\n'.join(stmts)

    context = {
        'module_name': MODULE_UNDER_TEST,
        'all_imports': None,
        'all_tests': [ UnitTestObject(function, testname, None, [stmt]) ]
    }

    # read template
    template_file = open("test_template.mustache", "r")
    template      = template_file.read()
    template_file.close()

    # write out unit test suite
    fout = open("test_%s.py" % MODULE_UNDER_TEST, "w")
    print >> fout, pystache.render(template, context)
    fout.close()
    del fout
    print ">> done!"
