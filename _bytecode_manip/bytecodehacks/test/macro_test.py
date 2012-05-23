from bytecodehacks import macro

def incr((x)):
    x = x + 1
    return x

def postincr((x)):
    t = x
    x = x + 1
    return t

macro.add_macro(incr)

def f(x):
    while incr(x) < 10:
        print x

ff = macro.expand(f)
gg = macro.expand_these(f,incr=postincr)

