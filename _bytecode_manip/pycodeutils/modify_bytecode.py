#!/usr/bin/env python

from codeutils import delegate_code
print ">> Importing bytecode module..."
import srcless

def delegatee(f, args, kw):
    a = args[0]
    return f(2 * a)

# modify factorial function to return twice as much
n = 5
print n, srcless.fac(n)
print ">> Modifying code via delegation..."
delegate_code(srcless.fac, delegatee)
print n, srcless.fac(n)
