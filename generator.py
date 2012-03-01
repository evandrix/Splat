#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import re
import dis
import types
import py
import inspect
import pprint
import byteplay
import random
import decorator
from cStringIO import StringIO
from common   import *  # AOP
from header   import *  # enable colors
from template_writer import *   # submodule support
from metaclass import *

MAX_ITERATIONS = 2**10

# Mock parameters
def f_noarg():
    return
def f_varg(*args, **kwargs):
    return
param_value_seq = [ None, 0, 0.0, '', f_noarg, f_varg ]

# Wrap function to catch Exception & print program output
def aspect_fmt_output(function, *vargs, **kwargs):
    sys.stdout = StringIO()  # suppress stdout to string
    try:
        return_value = function(*vargs, **kwargs)
    except Exception as e:
        raise e # propagate Exception upwards
    else:
        # no Exception encountered
        func_output = sys.stdout.getvalue()
        sys.stdout = sys.__stdout__
        print '$', func_output,
    sys.stdout = Writer(sys.__stdout__) # restore stdout
    return return_value
#############################################################################
class Generator(object):
    def __init__(self, target):
        self.target = target

    def run(self):
        print "** Testing top-level functions in '%s' **" \
            % self.target.__name__
        functions = inspect.getmembers(self.target, inspect.isfunction)
        all_tests = []
        for name,function in functions:
            all_tests.extend(self.test_function(function))
        tmpl_writer = TemplateWriter(self.target)
        tmpl_writer.run(all_tests)

    def test_function(self, function):
        assert hasattr(function, '__call__')

        print "\t'%s': %s" % \
            (function.__name__, inspect.getargspec(function))
        args, varargs, keywords, defaults = inspect.getargspec(function)
        tests = []
        function = decorator(aspect_fmt_output, function)
        #####################################################################
        # Case 1: Nones
        #####################################################################
        print "[test-all-Nones]:\t",
        arglist = [None] * len(args)    # correct number of arguments supplied
        assert len(arglist) == len(args)
        try:
            return_value = function(*arglist)
        except AttributeError as e:
            #print OKGREEN + 'Error' + ':' + ENDC, e
            assert isinstance(e, Exception)
            tests.append(UnitTestObject(
                function.__name__, "all_Nones", None,
                [ "self.assertRaises(%s, %s, *%s)" % \
                    (e.__class__.__name__, function.__name__, arglist) ]
            ))
        else:
            # function executed succesfully with Nones supplied
            # assert that return value is equal (also if None)
            statements = []
            statements.append("self.assertNotRaised(%s, *%s)" % \
                (function.__name__, arglist))
            if return_value is None:
                statements.append("self.assertIsNone(%s(*%s))" % (function.__name__, arglist))
            else:
                statements.append("self.assertEqual(%s(*%s), %r, 'function return value not equal')" % (function.__name__, arglist, return_value))
            tests.append(UnitTestObject(
                function.__name__, "all_Nones", None, statements))

        #####################################################################
        # Case 2: Lazy instantiation
        #####################################################################
        print "[test-all-params]:\t",
        param_states = {}           # dict() of param state info
        # tracks last instantiated parameter - (obj, attr, next_param_index)
        param_instantiated = set()
        arglist = [create_metaparam(index) for index,_ in enumerate(args)]
        iteration_no = 0
        while iteration_no < MAX_ITERATIONS:
            try:
                return_value = function(*arglist)
            except TypeError as e:
                assert 'last_instantiated' in param_states
                obj, attr, index = param_states['last_instantiated']
                err_param = re.split('^%d format: a number is required, not Param([0-9]+)$', e.message)[1:-1]
                if len(err_param) == 1: # error message parsed correctly
                    # extract var from msg
                    err_param     = int(err_param[0])
                    sz_err_param  = 'Param%d' % err_param
                    obj_err_param = arglist[err_param-1] # 1 to 0-based indexing
                    # check whether error is caused by last instantiated object
                    if obj != obj_err_param:
                        # 'last instantiated' object instantiated successfully
                        # => add to list of already instantiated parameters
                        param_instantiated.add(obj)

                        # fix error
                        # 1. instantiate this object with a number
                        numbers = [(i,n) for i,n in enumerate(param_value_seq) \
                                    if isinstance(n,int)]
                        index, number = numbers[random.randint(0,len(numbers)-1)]
                        arglist[err_param-1] = number

                        # 2. error should not occur again
                        #    => assume instantiated correctly
                        param_instantiated.add(obj_err_param)

                        # 3. update 'last instantiated' state
                        param_states[sz_err_param] = index
                        for i,n in enumerate(param_value_seq):
                            if isinstance(n,int):
                                next_param_index = i+1
                                break
                        param_states['last_instantiated'] = \
                            (obj_err_param, None, next_param_index)
                else:
                    self.handle_TypeError(obj, attr)
            except MetaAttributeError as e:
                if not self.handle_MetaAttrError(e, param_states, param_instantiated):
                    return tests
            except Exception as e:
                print "Unhandled exception:", e
            else:
                break   # all done now
            finally:
                iteration_no += 1
        # summary statistic
        print ">> Discovered parameters in %d/%d iteration%s (%.2f%%)\n" % (iteration_no, MAX_ITERATIONS, 's' if iteration_no > 1 else '', iteration_no/float(MAX_ITERATIONS)*100)
        return tests

    def handle_MetaAttrError(self, e, param_states, param_instantiated):
        lookup_key, obj, attr = str(e), e.target_object, e.missing_attr
        next_param_index = param_states.setdefault(lookup_key, 0)
        if next_param_index >= len(param_value_seq):
            print "No more possible arguments to try for %s" % lookup_key
            return False
        else:
            next_param = param_value_seq[next_param_index]
            param_states[lookup_key] += 1
            param_states['last_instantiated'] = (obj, attr, next_param_index)
            setattr(obj, attr, next_param)
            param_instantiated.add(obj)
            return True

    def get_traceback_info(self):
        exception_type, exception_value, tb = sys.exc_info()
        code = py.code.Traceback(tb)[-1]
        fn_name = code.name
        fn_frame = code.frame
        fn_code = fn_frame.code
        fn_lineno = code.lineno + 1
        #print code.getfirstlinesource(), code.locals, code.relline

    def get_bytecode_obj(self, obj, attr):
        # only applies to callables
        if not hasattr(obj.__dict__[attr], '__call__'):
            return
        try:
            code = Code.from_code(obj.__dict__[attr].func_code)
        except:
            return

    def handle_TypeError(self, obj, attr):
        self.get_traceback_info()
        self.get_bytecode_obj(obj, attr)
        del obj.__dict__[attr]  # retry with next argument in list

#############################################################################
@aspect_import_mut
@aspect_timer
def run(*vargs, **kwargs):
    generator = Generator(kwargs['module'])
    generator.run()

if __name__ == "__main__":
    run()
    sys.exit(0)
