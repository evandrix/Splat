#!/usr/bin/env python
# -*- coding: utf-8 -*-

import dis
import marshal
import struct
import sys
import os
import trace
import time
import types
import byteplay
import pprint
import inspect
from settings import *

TRACE_INTO = [ 'foo', 'foo1', 'foo2' ]  # specify functions for code coverage

num_lines_executed = 0  # tracks total number of lines of bytecode executed

# Function tracer module #
# details @ http://goo.gl/kryIB
#
# Features:
# - for measuring code coverage of unit tests generated
# - for tracing / profiling to optimise(?) bytecode
#

# Mock objects (before plugging into unit tests generated)
class A(object):
    def func3(self):
        return
class B(object):
    def func2(self):
        return

def trace_bytecode(frame, event, arg):
    """ Tracing through various function calls """

    global num_lines_executed # assignment to global variable

    # establish variables
    co       = frame.f_code
    lineno   = frame.f_lineno
#    filename = co.co_filename
    filename = frame.f_globals["__file__"]
    if filename.endswith(".pyc") or filename.endswith(".pyo"):
        filename = filename[:-1]
    name     = co.co_name #frame.f_globals["__name__"]
#    line     = linecache.getline(filename, lineno) # fails w/o src
    # unused
    #frame.f_locals
    #co.co_varnames[:co.co_argcount]

    # event filtering
    if event == 'line':
        # retrieve bytecode as list from code object, using 'byteplay'
        # filtering out (SetLineno, _)
        # for mapping bytecode line number to exact instruction
        cb = byteplay.Code.from_code(co)
        code_fragment = []
        take = False
        for opcode, arg in cb.code:
            if opcode == byteplay.SetLineno:
                take = arg == lineno
            elif take:
                code_fragment.append((opcode, arg))
        # strip list if only element (for prettyprinting)
        if len(code_fragment) == 1:
            code_fragment = code_fragment[0]

        num_lines_executed += 1
        print >> sys.stderr, "%s:%s %s" % (name, lineno, code_fragment)
    elif event == 'call':
        # monitor call stack for function & return values
        if name not in TRACE_INTO:
            return
        if name == 'write':
            # ignore write() calls from print statements
            return

        caller          = frame.f_back
        caller_lineno   = caller.f_lineno
        caller_co       = caller.f_code
        caller_filename = caller_co.co_filename

        print >> sys.stderr, "1: (%s:%s) => %s()@(%s:%s)" % \
            (caller_filename, caller_lineno, name, filename, lineno)

        if name in TRACE_INTO:
            # recursively trace into nested functions of interest
            return trace_bytecode
    elif event == 'exception':
        exc_type, exc_value, exc_traceback = arg
        print >> sys.stderr, '[exception]: %s "%s" - (%s:%s)' % \
            (exc_type.__name__, exc_value, name, lineno)
        # exc_type.args, exc_type.message
    elif event == 'return':
        print >> sys.stderr, '[return_value]: %s => %s' % (name, arg)
    else:
        print >> sys.stderr, "Unhandled event: %s" % event
    print >> sys.stderr, '2:\t>>%s()@(%s:%s)' % (name, filename, lineno)
    #return trace_bytecode
    return # do not recurse here

if __name__ == "__main__":
    the_module = __import__(MODULE_UNDER_TEST)
    functions = inspect.getmembers(the_module, inspect.isfunction)
    function = [ fn for name,fn in functions if name in TRACE_INTO ][0]

    ##########################################################################
    # Part I                                                                 #
    ##########################################################################
    # first measure total bytecode coverage, using 'byteplay'
    # excludes (SetLineno, _)
    cb = byteplay.Code.from_code(function.func_code)
    cb.code = [ (op,arg) for op,arg in cb.code if op != byteplay.SetLineno ]
    total_lines = len(cb.code)  # 100% = ? instructions
    #dis.dis(f.func_code.co_code)

    # begin tracing
    args = [ [None,None,None,None],
             [None,B(),None,None],
             [A(),B(),None,None],
             [A(),B(),3,None],
             [A(),B(),3,'4'] ]
    sys.settrace(trace_bytecode)
    for arg in args:
        num_lines_executed = 0
        try:
            function(*arg)
        except Exception as e:
            pass
        print "(Byte)code coverage: %d/%d instructions (%.2f%%)" % (num_lines_executed,total_lines, num_lines_executed/float(total_lines)*100)
    sys.settrace(None)
    print

    ##########################################################################
    # Part II                                                                #
    ##########################################################################
    tracer = trace.Trace(count=True, trace=True, outfile=None)
    tracer.runfunc(function, A(),B(),3,'4')
    # save results
    report_tracer = trace.Trace(count=False, trace=False, infile='trace_report.dat')
    results = tracer.results()
    results.write_results(summary=True, coverdir='coverdir')

