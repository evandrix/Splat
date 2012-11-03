class A(object):
    attr1 = attr2 = None

def function1(arg1, arg2, arg3='default'):
    arg1 = A()
    arg1.attr1 = 'arg1'
    return arg1