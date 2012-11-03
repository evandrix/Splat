#!/usr/bin/env python
#-*- coding: utf-8 -*-

import __builtin__
import logging
import os
import sys
import dis
import new
import byteplay
import pydot
import pickle
import types
import inspect
import random
import time
import timeit
import uuid
import pystache
import codecs
import markupsafe
import mypkg.template_writer
from collections import defaultdict
from pprint import pprint
from mypkg.constants import *

from opcode import opmap, HAVE_ARGUMENT, EXTENDED_ARG
from types import FunctionType, ClassType, CodeType
globals().update(opmap)

def initLogging(default_level = logging.INFO, stdout_wrapper = None, \
                stderr_wrapper = None):
    """
        Initialize the default logging subsystem
    """
    root_logger = logging.getLogger()
    strm_out = logging.StreamHandler(sys.__stdout__)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s')
    strm_out.setFormatter(formatter)
    root_logger.setLevel(default_level)
    root_logger.addHandler(strm_out)
    if stdout_wrapper:
        sys.stdout = stdout_wrapper
    if stderr_wrapper:
        sys.stderr = stderr_wrapper
    return root_logger

def get_color(bytecode, current_node):
    opcode, arg = bytecode
    if isinstance(opcode, byteplay.Label):
        return graph_node_colors['LIGHT_BLUE']
    elif opcode in reserved_rel:
        return graph_node_colors['GREEN']
    elif opcode in reserved_abs:
        return graph_node_colors['ORANGE']
    return None

def build_graph(bytecode):
    node_list, edge_list = defaultdict(pydot.Node), set()
    if bytecode:
        first = bytecode[0]
        first_opcode, first_arg = first
        value = first_opcode if any(isinstance(v, byteplay.Label) for v in first) else first
        node = pydot.Node(str((0, value)), style="filled")
        node_list[0] = (first, node)
        if len(bytecode) > 1:
            from_labels, to_labels = defaultdict(set), defaultdict(set)
            for index, (opcode, arg) in enumerate(bytecode[1:]):
                current_val = (opcode,) if any(isinstance(v, byteplay.Label) for v in [opcode,arg]) else (opcode,arg)
                current_node = pydot.Node( str((index+1,)+current_val) )
                node_list[index+1] = ((opcode,arg), current_node)
                if isinstance(arg, byteplay.Label):
                    from_labels[arg].add((index+1, current_node))
                elif isinstance(opcode, byteplay.Label):
                    to_labels[opcode] = (index+1, current_node)
                edge_list.add( (node, current_node) )
                node = current_node
            for label in from_labels.keys():
                for entry in from_labels[label]:
                    from_index, from_node = entry
                    to_index,   to_node   = to_labels[label]
                    if to_index - from_index != 1: # jumps
                        edge_list.add( (from_node, to_node) )

        # color nodes
        for node_id, value in node_list.iteritems():
            bytecode, node = value
            color = get_color(bytecode, node)
            if color:
                node.set_style("filled")
                node.set_fillcolor(color)
    return node_list, edge_list

def find_all_paths(src, dest, nodes, edges, path=[]):
    assert isinstance(src, pydot.Node) and isinstance(dest, pydot.Node)
    assert isinstance(nodes, defaultdict) and isinstance(edges, set)
    path = path + [src]
    if src == dest: return [path]
    paths = []
    for child in [e2 for e1,e2 in edges if e1 == src]:
        if child not in path:
            child_paths = find_all_paths(child, dest, nodes, edges, path)
            for child_path in child_paths:
                paths.append(child_path)
    return paths

def node_to_index(node_list, node):
    for i, (_, the_node) in node_list.iteritems():
        if the_node == node:
            return i
    raise RuntimeError # not found
def node_to_bytecode(node_list, node):
    for i, (bc, the_node) in node_list.iteritems():
        if the_node == node:
            return bc
    raise RuntimeError # not found

