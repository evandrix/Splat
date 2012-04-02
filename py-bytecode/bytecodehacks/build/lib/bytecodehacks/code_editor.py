#   Copyright 1999-2000 Michael Hudson mwh@python.net
#
#                        All Rights Reserved
#
#
# Permission to use, copy, modify, and distribute this software and
# its documentation for any purpose is hereby granted without fee,
# provided that the above copyright notice appear in all copies and
# that both that copyright notice and this permission notice appear in
# supporting documentation.
#
# THE AUTHOR MICHAEL HUDSON DISCLAIMS ALL WARRANTIES WITH REGARD TO
# THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS, IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL,
# INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER
# RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF
# CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
# CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

from bytecodehacks.fleshy import Flesher,Fleshable
import types,StringIO,struct,new

from bytecodehacks import ops

class CodeString(Fleshable):
    def __init__(self,cs=None,bytecodes=None):
        self.labels=[]
        self.byte2op={}
        self.opcodes=[]

        if bytecodes is None:
            bytecodes = ops._bytecodes

        if cs is None:
            pass
        elif type(cs) is type(""):
            self.disassemble_no_code(cs,bytecodes)
        else:
            self.disassemble(cs,bytecodes)
    def disassemble(self,code,bytecodes):
        self.labels = []
        self.byte2op = {}
        self.opcodes = []
        self.code = code

        cs=StringIO.StringIO(code.co_code)
        i, op, n = 0, 0, len(code.co_code)
        
        while i < n:
            self.byte2op[i]=op
            byte=cs.read(1)
            self.opcodes.append(bytecodes[byte](cs,self))
            i = cs.tell()
            op = op + 1

        del self.code

        for label in self.labels:
            label.resolve(self)
    def disassemble_no_code(self,codestring,bytecodes):
        self.labels = []
        self.byte2op = {}
        self.opcodes = []

        cs=StringIO.StringIO(codestring)
        i, op, n = 0, 0, len(codestring)
        
        while i < n:
            self.byte2op[i]=op
            byte=cs.read(1)
            self.opcodes.append(bytecodes[byte](cs,self))
            i = cs.tell()
            op = op + 1

        for label in self.labels:
            label.resolve(self)            
    def add_label(self,label):
        self.labels.append(label)
    def find_labels(self,index):
        labelled=self.opcodes[index]
        pointees=[]
        for l in self.labels:
            if l.op == labelled:
                pointees.append(l)
        return pointees
    def __getitem__(self,index):
        return self.opcodes[index].flesh(cs=self)
    def __setitem__(self,index,value):
        # find labels that point to the removed opcode
        pointees=self.find_labels(index)
        if self.opcodes[index].is_jump():
            self.labels.remove(self.opcodes[index].label)
        self.opcodes[index]=value.unflesh()
        for l in pointees:
            l.op=value
        if value.is_jump():
            self.labels.append(value.label)
    def __delitem__(self,index):
        # labels that pointed to the deleted item get attached to the
        # following insn (unless it's the last insn - in which case I
        # don't know what you're playing at, but I'll just point the
        # label at what becomes the last insn)
        pointees=self.find_labels(index)
        if index + 1 == len(self.opcodes):
            replacement = self.opcodes[index]
        else:
            replacement = self.opcodes[index + 1]
        for l in pointees:
            l.op=replacement
        going=self.opcodes[index]
        if going.is_jump():
            self.labels.remove(going.label)
        del self.opcodes[index]
    def __getslice__(self,lo,hi):
        ret = self.opcodes[lo:hi]
        for i in range(len(ret)):
            ret[i] = ret[i].flesh(cs=self)
        return ret
    def __setslice__(self,lo,hi,values):
        # things that point into the block being stomped on get
        # attached to the start of the new block (if there are labels
        # pointing into the block, rather than at its start, a warning
        # is printed, 'cause that's a bit dodgy)
        pointees=[]
        opcodes = self.opcodes
        indices=range(len(opcodes))[lo:hi]
        for i in indices:
            if opcodes[i].is_jump():
                self.labels.remove(opcodes[i].label)
            p=self.find_labels(i)
            if p and i <> lo:
                print "What're you playing at?"
            pointees.extend(p)
        codes = []
        for value in values:
            if value.is_jump():
                self.labels.append(value.label)
            codes.append(value.unflesh())
        opcodes[lo:hi]=codes
        if opcodes:
            replacement = opcodes[min(lo, len(opcodes)-1)]
            for l in pointees:
                l.op = replacement
    def __delslice__(self,lo,hi):
        self.__setslice__(lo, hi, [])
    def __len__(self):
        return len(self.opcodes)
    def append(self,value):
        self.opcodes.append(value.unflesh())
        if value.is_jump():
            self.labels.append(value.label)
    def extend(self,opcodes):
        map(self.append,opcodes)
    def insert(self,index,value):
        self.opcodes.insert(index,value.unflesh())     
        if value.is_jump():
            self.labels.append(value.label)
    def remove(self,x):
        del self[self.opcodes.index(x)]
    def index(self,x):
        return self.opcodes.index(x)
    def assemble(self):
        out=StringIO.StringIO()
        for i in self:
            i.byte=out.tell()
            out.write(i.assemble(self))
        for l in self.labels:
            l.write_refs(out)
        out.seek(0)
        return out.read()
    def compute_stack(self):
        class StackTracker:
            def __init__(self):
                self.level = 0
                self.max = 0
                self.blocks = []
