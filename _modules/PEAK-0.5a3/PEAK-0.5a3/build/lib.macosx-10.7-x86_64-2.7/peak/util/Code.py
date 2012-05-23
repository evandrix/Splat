"""Bytecode inspection and patching - like a simpler (faster!) bytecodehacks

    Similar to the Python 'bytecodehacks' package, this module supplies 'Code'
    and 'Function' objects which are mutable versions of the real things.  The
    main difference between this module and 'bytecodehacks' is that this module
    values speed above nearly all other considerations, and thus only offers
    in-place bytecode patching, and eschews most of the higher-level facilities
    offered by 'bytecodehacks'.  But it's plenty enough for what PEAK needs.

    The module makes available many useful values; you can get any opcode as a
    constant from it by explicit import, such as::

        from peak.util.Code import LOAD_NAME, STORE_NAME

    There's also an 'opcode' array that you can import that maps opcode names to
    values.
"""

from array import array
import new
from types import CodeType
from dis import HAVE_ARGUMENT, EXTENDED_ARG, opname

__all__ = ['Code', 'Function', 'opcode', 'codeIter', 'FunctionBinder', 'bind_func']

opcode = {}

for code in range(256):
    name=opname[code]
    if name.startswith('<'): continue
    if name.endswith('+0'): opcode[name[:-2]]=code
    opcode[name]=code

globals().update(opcode) # opcodes are now importable at will







class Code(object):
    """Editable version of Python 'code' objects"""

    def __init__(self, code=None):
        if code is None:
            self.init_code_defaults()
        elif isinstance(code,CodeType) or isinstance(code,Code):
            self.init_code(code)
        else:
            self.init_code_tuple(code)

    def init_code_defaults(self):
        self.init_code_tuple((
            0, 0,(),(),(),'<edited code>','no name',0,'','',(),(),
        ))

    def init_code(self,code):
        self.init_code_tuple((
            code.co_argcount,
            code.co_nlocals,
            code.co_stacksize,
            code.co_flags,
            code.co_code,
            code.co_consts,
            code.co_names,
            code.co_varnames,
            code.co_filename,
            code.co_name,
            code.co_firstlineno,
            code.co_lnotab,
            code.co_freevars,
            code.co_cellvars,
        ))

    def __iter__(self):
        return codeIter(self)

    def code(self):
        """Return a true Python bytecode object based on this code object"""
        return new.code(*self.code_as_tuple())

    def init_code_tuple(self,tup):
        ( self.co_argcount, self.co_nlocals, self.co_stacksize, self.co_flags,
          co_code, co_consts, co_names, co_varnames, self.co_filename,
          self.co_name, self.co_firstlineno, self.co_lnotab, self.co_freevars,
          self.co_cellvars
        ) = tup
        self.co_consts = list(co_consts)[:]
        self.co_names = list(co_names)[:]
        self.co_varnames = list(co_varnames)[:]
        self.co_code = array('B',co_code)


    def code_as_tuple(self):
        return (
            self.co_argcount,
            len(self.co_varnames),
            self.co_stacksize,
            self.co_flags,
            self.co_code.tostring(),
            tuple(self.co_consts),
            tuple(self.co_names),
            tuple(self.co_varnames),
            self.co_filename,
            self.co_name,
            self.co_firstlineno,
            self.co_lnotab,
            self.co_freevars,
            self.co_cellvars
        )


    def name_index(self,name):
        """Return an offset for 'name', extending 'co_names' if needed"""
        if name not in self.co_names:
            self.co_names.append(name)
        return self.co_names.index(name)





    def const_index(self,const):
        """Return the offset for 'const', extending 'co_consts' if needed"""
        c = self.co_consts
        if const not in c:
            c.append(const); return len(c)-1
        return c.index(const)

    def local_index(self,name):
        """Return the offset for 'name', extending 'co_varnames' if needed"""
        if name not in self.co_varnames:
            self.co_varnames.append(name)
        return self.co_varnames.index(name)

    def free_index(self,name):
        """Return the offset for 'name', extending 'co_freevars' if needed"""
        if name not in self.co_freevars:
            self.co_freevars.append(name)
        return self.co_freevars.index(name)

    def cell_index(self,name):
        """Return the offset for 'name', extending 'co_cellvars' if needed"""
        if name not in self.co_cellvars:
            self.co_cellvars.append(name)
        return self.co_cellvars.index(name)

    def findOp(self,op):
        """Return an iterator which will find instances of opcode 'op'"""
        return codeIter(self,0,[op])

    def findOps(self,oplist):
        """Return an iterator which will find opcodes in 'oplist'"""
        return codeIter(self,0,oplist)

    def namesUsed(self):
        """Return the names which are loaded by 'LOAD_NAME' in this code"""
        names = self.co_names
        used = [0] * len(names)
        cursor = self.findOps(LOAD_NAME)
        for op in cursor: used[cursor.arg]=1
        return [name for (name,wasUsed) in zip(names,used) if wasUsed]

    def renumberLines(self, toLine):

        """Renumber code's line numbers so that it starts at 'toLine'"""

        self.co_firstlineno = toLine
        cursor = self.findOp(SET_LINENO)
        cursor.next()
        offset = (toLine - cursor.arg)
        cursor.go(0)

        for op in cursor:
            cursor.write(SET_LINENO, cursor.arg + offset)


    def index(self):
        """Return a 'codeIndex' object for this code"""
        return codeIndex(self)


    def append(self, op, arg=None):

        """Append opcode 'op', w/optional argument 'arg'; arg can be 32 bit"""

        #if isinstance(op,str): op = opcode[op]

        append = self.co_code.append

        if arg is not None:

            if (arg & 0xFFFF0000) not in (0xFFFF0000, 0):
                append(EXTENDED_ARG)
                append(arg>>16 & 255)
                append(arg>>24 & 255)

            append(op)
            append(arg & 255)
            append(arg>>8 & 255)

        else:
            append(op)

