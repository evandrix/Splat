from bytecodehacks.xapply import xapply

def adder(x,y):
    return x + y

def repeater(count,thing):
    from string import join
    thing = str(thing)
    result = []
    for i in range(count):
        result.append( thing )
    return join( result, '' )

def f(x,y):
    x = x + 1
    y = y + x
    return y

assert xapply(adder,10)(10) == 20
assert xapply(repeater,3)("bob") == "bobbobbob"
assert xapply(f,3)(4) == 8

# test keyword arguments

def sub(x=10,y=20):
    return x - y

assert xapply(sub,y=100)() == -90
assert xapply(sub,x=100)() == 80
assert xapply(sub,100)() == 80

def g(a,b,c,d,e,f,g):
    return a,b,c,d,e,f,g

# get some fail cases

try:
    xapply(g,1,a=1)
    assert 0
except TypeError,why:
    print why
try:
    xapply(g,h=1)
    assert 0
except TypeError, why:
    print why
try:
    xapply(g,1,2,3,4,5,6,7,8)
    assert 0
except TypeError, why:
    print why

assert xapply(g,1,2,3,f=1)(8,9,0) == (1,2,3,8,9,1,0)

def h(**kw):
    return kw

assert xapply(h,a=1)()['a'] == 1
assert xapply(h,a=1)(a=0)['a'] == 0
assert len(xapply(h,a=1)(b=1)) == 2