##                 self.flag = 0
                self.end_finally_stack = []
            def push(self,amount=1):
                self.level = self.level + amount
                self.max = max(self.max,self.level)
            def pop(self,amount=1):
##                 if self.level - amount < 0:
##                     print "warning!"
##                     self.flag = 1
                self.level = max(self.level - amount,0)
            def block_push(self,is_finally=0):
                self.blocks.append( (self.level,is_finally) )
            def block_pop(self):
                s,f = self.blocks.pop()
                if f <> 0:
                    self.level = s + f
                    self.max = max(self.max,self.level)
                    self.end_finally_stack.append( f )                    
                else:
                    self.level = s
            def handle_end_finally(self):
                f = self.end_finally_stack.pop()
                if f == 2:
                    self.pop( 3 )
                
        tracker = StackTracker()
        for op in self.opcodes:
            op.stack_manipulate(push=tracker.push,
                                pop=tracker.pop,
                                block_pop=tracker.block_pop,
                                block_push=tracker.block_push,
                                tracker=tracker)
##             if tracker.flag:
##                 print op.__class__.__name__, self.opcodes.index(op)
##                 tracker.flag = 0
        return tracker.max
                              

class EditableCode(Flesher,Fleshable):
    # bits for co_flags
    CO_OPTIMIZED   = 0x0001
    CO_NEWLOCALS   = 0x0002
    CO_VARARGS     = 0x0004
    CO_VARKEYWORDS = 0x0008

    AUTO_RATIONALIZE = 0
    
    def __init__(self,code=None):
        Flesher.__init__(self)
        if code is None:
            self.init_defaults()
        elif type(code) in (type(()), type([])):
            self.init_tuple(code)
        else:
            self.init_code(code)
        self.make_fleshed("co_code",code=Flesher.MagicSelfValue)
    def name_index(self,name):
        if name not in self.co_names:
            self.co_names.append(name)
        return self.co_names.index(name)
    def local_index(self,name):
        if name not in self.co_varnames:
            self.co_varnames.append(name)
        return self.co_varnames.index(name)
    def rationalize(self):
        from bytecodehacks.rationalize import rationalize
        rationalize(self)
    def init_defaults(self):
        self.co_argcount = 0
        self.co_flags = 0 # ???
        self.co_consts = []
        self.co_names = []
        self.co_varnames = []
        self.co_filename = '<edited code>'
        self.co_name = 'no name'
        self.co_firstlineno = 0
        self.co_lnotab = '' # ???
        self.co_code = CodeString()
    def init_code(self,code):
        self.co_argcount = code.co_argcount
        self.co_flags = code.co_flags
        self.co_consts = list(code.co_consts)
        self.co_names = list(code.co_names)
        self.co_varnames = list(code.co_varnames)
        self.co_filename = code.co_filename
        self.co_name = code.co_name
        self.co_firstlineno = code.co_firstlineno
        self.co_lnotab = code.co_lnotab
        self.co_code = CodeString(code)
    def init_tuple(self,tup):
        ( self.co_argcount, ignored, ignored, self.co_flags
        , self.co_code, co_consts, co_names, co_varnames, self.co_filename
        , self.co_name, self.co_firstlineno, self.co_lnotab
        ) = tup
        self.co_consts = list(co_consts)
        self.co_names = list(co_names)
        self.co_varnames = list(co_varnames)
        self.co_code = CodeString(self)
    def make_code(self):
        if self.AUTO_RATIONALIZE:
            self.rationalize()
        else:
            # hack to deal with un-arg-ed names
            for op in self.co_code:
                if (op.has_name() or op.has_local()) and not hasattr(op, "arg"):
                    if op.has_name():
                      op.arg = self.name_index(op.name)
                    else:
                      op.arg = self.local_index(op.name)

        return apply(new.code, self.as_tuple())
    def set_function(self, function):
        self.function = function
    def as_tuple(self):
        # the assembling might change co_names or co_varnames - so
        # make sure it's done *before* we start gathering them.
        bytecode = self.co_code.assemble()
        stacklevel = self.co_code.compute_stack()
        return (
            self.co_argcount,
            len(self.co_varnames),
            stacklevel,
            self.co_flags,
            bytecode,
            tuple(self.co_consts),
            tuple(self.co_names),
            tuple(self.co_varnames),
            self.co_filename,
            self.co_name,
            self.co_firstlineno,
            self.co_lnotab)

