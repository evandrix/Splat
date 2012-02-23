"""
    hack to get .pyc files to do bytecode tracing instead of line tracing.
    @ http://nedbatchelder.com/blog/200804/wicked_hack_python_bytecode_tracing.html
"""
import dis
import marshal
import new
import sys
import types

class PycFile:
    def read(self, f):
        if isinstance(f, basestring):
            f = open(f, "rb")
        self.magic = f.read(4)
        self.modtime = f.read(4)
        self.code = marshal.load(f)
    def write(self, f):
        if isinstance(f, basestring):
            f = open(f, "wb")
        f.write(self.magic)
        f.write(self.modtime)
        marshal.dump(self.code, f)
    def hack_line_numbers(self):
        self.code = hack_line_numbers(self.code)

def hack_line_numbers(code):
    """
        Replace a code object's line number information to claim that every
        byte of the bytecode is a new line. Returns a new code object.
        Also recurses to hack the line numbers in nested code objects.
    """
    n_bytes = len(code.co_code)
    new_consts = []
    lb_ranges = [ ord(code.co_lnotab[b*2]) \
        for b in range(len(code.co_lnotab)/2) ]
    lb_ranges += [ n_bytes - sum(lb_ranges) ]
    prev_lb = 0
    new_lnotab = ''
    for lb in lb_ranges:
        new_lnotab += "\x00\xFF\x00\xFF\x00\xFF\x00"
        new_lnotab += chr(0xEB - prev_lb)
        new_lnotab += "\x01\x01" * lb
        prev_lb = lb
    for const in code.co_consts:
        if type(const) == types.CodeType:
            new_consts.append(hack_line_numbers(const))
        else:
            new_consts.append(const)
    new_code = new.code(
        code.co_argcount, code.co_nlocals, code.co_stacksize, code.co_flags,
        code.co_code, tuple(new_consts), code.co_names, code.co_varnames,
        code.co_filename, code.co_name, 0, new_lnotab
        )
    return new_code

def hack_file(f):
    pyc = PycFile()
    pyc.read(f)
    pyc.hack_line_numbers()
    pyc.write(f)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage: ./%s <pyc file>" % sys.argv[0]
    else:
        hack_file(sys.argv[1])
