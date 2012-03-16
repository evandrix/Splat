import sys
import time
import dis
import byteplay
import inspect
import gc
import multiprocessing
import logging
import numbers
import jsonpickle
import copy
import settings
from decorator       import decorator
from pprint          import pprint
from template_writer import *  # submodule support

def update_frame_param(current, event):
    """ mutate & propagate trace_params down the stack frames """

    params = [
        ("num_recursive_calls", lambda parent_val: parent_val+1),
        (       "stack_frames", lambda parent_val: parent_val+[current]),
    ]
    parent = current.f_back
    if event == 'call':
        for p,fn in params:
            parent.f_locals[TRACE_DICT].update({p: fn(parent.f_locals[TRACE_DICT][p])})
        current.f_locals[TRACE_DICT] = parent.f_locals[TRACE_DICT]
    elif event == 'return':
        parent.f_locals[TRACE_DICT] = current.f_locals[TRACE_DICT]
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
    functype = type(lambda: None)
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
        # pre: bytecode must be instrumented!
        cb = byteplay.Code.from_code(co)

        # ...(<Label>, None), (SetLineno, <#>)...
        #   => ...(SetLineno, <#>), (<Label>, None), (SetLineno, <#>)...
        code = []
        for i,(opcode,arg) in enumerate(cb.code):
            if i < len(cb.code)-1 and isinstance(opcode, byteplay.Label):
                code.append(cb.code[i+1])
            code.append((opcode,arg))
        cb.code = code

        # pre: assumes bytecode list of the form:
        # - [ ((SetLineno, <#>), (opcode, arg)) x ... ]
        code_fragments = zip(cb.code[::2],cb.code[1::2])
        code_fragment  = [inst_node for (lineno_node,inst_node) in code_fragments if lineno_node == (byteplay.SetLineno, lineno)]

        indexes = [i for i,(a,b) in enumerate(code_fragments) if a == (byteplay.SetLineno, lineno)]
        if len(indexes) < 1:
            raise RuntimeError("Please instrument bytecode under test first.")

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
        if name == 'write': return
        update_frame_param(frame, event)
        if name not in frame.f_locals[TRACE_DICT]['function']: return
        if frame.f_locals[TRACE_DICT]['num_recursive_calls'] > sys.getrecursionlimit():
            raise RuntimeError("Maximum recursion depth reached")

        #print >> sys.stderr, '[call]: 0x%x=>0x%x, %s,%s\n%s\n%s' % \
        #    (id(frame.f_back), id(frame), caller.f_lineno,
        #    caller.f_lasti, frame.f_locals, arg)
        # potential for branching off different trace functions (!)
        return trace
    elif event == 'return':
        update_frame_param(frame, event)
        #print >> sys.stderr, '[return]: 0x%x=>0x%x, %s,%s\n%s\n%s,%s' % \
        #    (id(frame), id(frame.f_back), frame.f_lineno,
        #    frame.f_lasti, frame.f_locals, arg, varnames)

        # factorial / hanoi
        param = None
        for f_param in [ 'n', 'height' ]:
            if f_param in frame.f_locals:
                param = frame.f_locals[f_param]
                break

        # factorial
        if isinstance(arg, numbers.Number):
            if isinstance(arg, int) and \
                long(arg)>sys.maxint or long(arg)<settings.SYS_MININT:
                arg = long(arg)
            # generate unit test object + memoize!
            if (arg,param) not in frame.f_locals[TRACE_DICT]["unit_test_objs"]:
                print "self.assertEqual(%d, %s(%s))" % (arg,name,param)
                frame.f_locals[TRACE_DICT]["unit_test_objs"].append((arg,param))

        # hanoi
        if 'self' in frame.f_locals:
            # construct object for test initialisation
            obj = frame.f_locals['self']
            obj_params,_,_,_ = inspect.getargspec(obj.__init__)
            paramlist = [obj.__dict__[param] \
                if param in obj.__dict__ else None \
                for param in obj_params[1:]]

            # construct assertion on function return value
            args,_,_,_       = inspect.getargspec(getattr(obj, name))
            arglist = [ frame.f_locals[f_arg] for f_arg in args[1:] ]

            # generate unit test object + memoize!
            if (arg,arglist) not in frame.f_locals[TRACE_DICT]["unit_test_objs"]:
                print "obj = %s(%s)" % \
                    (obj.__class__.__name__,','.join(map(str,paramlist)))
                print "self.assertEqual(%r, obj.%s(%s))" % \
                    (arg,name,','.join(map(str,arglist)))
                frame.f_locals[TRACE_DICT]["unit_test_objs"].append((arg,arglist))
    elif event == 'exception':
        exc_type, exc_value, exc_traceback = arg
        print >> sys.stderr, "Exception event: %s" % arg
    else:
        print >> sys.stderr, "Unhandled event: '%s'" % event
    return

import __builtin__
old_dir = __builtin__.dir
def new_dir(*args, **kwargs):
    """ builtin dir() without __var__ clutter """
    return [a for a in old_dir(*args, **kwargs) if not a.startswith("__")]

if __name__ == "__main__":
    t0 = time.time()
    __builtin__.dir = new_dir
    from factorial import *
    from hanoi     import *
    from fib       import *

    sys._getframe().f_locals[TRACE_DICT] = {
                   "function": factorial.func_name,
        "num_recursive_calls": 0,
               "stack_frames": [],
             "unit_test_objs": [],
    }
    sys.settrace(trace)
    for i in xrange(sys.maxint):
       try:
            factorial(i)
       except Exception as e:
            print >> sys.stderr, e.__class__.__name__+':', e.message
            break
    sys.settrace(None)
    print
    for k,v in sys._getframe().f_locals[TRACE_DICT].items():
        if k in ["stack_frames", "unit_test_objs"]:
            v = len(v)#'' => '.join(map(lambda f:'0x%x'%id(f), v))
        print k+':',v
    print

    h = Hanoi(0x41414141, 'blah')   # only last declared class constructor counts
    sys._getframe().f_locals[TRACE_DICT] = {
                   "function": h.hanoi.func_name,
        "num_recursive_calls": 0,
               "stack_frames": [],
             "unit_test_objs": [],
    }
    sys.settrace(trace)
    try:
        h.hanoi(9) # 10 exceeds recursion depth
    except Exception as e:
        print >> sys.stderr, e.__class__.__name__+':', e.message
        pass
    sys.settrace(None)
    print
    for k,v in sys._getframe().f_locals[TRACE_DICT].items():
        if k in ["stack_frames", "unit_test_objs"]:
            v = len(v)#'' => '.join(map(lambda f:'0x%x'%id(f), v))
        print k+':',v
    print

    sys._getframe().f_locals[TRACE_DICT] = {
                   "function": fib_recursive.func_name,
        "num_recursive_calls": 0,
               "stack_frames": [],
             "unit_test_objs": [],
    }
    sys.settrace(trace)
    for i in xrange(sys.maxint):
       try:
            fib_recursive(i)
       except Exception as e:
            print >> sys.stderr, e.__class__.__name__+':', e.message
            break
    sys.settrace(None)
    print
    for k,v in sys._getframe().f_locals[TRACE_DICT].items():
        if k in ["stack_frames", "unit_test_objs"]:
            v = len(v)#'' => '.join(map(lambda f:'0x%x'%id(f), v))
        print k+':',v
    print

    print "Time elapsed: %.3f seconds" % (time.time() - t0)
