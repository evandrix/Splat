import sys
import time
import dis
import byteplay
import inspect
import multiprocessing
import logging
from decorator import decorator
from pprint import pprint

sys.setrecursionlimit(2**10)
TRACE_INTO = []
NUM_RECURSIVE_CALLS = 0

def trace(frame, event, arg):
    global NUM_RECURSIVE_CALLS
    co       = frame.f_code
    lineno   = frame.f_lineno
    filename = co.co_filename
    name     = co.co_name
    f_locals = frame.f_locals
    varnames = co.co_varnames[:co.co_argcount]
    if event == 'line':
        cb = byteplay.Code.from_code(co)
        code_fragment = []
        take = False
        for opcode, arg in cb.code:
            if opcode == byteplay.SetLineno:
                take = arg == lineno
            elif take:
                code_fragment.append((opcode, arg))
        if len(code_fragment) == 1:
            code_fragment = code_fragment[0]
    elif event == 'call':
        if name == 'write':         return
        if name not in TRACE_INTO:  return
        caller          = frame.f_back
        caller_lineno   = caller.f_lineno
        caller_co       = caller.f_code
        caller_filename = caller_co.co_filename
        if name in TRACE_INTO:
            NUM_RECURSIVE_CALLS += 1

            print 'call', frame.f_lasti,     # last instruction
            print frame.f_lineno,    # line number (unhacked)
            print frame.f_locals, arg

            return trace
    elif event == 'return':
        if NUM_RECURSIVE_CALLS == 1:
            for k in dir(frame):
                if not k.startswith("__"):
                    #print k,
                    pass
            #print

        print 'return',NUM_RECURSIVE_CALLS, frame.f_lasti,     # last instruction
        print frame.f_lineno,
        print frame.f_locals, arg, varnames

        #f_param = 'n'
        f_param = 'height'
        param = frame.f_locals[f_param]

        if isinstance(arg, int) and long(arg) > sys.maxint:
            arg = long(arg)
            
        if 'self' in frame.f_locals:
            obj = frame.f_locals['self']
            print dir(obj), dir(co)
            import jsonpickle
            pickled = jsonpickle.encode(obj, unpicklable=False)
            print pickled

        print "obj = %s(%s)" % (obj.__class__.__name__, '')
        print "self.assertEquals(%r, h.%s(%s))" % (arg,name,param)

        NUM_RECURSIVE_CALLS -= 1
    elif event == 'exception':
        exc_type, exc_value, exc_traceback = arg
    else:
        print >> sys.stderr, "[Unhandled event]: %s" % event
    return

if __name__ == "__main__":
    old_dir = __builtins__.dir
    def new_dir(*args, **kwargs):
        """ builtin dir() without __var__ clutter """
        return [ a for a in old_dir(*args, **kwargs) if not a.startswith("__") ]
    __builtins__.dir = new_dir

    from hanoi import *
    NUM_RECURSIVE_CALLS = 0
    h = Hanoi()
    #dis.dis(h.hanoi)
    TRACE_INTO.append(h.hanoi.func_name)
    sys.settrace(trace)
    try:
        h.hanoi(3)
    except Exception as e:
        print >> sys.stderr, type(e), e.args, e.message
        pass
    sys.settrace(None)
    print "#(unbalanced recursive calls)=", NUM_RECURSIVE_CALLS

    from factorial import *
    #dis.dis(factorial)
    NUM_RECURSIVE_CALLS = 0
    TRACE_INTO.append(factorial.func_name)
    sys.settrace(trace)
    for i in xrange(3,4,1):
       try:
            factorial(i)
       except:
            continue
    sys.settrace(None)
    print NUM_RECURSIVE_CALLS

    sys.exit(0)
