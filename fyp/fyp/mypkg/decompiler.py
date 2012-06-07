import opcode

# @ http://goo.gl/YKFfO
def decompile(code_object):
  code = code_object.co_code
  variables = code_object.co_cellvars + code_object.co_freevars
  instructions = []
  n,i,e = len(code),0,0
  while i < n:
    i_offset = i
    i_opcode = ord(code[i])
    i = i + 1
    if i_opcode >= opcode.HAVE_ARGUMENT:
      i_argument = ord(code[i]) + (ord(code[i+1]) << (4*2)) + e
      i = i +2
      if i_opcode == opcode.EXTENDED_ARG:
        e = iarg << 16
      else:
        e = 0
      if i_opcode in opcode.hasconst:
        i_arg_value = repr(code_object.co_consts[i_argument])
        i_arg_type = 'CONSTANT'
      elif i_opcode in opcode.hasname:
        i_arg_value = code_object.co_names[i_argument]
        i_arg_type = 'GLOBAL VARIABLE'
      elif i_opcode in opcode.hasjrel:
        i_arg_value = repr(i + i_argument)
        i_arg_type = 'RELATIVE JUMP'
      elif i_opcode in opcode.haslocal:
        i_arg_value = code_object.co_varnames[i_argument]
        i_arg_type = 'LOCAL VARIABLE'
      elif i_opcode in opcode.hascompare:
        i_arg_value = opcode.cmp_op[i_argument]
        i_arg_type = 'COMPARE OPERATOR'
      elif i_opcode in opcode.hasfree:
        i_arg_value = variables[i_argument]
        i_arg_type = 'FREE VARIABLE'
      else:
        i_arg_value = i_argument
        i_arg_type = 'OTHER'
    else:
      i_argument = None
      i_arg_value = None
      i_arg_type = None
    instructions.append( (i_offset, i_opcode, opcode.opname[i_opcode],\
                          i_argument, i_arg_type, i_arg_value) )
    return instructions

def pretty_print(instructions):
  print '%5s %-20s %3s  %5s  %-20s  %s' % \
    ('OFFSET', 'INSTRUCTION', 'OPCODE', 'ARG', 'TYPE', 'VALUE')
  for (offset, op, name, argument, argtype, argvalue) in instructions:
    print '%5d  %-20s (%3d)  ' % (offset, name, op),
    if argument != None:
      print '%5d  %-20s  (%s)' % (argument, argtype, argvalue),
    print 
