#!/usr/bin/env python
# -*- coding: utf-8 -*-

import __builtin__
import os
import sys
import time
import re
import dis
import types
import py
import inspect
import byteplay
import random
import tracer
import trace
import opcode as op
import uuid
import tracer
import gc
import multiprocessing
import logging
import numbers
import jsonpickle
import copy
import settings
import warnings
from decorator       import decorator
from cStringIO       import StringIO
from pprint          import pprint
from common          import *
from constants       import *
from collections     import defaultdict
from metaclass       import *
from template_writer import *

def add_tracer(function, *vargs, **kwargs):
    """ add tracing facility to function under test """
    cb    = byteplay.Code.from_code(function.func_code)
    total = len([(op,arg) for op,arg in cb.code if op != byteplay.SetLineno])
    tracer.TRACE_INTO = [ function.func_name ]

    tracer.NUM_LINES_EXECUTED = 0
    tracer.CODE_FRAGMENT = []
    sys.settrace(tracer.trace_bytecode)
    try:
        function(*vargs, **kwargs)
    except Exception as e:
        raise e
    finally:
        sys.settrace(None)
        print ">> Bytecode coverage: %d/%d instruction%s (%.2f%%)" % \
            (tracer.NUM_LINES_EXECUTED,total,
            's' if tracer.NUM_LINES_EXECUTED > 1 else '',
            tracer.NUM_LINES_EXECUTED/float(total)*100)

def metaparam_to_stmts(item):
    stmts = []
    if not is_primitive(item) and hasattr(item, '__class__') \
        and isinstance(item.__class__, MetaParam) \
        and hasattr(item, '__dict__'):
        stmts.append("%s = type('',(object,), {})()" % (item))
        for key in item.__dict__:
            value = item.__dict__[key]
            if not key.startswith("__") and key not in ['index', 'attr', 'dct']:
                if callable(value):
                    stmts.append( \
                        "%s.%s = types.MethodType(%s, %s, %s.__class__)" % \
                        (item,key,value.func_name,item,item))
                elif isinstance(value.__class__, MetaParam):
                    stmts.extend(metaparam_to_stmts(value))
                    stmts.append("%s.%s = %s" % (item,key,value))
                else:
                    stmts.append("%s.%s = %s" % \
                        (item,key,"''" if value == '' else value))
    return stmts

def arglist_to_stmts(arglist, fn, val_or_exc=None):
    stmts = []

    for item in arglist:
        stmts.extend(metaparam_to_stmts(item))

    if isinstance(val_or_exc, Exception):
        if hasattr(val_or_exc, 'parent_exception'):
            stmts.append("self.assertRaises(%s, %s, *%s)" % \
                (val_or_exc.parent_exception.__name__, fn.__name__, arglist))
        else:
            exception_module = inspect.getmodule(val_or_exc.__class__)
            if hasattr(exception_module, '__file__'):
                # non-builtin Exception occurred
                exception_module_dir = os.path.dirname(exception_module.__file__)
                exception_module_filename = os.path.basename(exception_module.__file__)
                exception_module_name, _  = os.path.splitext(exception_module_filename)
                stmts.extend([
                    "exception_module = imp.load_compiled('%s', '%s')" % \
                        (exception_module_name, exception_module.__file__),
                    "self.assertRaisesException(exception_module.%s,self.module.%s,*%s)" % \
                        (val_or_exc.__class__.__name__, fn.__name__, arglist),
                    ])
            else:
                stmts.append("self.assertRaises(%s, self.module.%s, *%s)" % \
                    (val_or_exc.__class__.__name__, fn.__name__, arglist))
    else:
        stmts.append("self.assertNotRaises(self.module.%s, *%s)" % \
            (fn.__name__, arglist))

        if val_or_exc is None:
            stmts.append("self.assertIsNone(self.module.%s(*%s))" % \
                (fn.__name__, arglist))
        else:
            if is_primitive(val_or_exc):
                stmts.append("self.assertEqual(self.module.%s(*%s), %r, 'incorrect function return value encountered')" % \
                    (fn.__name__, arglist, val_or_exc))
            else:
                # object
                # check class name
                stmts.append("self.assertEqualClassName(self.module.%s(*%s), '%s', 'incorrect class name for return value encountered')" % \
                    (fn.__name__, arglist, val_or_exc.__class__.__name__))
                if not val_or_exc.__class__.__name__ in ['generator']:
                    # serialisable
                    ret_val_dict = jsonpickle.encode(val_or_exc, unpicklable=False)
                    stmts.append(
                        "self.assertEqualAttrs(self.module.%s(*%s), %r, 'incorrect attributes for return value encountered')" % \
                        (fn.__name__, arglist, ret_val_dict))
    return stmts

