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

"""\
bytecodehacks.xapply

Inspired by Don Beaudry's functor module.

xapply exports one public function, the eponymous xapply. xapply can
be thought of as `lazy apply' or `partial argument resolution'.

It takes a function and part of it's argument list, and returns a
function with the first parameters filled in. An example:

def f(x,y):
    return x+y

add1 = xapply(f,1)

add1(2) => 3

This xapply is now (I think) as general as that from the functor
module, but the functions returned are in simple cases as fast as
normal function, i.e. twice as fast as functors.

This may be generalised at some point in the future.
"""

import new,string,re,types
from bytecodehacks.ops import * # LOAD_FAST, LOAD_CONST, STORE_FAST
from bytecodehacks.code_editor import Function, InstanceMethod

import bytecodehacks.code_editor
CO_VARARGS     = bytecodehacks.code_editor.EditableCode.CO_VARARGS
CO_VARKEYWORDS = bytecodehacks.code_editor.EditableCode.CO_VARKEYWORDS

class XApplyError(Exception):
    pass

# modus operandi:

# if a paramter is referred but not stored to, just replace LOAD_FASTs
# with LOAD_CONSTs
# if a parameter is stored to, create a new local variable (at the end
# of the co_varnames) and store into this local via LOAD_CONST right
# at the start of the code.

# varadic functions? oo er misses.

# this function is too long (120 lines!). not clear what to do about
# it; at least it has fairly linear control flow.

def _xapply_munge(func, args, kw, except0=0):
    code = func.func_code
    cs = code.co_code

    mindefaultindex = code.co_argcount - len(func.func_defaults)
    nconsts = len(code.co_consts)
    nargs = len(args) + len(kw)

    if code.co_argcount < nargs:
        if code.co_flags & CO_VARKEYWORDS and len(args) <= code.co_argcount:
            pass
        elif code.co_flags & CO_VARARGS:
            raise TypeError, "sorry, can't bind * arguments (yet!)"
        else:
            raise TypeError, "too many arguments; expected %d, got %d"%(
                code.co_argcount,nargs)

    if except0:
        argsofinterest = range(1,len(args) + 1)
    else:
        argsofinterest = range(0,len(args))

    extrakw = {}

    kwkeys, kwvals = kw.keys(), kw.values()

    for i in range(len(kwkeys)):
        key = kwkeys[i]
        try:
            arg = code.co_varnames.index(key)
        except ValueError:
            if code.co_flags & CO_VARKEYWORDS:
                extrakw[key] = kwvals[i]
                nargs = nargs - 1
                del kwvals[i]
                continue
            else:
                raise TypeError, "unexpected keyword argument: %s"%key
        if arg < len(args):
            raise TypeError, "keyword parameter redefined"
        argsofinterest.append( arg )

    argsofinterest.sort()
    
    code.co_argcount = code.co_argcount - nargs
    code.co_consts.extend(list(args) + kwvals)

    var2var = {}
    var2const = {}
    for i in range(len(code.co_varnames)):
        if i not in argsofinterest:
            var2var[i] = len(var2var)
        else:
            var2const[i] = len(var2const) + nconsts

    loads = []
    stores = []
    storeargs = {}

    for op in cs:
        if op.__class__ is LOAD_FAST:
            if op.arg in argsofinterest:
                loads.append( op )
            elif op.arg > 0:
                op.arg = var2var[op.arg]
        elif op.__class__ is STORE_FAST:
            if op.arg in argsofinterest:
                stores.append( op )
                storeargs[op.arg] = 1
            elif op.arg > 0:
                op.arg = var2var[op.arg]

    storeargs = storeargs.keys()
    storeargs.sort()

    i = 0
    while i < len(loads):
        op = loads[i]
        if op.arg in storeargs:
            i = i + 1
        else:
            cs[cs.index(op)] = LOAD_CONST( var2const[op.arg] )
            del loads[i]
    
    newi = len(code.co_varnames) - nargs
    old2newi = {}
    prefix = []

    argsofinterest.reverse()
    for i in argsofinterest:
        if i in storeargs:
            prefix.extend( [ LOAD_CONST( var2const[i] ),
                             STORE_FAST( newi ) ] )
            old2newi[i] = newi
            newi = newi + 1
            code.co_varnames.append( code.co_varnames[i] )
        del code.co_varnames[i]
        if i > mindefaultindex:
            del func.func_defaults[i - mindefaultindex]

    if len(extrakw) > 0:
        prefix.extend( _write_extrakw_prefix(code,extrakw) )
        
    cs[0:0] = prefix

    for op in loads:
        op.arg = old2newi[op.arg]
    for op in stores:
        op.arg = old2newi[op.arg]

def _write_extrakw_prefix(code,extrakw):
    kwindex = code.co_argcount
    if code.co_flags & CO_VARARGS:
        kwindex = kwindex + 1
    defsi = len(code.co_consts)
    code.co_consts.append( extrakw )
    return [ LOAD_CONST( defsi ),
             DUP_TOP(),
             LOAD_ATTR( "update" ),
             LOAD_FAST( kwindex ),
             CALL_FUNCTION( 1 ),
             POP_TOP(),
             STORE_FAST( kwindex ) ]

def _xapply_func(func,args,kw):
    f = Function(func)
    _xapply_munge(f,args,kw,0)
    return f.make_function()

def _xapply_meth(meth,args,kw):
    im = InstanceMethod(meth)
    _xapply_munge(im.im_func,args,kw,1)
    return im.make_instance_method()

def _apply(func,args1,*args2,**kw):
    return apply(func,args1+args2,kw)

def _applyk(func,args1,kw1,*args2,**kw2):
    kw2.update(kw1) ## XXX hack! is this safe?
    return apply(func,args1+args2,kw2)

def xapply(func,*args,**kw):
    """xapply(func,arg1,arg2,...) -> callable

`Partial function application'; if

    f = xapply(func,arg1,arg2,...,argn)

then

    f(arg<n+1>,...,argm)

is equivalent to

    func(arg1,...,argn,arg<n+1>,...,argm)

Keyword arguments are now handled gracefully; \"special\" (ie. * or **
style) parameters are essentially invisible to this procedure, and
cannot be bound (this may change). """

    func_type=type(func)
    if not callable(func):
        raise XApplyError, "can't xapply to type %s"%func_type.__name__
    elif func_type is types.FunctionType:
        return _xapply_func(func,args,kw)
    elif func_type is types.UnboundMethodType:
        return _xapply_meth(func,args,kw)
    elif func_type is types.InstanceType:
        return _xapply_meth(func.__call__,args,kw)
    elif kw:
        return xapply(_applyk,func,args,kw)
    else:
        return xapply(_apply,func,args)
