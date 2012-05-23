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

from bytecodehacks.ops import *

def find_function_call(infunc,calledfuncname, allowkeywords=0, startindex=0):
    i = startindex
    code = infunc.func_code
    cs = code.co_code

    def match(op,name = calledfuncname):
        return getattr(op,'name',None) == name

    while i < len(cs):
        op = code.co_code[i]
        if match(op):
            try:
                if allowkeywords:
                    return simulate_stack_with_keywords(code,i)
                else:
                    return simulate_stack(code,i)
            except:
                i = i + 1
        i = i + 1
    if allowkeywords:
        return None,0
    else:
        return None
    
def call_stack_length_usage(arg):
    num_keyword_args=arg>>8
    num_regular_args=arg&0xFF
    return 2*num_keyword_args + num_regular_args

def simulate_stack(code,index_start):
    stack = []
    cs = code.co_code
    i, n = index_start, len(cs)
    
    while i < n:
        op = cs[i]
        if op.__class__ is CALL_FUNCTION and op.arg+1==len(stack):
            stack.append(op)
            return stack
        elif op.is_jump():
            i = cs.index(op.label.op)+1
        else:
            op.execute(stack)
            i = i + 1
    raise "no call found!"

def simulate_stack_with_keywords(code,index_start):
    stack = []
    cs = code.co_code
    i, n = index_start, len(cs)
    
    while i < n:
        op = cs[i]
        if op.__class__ is CALL_FUNCTION \
           and call_stack_length_usage(op.arg)+1==len(stack):
            stack.append(op)
            return stack, op.arg>>8
        elif op.is_jump():
            i = cs.index(op.label.op)+1
        else:
            op.execute(stack)
            i = i + 1
    raise "no call found!"
