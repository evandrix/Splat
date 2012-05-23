from bytecodehacks.code_editor import Function

# test the computation of co_stacksize

def test_it(f):
    diff = Function(f).func_code.co_code.compute_stack() \
           - f.func_code.co_stacksize
    print "stack diff on function %s of %d"%(f.func_name,diff)

def basic(x,y):
    return x + y
test_it(basic)

def call():
    return f()
test_it(call)

def test_finally():
    try:
        foo()
    finally:
        x=0
test_it(test_finally)

def test_except():
    try:
        foo()
    except:
        x=0
test_it(test_except)

def test_except2():
    try:
        foo()
    except NameError:
        x=0
test_it(test_except2)

def test_except3():
    try:
        foo()
    except NameError, why:
        print why
test_it(test_except3)

def test_nested_except():
    try:
        x=1
        try:
            pass
        except:
            try:
                pass
            except NameError:
                try:
                    pass
                except NameError, why:
                    print why
    finally:
        x=0
test_it(test_nested_except)

def complex(x):
    try:
        for i in x:
            del x
            x = 9
            if x<0:
                raise "bobbins"
        return 8
    except:
        try:
            cleanup()
        finally:
            x=0
test_it(complex)

import os,types

def quiet_test(f):
    diff = Function(f).func_code.co_code.compute_stack() \
           - f.func_code.co_stacksize
    if diff <> 0: raise "stack diff on function %s of %d"%(f.func_name,diff)

for name in dir(os):
    attr = getattr(os,name)
    if type(attr) is types.FunctionType:
        quiet_test(attr)