#logger = multiprocessing.log_to_stderr()
#logger.setLevel(logging.INFO)
def update_frame_param(current, event):
    """ mutate & propagate trace_params down the stack frames """
    # can only store stack frame ids across processes due to PicklingError of frame object
    params = [
        ("recursion_depth", lambda parent_val: parent_val+1),
        (   "stack_frames", lambda parent_val: parent_val+[id(current)]),
    ]
    parent = current.f_back
    if event == 'call':
        for p,fn in params:
            parent.f_locals['TRACE_DICT'].update({p: fn(parent.f_locals['TRACE_DICT'][p])})
        current.f_locals['TRACE_DICT'] = parent.f_locals['TRACE_DICT']
    elif event == 'return':
        parent.f_locals['TRACE_DICT'] = current.f_locals['TRACE_DICT']
    return current

def current_func():
    """ credits @ http://goo.gl/Um0Ig
    The stack frame tells us what code object we're in. If we can find a function
    object that refers to that code object in its func_code attribute, we have
    found the function.

    Fortunately, we can ask the garbage collector which objects hold a reference
    to our code object, and sift through those, rather than having to traverse
    every active object in the Python world. There are typically only a handful of
    references to a code object.

    Note: functions can share code objects (in the case where you return a
    function from a function, ie. a closure). When there's more than one function
    using a given code object, we can't tell which function it is, so we return
    None.
    """
    frame = inspect.currentframe(1)
    code  = frame.f_code
    globs = frame.f_globals
    functype = type(lambda: None)
    funcs = []
    for func in gc.get_referrers(code):
        if type(func) is functype:
            if getattr(func, "func_code", None) is code:
                if getattr(func, "func_globals", None) is globs:
                    funcs.append(func)
                    if len(funcs) > 1:
                        return None
    return funcs[0] if funcs else None

def trace_recursive(frame, event, arg):
    # frame
    co        = frame.f_code
    f_locals  = frame.f_locals
    lineno    = frame.f_lineno
    offset    = frame.f_lasti
    caller    = frame.f_back
    # code object
    filename  = co.co_filename
    name      = co.co_name
    varnames  = co.co_varnames[:co.co_argcount]
    if event == 'line':
        cb = byteplay.Code.from_code(co)
        code_fragment = []
        take = False
        for opcode, arg in cb.code:
            if opcode == byteplay.SetLineno:
                take = arg == lineno
            elif take:
                code_fragment.append((opcode, arg))
        if len(code_fragment) == 1:
            code_fragment = code_fragment[0]
        #print >> sys.stderr, "%s:%s %s" % (name, lineno, code_fragment)
        #print '0x%x'%id(frame),lineno,offset,code_fragment
    elif event == 'call':
        if name == 'write': return
        update_frame_param(frame, event)
        if name not in frame.f_locals['TRACE_DICT']['function']: return
        if frame.f_locals['TRACE_DICT']['recursion_depth'] > sys.getrecursionlimit():
            #raise RuntimeError("Maximum recursion depth reached")
            pass
        #print >> sys.stderr, '[call]: 0x%x=>0x%x, %s,%s\n%s\n%s' % \
        #    (id(frame.f_back), id(frame), caller.f_lineno,
        #    caller.f_lasti, frame.f_locals, arg)
        # potential for branching off different trace functions (!)
        return current_func()
    elif event == 'return':
        update_frame_param(frame, event)
        #print >> sys.stderr, '[return]: 0x%x=>0x%x, %s,%s\n%s\n%s,%s' % \
        #    (id(frame), id(frame.f_back), frame.f_lineno,
        #    frame.f_lasti, frame.f_locals, arg, varnames)

        # factorial / hanoi
        param = None
        for f_param in [ 'n', 'height' ]:
            if f_param in frame.f_locals:
                param = frame.f_locals[f_param]
                break
        # factorial
        if isinstance(arg, numbers.Number):
            if isinstance(arg, int) and \
                long(arg)>sys.maxint or long(arg)<settings.SYS_MININT:
                arg = long(arg)
            # generate unit test object + memoize!
            if id(param) not in frame.f_locals['TRACE_DICT']["unit_test_objs"]:
                frame.f_locals['TRACE_DICT']["unit_test_objs"][id(param)] \
                    = ["self.assertEqual(%r, self.module.%s(%s))" % (arg,name,param)]
        # hanoi
        if 'self' in frame.f_locals:
            # construct object for test initialisation
            obj = frame.f_locals['self']
            obj_params,_,_,_ = inspect.getargspec(obj.__init__)
            paramlist = [obj.__dict__[param] \
                if param in obj.__dict__ else None \
                for param in obj_params[1:]]
            # construct assertion on function return value
            args,_,_,_       = inspect.getargspec(getattr(obj, name))
            arglist = [ frame.f_locals[f_arg] for f_arg in args[1:] ]
            # generate unit test object + memoize!
            if id(arglist) not in frame.f_locals['TRACE_DICT']["unit_test_objs"]:
                frame.f_locals['TRACE_DICT']["unit_test_objs"][id(arglist)] = ["obj = %s(%s)" % (obj.__class__.__name__,','.join(map(str,paramlist))), "self.assertEqual(%r, obj.%s(%s))" % (arg,name,','.join(map(str,arglist)))]
    elif event == 'exception':
        exc_type, exc_value, exc_traceback = arg
        print >> sys.stderr, "Exception event: %s" % arg
    else:
        print >> sys.stderr, "Unhandled event: '%s'" % event
    return

