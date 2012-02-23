#!/usr/bin/env python
import sys
import marshal
import py_compile
import time
import ast
import os, os.path
import struct
import byteplay
codeobject = compile(ast.parse('print "Hello World"'), '<string>', 'exec')
with open('output.pyc', 'wb') as fc:
    fc.write(py_compile.MAGIC)
    py_compile.wr_long(fc, long(time.time()))
    marshal.dump(codeobject, fc)
    fc.flush()

def load_pyc(filename):
    f = open(filename, 'rb')
    try:
        magic = f.read(4)
        if struct.calcsize("i") == 4:
            # 64-bit
            unixtime = struct.unpack("i", f.read(4))[0]
        elif struct.calcsize("L") == 4:
            # 32-bit
            unixtime = struct.unpack("L", f.read(4))[0]
        timestamp = time.asctime(time.localtime(unixtime))
        code = marshal.load(f)
        print timestamp
    finally:
        f.close()
    return magic, timestamp, codeobject
magic, timestamp, codeobject = load_pyc('output.pyc')
print "Magic number:", py_compile.MAGIC.encode('hex'), magic.encode('hex')
cb = byteplay.Code.from_code(codeobject)
print cb.code
# try to convert codeobject (bytecode) => AST?
