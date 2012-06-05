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
from bytecodehacks.find_function_call import find_function_call

def iifize(func):
    func = Function(func)
    cs = func.func_code.co_code

    while 1:
        stack = find_function_call(func,"iif")

        if stack is None:
            break

        load, test, consequent, alternative, call = stack

        cs.remove(load)

        jump1 = JUMP_IF_FALSE(alternative)
        cs.insert(cs.index(test)+1,jump1)

        jump2 = JUMP_FORWARD(call)
        cs.insert(cs.index(consequent)+1,jump2)
        
        cs.remove(call)

    cs = None
    
    return func.make_function()