class TimeoutException(Exception): pass
class RunnableProcessing(multiprocessing.Process):
    def __init__(self, func, *args, **kwargs):
        self.queue = multiprocessing.Queue(maxsize=1)
        args = (func,) + args
        multiprocessing.Process.__init__(self, target=self.run_func, args=args, kwargs=kwargs)
    def run_func(self, func, *args, **kwargs):
        sys._getframe().f_locals['TRACE_DICT'] = kwargs['TRACE_DICT']
        del kwargs['TRACE_DICT']
        sys.settrace(trace_recursive)
        try:
            result = func(*args, **kwargs)
            sys.settrace(None)
            self.queue.put((True, (result, sys._getframe().f_locals['TRACE_DICT'])))
        except Exception as e:
            self.queue.put((False, e))
    def done(self):
        return self.queue.full()
    def result(self):
        return self.queue.get()

def run_recursive(function, *args, **kwargs):
    now = time.time()
    proc = RunnableProcessing(function, *args, **kwargs)
    proc.start()
    proc.join(settings.RECURSION_TIMEOUT)
    if proc.is_alive():
        proc.terminate()    # always force_kill process
        runtime = int(time.time() - now)
        raise TimeoutException('timed out after {0} seconds'.format(runtime))
    assert proc.done()
    success, result = proc.result()
    if success:
        return result
    else:
        raise result

def test_recursive(GLOBALS, function, tests):
    trace_dict = {
                   "function": function.func_name,
            "recursion_depth": 0,
               "stack_frames": [],
             "unit_test_objs": {},
    }
    lasti = 0
    for i in xrange(sys.maxint):
        try:
            result, trace_dict = run_recursive(function, i, TRACE_DICT=trace_dict)
        except Exception as e:
            print >> sys.stderr, e.__class__.__name__+':', e.message
            break
        else:
            lasti += 1
    print
    print "Last successful iteration = %d" % lasti
    for k,v in trace_dict.items():
        if k in ["stack_frames", "unit_test_objs"]:
            v = len(v)#'' => '.join(map(lambda f:'0x%x'%id(f), v))
        print k+':',v

    # transform into UnitTestObjects to write out unit test suite
    for key,value in trace_dict["unit_test_objs"].iteritems():
        tests.append(UnitTestObject(function.__name__,key,value))