class Function(Code):

    """Editable version of Python 'function' objects; includes code editing"""

    def __init__(self, func=None):
        if func is None:
            self.init_func_defaults()
        else:
            self.init_func(func)

    def init_func_defaults(self):
        self.func_globals={}
        self.func_name='unnamed function'
        self.func_dict=None
        self.func_doc=None
        self.func_closure=None
        self.func_defaults = ()
        self.init_code_defaults()

    def init_func(self, func):
        self.func_globals   = func.func_globals
        self.func_name      = func.func_name
        self.func_dict      = func.func_dict
        self.func_doc       = func.func_doc
        self.func_closure   = func.func_closure
        self.func_defaults  = func.func_defaults
        self.init_code(func.func_code)

    def func(self):
        """Return a true Python function based on this function/code object"""
        c = self.code()
        f = new.function(c, self.func_globals, self.func_name, self.func_defaults or ())
        f.func_dict = self.func_dict
        f.func_doc  = self.func_doc
        #f.func_closure = self.func_closure
        return f





allOps = [1]*256

class codeIter(object):
    """Iterator for stepping through bytecode"""

    op = None

    def __init__(self, code, startAt=0, findOps=None):
        """Iterator for 'code', starting at 'startAt', finding 'findOps'"""
        self.code = code
        self.codeArray = code.co_code
        self.end = self.start = startAt
        self.setMask(findOps)

    def setMask(self,findOps=None):
        """Set the list of opcodes this iterator will iterate over"""
        if findOps:
            opmap = self.findOps = [0]*256
            for f in findOps:
                #if isinstance(f,str): f = opcode[f]
                opmap[f]=1
        else:
            self.findOps = allOps

    def arg(self):
        """Argument value of current opcode, accessed as a property"""
        s, e = self.start, self.end
        l = e-s
        if l>=3:
            ca = self.codeArray
            arg = ca[s+1] | ca[s+2]<<8
            if l==6:
                arg <<= 16
                arg += (ca[s+4] | ca[s+5]<<8)
            return arg

    arg = property(arg)

    def __iter__(self):
        return self

    def go(self,offset):
        """Go to 'offset' in the code, returning the next matching opcode"""
        self.end = offset
        return self.next()

    def next(self):
        """Return the next matching opcode or raise 'StopIteration'"""
        ca = self.codeArray
        findOps = self.findOps
        end = self.end
        l = len(ca)
        start = end

        while end < l:

            op = ca[start]

            if op>=HAVE_ARGUMENT:
                if op==EXTENDED_ARG:
                    op = ca[start+3]
                    end = start+6
                else:
                    end = start+3
            else:
                end = start+1

            if findOps[op]:
                self.start = start
                self.end = end
                self.op = op
                return op

            start = end

        self.op = None
        self.start = start
        self.end = end
        raise StopIteration



    def write(self, op, arg=None, sameSize=1):

        """Write 'op' (w/optional 'arg') at current position"""

        #if isinstance(op,str): op = opcode[op]

        ca=self.codeArray
        start = self.start

        if arg is not None:
            bytes = [op, arg & 0xFF, (arg & 0xFF00)>>8]
            bl=3
            if (arg & 0xFFFF0000) not in (0xFFFF0000, 0):
                bl=6
                bytes[0:0] = [
                    EXTENDED_ARG, (arg & 0xFF0000)>>16, (arg & 0xFF000000)>>24
                ]

            if start==len(ca):
                ca.extend(array('B',bytes))
                self.end=len(ca)
                return

            elif sameSize and (self.end-start)<>bl:
                raise ValueError

            ca[start:start+bl] = array('B',bytes)
            self.end = start+bl

        else:
            if start==len(ca):
                ca.append(op)
                self.end += 1

            elif sameSize and self.end-self.start<>1:
                raise ValueError

            ca[self.start]=op



