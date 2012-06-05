from constants import *
import inspect
import pydot

# bytecode Function data model
class Function(object):
    def __init__(self, num_args):
        self.name = None
        self.num_args = num_args
        self.args = []
    def __repr__(self):
        my_name = self.name
        if not isinstance(self.name, basestring):
            my_name = '.'.join(map(str,self.name))
        if self.args:
            return "%s(%s)" %(my_name,','.join(map(str,self.args)))
        else:
            return "%s()" %(my_name)

def write_graph(GLOBALS, globals_key, graphname, suffix, pred_node, pred_edge):
    basename = GLOBALS['basename']
    graph_nodes = GLOBALS[globals_key]['nodes']
    graph_edges = GLOBALS[globals_key]['edges']

    graph = pydot.Dot(graphname, graph_type='digraph')
    for node in graph_nodes:
        if pred_node(node):
            graph.add_node( graph_nodes[node] )
    for start,end in graph_edges:
        if pred_edge(start, end):
            graph.add_edge( pydot.Edge(start, end) )

    # without class member functions
    if not graph.get_node_list() and not graph.get_edge_list():
        pass
    elif not graph.get_edge_list():
        graph.write_png('%s_%s.png' % (basename,suffix), prog='neato')
    else:
        graph.write_png('%s_%s.png' % (basename,suffix))

def debug(GLOBALS):
    all_classes = GLOBALS['all_classes']
    all_functions = GLOBALS['all_functions']

    write_graph(GLOBALS, 'graph_fn_fn', 'function dependency', 'fns_nocls',
        lambda node: '.' not in node,
        lambda start,end: '.' not in start.get_name() and '.' not in end.get_name())
    write_graph(GLOBALS, 'graph_fn_fn', 'function dependency', 'fns_cls',
        lambda node: '.' in node,
        lambda start,end: '.' in start.get_name() or '.' in end.get_name())

    write_graph(GLOBALS, 'graph_fn_cls', 'class dependency', 'cls', lambda _: True, lambda s,e: True)

