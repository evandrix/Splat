import pydot
import dis
import byteplay
from pprint import pprint

def f1(limit):
    for i in xrange(1,limit+1):print"FizzBuzz"[i*i%3*4:8--i**4%5]or i

def f2(limit):
    print '\n'.join(['Fizz'*(not i%3) + 'Buzz'*(not i%5) or str(i) for i in xrange(1, limit+1)])

def f3(limit):
    for x in xrange(limit): print x%3/2*'Fizz'+x%5/4*'Buzz' or x+1

def f4(limit):
    for i in xrange(1, limit+1):
	    if i%3==0 and i%5==0:
		    print "FizzBuzz"
	    elif i%5==0:
		    print "Buzz"
	    elif i%3==0:
		    print "Fizz"
	    else:
		    print i

reserved_rel = [
    byteplay.FOR_ITER,
    byteplay.JUMP_FORWARD,
    byteplay.SETUP_LOOP,
    byteplay.SETUP_EXCEPT,
    byteplay.SETUP_FINALLY,
    byteplay.SETUP_WITH,
]
reserved_abs = [
    byteplay.JUMP_IF_FALSE_OR_POP,
    byteplay.JUMP_IF_TRUE_OR_POP,
    byteplay.JUMP_ABSOLUTE,
    byteplay.POP_JUMP_IF_FALSE,
    byteplay.POP_JUMP_IF_TRUE,
    byteplay.CONTINUE_LOOP,
]
reserved_loads = [
    byteplay.LOAD_ATTR,
    byteplay.LOAD_CLOSURE,
    byteplay.LOAD_CONST,
    byteplay.LOAD_DEREF,
    byteplay.LOAD_FAST,
    byteplay.LOAD_GLOBAL,
    byteplay.LOAD_LOCALS,
    byteplay.LOAD_NAME,
]
reserved_try = [
    byteplay.POP_BLOCK,
]
def color_node(opcode, arg, current_node, function_globals):
    current_node.set_style("filled")
    if opcode in reserved_rel:
        current_node.set_fillcolor("green")
    elif opcode in reserved_abs:
        current_node.set_fillcolor("#976856")
    elif opcode in reserved_loads and arg in function_globals:
        current_node.set_fillcolor("red")
    return current_node

def build_graph(function_name, function_globals, bytecode):
    graph = pydot.Dot(function_name, graph_type='digraph')

    if len(bytecode) > 0:
        value = (0,)+bytecode[0]
        if any(isinstance(v, byteplay.Label) for v in bytecode[0]):
            value = (0,bytecode[0][0])

        node = pydot.Node( str( value ), style="filled" )
        color_node(bytecode[0][0], bytecode[0][1], node, function_globals)
        graph.add_node(node)

        if len(bytecode) > 1:
            from collections import defaultdict
            from_labels = defaultdict(set)
            to_labels = defaultdict(set)

            for index, (opcode, arg) in enumerate(bytecode[1:]):
                current_node = pydot.Node( str((index+1,opcode,arg)) )
                if any(isinstance(v, byteplay.Label) for v in [opcode,arg]):
                    current_node = pydot.Node( str((index+1,opcode)) )

                color_node(opcode, arg, current_node, function_globals)

                if isinstance(arg, byteplay.Label):
                    from_labels[arg].add((index+1, current_node))
                elif isinstance(opcode, byteplay.Label):
                    to_labels[opcode] = (index+1, current_node)

                graph.add_node(current_node)
                edge = pydot.Edge(node, current_node)
                graph.add_edge(edge)
                node = current_node

            for label in from_labels.keys():
                for entry in from_labels[label]:
                    from_index, from_node = entry
                    to_index, to_node = to_labels[label]
                    if to_index - from_index != 1:
                        graph.add_edge(pydot.Edge(from_node, to_node))

        graph.write_png('%s.png' % function_name)

if __name__ == "__main__":
    for f in [f1,f2,f3,f4]:
        co = byteplay.Code.from_code(f.func_code)
        bytecode = [(a,b) for a,b in co.code if a != byteplay.SetLineno]
        #pprint(bytecode)
        build_graph(f.func_name, ['limit'], bytecode)

    from lang_all import *
    for f in [ctrl_try, ctrl_with]:
        co = byteplay.Code.from_code(f.func_code)
        bytecode = [(a,b) for a,b in co.code if a != byteplay.SetLineno]
        #pprint(bytecode)
        build_graph(f.func_name, [], bytecode)

