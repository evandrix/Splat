import dis
import marshal
import struct
import sys
import time
import types
import byteplay
from headers import *

# @ http://www.dalkescientific.com/writings/diary/archive/2005/04/20/tracing_python_code.html
def trace(frame, event, arg):    
    if event == 'line':
        lineno = frame.f_lineno
        # frame.f_code.co_filename
        filename = frame.f_globals["__file__"]
        if (filename.endswith(".pyc") or
            filename.endswith(".pyo")):
            filename = filename[:-1]
        # frame.f_code.co_name
        name = frame.f_globals["__name__"]
        line = linecache.getline(filename, lineno)

        func_line_no = frame.f_lineno
        co = frame.f_code
        cb = byteplay.Code.from_code(co)
        code_fragment = []
        take = False
        for pair in cb.code:
            opcode, arg = pair
            if opcode == byteplay.SetLineno:
                take = arg == func_line_no
            elif take:
                code_fragment.append(pair)

        if name == MODULE_UNDER_TEST:
            print "%s:%s: %s" % (name, lineno, code_fragment)
        #print '\t', frame.f_locals
        #print '\t', frame.f_code.co_varnames[:frame.f_code.co_argcount]
    return trace

class A(object):
    def func3(self):
        return
class B(object):
    def func2(self):
        return

if __name__ == "__main__":
    if len(sys.argv) > 1:
        M = __import__(sys.argv[1]) # import module as string
        dis.dis(M)
        sys.exit(0)

    M = __import__(MODULE_UNDER_TEST)
    functions = getmembers(M, isfunction)
    print '---'
    f = [ fn for name,fn in functions if name == 'foo' ][0]
    sys.settrace(trace)
    f(A(),B(),3,'4')
    sys.settrace(None)
    print '***'
    #dis.dis(M)
    print '---'