class FunctionBinder(object):

    def __init__(self, func):

        if not isinstance(func,Function):
            func = Function(func)

        self.func = func
        cursor = func.findOp(LOAD_GLOBAL)
        bindables = self.bindables = {}
        sd = bindables.setdefault
        names = func.co_names

        for op in cursor:
            sd(names[cursor.arg], []).append(cursor.start)

    def _rebind(self, kw):
        get = self.bindables.get
        func = self.func
        cursor = iter(func)

        for k,v in kw.items():
            fixups = get(k)
            if fixups:
                ci = func.const_index(v)
                for f in fixups:
                    cursor.go(f)
                    cursor.write(LOAD_CONST,ci)

    def boundCode(self, **kw):
        self._rebind(kw)
        return self.func.code()

    def boundFunc(self, **kw):
        self._rebind(kw)
        return self.func.func()





def bind_func(func, **kw):
    b=FunctionBinder(func)
    func.func_code = b.boundCode(**kw)
    return func


def copy_func(func):
    return Function(func).func()



# And now, as a demo... self-modifying code!

builtIns   = getattr(__builtins__,'__dict__',__builtins__)
globalDict = globals()

def _bindAll(f):
    b = FunctionBinder(f)
    b._rebind(globalDict)
    f.func_code = b.boundCode(**builtIns)
    return f

for f in (
        codeIter.next, codeIter.write, Code.renumberLines, Code.append,
        FunctionBinder.__init__, FunctionBinder._rebind,
    ):
    _bindAll(f.im_func)














