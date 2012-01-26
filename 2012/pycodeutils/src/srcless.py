#!/usr/bin/env python

def factorial(n):
     if n == 0:
         return 1
     else:
         return n * factorial(n - 1)

def fac(n):
    return "Factorial of %d is %d" % (n, factorial(n))
