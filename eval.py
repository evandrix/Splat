#!/usr/bin/env python
from math import *
user_func = raw_input("type a function: y = ")
for x in range(1,10):
	print "x = ", x , ", y = ", eval(user_func)

class Foo:
    def hello(self):
        print "hello"
        return self

# without reflection
Foo().hello()
# with reflection
getattr(globals()['Foo'](), 'hello')()
