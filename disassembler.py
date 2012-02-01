#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dis import dis

def myfunc(alist):
    return len(alist)

# normal functions
def f(x): return x**2

# lambdas
g = lambda x: x**2

dis(myfunc)

# bytecode generated for normal functions and lambdas identical
dis(f)
dis(g)

# dict building

# arguments for the opcode; in the case of CONST, it shows the index as well as the const object indexed

# BUILD_MAP: create a new dictionary on the stack, with 2 entries.
# load the constant with index 0 onto the stack (which happens to be the integer object '1', the value of the 'a' key)
# load the constant with index 1 onto the stack (which happens to be the string object 'a', the key for the '1' value)
# STORE_MAP: pops the key and the value off the stack, storing them in the dict.
# Note that the key was indeed loaded on the stack after the value.
# Now only the dictionary is left on the stack.
# Repeat LOAD_CONST, LOAD_CONST and STORE_MAP for the next set.
# RETURN_VALUE: returns the current value on the stack to the caller.
f = lambda: {'a': 1, 'b': 2}
dis(f)
