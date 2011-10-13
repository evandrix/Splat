#!/usr/bin/env python

def factorial(n):
     if n == 0:
         return 1
     else:
         return n * factorial(n-1)

def foo():
    return
    
def bar(x):
    print "bar"
    yield

if __name__ == "__main__":
    print factorial(1)
