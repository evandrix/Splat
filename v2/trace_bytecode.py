#!/usr/bin/env python
# encoding: utf-8
import sys
import os
import trace
from pprint import pprint
from dis import dis
from byteplay import *

def trace_calls_and_returns(frame, event, arg):
    """ Tracing function calls """
    co = frame.f_code
    func_filename = co.co_filename
    func_line_no = frame.f_lineno
    func_name = co.co_name

    # Watch the stack ie. which functions called & return values
    if event == 'call':
        if func_filename.startswith('/'):
            return
        if func_name == 'write':
            # Ignore write() calls from print statements
            return
        caller = frame.f_back
        caller_line_no = caller.f_lineno
        caller_filename = caller.f_code.co_filename
        print "1: (%s:%s) => %s()@(%s:%s)" % \
            (caller_filename, caller_line_no,
            func_name, func_filename, func_line_no)
        if func_name in TRACE_INTO:
            # Trace into this function recursively
            return trace_calls_and_returns
    elif event == 'line':
        # get exact bytecode line using byteplay
        cb = Code.from_code(co)
        code_fragment = []
        take = False
        for pair in cb.code:
            opcode, arg = pair
            if opcode == SetLineno:
                take = arg == func_line_no
            elif take:
                code_fragment.append(pair)
        print "line", func_line_no, code_fragment             
    elif event == 'exception':
        exc_type, exc_value, exc_traceback = arg
        print '[EXCEPTION] %s "%s" on (%s:%s)' % \
        (exc_type.__name__, exc_value, func_name, func_line_no)
        #[exc_type.args, exc_type.message]
    elif event == 'return':
        print '[RETURN_VAL] %s => %s' % (func_name, arg)
    print '2:\t>>%s()@(%s:%s)' % (func_name, func_filename, func_line_no)
    return

from program import foo, foo1, foo2
class A(object):
    def func3(self):
        return
class B(object):
    def func2(self):
        return
# test nested function return values
def b():
    print 'in b()'
    return 'response_from_b '
def a():
    print 'in a()'
    val = b()
    return val * 2
tracer = trace.Trace(count=True, trace=True, outfile=None)
TRACE_INTO = ['a', 'b', 'foo', 'foo1', 'foo2']
sys.settrace(trace_calls_and_returns)
try:
    foo(A(),B(),3,'4')
except Exception as e:
    #print e
    pass
#a()
sys.settrace(None)

print
tracer.runfunc(foo, A(),B(),3,'4')
# save results
report_tracer = trace.Trace(count=False, trace=False, infile='trace_report.dat')
results = tracer.results()
results.write_results(summary=True, coverdir='coverdir')
print

print
dis(foo)