def test_random(GLOBALS, function, arglist, constants, tests):
    # assume no Exceptions from now on
    for i, item in enumerate(arglist):
        if not is_primitive(item) and hasattr(item, '__class__') \
            and isinstance(item.__class__, MetaParam) \
            and hasattr(item, '__dict__'):
            for key in item.__dict__:
                value = item.__dict__[key]
                if not key.startswith("__") and key not in ['index', 'attr', 'dct']:
                    if is_primitive(value):
                        for v in constants:
                            if type(v) == type(value):
                                setattr(arglist[i], key, v)
                                return_value = function(*arglist)
                                tests.append(UnitTestObject(function.__name__,
                                    str(uuid.uuid4()).replace('-',''),
                                    arglist_to_stmts(arglist, function, return_value)))
                        if isinstance(value, int):
                            for j in xrange(7):
                                v = random.randint(SYS_MININT,sys.maxint)
                                setattr(arglist[i], key, v)
                                return_value = function(*arglist)
                                tests.append(UnitTestObject(function.__name__,
                                    str(uuid.uuid4()).replace('-',''),
                                    arglist_to_stmts(arglist, function, return_value)))
        elif is_primitive(item):
            for v in constants:
                if type(v) == type(item):
                    arglist[i] = v
                    return_value = function(*arglist)
                    tests.append(UnitTestObject(function.__name__,
                        str(uuid.uuid4()).replace('-',''),
                        arglist_to_stmts(arglist, function, return_value)))
            if isinstance(item, int):
                for j in xrange(7):
                    arglist[i] = random.randint(SYS_MININT,sys.maxint)
                    return_value = function(*arglist)
                    tests.append(UnitTestObject(function.__name__,
                        str(uuid.uuid4()).replace('-',''),
                        arglist_to_stmts(arglist, function, return_value)))

def test_function(GLOBALS, function):
    assert callable(function)
    args, varargs, keywords, defaults = inspect.getargspec(function)
    module_name = inspect.getmodule(function).__name__
    module_path = inspect.getmodule(function).__file__
    pkg_path = os.path.abspath(GLOBALS['pkg_path'])
    dirname, filename = os.path.split(module_path)
    module_name, ext  = os.path.splitext(filename)
    submodule_key = dirname[len(pkg_path)+1:]+'/'+module_name
    fn_cfg_nodes = GLOBALS['graph_fn_cfg'][function.func_name]['nodes']
    fn_cfg_edges = GLOBALS['graph_fn_cfg'][function.func_name]['edges']
    fn_cfg_usages, fn_cfg_jmps, fn_cfg_lbls = defaultdict(list), [], []
    for node_id, value in fn_cfg_nodes.iteritems():
        (opcode, arg), node = value
        if node.get_fillcolor() == graph_node_colors['PINK']:
            next_node = fn_cfg_nodes[node_id+1]
            if next_node:
                (next_node_opcode, next_node_arg), _ = next_node
                if next_node_opcode == byteplay.LOAD_ATTR:
                    fn_cfg_usages[arg].append(next_node_arg)
        elif node.get_fillcolor() == graph_node_colors['GREEN'] \
            or node.get_fillcolor() == graph_node_colors['ORANGE']:
            fn_cfg_jmps.append((node_id, (opcode, arg), node))
        elif node.get_fillcolor() == graph_node_colors['LIGHT_BLUE']:
            fn_cfg_lbls.append((node_id, (opcode, arg), node))
    fn_cls = [b.get_name().replace(u"\u200B",'') \
        for a,b in GLOBALS['graph_fn_cls']['edges'] \
        if a.get_name() == function.func_name]
    module = GLOBALS['modules'][submodule_key]
    pyc    = GLOBALS['pyc_info'][submodule_key]
    constants = [ c for c in function.func_code.co_consts if c ]
    dependent_fns = []
    for a,b in GLOBALS['graph_fn_fn']['edges']:
        if a.get_name() == function.func_name:
            for f in GLOBALS['dependent_fn'][function.func_name]:
                if f.name == b.get_name():
                    dependent_fns.append(f)
    co = byteplay.Code.from_code(function.func_code)
    used_args = set([arg for opcode,arg in co.code \
        if opcode in reserved_loads and isinstance(arg, basestring) \
        and arg in inspect.getargspec(function).args])

    ### ACTUAL TESTING WORK ###
    tests = []
    #########################################################################
    # 1. all Nones
    stmts = []
    arglist = [None] * len(args)
    assert len(arglist) == len(args)
