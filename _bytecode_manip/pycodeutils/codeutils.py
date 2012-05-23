# Code Object Utilities - Copyright (c) 2006 Oliver Horn.
# @ http://www.oliverh.com/projects/python-codeutils
# MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

from compiler import consts
from types import CodeType
from inspect import ismethod, isfunction
from opcode import opmap

def delegate_code(funcs, delegatee):
    if not hasattr(funcs, '__iter__'):
        funcs = (funcs,)
    for func in funcs:
        if isfunction(func):
            pass
        elif ismethod(func) and func.im_self is None:
            func = func.im_func
        else:
            raise TypeError()    
        func.func_code = _make_delegation_codeobj(func.func_code, delegatee)

def _make_delegation_codeobj(f_code, delegatee):
    # New code
    d_code = CodeGen()
    # Load delegatee on stack
    d_code.append('LOAD_CONST', 2)
    # Make function (or closure) from original code object
    if f_code.co_freevars:
        ncellvars = len(f_code.co_cellvars)
        for i in range(ncellvars, ncellvars+len(f_code.co_freevars)):
            d_code.append('LOAD_CLOSURE', i)
        d_code.append('LOAD_CONST', 1)
        d_code.append('MAKE_CLOSURE', 0)
    else:
        d_code.append('LOAD_CONST', 1)
        d_code.append('MAKE_FUNCTION', 0)
    # Make tuple from positional arguments
    argi = 0
    while argi < f_code.co_argcount:
        d_code.append('LOAD_FAST', argi)
        argi += 1
    d_code.append('BUILD_TUPLE', argi)
    # Append var args (if any)
    if f_code.co_flags & consts.CO_VARARGS:
        d_code.append('LOAD_FAST', argi)
        argi += 1
        d_code.append('BINARY_ADD')
    # Load keyword args dictionary (or create empty dictionary)
    if f_code.co_flags & consts.CO_VARKEYWORDS:
        d_code.append('LOAD_FAST', argi)
        argi += 1
    else:
        d_code.append('BUILD_MAP', 0)
    # Call delegatee with three arguments
    d_code.append('CALL_FUNCTION', 3)
    d_code.append('RETURN_VALUE')
    # for i in instrs: print i
    # Generating new code object
    return CodeType(
            f_code.co_argcount,
            argi,                                       # nlocals
            max(len(f_code.co_freevars)+1,argi+2,4),    # stacksize             
            f_code.co_flags & ~(consts.CO_GENERATOR),   # same flags (except CO_GENERATOR)
            d_code.codestring,                          # codestring
            (None, f_code, delegatee),                  # constants
            (),                                         # names
            f_code.co_varnames,
            '',                                         # filename
            '',                                         # name
            0,                                          # firstlineno
            '',                                         # lnotab
            f_code.co_freevars,
            ())                                         # cellvars

class CodeGen(object):
    def __init__(self):
        self.codestring = ''
    def append(self, opname, oparg=None):
        self.codestring += chr(opmap[opname])
        if oparg is not None: 
            self.codestring += chr(oparg&0xFF) + chr((oparg&0xFF00)>>8)
