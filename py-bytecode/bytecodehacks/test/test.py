from bytecodehacks import code_editor,ops

def f():
    return "This function does something really interesting"
    
g=code_editor.Function(f)
g.func_code.co_code[:]=[ops.SET_LINENO(3),
                        ops.LOAD_CONST(len(g.func_code.co_consts)),
                        ops.RETURN_VALUE()]
g.func_code.co_consts.append("Not any more!")
g=g.make_function()
print f()
print g()

from bytecodehacks import attr_freeze
import sys

def ff(x):
    if x:
        print sys.exit
    else:
        print sys.copyright

_=attr_freeze.Ref()

gg=attr_freeze.freeze_attrs(ff,
                            _.sys.exit,sys.exit,
                            _.sys.copyright,sys.copyright)
