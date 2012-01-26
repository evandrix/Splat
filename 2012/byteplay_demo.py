#!/usr/bin/env python
# -*- coding: utf-8 -*-

from byteplay import *
from pprint import pprint
from simple import a, b

ca = Code.from_code(a.func_code)
pprint(ca.code)
print

cb = Code.from_code(b.func_code)
pprint(cb.code)
print

print [ x for x in cb.code if x not in ca.code ]
print

cc = ca.code[:1] \
 + [(LOAD_CONST, 4)] \
 + ca.code[2:4] \
 + [(LOAD_CONST, 2),(STORE_FAST, 'b'),(SetLineno, 4)] \
 + ca.code[4:5] \
 + [(LOAD_FAST, 'b'),(BINARY_ADD, None)] \
 + ca.code[5:]

print "before",
a()

ca.code = cc
a.func_code = ca.to_code()

print "after",
a()