#    print "[test-all-None]:",
    try:
        sys.stdout = StringIO()
        return_value = function(*arglist)
    except Exception as e:
        sys.stdout = sys.__stdout__
        stmts = arglist_to_stmts(arglist, function, e)
    else:
        sys.stdout = sys.__stdout__
        stmts = arglist_to_stmts(arglist, function, return_value)
    finally:
        tests.append(UnitTestObject(function.__name__, "all_None", stmts))
#    print '\t...done!'
    #########################################################################
    # 2. all None, with structure information derived from bytecode
    stmts = []
    # first enrich arglist
    for pos,arg in enumerate(args):
        if arg in used_args:
            if arg in fn_cfg_usages:
                arglist[pos] = {key:None for key in fn_cfg_usages[arg] if not key.startswith("__")}
    # default arguments
    if defaults:
        assert len(arglist) >= len(defaults)
        arglist = arglist[:-len(defaults)] + list(defaults)
    ###
#    print "[test-all-attrs-None-with-defaults]:",
    try:
        sys.stdout = StringIO()
        return_value = function(*arglist)
    except Exception as e:
        sys.stdout = sys.__stdout__
        stmts = arglist_to_stmts(arglist, function, e)
    else:
        sys.stdout = sys.__stdout__
        stmts = arglist_to_stmts(arglist, function, return_value)
    finally:
        tests.append(UnitTestObject(function.__name__, "all_attr_None_wdef", stmts))
    #########################################################################
    # 3. all MetaParam, with structure information derived from bytecode
    stmts = []
    # first enrich arglist
    for pos,arg in enumerate(args):
        if arg in used_args:
            if arg in fn_cfg_usages:
                obj_dct = {key:create_metaparam(pos,key) for key in fn_cfg_usages[arg]}
                arglist[pos] = create_metaparam(pos, None, obj_dct)
    # default arguments
    if defaults:
        assert len(arglist) >= len(defaults)
        arglist = arglist[:-len(defaults)] + list(defaults)
    ###
#    print "[test-all-attrs-None-with-defaults]:",
    try:
        sys.stdout = StringIO()
        return_value = function(*arglist)
    except Exception as e:
        sys.stdout = sys.__stdout__
        stmts = arglist_to_stmts(arglist, function, e)
    else:
        sys.stdout = sys.__stdout__
        stmts = arglist_to_stmts(arglist, function, return_value)
    finally:
        tests.append(UnitTestObject(function.__name__, "all_attr_MetaParam_wdef", stmts))
