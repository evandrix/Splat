import sys
import time
import dis
import byteplay
import inspect
import multiprocessing
import logging
from pprint import pprint

from hanoi import *

sys.setrecursionlimit(2**10)

class ValNode(object):
    def __init__(self, bytecodes):
        self.bytecodes = bytecodes
    def __str__(self):
        return repr(self.bytecodes)

class CmpNode(object):
    def __init__(self, op, arg1, arg2):
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2
    def __str__(self):
        return "Cmp(%s, %s, %s)" % (self.op, self.arg1, self.arg2)

class CondNode(object):
    def __init__(self, node_id, jmp_node, cmp_node):
        self.node_id = node_id
        self.jmp_id, self.jmp_label = jmp_node
        self.cmp_node = cmp_node
    def __str__(self):
        return "Cond(node_id:%s, jmp_to:(%s,%s), %s)" % (self.node_id, self.jmp_id, self.jmp_label, self.cmp_node)

class RecursiveFnTester(object):
    def __init__(self, code_object):
        self.name = code_object.name
        self.code = code_object.code

    def parse(self):
        if isinstance(self.code, byteplay.CodeList):
            cleaned_code = [ (a,b) for a,b in self.code if a != byteplay.SetLineno ]
            pprint([ n for n in enumerate(cleaned_code)])
            print

            # finds first pop_jump_if label




            for i, (a,b) in enumerate(cleaned_code):
                if a == byteplay.POP_JUMP_IF_FALSE or \
                    a == byteplay.POP_JUMP_IF_TRUE:
                    jmp_label = b
                    jmp_node = i
                    break
            assert(cleaned_code[jmp_node-1][0] == byteplay.COMPARE_OP)
            cmp_op = cleaned_code[jmp_node-1][1]
            jmp_label_id = -1
            for i, (a,b) in enumerate(cleaned_code):
                if a == jmp_label:
                    jmp_label_id = i
                    break

            node1 = CondNode(jmp_node, (jmp_label_id, jmp_label), CmpNode(cmp_op,
                ValNode([(byteplay.LOAD_FAST, 'height')]),
                ValNode([(byteplay.LOAD_CONST, 0)])))

            load_cmds = [k for k,v in byteplay.opname.items() if v.startswith("LOAD_")]
            recursive_calls = [(i,a,b) for i, (a,b) in enumerate(cleaned_code) if a in load_cmds and b == self.name]
            returns = [(i,n) for i,n in enumerate(cleaned_code) if n==(byteplay.RETURN_VALUE,None)]

            print 'condition node:', node1
            print 'recursive function calls:', recursive_calls
            print 'return statements:', returns
            print

if __name__ == "__main__":
    h = Hanoi()
    co = byteplay.Code.from_code(h.hanoi.func_code)
    r = RecursiveFnTester(co)
    r.parse()

    from factorial import factorial
    co = byteplay.Code.from_code(factorial.func_code)
    RecursiveFnTester(co).parse()

