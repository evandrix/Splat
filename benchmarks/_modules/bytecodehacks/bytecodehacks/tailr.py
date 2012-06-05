#   Copyright 1999-2000 Michael Hudson mwh@python.net
#
#                        All Rights Reserved
#
#
# Permission to use, copy, modify, and distribute this software and
# its documentation for any purpose is hereby granted without fee,
# provided that the above copyright notice appear in all copies and
# that both that copyright notice and this permission notice appear in
# supporting documentation.
#
# THE AUTHOR MICHAEL HUDSON DISCLAIMS ALL WARRANTIES WITH REGARD TO
# THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS, IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL,
# INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER
# RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF
# CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
# CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

from bytecodehacks.code_editor import Function
from bytecodehacks.find_function_call import find_function_call
from bytecodehacks.ops import *

def make_tail_recursive(func):
    func = Function(func)
    code = func.func_code
    cs = code.co_code
    
    index = 0

    while 1:
        stack = find_function_call(func,func.func_name,startindex=index)

        if stack is None:
            break

        index = cs.index(stack[-1])

        if cs[index + 1].__class__ is RETURN_VALUE:
            cs.remove(stack[0])
            newop = JUMP_ABSOLUTE()
            cs[index - 1:index] = [newop]
            newop.label.op = cs[0]
            del stack[0],stack[-1]

            nlocals = len(code.co_varnames)

            code.co_varnames = code.co_varnames + code.co_varnames

            for op in stack:
                cs.insert(cs.index(op)+1,STORE_FAST(stack.index(op)+nlocals))

            iindex = cs.index(newop)

            for i in range(len(stack)):
                cs.insert(iindex,STORE_FAST(i))
                cs.insert(iindex,LOAD_FAST(i+nlocals))

            index = iindex

    return func.make_function()

def _facr(n,c,p):
    if c <= n:
        return _facr(n,c+1,c*p)
    return p

def facr(n,_facr=_facr):
    return _facr(n,1,1l)

_factr = make_tail_recursive(_facr)

def factr(n,_factr=_factr):
    return _factr(n,1,1l)

def faci(n):
    p = 1l; c = 1;
    while c <= n:
        p = c*p
        c = c+1
    return p

import time

def suite(n,c=10,T=time.time):
    r = [0,0,0]
    for i in range(c):
        t=T(); facr(n); r[0] = T()-t + r[0]
        t=T(); factr(n); r[1] = T()-t + r[1]
        t=T(); faci(n); r[2] = T()-t + r[2]
    print "     recursive: 1.000000000000 (arbitrarily)"
    print "tail recursive:",r[1]/r[0]
    print "     iterative:",r[2]/r[0]
    
