import sys
import time
import dis
import byteplay
import inspect
import gc
import multiprocessing
import logging
import numbers
import copy
from decorator import decorator
from pprint import pprint

sys.setrecursionlimit(2**10)
TRACE_INTO = []
TRACE_DICT = 'trace_params'

def update_frame_param(current, event):
    params = [
        ("num_recursive_calls", lambda parent: parent+1),
        (       "stack_frames", lambda parent: parent+[current]),
    ]
    parent = current.f_back
    if event == 'call':
        for p,fn in params:
            parent.f_locals[TRACE_DICT].update({p: fn(parent.f_locals[TRACE_DICT][p])})
        current.f_locals[TRACE_DICT] = parent.f_locals[TRACE_DICT]
    elif event == 'return':
        for p,_ in params:
            parent.f_locals[TRACE_DICT][p] = current.f_locals[TRACE_DICT][p]
    return current

def current_func():
    """ credits @ http://goo.gl/Um0Ig
    The stack frame tells us what code object we're in. If we can find a function object that refers to that code object in its func_code attribute, we have found the function.

    Fortunately, we can ask the garbage collector which objects hold a reference to our code object, and sift through those, rather than having to traverse every active object in the Python world. There are typically only a handful of references to a code object.

    Note: functions can share code objects (in the case where you return a function from a function, ie. a closure). When there's more than one function using a given code object, we can't tell which function it is, so we return None.
    """

    frame = inspect.currentframe(1)
    code  = frame.f_code
    globs = frame.f_globals
    functype = type(lambda: 0)
    funcs = []
    for func in gc.get_referrers(code):
        if type(func) is functype:
            if getattr(func, "func_code", None) is code:
                if getattr(func, "func_globals", None) is globs:
                    funcs.append(func)
                    if len(funcs) > 1:
                        return None
    return funcs[0] if funcs else None

def trace(frame, event, arg):
    # frame
    co        = frame.f_code
    f_locals  = frame.f_locals
    lineno    = frame.f_lineno
    offset    = frame.f_lasti
    caller    = frame.f_back

    # code object
    filename  = co.co_filename
    name      = co.co_name
    varnames  = co.co_varnames[:co.co_argcount]

    if event == 'line':
        cb = byteplay.Code.from_code(co)
        # ...(<Label>, None), (SetLineno, <#>)...
        #   => ...(SetLineno, <#>), (<Label>, None), (SetLineno, <#>)...
        code = []
        for i,(opcode,arg) in enumerate(cb.code):
            if isinstance(opcode, byteplay.Label):
                code.append(cb.code[i+1])
            code.append((opcode,arg))
        cb.code = code
        code_fragments = zip(cb.code[::2],cb.code[1::2])
        code_fragment  = [inst_node for (lineno_node,inst_node) in code_fragments if lineno_node == (byteplay.SetLineno, lineno)]
        next_i = [i for i,(a,b) in enumerate(code_fragments) if a == (byteplay.SetLineno, lineno)][-1] + 1
        if next_i < len(code_fragments)-1:
            _, next_node = code_fragments[next_i]  
            if next_node[0] in [byteplay.POP_JUMP_IF_TRUE, byteplay.POP_JUMP_IF_FALSE]:
                code_fragment.append(next_node)
        # possible code_fragment elements:
        # - [(opcode, arg)]
        # - [(opcode, arg), (POP_JUMP_IF_*, <label>)]
        # - [(<label>, None), (opcode, arg)]
        #print '0x%x'%id(frame),lineno,offset,code_fragment
    elif event == 'call':
        if name == 'write':        return
        if name not in TRACE_INTO: return
        update_frame_param(frame, event)
        #print >> sys.stderr, '[call]: 0x%x=>0x%x, %s,%s\n%s\n%s' % \
        #    (id(frame.f_back), id(frame), caller.f_lineno,
        #    caller.f_lasti, frame.f_locals, arg)

        # potential for branching off different trace functions (!)
        return current_func()
    elif event == 'return':
        update_frame_param(frame, event)
        #print >> sys.stderr, '[return]: 0x%x=>0x%x, %s,%s\n%s\n%s,%s' % \
        #    (id(frame), id(frame.f_back), frame.f_lineno,
        #    frame.f_lasti, frame.f_locals, arg, varnames)

        param = None
        for f_param in [ 'n', 'height' ]:
            if f_param in frame.f_locals:
                param = frame.f_locals[f_param]
                break

        # factorial
        if isinstance(arg, int) and long(arg) > sys.maxint:
            arg = long(arg)
        if isinstance(arg, numbers.Number):
            print "self.assertEquals(%d, %s(%s))" % (arg,name,param)

        # hanoi
        if 'self' in frame.f_locals:
            obj = frame.f_locals['self']
            import jsonpickle
            pickled = jsonpickle.encode(obj, unpicklable=False)
            print pickled
            print "obj = %s(%s)" % (obj.__class__.__name__, '')
            print "self.assertEquals(%r, h.%s(%s))" % (arg,name,param)
    elif event == 'exception':
        exc_type, exc_value, exc_traceback = arg
    else:
        print >> sys.stderr, "Unhandled event '%s'" % event
    return

if __name__ == "__main__":
    old_dir = __builtins__.dir
    def new_dir(*args, **kwargs):
        """ builtin dir() without __var__ clutter """
        return [a for a in old_dir(*args, **kwargs) if not a.startswith("__")]
    __builtins__.dir = new_dir

    from factorial import *
    from hanoi     import *
    h = Hanoi()
    TRACE_INTO = [ factorial.func_name, h.hanoi.func_name ]
    sys._getframe().f_locals[TRACE_DICT] = {
        
        "num_recursive_calls": 0,
        "stack_frames": []
    }
    sys.settrace(trace)
    for i in xrange(3,4,1):
       try:
            factorial(i)
       except Exception as e:
            print >> sys.stderr, e.__class__.__name__, e.message
            continue
    sys.settrace(None)
    print
    for k,v in sys._getframe().f_locals[TRACE_DICT].items():
        if k == "stack_frames":
            v = ' => '.join(map(lambda f:'0x%x'%id(f), v))
        print k+':',v
    print

    sys.exit(0)
    sys._getframe().f_locals[TRACE_DICT] = \
        { "num_recursive_calls": 0, "stack_frames": [] }
    sys.settrace(trace)
    try:
        h.hanoi(5)
    except Exception as e:
        print >> sys.stderr, e.__class__.__name__, e.message
        pass
    sys.settrace(None)