def main(GLOBALS):
    all_classes = GLOBALS['all_classes']
    all_functions = GLOBALS['all_functions']

    print "(IIa): function -> function"
    graph_nodes, graph_edges = {}, set()
    for name, fn in GLOBALS['all_functions'].iteritems():
        co = byteplay.Code.from_code(fn.func_code)
        func_calls = []
        func_stack = []
        # find rightmost occurrence of (CALL_FUNCTION, _)
        end_index = -1
        for i,x in enumerate(co.code[::-1]):
            opcode, arg = x
            if opcode == byteplay.CALL_FUNCTION:
                end_index = len(co.code) - i
                break
        if end_index < 1:   continue
        bytecode_list = [(a,b) for a,b in co.code[:end_index] if a != byteplay.SetLineno]
        # transform bytecode - merge into single LOAD_* instr
        affected_instrs = reserved_slices.keys() + reserved_binary + [byteplay.LOAD_ATTR, byteplay.BUILD_TUPLE]
        for i,(opcode, arg) in enumerate(bytecode_list):
            if opcode not in affected_instrs:
                continue
            the_offset, the_opcode = None, None
            if opcode == byteplay.LOAD_ATTR:
                if i-1 > 0 and bytecode_list[i-1][0] == byteplay.BUILD_MAP:
                    pass
                else:
                    new_bytecode = (LOAD_OBJ_FN,
                        tuple([v[1] for v in bytecode_list[i-1:i+1]]))
                    del bytecode_list[i-1:i+1]
                    bytecode_list.insert(i-1, new_bytecode)
                    end_index -= 1
                continue
            elif opcode == byteplay.BUILD_TUPLE:
                new_bytecode = (byteplay.BUILD_TUPLE,
                    tuple([v[1] for v in bytecode_list[i-2:i]]))
                del bytecode_list[i-2:i]
                bytecode_list.insert(i-2, new_bytecode)
                end_index -= 2
                continue
            if opcode in reserved_slices:
                the_opcode = LOAD_SLICE
                the_offset = reserved_slices[opcode]
                if opcode == byteplay.BUILD_SLICE:
                    the_offset = arg
            elif opcode in reserved_binary:
                the_opcode = opcode
                the_offset = 1
            new_bytecode = (the_opcode,
                    tuple([v[1] for v in bytecode_list[i-the_offset-1:i]]))
            del bytecode_list[i-the_offset-1:i+1]
            bytecode_list.insert(i-the_offset-1, new_bytecode)
            end_index -= the_offset + 1
        # actual parsing work
        bytecode_list = bytecode_list[::-1]
        for i,(opcode, arg) in enumerate(bytecode_list):
            if opcode == byteplay.CALL_FUNCTION:
                if i+1 < len(bytecode_list) and bytecode_list[i+1][0] == byteplay.STORE_MAP:
                    continue
                else:
                    func_stack.append(Function(arg))
            elif opcode in reserved_loads+reserved_binary+[LOAD_OBJ_FN]:
                if func_stack:
                    last_func = func_stack[-1]
                    if len(last_func.args) < last_func.num_args:
                        last_func.args.insert(0, arg)
                    elif len(last_func.args) == last_func.num_args:
                        last_func.name = arg
                        while len(func_stack) > 1 and last_func.name and len(last_func.args) == last_func.num_args:
                            func_stack[-2].args.insert(0, last_func)
                            func_stack = func_stack[:-1]
                        if len(func_stack) == 1 and func_stack[0].name and len(func_stack[0].args) == func_stack[0].num_args:
                            # not a class constructor
                            if func_stack[0].name not in all_classes:
                                func_calls.append(func_stack[0])
                            func_stack = []
        # output - with sanity check on #args
        # TODO: sanity check on validity of #args on obj fn calls
        #   - need to be able to determine obj/classdef from bytecode
        fn_arglen = [(f_name,len(inspect.getargspec(f_fn).args)) for f_name,f_fn in all_functions.iteritems()]
        called_fns = set()
        for called_f in func_calls:
            assert isinstance(called_f, Function)
            # for now, assume all obj member fn calls are VALID
            if (called_f.name, called_f.num_args) in fn_arglen \
                or isinstance(called_f.name, tuple):
                called_fns.add((called_f.name, called_f.num_args))
                # draw edge to represent function usage
                dest_fn_name = called_f.name if isinstance(called_f.name, basestring) else '.'.join(map(str,called_f.name))
                if name not in graph_nodes:
                    graph_nodes[name] = pydot.Node(name)
                if dest_fn_name not in graph_nodes:
                    graph_nodes[dest_fn_name] = pydot.Node(dest_fn_name)
                graph_edges.add( (graph_nodes[name], graph_nodes[dest_fn_name]) )
    GLOBALS['graph_fn_fn']['nodes'] = graph_nodes
    GLOBALS['graph_fn_fn']['edges'] = graph_edges

    print "(IIb): function -> class"
    graph_nodes, graph_edges = {}, set()
    graph = pydot.Dot('class dependency', graph_type='digraph')
    for name, fn in GLOBALS['all_functions'].iteritems():
        co = byteplay.Code.from_code(fn.func_code)
        usage_class = set()
        for opcode, arg in co.code:
            if opcode in reserved_loads and isinstance(arg, basestring) and not arg.startswith('_'):
                if arg in all_classes:
                    usage_class.add(all_classes[arg])
        if usage_class:
            for c in usage_class:
                graph_nodes[name] = pydot.Node(name)
                graph_nodes[c] = pydot.Node(c.__name__+u"\u200B")
                graph_edges.add( (graph_nodes[name], graph_nodes[c]) )
    GLOBALS['graph_fn_cls']['nodes'] = graph_nodes
    GLOBALS['graph_fn_cls']['edges'] = graph_edges
