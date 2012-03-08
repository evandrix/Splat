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
import instrumentor
import bytecode
import tracer
from cStringIO       import StringIO
from common          import *  # AOP
from header          import *  # enable colors
from template_writer import *   # submodule support
from metaclass       import *

MAX_ITERATIONS  = 2**10
def f_noarg(): return                   # Mock parameters
def f_varg(*args, **kwargs): return
PARAM_VALUE_SEQ = [ None, 0, 0.0, '', f_noarg, f_varg ]
class ClassType:    OLD, NEW = range(2)

# add tracing facility to function under test
def add_tracer(function, *vargs, **kwargs):
    cb    = byteplay.Code.from_code(function.func_code)
    total = len([(op,arg) for op,arg in cb.code if op != byteplay.SetLineno])
    tracer.NUM_LINES_EXECUTED = 0
    sys.settrace(tracer.trace_bytecode)
    try:
        function(*vargs, **kwargs)
    except Exception as e:
        if function.aop_single_exec:
            pass
        else:
            raise e
    finally:
        sys.settrace(None)
        print "(Byte)code coverage: %d/%d instruction%s (%.2f%%)" % \
            (tracer.NUM_LINES_EXECUTED,total,
            's' if tracer.NUM_LINES_EXECUTED > 1 else '',
            tracer.NUM_LINES_EXECUTED/float(total)*100)

# Wrap function to catch Exception & print program output
def add_formatter(function, *vargs, **kwargs):
    try:
        sys.stdout = StringIO()  # suppress stdout to string
        return_value = function(*vargs, **kwargs)
    except Exception as e:
        sys.stdout = sys.__stdout__
        if function.aop_newline:    print
        raise e # propagate Exception upwards
    else:
        # no Exception encountered
        func_output = sys.stdout.getvalue()
        sys.stdout = sys.__stdout__
        print '$', func_output,
    finally:
        sys.stdout = Writer(sys.__stdout__) # restore stdout
    return return_value

