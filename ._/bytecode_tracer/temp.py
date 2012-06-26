import cPickle
import dis
import os
import shutil
import sys
import tempfile
import opcode
import re
from types import CodeType, MethodType

def has_been_rewritten(code):
    return re.match(r"\A(\x01\x01)+\Z", code.co_lnotab) is not None

def rewrite_lnotab(code):
    if has_been_rewritten(code):
        return code
    n_bytes = len(code.co_code)
    new_lnotab = "\x01\x01" * (n_bytes-1)
    new_consts = []
    for const in code.co_consts:
        if type(const) is CodeType:
            new_consts.append(rewrite_lnotab(const))
        else:
            new_consts.append(const)
    return CodeType(code.co_argcount, code.co_nlocals, code.co_stacksize,
        code.co_flags, code.co_code, tuple(new_consts), code.co_names,
        code.co_varnames, code.co_filename, code.co_name, 0, new_lnotab,
        code.co_freevars, code.co_cellvars)

def rewrite_function(function):
    if isinstance(function, MethodType):
        function = function.im_func
    function.func_code = rewrite_lnotab(function.func_code)

def install(callback):
    pass
def uninstall():
    pass

class StandardBytecodeTracer(object):
    def __init__(self):
        # Will contain False for calls to Python functions and True for calls to
        # C functions.
        self.call_stack = []

    def setup(self):
        install(rewrite_lnotab)

    def teardown(self):
        uninstall()

    def trace(self, frame, event):
        if event == 'line':
            if self.call_stack[-1]:
                self.call_stack.pop()
                stack = get_value_stack_top(frame)
                # Rewrite a code object each time it is returned by some
                # C function. Most commonly that will be the 'compile' function.
                # TODO: Make sure the old code is garbage collected.
                if type(stack[-1]) is CodeType:
                    stack[-1] = rewrite_lnotab(stack[-1])
                yield 'c_return', stack[-1]
            bcode = current_bytecode(frame)
            if bcode.name.startswith("CALL_FUNCTION"):
                value_stack = ValueStack(frame, bcode)
                function = value_stack.bottom()
                # Python functions are handled by the standard trace mechanism, but
                # we have to make sure any C calls the function makes can be traced
                # by us later, so we rewrite its bytecode.
                if not is_c_func(function):
                    rewrite_function(function)
                    return
                self.call_stack.append(True)
                pargs = value_stack.positional_args()
                kargs = value_stack.keyword_args()
                # Rewrite all callables that may have been passed to the C function.
                rewrite_all(pargs + kargs.values())
                yield 'c_call', (function, pargs, kargs)
            elif bcode.name == "PRINT_NEWLINE":
                yield 'print', os.linesep
            else:
                stack = get_value_stack_top(frame)
                if bcode.name == "PRINT_NEWLINE_TO":
                    yield 'print_to', (os.linesep, stack[-1])
                elif bcode.name == "PRINT_ITEM":
                    yield 'print', stack[-1]
                elif bcode.name == "PRINT_ITEM_TO":
                    yield 'print_to', (stack[-2], stack[-1])
                elif bcode.name == "STORE_ATTR":
                    yield 'store_attr', (stack[-1], name_from_arg(frame, bcode), stack[-2])
                elif bcode.name == "DELETE_ATTR":
                    yield 'delete_attr', (stack[-1], name_from_arg(frame, bcode))
                elif bcode.name == "LOAD_GLOBAL":
                    module = frame_module(frame)
                    if module:
                        try:
                            name = name_from_arg(frame, bcode)
                            value = frame.f_globals[name]
                            yield 'load_global', (module.__name__, name, value)
                        except KeyError:
                            pass
                elif bcode.name == "STORE_GLOBAL":
                    module = frame_module(frame)
                    if module:
                        yield 'store_global', (module.__name__,
                                               name_from_arg(frame, bcode),
                                               stack[-1])
                elif bcode.name == "DELETE_GLOBAL":
                    module = frame_module(frame)
                    if module:
                        yield 'delete_global', (module.__name__,
                                                name_from_arg(frame, bcode))
        elif event == 'call':
            self.call_stack.append(False)
        # When an exception happens in Python >= 2.4 code, 'exception' and
        # 'return' events are reported in succession. Exceptions raised from
        # C functions don't generate the 'return' event, so we have to pop
        # from the stack right away and simulate the 'c_return' event
        # ourselves.
        elif event == 'exception' and self.call_stack[-1]:
            yield 'c_return', None
            self.call_stack.pop()
        # Python functions always generate a 'return' event, even when an exception
        # has been raised, so let's just check for that.
        elif event == 'return':
            self.call_stack.pop()

def trace_function(fun):
    dis.dis(fun.func_code)
    rewrite_function(fun)
    tracer = StandardBytecodeTracer()
    tracer.setup()

    def _trace(self, frame, event, arg):
        try:
            if arg is not sys.settrace:
                for ret in self.btracer.trace(frame, event):
                    if ret[0] is not None and ret[0] not in self._ignored_events:
                        self._traces.append(ret)
        except TypeError:
            pass
        return self._trace
    
    sys.settrace(_trace)
    try:
        fun('1','2',3,'4')
    finally:
        sys.settrace(None)

from program import foo
trace_function(foo)
