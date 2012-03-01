#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Byteplay wrapper to pretty_print bytecode #

import sys
import opcode
import dis
import pprint
from common import *    # decorators

class Bytecode(object):
    def __init__(self, target):
        self.target = target

    def decompile(self):
        """
            The bytecode decompiler
            Returns a list of tuples representing (opcode,arg) in code object
            credits @ http://goo.gl/U5YBZ
        """

        code_object = self.target
        code = code_object.co_code
        variables = code_object.co_cellvars + code_object.co_freevars
        instructions = []
        n = len(code)
        i = e = 0
        labls = [item for item in dis.findlabels(self.target)] # unused
        linestarts = [item for item in dis.findlinestarts(self.target)]
        while i < n:
            i_offset = [actual for rel,actual in linestarts if rel == i][0]
            i_opcode = ord(code[i])
            i += 1
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
                i_arg_type = 'GLOBAL_VARIABLE'
              elif i_opcode in opcode.hasjrel:
                i_arg_value = repr(i + i_argument)
                i_arg_type = 'RELATIVE_JUMP'
              elif i_opcode in opcode.haslocal:
                i_arg_value = code_object.co_varnames[i_argument]
                i_arg_type = 'LOCAL_VARIABLE'
              elif i_opcode in opcode.hascompare:
                i_arg_value = opcode.cmp_op[i_argument]
                i_arg_type = 'COMPARE_OPERATOR'
              elif i_opcode in opcode.hasfree:
                i_arg_value = variables[i_argument]
                i_arg_type = 'FREE_VARIABLE'
              else:
                i_arg_value = i_argument
                i_arg_type = 'OTHER'
            else:
              i_argument = i_arg_value = i_arg_type = None
            instructions.append((i_offset, i_opcode, opcode.opname[i_opcode],\
                                 i_argument, i_arg_type, i_arg_value))
        return instructions

    def pretty_print(self, instructions):
        """ print bytecode in human-readable format """

        print '%5s %-20s %3s  %5s  %-20s  %s' % \
            ('OFFSET', 'INSTRUCTION', 'OPCODE', 'ARG', 'TYPE', 'VALUE')
        for (offset, op, name, argument, argtype, argvalue) in instructions:
            print '%5d  %-20s (%3d)  ' % (offset, name, op),
            if argument != None:
              print '%5d  %-20s  (%s)' % (argument, argtype, argvalue),
            print

    def disassemble(self):
        """
            Unlike dis.dissasemble, this returns the disassembled code in machine,
            not human-readable form, allowing it to be examined programmatically.
            Each bytecode operation is returned as a tuple (opcode, arg kind, argument),
            where opcode is the string name of the opcode, and arg kind is what sort of
            argument the opcode uses (not the type of the argument, but whether it's
            a local, global, constant etc). The argument is typically an identifier or
            offset. arg kind and argument may be None.

            Note: Any magic numbers in this code are from dis.dis and were just as
            magic there :)
            credits @ http://goo.gl/X8S8i
        """

        co = self.target
        code = co.co_code
        n = len(code)
        i = 0
        extended_arg = 0
        free = None
        disassembly = []
        opname = dis.opname
        hasconst = dis.hasconst
        HAVE_ARGUMENT = dis.HAVE_ARGUMENT
        EXTENDED_ARG = dis.EXTENDED_ARG
        cmp_op = dis.cmp_op
        hasconst = dis.hasconst
        hasname = dis.hasname
        hasjrel = dis.hasjrel
        haslocal = dis.haslocal
        hascompare = dis.hascompare
        hasfree = dis.hasfree
        while i < n:
            c = code[i]
            op = ord(c)
            instruction = (opname[op], None, None)
            i = i+1
            if op >= HAVE_ARGUMENT:
                oparg = ord(code[i]) + ord(code[i+1])*256 + extended_arg
                extended_arg = 0
                i = i+2
                if op == EXTENDED_ARG:
                    extended_arg = oparg*65536L
                if op in hasconst:
                    instruction = (instruction[0], 'const', co.co_consts[oparg])
                elif op in hasname:
                    instruction = (instruction[0], 'name', co.co_names[oparg])
                elif op in hasjrel:
                    instruction = (instruction[0], 'addr', i+oparg)
                elif op in haslocal:
                    instruction = (instruction[0], 'var', co.co_varnames[oparg])
                elif op in hascompare:
                    instruction = (instruction[0], 'cmp', cmp_op[oparg])
                elif op in hasfree:
                    if free is None:
                        free = co.co_cellvars + co.co_freevars
                    instruction = (instruction[0], 'free', free[oparg])
            disassembly.append( instruction )
        return disassembly        

    def get_accessed_globals(code_obj):
        """Returns a set of the global names accessed by a code object."""
        dissed = disassemble(code_obj)
        lambdas = set()
        found = set()
        for entry in dissed:
            if entry[0]=='LOAD_GLOBAL':
                found.add(entry[-1])
            elif entry[0]=='LOAD_CONST':
                const = entry[-1]
                if const not in lambdas and hasattr(const,'co_code'):
                    lambdas.add(const)
                    found.update(get_accessed_globals(const))
        return found

@aspect_import_mut
def run(*vargs, **kwargs):
    co = kwargs['module'].foo.func_code
    bytecode = Bytecode(co)
    inst = bytecode.decompile()

    bytecode.pretty_print(inst)
    print
    pprint.pprint(bytecode.disassemble())

if __name__ == "__main__":
    run()
    sys.exit(0)