class codeIndex(object):

    """Useful indexes over a code object

        opcodeLocations[op] -- list of instruction numbers with 'op' as opcode

        opcode[i] -- the i'th instruction's opcode

        operand[i] -- the i'th instruction's operand (or None)

        offset[i]  -- location of the i'th instruction

        byteIndex[b] -- instruction number 'i' for byte 'b'

        byteLine[b] -- source line number that generated byte 'b'

        nextLine[b] -- offset of next line number change following byte 'b'

        nextSplit[b] -- offset of next "safe code split point" following 'b'
    """





















    def __init__(self, codeObject):

        self.code = codeObject

        opcodeLocations = self.opcodeLocations = [[] for x in range(256)]
        addLoc = [x.append for x in opcodeLocations]
        opcode = self.opcode = [];  addOp = opcode.append
        operand = self.operand = []; addArg = operand.append
        offset = self.offset = [];   addOfs = offset.append

        p=0

        ca = codeObject.co_code
        end = 0
        l = len(ca)
        start = end

        while end < l:

            op = ca[start]

            if op>=HAVE_ARGUMENT:
                arg = ca[start+1] | ca[start+2]<<8
                if op==EXTENDED_ARG:
                    op = ca[start+3]
                    end = start+6
                    arg <<= 16
                    arg += (ca[start+4] | ca[start+5]<<8)
                else:
                    end = start+3
            else:
                arg = None
                end = start+1

            addOp(op); addArg(arg); addOfs(start); addLoc[op](p)
            p += 1

            start = end

    _bindAll(__init__)

    def byteLine(self):
        """Property: line number for each byte"""

        code = self.code; lnotab = array('B', code.co_lnotab)
        table  = []; extend = table.extend
        line   = code.co_firstlineno

        for i in range(0,len(lnotab),2):
            extend( [line] * lnotab[i] ); line += lnotab[i+1]

        codeLen = len(code.co_code)
        tblLen  = len(table)
        if tblLen<codeLen:
            extend( [line] * (codeLen-tblLen) )

        self.__dict__['byteLine'] = table
        return table

    byteLine = property(_bindAll(byteLine))


    def byteIndex(self):

        """Property: instruction sequence number by byte"""

        index = []; extend = index.extend
        offset = self.offset[:]
        offset.append(len(self.code.co_code))

        for i in range(len(offset)-1):
            extend([i] * (offset[i+1]-offset[i]))

        self.__dict__['byteIndex'] = index
        return index

    byteIndex = property(_bindAll(byteIndex))





    def nextLine(self):
        """Property: offset of next line number change for each byte"""
        code = self.code; lnotab = array('B', code.co_lnotab)
        table  = []; extend = table.extend
        byte   = 0

        for i in range(0,len(lnotab),2):
            bytes = lnotab[i]; byte+=bytes
            extend( [byte] * bytes )

        codeLen = len(code.co_code)
        tblLen  = len(table)

        if tblLen<codeLen:
            extend( [codeLen] * (codeLen-tblLen) )

        self.__dict__['nextLine'] = table
        return table

    nextLine = property(_bindAll(nextLine))


    def nextSplit(self):
        """Property: next safe code split offset by byte"""

        offsets = self.nextLine[:]  # start with offsets of next lines

        fwd_jump = [0] * 256
        isCleanup  = fwd_jump[:]

        for j in (
            FOR_LOOP, SETUP_LOOP, SETUP_EXCEPT, SETUP_FINALLY, FOR_ITER,
            JUMP_IF_TRUE, JUMP_IF_FALSE, JUMP_FORWARD
        ):
            fwd_jump[j] = 1

        for c in (POP_TOP, POP_BLOCK, END_FINALLY): isCleanup[c] = 1

        i = 0; opcode=self.opcode; codeLen = len(opcode); operand=self.operand
        bi = self.byteIndex; ofs = self.offset

        while i<codeLen:
            if not fwd_jump[opcode[i]]:
                i += 1
                continue

            # Save location and opcode
            op = opcode[i]; startLoc = ofs[i]

            # Follow the jump forward
            i = bi[ofs[i+1] + operand[i]]

            if op==SETUP_EXCEPT:
                # back up to the jump to the "else" block
                i -= 1

                # jump forward again
                i = bi[ofs[i+1] + operand[i]]

                # check for END_FINALLY before this point
                assert opcode[i-1]==END_FINALLY and fwd_jump[opcode[i-2]]
                i -= 2

            elif op==SETUP_FINALLY:
                # find the END_FINALLY
                while opcode[i] != END_FINALLY:
                    i += 1

            while fwd_jump[opcode[i]]:
                i = bi[ofs[i+1] + operand[i]]

            while isCleanup[opcode[i]]:
                i += 1

            endLoc = ofs[i]
            offsets[startLoc:endLoc] = [endLoc] * (endLoc-startLoc)

        self.__dict__['nextSplit'] = offsets
        return offsets

    nextSplit = property(_bindAll(nextSplit))

del builtIns, globalDict

if __name__ == '__main__':

    s = """
for x in 27,35,51:
    y = x * 2
else:
    z = 999

try:
    a = 1
    try:
        a=10
    finally:
        b=20
finally:
    b = 2

while 1:
    c = 3
    if c==3:
        break
    continue

if a:
    d = 4
elif c:
    e = 5
else:
    f = 6

class Foo:
    g = 7

try:
    h = 8
except (NameError,ValueError):
    i = 9
except:
    j = 10
#else:
#    k = 11
"""

    co = Code(compile(s,"<string>","exec"))
    ix = co.index()
    for i in ix.opcodeLocations[STORE_NAME]:
        ns = ix.nextSplit[ix.offset[i]]
        print co.co_names[ix.operand[i]], ns,
        if ns<len(ix.byteLine): print ix.byteLine[ns],
        print


'''
    foo = "foo"

    def bar():
        print foo

    baz = bind_func(copy_func(bar), foo="Hello, World!")

    bar(); baz()

    foo = "it worked!"

    bar(); baz()
'''














