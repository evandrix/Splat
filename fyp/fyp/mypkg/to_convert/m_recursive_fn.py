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
import warnings
from decorator       import decorator
from pprint          import pprint
from template_writer import *  # submodule support
logger = multiprocessing.log_to_stderr()
logger.setLevel(logging.INFO)

def update_frame_param(current, event):
    """ mutate & propagate trace_params down the stack frames """
    # can only store stack frame ids across processes due to PicklingError of frame object
    params = [
        ("recursion_depth", lambda parent_val: parent_val+1),
        (   "stack_frames", lambda parent_val: parent_val+[id(current)]),
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
        if frame.f_locals[TRACE_DICT]['recursion_depth'] > sys.getrecursionlimit():
            #raise RuntimeError("Maximum recursion depth reached")
            pass
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
            if id(param) not in frame.f_locals[TRACE_DICT]["unit_test_objs"]:
                frame.f_locals[TRACE_DICT]["unit_test_objs"][id(param)] = ["self.assertEqual(%r, %s(%s))" % (arg,name,param)]
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
            if id(arglist) not in frame.f_locals[TRACE_DICT]["unit_test_objs"]:
                frame.f_locals[TRACE_DICT]["unit_test_objs"][id(arglist)] = ["obj = %s(%s)" % (obj.__class__.__name__,','.join(map(str,paramlist))), "self.assertEqual(%r, obj.%s(%s))" % (arg,name,','.join(map(str,arglist)))]
    elif event == 'exception':
        exc_type, exc_value, exc_traceback = arg
        print >> sys.stderr, "Exception event: %s" % arg
    else:
        print >> sys.stderr, "Unhandled event: '%s'" % event
    return

class TimeoutException(Exception): pass
class RunableProcessing(multiprocessing.Process):
    def __init__(self, func, *args, **kwargs):
        self.queue = multiprocessing.Queue(maxsize=1)
        args = (func,) + args
        multiprocessing.Process.__init__(self, target=self.run_func, args=args, kwargs=kwargs)
    def run_func(self, func, *args, **kwargs):
        sys._getframe().f_locals[TRACE_DICT] = kwargs['TRACE_DICT']
        del kwargs['TRACE_DICT']
        sys.settrace(trace)
        try:
            result = func(*args, **kwargs)
            sys.settrace(None)
            self.queue.put((True, (result, sys._getframe().f_locals[TRACE_DICT])))
        except Exception as e:
            self.queue.put((False, e))
    def done(self):
        return self.queue.full()
    def result(self):
        return self.queue.get()
def run(function, *args, **kwargs):
    now = time.time()
    proc = RunableProcessing(function, *args, **kwargs)
    proc.start()
    proc.join(settings.RECURSION_TIMEOUT)
    if proc.is_alive():
        proc.terminate()    # always force_kill process
        runtime = int(time.time() - now)
        raise TimeoutException('timed out after {0} seconds'.format(runtime))
    assert proc.done()
    success, result = proc.result()
    if success:
        return result
    else:
        raise result

import __builtin__
old_dir = __builtin__.dir
def new_dir(*args, **kwargs):
    """ builtin dir() without __var__ clutter """
    return [a for a in old_dir(*args, **kwargs) if not a.startswith("__")]

def test_recursive_func(module, function):
    t0 = time.time()
    # TODO: need to make it work for function recursing on multiple parameters
    trace_dict = {
                   "function": function.func_name,
            "recursion_depth": 0,
               "stack_frames": [],
             "unit_test_objs": {},
    }
    lasti = 0
    for i in xrange(sys.maxint):
        try:
            result, trace_dict = run(function, i, TRACE_DICT=trace_dict) # 10 exceeds recursion depth
        except TimeoutException as e:
            print >> sys.stderr, e.__class__.__name__+':', e.message
            break
        except Exception as e:
            print >> sys.stderr, e.__class__.__name__+':', e.message
            break
        else:
            lasti += 1
    print
    print "Last successful iteration = %d" % lasti
    for k,v in trace_dict.items():
        if k in ["stack_frames", "unit_test_objs"]:
            v = len(v)#'' => '.join(map(lambda f:'0x%x'%id(f), v))
        print k+':',v
    
    # transform into UnitTestObjects to write out unit test suite
    all_tests = []
    for key,value in trace_dict["unit_test_objs"].iteritems():
        all_tests.append(UnitTestObject(function.__name__,key,value))
    tmpl_writer = TemplateWriter(module)
    tmpl_writer.run(all_tests)
    print "Time elapsed: %.3f seconds" % (time.time() - t0)
    print
    return

if __name__ == "__main__":
    __builtin__.dir = new_dir
    import factorial, hanoi, fib
    # only last declared class constructor counts
    test_recursive_func(hanoi, hanoi.Hanoi(0x41414141, 'blah').hanoi)    
    test_recursive_func(factorial, factorial.factorial)
    test_recursive_func(fib, fib.fib_recursive)
    warnings.warn("(test) possible infinite recursion")

