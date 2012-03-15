class Test(object):
    def foo(self,a,b,c):
        self.foo = 5
        print self.foo
        return self.foo(a,b,c)
def bar():
    return bar()

def strcmp():
    guess, correct = "a", "b"
    if guess == correct:
        print "That's it!\n"

def recurse():
    recurse()
    return None

def factorial(n):
    if n:
        return n * factorial(n-1)
    else:
        return 1

def foo(n):
    if not n != foo():
        return 1
    n = 2

def bar(n):
    while n > 0:
        pass

for i in xrange(2**5,0,-1):
    try:
        hanoi(i)
    except RuntimeError as e:
        continue
    else:
        print i
        break

import time
for i in xrange(2**4):
    t0 = time.time()
    hanoi(i)
    print "#%d: time = %.10f seconds" % (i,time.time()-t0)