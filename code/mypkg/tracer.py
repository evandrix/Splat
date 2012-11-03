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

# Function tracer module #
# details @ http://goo.gl/kryIB
#
# Features:
# - for measuring code coverage of unit tests generated
# - for tracing / profiling to optimise(?) bytecode
#

TRACE_INTO = []         # specify functions to measure for code coverage
NUM_LINES_EXECUTED = 0  # tracks total number of lines of bytecode executed
CODE_FRAGMENT = []

def trace_bytecode(frame, event, arg):
    """ Tracing through various function calls """

    global NUM_LINES_EXECUTED, CODE_FRAGMENT # assignment to global variable

    # establish variables
    co       = frame.f_code
    lineno   = frame.f_lineno
    filename = co.co_filename
    if filename.endswith(".pyc") or filename.endswith(".pyo"):
        filename = filename[:-1]
    name     = co.co_name
    # unused
    frame.f_locals
    co.co_varnames[:co.co_argcount]

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
                take = (arg == lineno)
            elif take:
                code_fragment.append((opcode, arg))
        # strip list if only element (for prettyprinting)
#        if len(code_fragment) == 1:
#            code_fragment = code_fragment[0]

        NUM_LINES_EXECUTED += 1
        CODE_FRAGMENT.extend(code_fragment)
        #print >> sys.stderr, "%s:%s %s" % (name, lineno, code_fragment)
    elif event == 'call':
        # ignore write() calls from print statements
        if name == 'write':         return
        # monitor call stack for function & return values
        if name not in TRACE_INTO:  return
        caller          = frame.f_back
        caller_lineno   = caller.f_lineno
        caller_co       = caller.f_code
        caller_filename = caller_co.co_filename
        #print >> sys.stderr, "[call]: (%s:%s) => %s()@(%s:%s)" % \
        #    (caller_filename, caller_lineno, name, filename, lineno)
        if name in TRACE_INTO:
            # recursively trace into nested functions of interest
            return trace_bytecode
    elif event == 'exception':
        exc_type, exc_value, exc_traceback = arg
        #print >> sys.stderr, '[exception]: %s "%s" - (%s:%s)' % \
        #    (exc_type.__name__, exc_value, name, lineno)
        # exc_type.args, exc_type.message
    elif event == 'return':
        #print >> sys.stderr, '[return_value]: %s => %s' % (name, arg)
        pass
    else:
        print >> sys.stderr, "[Unhandled event]: %s" % event
    #print >> sys.stderr, '[*]:\t>>%s()@(%s:%s)' % (name, filename, lineno)
    return # no recursion here
