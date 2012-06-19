import os
import sys
import pydot
import dis
import byteplay
from pprint import pprint
from constants import *
from collections import defaultdict

def get_color(bytecode, current_node, function_globals):
    opcode, arg = bytecode
    if opcode in reserved_loads \
        and isinstance(arg, basestring) and arg in function_globals:
        return graph_node_colors['PINK']
    elif isinstance(opcode, byteplay.Label):
        return graph_node_colors['LIGHT_BLUE']
    elif opcode in reserved_rel:
        return graph_node_colors['GREEN']
    elif opcode in reserved_abs:
        return graph_node_colors['ORANGE']
    return None

def write_graph(GLOBALS, graph_nodes, graph_edges, function_name, function_globals):
    graph = pydot.Dot(function_name, graph_type='digraph')
    for node_index in graph_nodes:
        bytecode, node = graph_nodes[node_index]
        graph.add_node( node )
    for start,end in graph_edges:
        graph.add_edge( pydot.Edge(start, end) )
    if not os.path.exists('%s-pngs' % GLOBALS['basename']):
        os.makedirs('%s-pngs' % GLOBALS['basename'])
    graph.write_png('%s-pngs/%s.png' % (GLOBALS['basename'],function_name))

def collapse_graph(GLOBALS, node_list, edge_list, function_globals):
    new_node_list, new_edge_list = defaultdict(pydot.Node), set()
    ctrl_pts = set()
    for node_index in node_list:
        bytecode, node = node_list[node_index]
        if get_color(bytecode, node, function_globals):
            new_node_list[node_index] = (bytecode, node)
            ctrl_pts.add(node)
    for node_index in node_list:
        bytecode, node = node_list[node_index]
        # immediate edge from/to control point
        if node not in ctrl_pts:
            if [1 for start,end in edge_list if start in ctrl_pts and end == node]:
                new_edge_list.update([(start,end) for start,end in edge_list if start in ctrl_pts and end == node])

                # search for segment ending
                # assert (no branching from start-end & end links to ctrl pt)
                _, last_node = node_list[max(node_list.keys())]
                prev_node, current_node = None, node
                while current_node not in ctrl_pts and current_node != last_node:
                    for start,end in edge_list:
                        if start == current_node:
                            prev_node = current_node
                            current_node = end
                            break
                end_node_index = node_index
                for index in node_list:
                    _, n = node_list[index]
                    if n == prev_node:
                        end_node_index = index
                        break
                for start,end in edge_list:
                    if start == prev_node:
                        # transfer edge from end to start of segment
                        new_edge_list.add( (node, end) )

                if node_index == end_node_index:
                    node.set_name('(%d, %s, %s)' %(node_index, bytecode[0], bytecode[1]))
                else:
                    node.set_name('(%d-%d, ...)' %(node_index,end_node_index))
                new_node_list[node_index] = (bytecode, node)
    for start,end in edge_list:
        if start in ctrl_pts and end in ctrl_pts:
            new_edge_list.add( (start, end) )
    return new_node_list, new_edge_list

def build_graph(GLOBALS, function_name, bytecode, function_globals):
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
            color = get_color(bytecode, node, function_globals)
            if color:
                node.set_style("filled")
                node.set_fillcolor(color)
    return node_list, edge_list

def main(GLOBALS, write=False):
    all_functions = GLOBALS['all_functions']
    all_functions_len = len(all_functions)

    for i, (name, fn) in enumerate(all_functions.iteritems()):
        GLOBALS['graph_fn_cfg'][name]['fn'] = fn
        sz_status = "\r\x1b[K" \
            + "[%.2f%%] Processing function %s.%s..." \
            % (100*i/float(all_functions_len), fn.__module__, name)
        if sys.stderr.isatty():
            print >> sys.stderr, sz_status,
        co = byteplay.Code.from_code(fn.func_code)
        bytecode = [(a,b) for a,b in co.code if a != byteplay.SetLineno]
        function_globals = inspect.getargspec(fn).args
        node_list, edge_list = build_graph(GLOBALS, name, bytecode, function_globals)
        GLOBALS['graph_fn_cfg'][name]['nodes'] = node_list
        import copy
        GLOBALS['graph_fn_cfg'][name]['edges'] = edge_list #copy.deepcopy(edge_list)
        new_node_list, new_edge_list \
            = collapse_graph(GLOBALS, node_list, edge_list, function_globals)

        if new_node_list:
            if write:
                write_graph(GLOBALS, new_node_list, new_edge_list, name, function_globals)
        if node_list:
            if write:
                write_graph(GLOBALS, node_list, edge_list, name, function_globals)
    print "\r\x1b[K"

