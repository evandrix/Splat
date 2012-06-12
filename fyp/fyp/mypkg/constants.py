import imp
import inspect
import byteplay
from blessings import Terminal
###
module_types = {
    imp.PY_SOURCE: 'source',
    imp.PY_COMPILED: 'compiled',
    imp.C_EXTENSION: 'extension',
    imp.PY_RESOURCE: 'resource',
    imp.PKG_DIRECTORY: 'pkg_path',
}
inspect_types = {
    'class': inspect.isclass,
    'function': inspect.isfunction,
#    'generator_fn': inspect.isgeneratorfunction,
#    'method': inspect.ismethod,
#    'builtin': inspect.isbuiltin,
#    'routine': inspect.isroutine,
#    'module': inspect.ismodule,
#    'abstract': inspect.isabstract,
#    'frame': inspect.isframe,
#    'code': inspect.iscode,
#    'generator': inspect.isgenerator,
#    'tb': inspect.istraceback,
#    'data_descriptor': inspect.isdatadescriptor,
#    'method_descriptor': inspect.ismethoddescriptor,
#    'getset_descriptor': inspect.isgetsetdescriptor,
#    'member_descriptor': inspect.ismemberdescriptor,
}
###
reserved_stores = [
    byteplay.STORE_ATTR,
    byteplay.STORE_FAST,
    byteplay.STORE_MAP,
    byteplay.STORE_SLICE_0,
    byteplay.STORE_SLICE_1,
    byteplay.STORE_SLICE_2,
    byteplay.STORE_SLICE_3,
    byteplay.STORE_SUBSCR,
    byteplay.STORE_DEREF,
    byteplay.STORE_GLOBAL,
    byteplay.STORE_NAME,
]
LOAD_SLICE  = 'LOAD_SLICE'
LOAD_OBJ_FN = 'LOAD_OBJ_FN'
LOAD_LIST   = 'LOAD_LIST'
reserved_loads = [
    byteplay.LOAD_ATTR,
    byteplay.LOAD_CLOSURE,
    byteplay.LOAD_CONST,
    byteplay.LOAD_DEREF,
    byteplay.LOAD_FAST,
    byteplay.LOAD_GLOBAL,
    byteplay.LOAD_LOCALS,
    byteplay.LOAD_NAME,
    LOAD_SLICE, # custom
    LOAD_OBJ_FN,
    LOAD_LIST,
]
reserved_binary = [
     byteplay.BINARY_POWER,
     byteplay.BINARY_MULTIPLY,
     byteplay.BINARY_DIVIDE,
     byteplay.BINARY_MODULO,
     byteplay.BINARY_ADD,
     byteplay.BINARY_SUBTRACT,
     byteplay.BINARY_SUBSCR,
     byteplay.BINARY_FLOOR_DIVIDE,
     byteplay.BINARY_TRUE_DIVIDE,
     byteplay.BINARY_LSHIFT,
     byteplay.BINARY_RSHIFT,
     byteplay.BINARY_AND,
     byteplay.BINARY_XOR,
     byteplay.BINARY_OR,
]
reserved_slices = {
    byteplay.SLICE_0: 0,
    byteplay.SLICE_1: 1,
    byteplay.SLICE_2: 1,
    byteplay.SLICE_3: 2,
    byteplay.BUILD_SLICE: None,
}
###
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
###
MAX_ITERATIONS  = 2**10
def f_noarg(): return                   # Mock parameters
def f_varg(*args, **kwargs): return
PARAM_VALUE_SEQ = [ None, 0, 0.0, '', f_noarg, f_varg ]
class ClassType:    OLD, NEW = range(2)
###
graph_node_colors = {
    'PINK':         "#EE82EE",
    'LIGHT_BLUE':   "#87CEFA",
    'GREEN':        "#00FF7F",
    'ORANGE':       "#F4A460",
}
###
is_primitive = lambda var: isinstance(var, \
            (int, float, long, complex, basestring, \
            bool, tuple, list, dict))

