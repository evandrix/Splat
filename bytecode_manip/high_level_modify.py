import sys
import dis
import byteplay
import inspect
from pprint import pprint
from fib import fib
from peak.util.assembler import *
from peak.util.assembler import dump

def fib(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib(n-1) + fib(n-2)

mydict = {
    'n': 11, 'fib': fib
}

co = byteplay.Code.from_code(fib.func_code)
co.code = [ c for c in co.code if c[0] != byteplay.SetLineno ]
co.args = ()    # remove function arguments

for i,c in enumerate(co.code):
    op, arg = c
    if op == byteplay.STORE_FAST:
        op = byteplay.STORE_GLOBAL#NAME
    elif op == byteplay.LOAD_FAST:
        op = byteplay.LOAD_GLOBAL#NAME
    elif op == byteplay.INPLACE_ADD:
        op = byteplay.INPLACE_SUBTRACT
    co.code[i] = (op, arg)

co.code = co.code[:-10] + [(byteplay.DUP_TOP, None),(byteplay.STORE_GLOBAL, 'arg1')] + [co.code[-10]] + [(byteplay.DUP_TOP, None),(byteplay.STORE_GLOBAL, 'call1')] + co.code[-9:]
co.code = co.code[:-5] + [(byteplay.DUP_TOP, None),(byteplay.STORE_GLOBAL, 'arg2')] + [co.code[-5]] + [(byteplay.DUP_TOP, None),(byteplay.STORE_GLOBAL, 'call2')] + co.code[-4:]

pprint(co.code)
sys.settrace(trace)
exec(co.to_code(), mydict)
sys.settrace(None)
print sorted([ (x,mydict[x]) for x in mydict if x not in globals() ])

c = Code()
block = Label()
loop = Label()
else_ = Label()
c(
     block.SETUP_LOOP,
         5,      # initial setup - this could be a GET_ITER instead
     loop,
         else_.JUMP_IF_FALSE,        # while x:
         1, Code.BINARY_SUBTRACT,    #     x -= 1
         loop.CONTINUE_LOOP,
     else_,                          # else:
         Code.POP_TOP,
     block.POP_BLOCK,
         Return(42),                 #     return 42
     block,
     Return()
)

print "stack frame (main): " + str(hex(id(sys._getframe())))
stack = inspect.stack()
mydict['n'] = eval(c.code(), mydict)
print stack[0][0].f_globals['mydict'], stack[0][0].f_locals
exec(c.code(), mydict)  # exec discards the return value, so no output here
print "mydict: { 'n':", mydict['n'], '}'

mydict = {
    'n': 5, 'fib': dummy
}

co = byteplay.Code.from_code(fib.func_code)
co.code = [ c for c in co.code if c[0] != byteplay.SetLineno ]
co.args = ()    # remove function arguments

for i,c in enumerate(co.code):
    op, arg = c
    if op == byteplay.STORE_FAST:
        op = byteplay.STORE_NAME
    elif op == byteplay.LOAD_FAST:
        if arg != 'fib':
            op = byteplay.LOAD_GLOBAL#NAME
    co.code[i] = (op, arg)

dummy.__code__ = co.to_code()
print co.code
exec(co.to_code(), mydict)
code = compile(fib.func_code, '<string>', 'exec')

