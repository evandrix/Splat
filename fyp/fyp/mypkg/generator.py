#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import re
import dis
import types
import py
import inspect
import byteplay
import random
import decorator
import tracer
import trace
import opcode as op
from cStringIO import StringIO
from pprint import pprint
from constants import *
from collections import defaultdict
from metaclass       import *
from template_writer import *

def test_function(GLOBALS, function):
    assert callable(function)
    args, varargs, keywords, defaults = inspect.getargspec(function)
    module_name = inspect.getmodule(function).__name__
    module_path = inspect.getmodule(function).__file__
    pkg_path = os.path.abspath(GLOBALS['pkg_path'])
    dirname, filename = os.path.split(module_path)
    module_name, ext  = os.path.splitext(filename)
    submodule_key = dirname[len(pkg_path)+1:]+'/'+module_name

    fn_cfg_nodes = GLOBALS['graph_fn_cfg'][function.func_name]['nodes']
    fn_cfg_edges = GLOBALS['graph_fn_cfg'][function.func_name]['edges']
    fn_cfg_usages, fn_cfg_jmps, fn_cfg_lbls = defaultdict(list), [], []
    for node_id, value in fn_cfg_nodes.iteritems():
        (opcode, arg), node = value
        if node.get_fillcolor() == graph_node_colors['PINK']:
            next_node = fn_cfg_nodes[node_id+1]
            if next_node:
                (next_node_opcode, next_node_arg), _ = next_node
                if next_node_opcode == byteplay.LOAD_ATTR:
                    fn_cfg_usages[arg].append(next_node_arg)
        elif node.get_fillcolor() == graph_node_colors['GREEN'] \
            or node.get_fillcolor() == graph_node_colors['ORANGE']:
            fn_cfg_jmps.append((node_id, (opcode, arg), node))
        elif node.get_fillcolor() == graph_node_colors['LIGHT_BLUE']:
            fn_cfg_lbls.append((node_id, (opcode, arg), node))
    fn_cls = [b.get_name().replace(u"\u200B",'') \
        for a,b in GLOBALS['graph_fn_cls']['edges'] \
        if a.get_name() == function.func_name]
    module = GLOBALS['modules'][submodule_key]
    pyc    = GLOBALS['pyc_info'][submodule_key]
    constants = [ c for c in function.func_code.co_consts if c ]
    dependent_fns = []
    for a,b in GLOBALS['graph_fn_fn']['edges']:
        if a.get_name() == function.func_name:
            for f in GLOBALS['dependent_fn'][function.func_name]:
                if f.name == b.get_name():
                    dependent_fns.append(f)
    co = byteplay.Code.from_code(function.func_code)
    used_args = set([arg for opcode,arg in co.code if opcode in reserved_loads and isinstance(arg, basestring) and arg in inspect.getargspec(function).args])

    # ACTUAL TESTING WORK #
    tests = []
    # 1. all Nones
    arglist = [None] * len(args)
    assert len(arglist) == len(args)
    print "[test-all-Nones]:\t",
    try:
        return_value = function(*arglist)
    except Exception as e:
        assert isinstance(e, Exception)
        tests.append(UnitTestObject(
            function.__name__, "all_Nones",
            [ "self.assertRaises(%s, %s, *%s)" % \
                (e.__class__.__name__, 'self.module.'+function.__name__, arglist) ]
        ))
    else:
        # function executed successfully with Nones supplied
        # assert that return value is equal (also if None)
        statements = []
        statements.append("self.assertNotRaises(%s, *%s)" % \
            ('self.module.'+function.__name__, arglist))
        if return_value is None:
            statements.append("self.assertIsNone(%s(*%s))" % \
            ('self.module.'+function.__name__, arglist))
        else:
            statements.append("self.assertEqual(%s(*%s), %r, %s)" % \
                ('self.module.'+function.__name__, arglist, return_value,
                'function return value not equal'))
        tests.append(UnitTestObject(
            'self.module.'+function.__name__, "all_Nones", statements))
    print
    ###
    GLOBALS['unittest_cache'][function.func_name] \
        = {'module': submodule_key, 'testcases': tests}

    if False:
        print '=== fn_cfg_nodes ==='
        pprint(sorted([(a,b) \
            for a,b in GLOBALS['graph_fn_cfg'][function.func_name]['nodes'].iteritems()]))
        print '=== fn_cfg_edges ==='
        pprint(sorted([(a.get_name(), b.get_name()) \
            for a,b in GLOBALS['graph_fn_cfg'][function.func_name]['edges']]))
        temp = {}
        for k,v in fn_cfg_usages.iteritems():
            temp[k] = v
        print '=== fn_cfg_usages ==='
        pprint(temp)
        print '=== fn_cfg_jmps ==='
        pprint(fn_cfg_jmps)
        print '=== fn_cfg_lbls ==='
        pprint(fn_cfg_lbls)
        print '=== fn_cls ==='
        pprint(fn_cls)
        print '=== constants ==='
        pprint(constants)
        print '=== dependent functions ==='
        pprint(sorted(dependent_fns))
        print '=== used arguments ==='
        pprint(sorted(used_args))

def main(GLOBALS):
    print 'recursive functions:', GLOBALS['recursive_functions']
    print '[ISOLATED]'
    for function in GLOBALS['function_test_order']['isolated']:
        print 'Testing %s...' % function.func_name
        test_function(GLOBALS, function)
    print '[L]'
    for function in GLOBALS['function_test_order']['L']:
        print 'Testing %s...' % function.func_name
        test_function(GLOBALS, function)

