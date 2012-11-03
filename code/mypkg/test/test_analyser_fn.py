# Sample test cases

def a(x):
    def b():
        pass
    a = 42
    print a
    a(b())

def b(x):
    b(x)

def c(x,y):
    c(x,y[:])
    c(x,y[1:])
    c(x,y[:2])
    c(x,y[1:2])
    c(x,y[1:2:-3])

def d(d,e,f):
    d(a,b,c)
    b()
    b(x(g))

def e(_,f,g):
    e(x,y,z)

def h(_,f,g):
    h(x,h(a,b,c),z)

def factorial(n):
     if n == 0:
         return 1
     else:
         return n * factorial(n-1)

def fib(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib(n-1) + fib(n-2)

class Hanoi(object):
    def hanoi(self, height=3, start=1, end=3):
        steps = []
        if height > 0:
            helper = ({1, 2, 3} - {start} - {end}).pop()
            steps.extend(self.hanoi(height - 1, start, helper))
            steps.append((start, end))
            steps.extend(self.hanoi(height - 1, helper, end))
        return steps
def hanoi(hanoi):
    hanoi.hanoi()
def hanoi1(h):
    hanoi = Hanoi()
    hanoi.hanoi1()
def hanoi2(hanoi):
    hanoi.hanoi2()

