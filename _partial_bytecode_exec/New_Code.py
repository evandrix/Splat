import dis
import new
def foo(a, b):
     return a * b
print foo(3, 5)
dis.dis(foo)
ff = foo.func_code
#ff.co_code => '|\x00\x00|\x01\x00\x14S'
modified_code = '|\x00\x00|\x00\x00\x14S'

print ff.co_argcount, ff.co_nlocals
print ff.co_stacksize, ff.co_flags
print modified_code
print ff.co_consts, ff.co_names, ff.co_varnames
print ff.co_filename, ff.co_name, ff.co_firstlineno
print ff.co_lnotab, ff.co_freevars, ff.co_cellvars

foo.func_code = new.code(ff.co_argcount, ff.co_nlocals,
                          ff.co_stacksize, ff.co_flags,
                          modified_code,
                          ff.co_consts, ff.co_names, ff.co_varnames,
                          ff.co_filename, ff.co_name, ff.co_firstlineno,
                          ff.co_lnotab, ff.co_freevars, ff.co_cellvars)
print foo(3, 5)
print foo(3, 17)