def is_prime(n):
    if n < 2:
        return False
    for i in xrange(2, n):
        if n%i == 0:
            return False
    return True
print sum(is_prime(n) for n in xrange(100))

# the Python Virtual Machine Instructions (bytecode)
# can be disassembled to mimic assembly code
# for instance:
# LOAD_FAST   var_num 
#   --> pushes a reference to local co_varnames[var_num] onto the stack
# STORE_FAST  var_num
#   --> stores top of stack into the local co_varnames[var_num]
# LOAD_CONST  consti
#    --> pushes co_consts[consti] onto the stack

import dis

def myfunc():
    a = 2
    b = 3
    print "adding a and b and 3"
    c = a + b + 3
    if c > 7:
        return c
    else:
        return None

# this disassembles the above function's code
dis.dis(myfunc)

"""
  7           0 LOAD_CONST               1 (2)
              3 STORE_FAST               0 (a)

  8           6 LOAD_CONST               2 (3)
              9 STORE_FAST               2 (b)

  9          12 LOAD_CONST               3 ('adding a and b and 3')
             15 PRINT_ITEM
             16 PRINT_NEWLINE

 10          17 LOAD_FAST                0 (a)
             20 LOAD_FAST                2 (b)
             23 BINARY_ADD
             24 LOAD_CONST               2 (3)
             27 BINARY_ADD
             28 STORE_FAST               1 (c)

 11          31 LOAD_FAST                1 (c)
             34 LOAD_CONST               4 (7)
             37 COMPARE_OP               4 (>)
             40 JUMP_IF_FALSE            8 (to 51)
             43 POP_TOP

 12          44 LOAD_FAST                1 (c)
             47 RETURN_VALUE
             48 JUMP_FORWARD             5 (to 56)
        >>   51 POP_TOP

 14          52 LOAD_CONST               0 (None)
             55 RETURN_VALUE
        >>   56 LOAD_CONST               0 (None)
             59 RETURN_VALUE

"""
