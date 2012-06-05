import sys
import dis
import byteplay
import inspect
from pprint import pprint
from peak.util.assembler import *
from peak.util.assembler import dump

def h(_,f,g):
    h(x,h(a,b,c),z)
def accessibility(graph):
    recursionlimit = getrecursionlimit()
    setrecursionlimit(max(len(graph.nodes())*2,recursionlimit))
    accessibility = {}
    for each in graph:
        access = {}
        _dfs(graph, access, 1, each)
        accessibility[each] = list(access.keys())
    setrecursionlimit(recursionlimit)
    return accessibility
def pagerank(graph, damping_factor=0.85, max_iterations=100, min_delta=0.00001):
    nodes = graph.nodes()
    graph_size = len(nodes)
    if graph_size == 0:
        return {}
    min_value = (1.0-damping_factor)/graph_size
    pagerank = dict.fromkeys(nodes, 1.0/graph_size)
    for i in range(max_iterations):
        diff = 0
        for node in nodes:
            rank = min_value
            for referring_page in graph.incidents(node):
                rank += damping_factor * pagerank[referring_page] / len(graph.neighbors(referring_page))
            diff += abs(pagerank[node] - rank)
            pagerank[node] = rank
        if diff < min_delta:
            break    
    return pagerank

co = byteplay.Code.from_code(accessibility.func_code)
co.code = [ c for c in co.code if c[0] != byteplay.SetLineno ]
pprint(co.code)
co = byteplay.Code.from_code(pagerank.func_code)
co.code = [ c for c in co.code if c[0] != byteplay.SetLineno ]
pprint(co.code)

co = byteplay.Code.from_code(h.func_code)
co.code = co.code[1:10]
co.code = [ c for c in co.code if c[0] != byteplay.SetLineno ]
co.args = ()    # remove function arguments

pprint(co.code)
#exec(co.to_code(), {})
print "stack frame (main): " + str(hex(id(sys._getframe())))
stack = inspect.stack()

x = Code()
for i,c in enumerate(co.code):
    op, arg = c
    if op == byteplay.LOAD_GLOBAL:
        x.LOAD_GLOBAL(arg)
    elif op == byteplay.CALL_FUNCTION:
        x.CALL_FUNCTION(arg)

#print stack[0][0].f_globals['mydict'], stack[0][0].f_locals
#exec(c.code(), mydict)  # exec discards the return value, so no output here
#print "mydict: { 'n':", mydict['n'], '}'