class Function(Fleshable,Flesher):
    def __init__(self,func=None):
        Flesher.__init__(self)
        if func is None:
            self.init_defaults()
        elif type(func) in (type(()), type([])):
            self.init_tuple(func)
        else:
            self.init_func(func)
        self.make_fleshed("func_code",function=Flesher.MagicSelfValue)
    def init_defaults(self):
        self.__name = "no name"
        self.__doc = None
        self.func_code = EditableCode()
        self.func_defaults = []
        self.func_globals = {} # ???
    def init_func(self,func):
        self.__name = func.func_name
        self.__doc = func.func_doc
        self.func_code = EditableCode(func.func_code)
        if func.func_defaults is not None:
            self.func_defaults = list(func.func_defaults)
        else:
            self.func_defaults = []
        self.func_globals = func.func_globals
    def init_tuple(self,tup):
        ( self.__name, self.__doc, func_code, self.func_defaults
        , self.func_globals
        ) = tup
        self.func_code = EditableCode(func_code)
    def __getattr__(self,attr):
        # for a function 'f.__name__ is f.func_name'
        # so lets hack around to support that...
        if attr in ['__name__','func_name']:
            return self.__name
        elif attr in ['__doc__','func_doc']:
            return self.__doc
        else:
            return Flesher.__getattr__(self,attr)
    def __setattr__(self,attr,value):
        if attr in ['__name__','func_name']:
            self.__name = value
        elif attr in ['__doc__','func_doc']:
            self.__doc = value
        else:
            self.__dict__[attr]=value
    def make_function(self):
        newfunc = new.function(
            self.func_code.make_code(),
            self.func_globals,
            self.__name)
        if not self.func_defaults:
            defs = None
        else:
            defs = tuple(self.func_defaults)
        newfunc.func_defaults = defs
        newfunc.func_doc = self.__doc
        return newfunc
    def __call__(self,*args,**kw):
        return apply(self.make_function(),args,kw)
    def set_method(self, method):
        self.method = method
    def as_tuple(self):
        if not self.func_defaults:
            defs=None
        else:
            defs=tuple(self.func_defaults)
        return (self.__name, self.__doc, self.func_code.as_tuple(), defs, {})
    
class InstanceMethod(Flesher):
    def __init__(self,meth=None):
        Flesher.__init__(self)
        if meth is None:
            self.init_defaults()
        else:
            self.init_meth(meth)
        self.make_fleshed("im_func",method=Flesher.MagicSelfValue)
    def init_defaults(self):
        self.im_class = None
        self.im_func = Function()
        self.im_self = None
    def init_meth(self,meth):
        self.im_class = meth.im_class
        self.im_func = Function(meth.im_func)
        self.im_self = meth.im_self
    def make_instance_method(self):
        return new.instancemethod(
            self.im_func.make_function(),
            self.im_self,self.im_class)

class FunctionOrMethod:
    def __init__(self,functionormethod):
        if type(functionormethod) is types.FunctionType:
            self.is_method = 0
            self.function = Function(functionormethod)
        elif type(functionormethod) is types.UnboundMethodType:
            self.is_method = 1
            self.method = InstanceMethod(functionormethod)
            self.function = self.method.im_func
    def make_function_or_method(self):
        if self.is_method:
            return self.method.make_instance_method()
        else:
            return self.function.make_function()
        