class Generator(object):
    def __init__(self, target):
        self.target = target
    ########################################################################
    def run(self):
        PYC_NAME     = self.target.__name__
        PYC_FILENAME = os.path.basename(self.target.__file__)

        print "** Instrumenting Python bytecode '%s'" % PYC_FILENAME
        assert os.path.exists(PYC_FILENAME), "'%s' not found" % PYC_FILENAME
        instrumentor.Instrumentor(PYC_NAME).run()
        reload(self.target)
        #####################################################################
        print "** Collecting class definitions with methods & functions"
        program_states = {}
        classes_states = {}
        classes = inspect.getmembers(self.target, inspect.isclass)
        for label, klass in classes:
            # methods within classes
            methods_states = {}
            for item in inspect.getmembers(klass, inspect.ismethod):
                name, method = item
                methods_states[name] = method
            # store class definition into dict()
            if type(klass) is types.TypeType:
                classes_states[label] = (ClassType.NEW, klass, methods_states)
            elif type(klass) is types.ClassType:
                classes_states[label] = (ClassType.OLD, klass, methods_states)
        program_states['classes'] = classes_states
        functions_states = {}
        functions = inspect.getmembers(self.target, inspect.isfunction)
        for name,function in functions:
            tracer.TRACE_INTO.append(name)
            fn_bytecode = bytecode.Bytecode(function.func_code)
            #fn_bytecode.pretty_print(sys.stderr)   # human-readable
            #fn_bytecode.debug_print(sys.stderr)    # programmatic
            functions_states[name] = (function, fn_bytecode)
        program_states['functions'] = functions_states
        #####################################################################
        print "** Testing top-level functions in '%s' **" % PYC_NAME
        all_tests = []
        for name,function in functions:
            test_obj = self.test_function(function)
            all_tests.extend(test_obj)
        tmpl_writer = TemplateWriter(self.target)
        tmpl_writer.run(all_tests)
    ########################################################################
    def test_function(self, fn):
        assert callable(fn)
        #print "\t'%s': %s" % (fn.__name__, inspect.getargspec(fn))
        args, varargs, keywords, defaults = inspect.getargspec(fn)
        tests = []
        #####################################################################
        # Case 1: Nones
        #####################################################################
        fn.aop_newline     = True
        fn.aop_single_exec = True
        function = decorator(add_formatter, decorator(add_tracer, fn))

        print "[test-all-Nones]:\t",
        arglist = [None] * len(args)    # correct number of arguments supplied
        assert len(arglist) == len(args)
        try:
            return_value = function(*arglist)
        except AttributeError as e:
            #print OKGREEN + 'Error' + ':' + ENDC, e
            assert isinstance(e, Exception)
            tests.append(UnitTestObject(
                function.__name__, "all_Nones",
                [ "self.assertRaises(%s, %s, *%s)" % \
                    (e.__class__.__name__, function.__name__, arglist) ]
            ))
        else:
            # function executed succesfully with Nones supplied
            # assert that return value is equal (also if None)
            statements = []
            statements.append("self.assertNotRaises(%s, *%s)" % \
                (function.__name__, arglist))
            if return_value is None:
                statements.append("self.assertIsNone(%s(*%s))" % \
                (function.__name__, arglist))
            else:
                statements.append("self.assertEqual(%s(*%s), %r, %s)" % \
                    (function.__name__, arglist, return_value,
                    'function return value not equal'))
            tests.append(UnitTestObject(
                function.__name__, "all_Nones", statements))

        #####################################################################
        # Case 2: Lazy instantiation
        #####################################################################
        fn.aop_newline     = False
        fn.aop_single_exec = False
        function = decorator(add_formatter, decorator(add_tracer, fn))

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

                # transform arglist for assertion in test case
                stmt = []
                for item in arglist:
                    stmt.append("%s = type('',(object,), {})()" % (item))
                    for key in item.__dict__:
                        value = item.__dict__[key]
                        if not key.startswith("__") and key != 'index':
                            if callable(value):
                                stmt.append("%s.%s = types.MethodType(%s, %s, %s.__class__)" % (item,key,value.func_name,item,item))
                            else:
                                stmt.append("%s.%s = %s" % (item,key,"''" if value == '' else value))
                stmt.append("self.assertRaises(%s, %s, *%s)" % \
                    (e.__class__.__name__, function.__name__, arglist))
                tests.append(UnitTestObject(function.__name__, str(iteration_no), stmt))
                # generate test for this case
                #print >> sys.__stderr__, 1, "#"+str(iteration_no), ':', e, map(todict, arglist)

                if len(err_param) == 1: # error message parsed correctly
                    self.handle_TypeError_require_number(err_param, arglist, obj, param_instantiated, param_states)
                else:
                    self.handle_TypeError(obj, attr)
            except MetaAttributeError as e:
                if not self.handle_MetaAttrError(e, param_states, param_instantiated, arglist, function, tests, iteration_no):
                    return tests
            except Exception as e:
                print >> sys.stderr, "Unhandled exception:", e
            else:
                break   # all done now
            finally:
                iteration_no += 1

        # transform arglist for assertion in test case
        is_primitive = lambda var: isinstance(var, (int, basestring, float, long, bool, tuple, list, dict))
        stmt = []
        for item in arglist:
            if not is_primitive(item) and hasattr(item, '__class__') \
                and isinstance(item.__class__, MetaParam) \
                and hasattr(item, '__dict__'):
                stmt.append("%s = type('',(object,), {})()" % (item))
                for key in item.__dict__:
                    value = item.__dict__[key]
                    if not key.startswith("__") and key != 'index':
                        if callable(value):
                            stmt.append("%s.%s = types.MethodType(%s, %s, %s.__class__)" % (item,key,value.func_name,item,item))
                        else:
                            stmt.append("%s.%s = %s" % (item,key,"''" if value == '' else value))

        stmt.append("self.assertNotRaises(%s, *%s)" % \
            (function.__name__, arglist))
        tests.append(UnitTestObject(function.__name__, str(iteration_no), stmt))
        # generate test for this case
        #print >> sys.__stderr__, 0, map(todict, arglist)
        # summary statistics
        print ">> Discovered parameters in %d/%d iteration%s (%.2f%%)\n" % (iteration_no, MAX_ITERATIONS, 's' if iteration_no > 1 else '', iteration_no/float(MAX_ITERATIONS)*100)
        return tests

    def handle_MetaAttrError(self, e, param_states, param_instantiated, arglist, function, tests, iteration_no):
        # attr lookup on param object certainly fails => trap
        lookup_key, obj, attr = str(e), e.target_object, e.missing_attr
        next_param_index = param_states.setdefault(lookup_key, 0)

        if next_param_index >= len(PARAM_VALUE_SEQ):
            print "No more possible arguments to try for %s" % lookup_key
            return False
        else:
            if 'last_instantiated' not in param_states \
                or obj != param_states['last_instantiated'][0]:
                stmt = []
                for item in arglist:
                    stmt.append("%s = type('',(object,), {})()" % (item))
                    for key in item.__dict__:
                        value = item.__dict__[key]
                        if not key.startswith("__") and key != 'index':
                            if callable(value):
                                stmt.append("%s.%s = types.MethodType(%s, %s, %s.__class__)" % (item,key,value.func_name,item,item))
                            else:
                                stmt.append("%s.%s = %s" % (item,key,"''" if value == '' else value))
                stmt.append("self.assertRaises(%s, %s, *%s)" % \
                    (e.parent_exception.__name__, function.__name__, arglist))
                tests.append(UnitTestObject(function.__name__, str(iteration_no), stmt))
            # generate test for this case
            #print >> sys.__stderr__, 2, "#"+str(iteration_no), ':', e, map(todict, arglist)

            next_param = PARAM_VALUE_SEQ[next_param_index]
            param_states[lookup_key] += 1
            param_states['last_instantiated'] = (obj, attr, next_param_index)
            setattr(obj, attr, next_param)
            param_instantiated.add(obj)
            return True

    def handle_TypeError_require_number(self, err_param, arglist, obj, param_instantiated, param_states):
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
            numbers = []
            next_param_index = None
            for i,n in enumerate(PARAM_VALUE_SEQ):
                if isinstance(n,int):
                    numbers.append((i,n))
                    if next_param_index is not None:
                        next_param_index = i+1
            index, number = numbers[random.randint(0,len(numbers)-1)]
            arglist[err_param-1] = number

            # 2. error should not occur again
            #    => assume instantiated correctly
            param_instantiated.add(obj_err_param)

            # 3. update 'last instantiated' state
            param_states[sz_err_param] = index
            param_states['last_instantiated'] = \
                (obj_err_param, None, next_param_index)

    def handle_TypeError(self, obj, attr):
        # diagnostics #
        # traceback info
        exception_type, exception_value, traceback = sys.exc_info()
        code = py.code.Traceback(traceback)[-1]
        fn_frame = code.frame
        print >> StringIO(), "(name, frame, code, lineno): (%s,%s,%s,%s)" % \
            (code.name, fn_frame, fn_frame.code, code.lineno+1)
        # function bytecode
        if callable(obj.__dict__[attr]):
            code = Code.from_code(obj.__dict__[attr].func_code)
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

