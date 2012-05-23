#!/usr/bin/env python
# @ http://geofft.mit.edu/blog/sipb/73

import dis
import new

def foo(a, b):
    return a * b

if __name__ == "__main__":
    print "foo(3,5) = %d" % foo(3,5)

    print "dis.dis(foo):"
    dis.dis(foo)

    ff = foo.func_code
    print repr(ff.co_code)
    
    modified_code = '|\x00\x00|\x00\x00\x14S'
    foo.func_code = new.code(ff.co_argcount, ff.co_nlocals,
                          ff.co_stacksize, ff.co_flags,
                          modified_code,
                          ff.co_consts, ff.co_names, ff.co_varnames,
                          ff.co_filename, ff.co_name, ff.co_firstlineno,
                          ff.co_lnotab, ff.co_freevars, ff.co_cellvars)

    print "foo(3,5) = %d" % foo(3,5)
    print "foo(3,17) = %d" % foo(3,17)