def all_paths_for_function(function):
    co = byteplay.Code.from_code(function.func_code)
    bytecode = [(a,b) for a,b in co.code if a != byteplay.SetLineno]

    # sanity check
    pattern = [
        { 'before': [
            (byteplay.RETURN_VALUE, None),
            (byteplay.LOAD_CONST, None),
            (byteplay.RETURN_VALUE, None)
        ], 'after': [(byteplay.RETURN_VALUE, None)] }
    ]
    for item in pattern:
        if bytecode[-len(item['before']):] == item['before']:
            bytecode = bytecode[:-len(item['before'])] + item['after']
    print 'bytecode', bytecode

    if not os.path.exists('%s-pngs' % function.func_name):
        os.makedirs('%s-pngs' % function.func_name)

    node_list, edge_list = build_graph(bytecode)
    graph = pydot.Dot('%s_org'%function.func_name, graph_type='digraph')
    for node_index in node_list:
        bytecode, node = node_list[node_index]
        graph.add_node( node )
    for start,end in edge_list:
        opcode, arg = node_to_bytecode(node_list, start)
        if opcode != byteplay.RETURN_VALUE:
            graph.add_edge( pydot.Edge(start, end) )
    graph.write_png('%s-pngs/%s-0-original.png'%(function.func_name,function.func_name))
    all_node_list = node_list
    all_edge_list = edge_list

    new_edge_list = set()
    for start,end in edge_list:
        opcode, arg = node_to_bytecode(node_list, start)
        if opcode != byteplay.RETURN_VALUE:
            new_edge_list.add( (start,end) )

    start, end = min(node_list.keys()), max(node_list.keys())
    print "Finding all paths from start#%d to end#%d" %(start,end)
#        print "in graph", node_list, edge_list
    _, start_node = node_list[start]
    _, end_node = node_list[end]

    all_paths, result = [], defaultdict(list)
    for i, r in enumerate([node for index, ((opcode,arg), node) in node_list.iteritems() if opcode == byteplay.RETURN_VALUE]):
        print 'target end node =', node_to_index(node_list, r)
        for j, p in enumerate(find_all_paths(start_node, r, node_list, new_edge_list)):
            all_paths.append(p)

            edges_subset = []
            graph = pydot.Dot(function.func_name, graph_type='digraph')
            for j, node in enumerate(p):
                graph.add_node( node )
            for j, node in enumerate(p):
                if j+1 < len(p):
                    opcode, arg = node_to_bytecode(node_list, p[j])
                    if opcode != byteplay.RETURN_VALUE:
                        edges_subset.append( (p[j], p[j+1]) )
                        graph.add_edge( pydot.Edge(p[j], p[j+1]) )
            #graph.write_png('%s-pngs/%s-%d-path-subset.png' % (function.func_name,function.func_name,len(all_paths)))
            print 'path#%d:'%len(all_paths), map(lambda n: node_to_index(node_list, n), p)

            graph = pydot.Dot(function.func_name, graph_type='digraph')
            for node_index in node_list:
                bytecode, node = node_list[node_index]
                graph.add_node( node )
            for start,end in edge_list:
                opcode, arg = node_to_bytecode(node_list, start)
                if opcode != byteplay.RETURN_VALUE:
                    the_edge = pydot.Edge(start, end)
                    if (start,end) in edges_subset:
                        the_edge.set_color("red")
                    graph.add_edge( the_edge )

            graph.write_png('%s-pngs/%s-%d-path-highlight.png' % (function.func_name,function.func_name,len(all_paths)))

            result[node_to_index(node_list, r)].append(map(lambda n: node_to_bytecode(node_list, n), p))
    print "Total: %d paths discovered" % len(all_paths)
    return result

BYTECODE_LIST = []
def tracer(frame, event, arg):
    global BYTECODE_LIST

    co       = frame.f_code
    lineno   = frame.f_lineno
    filename = co.co_filename
    name     = co.co_name
    the_locals = frame.f_locals
    varnames   = co.co_varnames[:co.co_argcount]
#    print co,lineno,filename,name,the_locals,varnames

    if event == 'call':
        return tracer
    elif event == 'line':
        cb = byteplay.Code.from_code(co)
        code_fragment = []
        take = False
        for opcode, arg in cb.code:
            if opcode == byteplay.SetLineno:
                take = (arg == lineno)
            elif take:
                code_fragment.append((opcode, arg))
        BYTECODE_LIST.extend(code_fragment)

