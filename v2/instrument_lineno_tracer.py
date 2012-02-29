import dis
import marshal
import struct
import sys
import time
import types
import byteplay
from headers import *

TOTAL_LINE_COVERAGE=-1
ACTUAL_LINE_COVERAGE=[]

# @ http://www.dalkescientific.com/writings/diary/archive/2005/04/20/tracing_python_code.html
def trace(frame, event, arg):
    global ACTUAL_LINE_COVERAGE
    if event == 'line':
        lineno = frame.f_lineno
        # frame.f_code.co_filename
        filename = frame.f_globals["__file__"]
        if (filename.endswith(".pyc") or
            filename.endswith(".pyo")):
            filename = filename[:-1]
        # frame.f_code.co_name
        name = frame.f_globals["__name__"]
        
        # won't work - missing source code!
        #line = linecache.getline(filename, lineno)

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
        if len(code_fragment) == 1:
            code_fragment = code_fragment[0]

        if name == MODULE_UNDER_TEST:
            print "%s:%s: %s" % (name, lineno, code_fragment)
            ACTUAL_LINE_COVERAGE.append(code_fragment)
        #print '\t', frame.f_locals
        #print '\t', frame.f_code.co_varnames[:frame.f_code.co_argcount]
    else:
        print "event:", event
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

    M = __import__(MODULE_UNDER_TEST)
    functions = getmembers(M, isfunction)
    f = [ fn for name,fn in functions if name == 'foo' ][0]
    c = byteplay.Code.from_code(f.func_code)
    c.code = [ (op,arg) for op,arg in c.code if op != byteplay.SetLineno ]
    TOTAL_LINE_COVERAGE = len(c.code)
    #print "100%% bytecode line coverage = %d instructions" % len(c.code)

    #dis.dis(f.func_code.co_code)

    M = __import__(MODULE_UNDER_TEST)
    functions = getmembers(M, isfunction)
    print '---'
    f = [ fn for name,fn in functions if name == 'foo' ][0]
    sys.settrace(trace)
    try:
        f(A(),B(),3,'4')
        #f(None,B(),None,None)
    except:
        pass
    sys.settrace(None)
    print '***'
    #dis.dis(M)
    print '---'

    final_coverage = []
    omit = False
    for opcode, arg in ACTUAL_LINE_COVERAGE:
        if omit and opcode == byteplay.RETURN_VALUE:
            omit = False
            continue
        if opcode == byteplay.CALL_FUNCTION and arg == 1:
            omit = True
            continue
        if not omit:
            final_coverage.append((opcode, arg))
    print final_coverage
            
    ACTUAL_LINE_COVERAGE = len(final_coverage)

    print "(Byte)code coverage: %d/%d instructions (%.2f%%)" % (ACTUAL_LINE_COVERAGE,TOTAL_LINE_COVERAGE, ACTUAL_LINE_COVERAGE/float(TOTAL_LINE_COVERAGE)*100)
    sys.exit(0)
