#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys

GLOBAL_CONST = 'global constant'

# classes
class old:
    def old_f1():
        pass
    def old_f2(self):
        pass
class new(object):
    def new_f1():
        pass
    def new_f2(self):
        pass

# functions
def func():
    pass
def nested_func():
    class c1(object):
        def nest_f1(self):
            return

def ctrl_if(a,b):
    if a:
        return 1
    elif b:
        return 2
    else:
        return 3

def ctrl_while(a,b):
    while a:
        return 1
    else:
        return 2

def ctrl_for(a,b):
    for i in [1,2,3]:
        pass
    else:
        return 1
    return 2

def ctrl_try(a,b):
    try:
        1/0
    except ZeroDivisionError as e:
        return 1
    else:
        return 2
    finally:
        return 3
    return 4

def ctrl_with(a,b):
    with open('/tmp/foo', 'w') as file:
        return 1
    return 2

def flow_break(a,b):
    while a:
        break
    return 1

def flow_continue(a,b):
    i = 2
    while i:
        continue
        i-=1
    return 1

def flow_raise(a,b):
    raise RuntimeError('rte')

def flow_yield(a,b):
    yield (b,a)

# statements
def stmts():
    """ sample docstring """

    global GLOBAL_CONST     # absent in bytecode unless assigned

    # atoms
    (1,)            #tuple
    x=[1,2]; y={1,2}; z={1:2}

    # list functions
    x[0]
    x[::-1]
    x[0:1:-1]    #ValueError: slice step cannot be zero

    # x[1:0:-1] == [2]
    # x[1:0] ==[]

    # used to make copies
    # legal calls
    list(x)     #TypeError: arg must be iterable
    list(y)
    list(z)
    set(x)      #legal like list()
    set(y)
    set(z)

    # iterators
    {}
    []
    ()  # invalid tuple: (,)

    ''; ""  #empty str
    None

    # legal calls
    dict(z)     #TypeError: arg must be dict

    # => String, Num, NAME
    lambda:None
    lambda x:None

    # OBJECTS #
    class a(object):
        b = ''
        def __init__(self, a):
            self.a = a
            self.b = 'b'
            self.c = 'c'
    a = a(1)

    a,b = 1,0    # check for unsupported operand types
    # expr - binop
    a += b  # arithmetic
    a -= b
    a *= b
    a /= b      #ZeroDivisionError
    a %= b      #ZeroDivisionError
    a &= b  # bitwise
    a |= b
    a ^= b
    a <<= b
    a >>= b
    a **= b
    a //= b     #ZeroDivisionError

    # cond test
    not a
    a or b
    a and b
    ~a          #TypeError bad operand type for unary ~: (if not int)
    a > b
    a >= b
    a < b
    a <= b
    a == b; a is b; a is not b; # is->id();==->dict()
    a != b; a <> b;
    a not in [b]      #TypeError: argument of type(b) is not iterable
    a in [b]

    # standard streams
    #sys.stdin.read()
    print >> sys.stdout, 'out'
    print >> sys.stderr, 'err'

    del a,b

    # control flow
    a,b = True,False
    ctrl_if(a,b)
    ctrl_while(a,b)
    ctrl_for(a,b)
    ctrl_try(a,b)
    ctrl_with(a,b)

    # terminate flow
    flow_break(a,b)
    flow_continue(a,b)
    flow_raise(a,b)
    flow_yield(a,b)

    eval(compile('a=1+2', '<string>', 'exec'))
    assert True

if __name__ == "__main__":
    sys.exit(0)