def main():
    global BYTECODE_LIST
    initLogging()

    import absolute
    function = absolute.absolute
    # debug, info, warning, error, critical
    logging.info('function: ' + str(function.func_name))
    all_paths = all_paths_for_function(function)
    MAX_ITERATIONS = 2**10
    SYS_MININT = -sys.maxint-1
    int_intervals = [
        (SYS_MININT,SYS_MININT/2),
        (SYS_MININT/2,0),
        (-2**10,0),
        (0,0),
        (0,2**10),
        (0,sys.maxint/2),
        (sys.maxint/2,sys.maxint)]
    iteration_no, coverage, total, test_objects = 0, 0, len(all_paths.keys()), []
    start_time = time.time()
    while coverage < total:
        # num arguments to be given known using inspect
        num_args = len(inspect.getargspec(function).args)

        arglist = []
        for _ in xrange(num_args):
            low, high = int_intervals[random.randint(0,len(int_intervals)-1)]
            arglist.append(random.randint(low,high))

        BYTECODE_LIST = []
        sys.settrace(tracer)
        return_value = function(*arglist)
        sys.settrace(None)
        test_objects.append(mypkg.template_writer.UnitTestObject(
            function.func_name,
            str(uuid.uuid4()).replace('-',''),
            ['self.assertEqual(self.module.%s(*%s), %s)' \
                % (function.func_name,arglist,return_value)])
        )
        BYTECODE_LIST = [(opcode,arg) for opcode,arg in BYTECODE_LIST if not isinstance(opcode, byteplay.Label) and not isinstance(arg, byteplay.Label)]
        # sanity check
        pattern = [
            { 'before': [
                (byteplay.RETURN_VALUE, None),
                (byteplay.LOAD_CONST, None),
                (byteplay.RETURN_VALUE, None)
            ], 'after': [(byteplay.RETURN_VALUE, None)] }
        ]
        for item in pattern:
            if BYTECODE_LIST[-len(item['before']):] == item['before']:
                BYTECODE_LIST = BYTECODE_LIST[:-len(item['before'])] + item['after']

        if len([ x for x in BYTECODE_LIST if x == (byteplay.RETURN_VALUE, None)]) > 1:
            BYTECODE_LIST = BYTECODE_LIST[:BYTECODE_LIST.index((byteplay.RETURN_VALUE, None))+1]

        found = False
        for end_node, paths in all_paths.iteritems():
            for p in paths:
                p = [(opcode,arg) for opcode,arg in p if not isinstance(opcode, byteplay.Label) and not isinstance(arg, byteplay.Label)]

                if p == BYTECODE_LIST:
                    del all_paths[end_node]
                    coverage += 1
                    print 'iteration#%d: (time elapsed: %.3f sec) Coverage ='%(iteration_no,time.time()-start_time), str(100*coverage/float(total))+'%', arglist, return_value
                    found = True
                    break
            if found:
                break

        iteration_no += 1
        if coverage == total:
            print 'Full coverage achieved after %d iterations. Stopping...'%(iteration_no)
            break

    template_file = "mypkg/test_template_py.mustache"
    with open(template_file, "rU") as template:
        template = template.read()
    context = {
        'module_name': absolute.absolute.func_name,
        'base_import_path': os.getcwd(),
        'module_path': os.getcwd(),
        'all_imports': None,
        'all_tests':   test_objects
    }
    data = pystache.render(template, context)
    with codecs.open('test_%s.py'%absolute.absolute.func_name, "w", "utf-8") as fout:
        if isinstance(data, markupsafe.Markup):
            print >> fout, data.unescape() \
                .replace("&#34;",'"').replace("&#39;","'")
        else:
            print >> fout, data
    sys.exit(0)
    sys.exit(0)
#############################################################################
    for i, path in enumerate(all_paths):
        new_path = []
        for j, (opcode, arg) in enumerate(path):
            if isinstance(opcode, byteplay.Label) or isinstance(arg, byteplay.Label):
                continue
            new_path.append( (opcode,arg) )
            if opcode == byteplay.RETURN_VALUE:
                break
        all_paths[i] = new_path
        print 'path#%d:'%i, new_path
#############################################################################
    # optimise branch/path coverage
    # idea 1:
    #   - enumerate through given range
    #   - trace function execution for each element
    #   - examine resulting bytecode_list, compare against known paths
    #   - unit test assert on return value
    coverage, total, test_objects = 0, len(all_paths), []
    MAX_ITERATIONS = 2**10
    # Interval random testing! #
    for N, i in enumerate([random.randint(-sys.maxint-1,sys.maxint) for r in xrange(MAX_ITERATIONS)] + [-sys.maxint-1, (-sys.maxint-1)/2, 0, sys.maxint/2, sys.maxint]):
        BYTECODE_LIST = []
        # num arguments to be given known using inspect
        num_args = len(inspect.getargspec(absolute.absolute).args)
        arglist  = [i] * num_args   # TODO: duplicate args to correct length for now
        sys.settrace(tracer)
        return_value = absolute.absolute(*arglist)
        sys.settrace(None)
        test_objects.append(mypkg.template_writer.UnitTestObject(
            absolute.absolute.func_name,
            str(uuid.uuid4()).replace('-',''),
            ['self.assertEqual(self.module.absolute(*%s), %s)' \
                % (arglist, return_value)])
        )
        bytecode_list = [(opcode,arg) for (opcode,arg) in BYTECODE_LIST if not isinstance(opcode, byteplay.Label)]
        for j,p in enumerate(all_paths):
            if p == bytecode_list:
                del all_paths[j]
                coverage += 1
                print 'Coverage =', str(100*coverage/float(total))+'%'
        if coverage == total:
            print 'Full coverage achieved in %d iterations. Stopping...' % N
            break

    template_file = "test_template_py.mustache"
    with open(template_file, "rU") as template:
        template = template.read()
    context = {
        'module_name': absolute.absolute.func_name,
        'base_import_path': os.getcwd(),
        'module_path': os.getcwd(),
        'all_imports': None,
        'all_tests':   test_objects
    }
    data = pystache.render(template, context)
    with codecs.open('test_%s.py'%absolute.absolute.func_name, "w", "utf-8") as fout:
        if isinstance(data, markupsafe.Markup):
            print >> fout, data.unescape() \
                .replace("&#34;",'"').replace("&#39;","'")
        else:
            print >> fout, data
    sys.exit(0)