#    print '\t...done!'
    #########################################################################
    # 4. lazy instantiation
    stmts = []
    # first enrich arglist
    for pos,arg in enumerate(arglist):
        if not arg:
            arglist[pos] = create_metaparam(pos)
    print "[test-all-params-with-defaults]:",
    param_state_info, num_iter, MAX_ITERATIONS, success = {}, 0, 20, False
    #######
    while num_iter < MAX_ITERATIONS:
        print 'Argument list:', arglist, param_state_info
        try:
            return_value = function(*arglist)
        except TypeError as e:
            print "TypeError:", e
            tests.append(UnitTestObject(function.__name__,
                str(uuid.uuid4()).replace('-',''),
                arglist_to_stmts(arglist, function, e)))
            def process_0(msg):
                if msg:
                    print "process_0()"
                    param_pos = msg
                    return True
                return False
            def process_1(msg):
                if msg:
                    print "process_1()"
                    arg1, arg2 = msg
                    if arg1.startswith('Param'):
                        arg1 = int(arg1[len('Param'):])
                    if arg2.startswith('Param'):
                        arg2 = int(arg2[len('Param'):])
                    return True
                return False
            def process_2(msg):
                if msg:
                    print "process_2()"
                    op, arg1, arg2 = msg
                    # No 'type' and 'type'
                    assert(not (not arg1.startswith('Param') \
                        and not arg2.startswith('Param')))

                    if arg1.startswith('Param'):
                        param, attr = arg1.partition('_')[::2]
                        arg1 = {
                            'param': param,
                            'attr': None if attr == '' else attr,
                            'param_pos': int(param[len('Param'):])-1,
                            'type': 'param',
                        }
                    if arg2.startswith('Param'):
                        param, attr = arg2.partition('_')[::2]
                        arg2 = {
                            'param': param,
                            'attr': None if attr == '' else attr,
                            'param_pos': int(param[len('Param'):])-1,
                            'type': 'param',
                        }

                    if isinstance(arg1, dict) and isinstance(arg2, dict):
                        if op in op_arithmetic:
                            if arg1['attr']:
                                setattr(arglist[arg1['param_pos']], arg1['attr'], 0)
                                param_state_info['last_instantiated_attr'] = arg1['attr']
                            else:
                                arglist[arg1['param_pos']] = 0
                            param_state_info['last_instantiated'] = arg1['param_pos']
                    else:
                        the_param, the_type = None, None
                        def sz_to_type(typename):
                            # assuming primitive
                            if typename == 'str':
                                return basestring
                            for p_type in PRIMITIVE_TYPES:
                                if p_type.__name__ == typename:
                                    return p_type
                            return None
                        if isinstance(arg1, dict):
                            the_param = arg1
                            the_type  = sz_to_type(arg2)
                        elif isinstance(arg2, dict):
                            the_param = arg2
                            the_type  = sz_to_type(arg1)

                        for i,n in enumerate(PARAM_VALUE_SEQ):
                            if isinstance(n, the_type):
                                if the_param['attr']:
                                    setattr(arglist[the_param['param_pos']], the_param['attr'], n)
                                    param_state_info['last_instantiated_attr'] = the_param['attr']
                                else:
                                    arglist[the_param['param_pos']] = n
                                param_state_info['last_instantiated'] = the_param['param_pos']
                                break
                    return True
                return False
            def process_3(msg):
                return False
            def process_4(msg):
                return False
            def process_5(msg):
                return False
            def process_6(msg):
                return False
            def process_7(msg):
                return False
            def process_8(msg):
                return False
            def process_9(msg):
                return False
            err_msgs = {
                '^%d format: a number is required, not Param([0-9]+)$': process_0,
                "^unsupported operand type\(s\) for \*\* or pow\(\): '(.*)' and '(.*)'$": process_1,
                "^unsupported operand type\(s\) for (.*): '(.*)' and '(.*)'$": process_2,
                "^'Param([0-9]+)' object has no attribute '(.*)'$": process_3,
                "^must be string or read-only buffer, not Param([0-9]+)$": process_4,
                "^range() integer end argument expected, got Param([0-9]+).$": process_5,
                "^'Param([0-9]+)' object does not support indexing$": process_6,
                "^'Param([0-9]+)' object is not iterable$": process_7,
                "^can't multiply sequence by non-int of type 'Param([0-9]+)'$": process_8,
                "^object of type 'Param([0-9]+)' has no len()$": process_9,
            }
            handled_err_msg = False
            for re_msg, re_fn in err_msgs.iteritems():
                if re_fn(re.split(re_msg, e.message)[1:-1]):
                    # produce test case
                    handled_err_msg = True
                    break
            if not handled_err_msg:
                print "iteration#%d: TypeError -" % num_iter, e
        except MetaAttributeError as e:
            print "iteration#%d: MetaAttributeError -" % num_iter, e
            # produce test case
        except Exception as e:
            if hasattr(e, '__module__'):
                print "\riteration#%d: Unhandled custom Exception:"%num_iter,e.__class__
                tests.append(UnitTestObject(function.__name__,
                    str(uuid.uuid4()).replace('-',''),
                    arglist_to_stmts(arglist, function, e)))
                print arglist_to_stmts(arglist, function, e)
            else:
                print "\riteration#%d: Unhandled builtin Exception:"%num_iter,e.message
                tests.append(UnitTestObject(function.__name__,
                    str(uuid.uuid4()).replace('-',''),
                    arglist_to_stmts(arglist, function, e)))
        else:
            print '...done!', arglist
            print ">> Discovered parameters in %d/%d iteration%s (%.2f%%)" % \
                (num_iter, MAX_ITERATIONS, 's' if num_iter > 1 else '', \
                 num_iter/float(MAX_ITERATIONS)*100)
            success = True
            old_function = function
            function = decorator.decorator(add_tracer, function)
            function(*arglist)
            function = old_function
            tests.append(UnitTestObject(function.__name__,
                str(uuid.uuid4()).replace('-',''),
                arglist_to_stmts(arglist, function, return_value)))

            if function in GLOBALS['function_test_order']['recursive']:
                test_recursive(GLOBALS, function, tests)
            else:
                test_random(GLOBALS, function, arglist, constants, tests)
            break   # all done now, no Exceptions raised
        num_iter += 1
    #######
    GLOBALS['unittest_cache'][function.func_name] \
        = {'module': submodule_key, 'testcases': tests}

    if False:
        import pydot
        graph_nodes = GLOBALS['graph_fn_cfg'][function.func_name]['nodes']
        graph_edges = GLOBALS['graph_fn_cfg'][function.func_name]['edges']
        trace_nodes = tracer.CODE_FRAGMENT
        node_to_index = {}
        for node_index in graph_nodes:
            bytecode, node = graph_nodes[node_index]
            node_to_index[node] = node_index
        adj_list = defaultdict(list)
        for node_index in graph_nodes:
            bytecode, node = graph_nodes[node_index]
            if '...' in node.get_name(): continue
            for start,end in graph_edges:
                if start == node:
                    adj_list[node_index].append(end)
        current_node, current_index = None, -1
        for i, t_bc in enumerate(trace_nodes):
            for node_index in graph_nodes:
                bc, node = graph_nodes[node_index]
                if t_bc == bc:
                    current_node = node
                    current_index = node_index
                    break
            if current_node:
                break
        colored_edges = []
        while trace_nodes:
            if len(adj_list[current_index]) == 1:
                colored_edges.append( (current_node, adj_list[current_index][0] ) )
                current_node = adj_list[current_index][0]
                current_index = node_to_index[current_node]
                del trace_nodes[0]
            else:
                next_node = [v for v in adj_list[current_index] if str(trace_nodes[0])[1:-1] in v.get_name()][0]
                colored_edges.append( (current_node, next_node ) )
                current_node = next_node
                current_index = node_to_index[current_node]
                del trace_nodes[0]
        graph = pydot.Dot(function.func_name, graph_type='digraph')
        for node_index in graph_nodes:
            bytecode, node = graph_nodes[node_index]
            if '...' in node.get_name(): continue
            graph.add_node( node )
        for start,end in graph_edges:
            the_edge = pydot.Edge(start, end)
            if (start, end) in colored_edges:
                the_edge.set_color("red")
            graph.add_edge( the_edge )
        if not os.path.exists('%s-pngs' % GLOBALS['basename']):
            os.makedirs('%s-pngs' % GLOBALS['basename'])
        graph.write_png('%s-pngs/%s_trace.png' % (GLOBALS['basename'],function.func_name))

    if False:
        print '=== fn_cfg_nodes ==='
        pprint(sorted([(a,b) \
            for a,b in GLOBALS['graph_fn_cfg'][function.func_name]
            ['nodes'].iteritems()]))
        print '=== fn_cfg_edges ==='
        pprint(sorted([(a.get_name(), b.get_name()) \
            for a,b in GLOBALS['graph_fn_cfg'][function.func_name]['edges']]))
        temp = {}
        for k,v in fn_cfg_usages.iteritems():
            temp[k] = v
        print '=== fn_cfg_usages ==='
        pprint(temp)
        print '=== fn_cfg_jmps ==='
        pprint(fn_cfg_jmps)
        print '=== fn_cfg_lbls ==='
        pprint(fn_cfg_lbls)
        print '=== fn_cls ==='
        pprint(fn_cls)
        print '=== constants ==='
        pprint(constants)
        print '=== dependent functions ==='
        pprint(sorted(dependent_fns))
        print '=== used arguments ==='
        pprint(sorted(used_args))

def main(GLOBALS):
    tested_functions = []
    for key in [ 'recursive', 'isolated', 'L']:
        print '\t === %s ===' % key
        for function in GLOBALS['function_test_order'][key]:
            if function in tested_functions: continue
            print 'Testing %s.%s\t%s...' % \
                (function.__module__, function.func_name,
                    inspect.getargspec(function))
            test_function(GLOBALS, function)
            tested_functions.append(function)
