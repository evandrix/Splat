import sys
import dis
import new
import byteplay
import inspect
from pprint import pprint
from peak.util.assembler import *
from peak.util.assembler import dump

# using byteplay, given initial state dict, manipulate bytecode list
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
#sys.settrace(trace)
# exec discards the return value, so no output here
exec(co.to_code(), mydict)  #or exec(co.to_code(), {})
#sys.settrace(None)

print "stack frame (main): " + str(hex(id(sys._getframe())))
stack = inspect.stack()
print stack[0][0].f_globals['mydict'], stack[0][0].f_locals

print sorted([ (x,mydict[x]) for x in mydict if x not in globals() ])
print "mydict: { 'n':", mydict['n'], '}'

#alternative
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
pprint(co.code)
exec(co.to_code(), mydict)
code = compile(fib.func_code, '<string>', 'exec')

# using peak.util.assembler
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

# convert from peak.util.assembler to byteplay
x = Code()
for i, c in enumerate(co.code):
    op, arg = c
    if op == byteplay.LOAD_GLOBAL:
        x.LOAD_GLOBAL(arg)
    elif op == byteplay.CALL_FUNCTION:
        x.CALL_FUNCTION(arg)

print "stack frame (main): " + str(hex(id(sys._getframe())))
stack = inspect.stack()
mydict['n'] = eval(c.code(), mydict)
print stack[0][0].f_globals['mydict'], stack[0][0].f_locals
exec(c.code(), mydict)  # exec discards the return value, so no output here
print "mydict: { 'n':", mydict['n'], '}'

# modify bytes in bytecode directly
ff = foo.func_code
modified_code = '|\x01\x00|\x01\x00\x14S'
print 'arg_size =',ff.co_argcount, 'locals =',ff.co_nlocals
print 'stack_size =',ff.co_stacksize, 'flags =',ff.co_flags
print ff.co_consts, ff.co_names, ff.co_varnames
print ff.co_filename, ff.co_name, ff.co_firstlineno
print ff.co_lnotab, ff.co_freevars, ff.co_cellvars
# modify code
foo.func_code = new.code(ff.co_argcount, ff.co_nlocals,
                          ff.co_stacksize, ff.co_flags,
                          modified_code,
                          ff.co_consts, ff.co_names, ff.co_varnames,
                          ff.co_filename, ff.co_name, ff.co_firstlineno,
                          ff.co_lnotab, ff.co_freevars, ff.co_cellvars)