#############################################################################
        # eval/exec() version
#        return_value = eval(code, context)  # exec discards return value
#        del context['__builtins__']
#        print "stack frame ID =", str(hex(id(sys._getframe())))
#        stack = inspect.stack()
#        print context #stack[0][0].f_globals['context']
#############################################################################
    # idea 2: take segment of bytecode up to first jump, ie. 0-6
    # bytecode manipulation
#    code = compile(absolute.absolute.func_code, '<string>', 'exec')
    context = { v:0 for v in inspect.getargspec(absolute.absolute).args }
    # using byteplay: given initial state dict, manipulate bytecode list
    co = byteplay.Code.from_code(absolute.absolute.func_code)
    co.code = [ c for c in co.code if c[0] != byteplay.SetLineno ]
    co.args = ()    # remove function arguments
    for i,c in enumerate(co.code):
        op, arg = c
        if op == byteplay.STORE_FAST:   # un-scope variables
            op = byteplay.STORE_GLOBAL
        elif op == byteplay.LOAD_FAST:
            op = byteplay.LOAD_GLOBAL
        elif op == byteplay.INPLACE_ADD:
            op = byteplay.INPLACE_SUBTRACT
        co.code[i] = (op, arg)
    code = co.to_code()
#    <the_function>.__code__ = code
    # method
    # 1. function -> byteplay code object
    # 2. modify bytecode object list as necessary
    # 3. ERROR on co.to_code()! (list -> code object)
    #   3a. new types.CodeType -> FunctionType object (byte manipulation)
#   modify bytes in bytecode directly
#    ff = <the_function>.func_code
#    new_lnotab = "\x01\x01" * (len(code.co_code)-1)
#    codestr = ''.join(map(chr, newcode))
#    <the_function>.func_code = types.CodeType(ff.co_argcount, ff.co_nlocals,
#                              ff.co_stacksize, ff.co_flags,
#                              '\x01\x00\x01\x00\x14S',    # code.co_code
#                              ff.co_consts,               # tuple(newconsts)
#                              ff.co_names, ff.co_varnames,
#                              ff.co_filename, ff.co_name, ff.co_firstlineno,
#                              ff.co_lnotab, ff.co_freevars, ff.co_cellvars)
#    print ''.join( [ "\\x%02X" % ord( x ) for x in code.co_code ] ).strip()
    #       - pickle to serialise
#    co_tup=[co.co_argcount,co.co_nlocals, co.co_stacksize,co.co_flags,
#    co.co_code,co.co_consts,co.co_names,co.co_varnames,co.co_filename,
#    co.co_name,co.co_firstlineno,co.co_lnotab]
#    s = pickle.dumps(co_tup)
#    r = pickle.loads(s)
#    f = new.code(r[0],r[1],r[2],r[3],r[4],r[5],r[6],r[7],r[8],r[9],r[10],r[11])
#    exec(f)
    #   3b. reconstruct using peak.util.Assembler (1-to-1 byteplay translation)
# using peak.util.assembler
# c = Code()
# block = Label()
# loop = Label()
# else_ = Label()
# c(
#      block.SETUP_LOOP,
#          5,      # initial setup - this could be a GET_ITER instead
#      loop,
#          else_.JUMP_IF_FALSE,        # while x:
#          1, Code.BINARY_SUBTRACT,    #     x -= 1
#          loop.CONTINUE_LOOP,
#      else_,                          # else:
#          Code.POP_TOP,
#      block.POP_BLOCK,
#          Return(42),                 #     return 42
#      block,
#      Return()
# )
# convert from peak.util.assembler to byteplay
# x = Code()
# for i, c in enumerate(co.code):
#     op, arg = c
#     if op == byteplay.LOAD_GLOBAL:
#         x.LOAD_GLOBAL(arg)
#     elif op == byteplay.CALL_FUNCTION:
#         x.CALL_FUNCTION(arg)
    #   3c. eval(code object, {}) - can't do this if co.to_code() does not work! can't trace through bytecode statement execution either!

if __name__ == "__main__":
    main()
