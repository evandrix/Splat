from bytecodehacks import inline,macro

def f(x,y):
    return x+y

def f2((x),(y)):
    return x+y

def integ_global(dx,x0,x1,y):
    x=x0
    while x<x1:
        dy=f(x,y)
        y=y+dx*dy
        x=x+dx
    return y

# modulo SET_LINENOs integ_inline2 has *exactly*the*same* bytecodes as
# integ_hand - and so is the same in python -O mode. I'm quite proud
# of that...
integ_inline2=macro.expand_these(integ_global,f=f2)

def integ_local(dx,f,x0,x1,y):
    x=x0
    while x<x1:
        dy=f(x,y)
        y=y+dx*dy
        x=x+dx
    return y

integ_inline=inline.inline(integ_global,f=f)

def integ_hand(dx,x0,x1,y):
    x=x0
    while x<x1:
        dy=x+y
        y=y+dx*dy
        x=x+dx
    return y

def test(param = 0.00001):
    import time
    T=time.time
    t=T(); integ_global(param,0,1,1); gf=T()-t
    print "        global function call: ",gf
    t=T(); integ_local(param,f,0,1,1); lf=T()-t
    print "         local function call: ",lf
    t=T(); integ_inline(param,0,1,1); ifc=T()-t
    print "       inlined function call: ",ifc
    t=T(); integ_inline2(param,0,1,1); ifc2=T()-t
    print "      inlined2 function call: ",ifc2
    t=T(); integ_hand(param,0,1,1); hif=T()-t
    print "  hand inlined function call: ",hif
    print "        global function call %010.10f %010.10f %010.10f %010.10f %010.10f"%(gf  /gf  ,gf  /lf  ,gf  /ifc ,gf  /ifc2,gf  /hif )
    print "         local function call %010.10f %010.10f %010.10f %010.10f %010.10f"%(lf  /gf  ,lf  /lf  ,lf  /ifc ,lf  /ifc2,lf  /hif )
    print "       inlined function call %010.10f %010.10f %010.10f %010.10f %010.10f"%(ifc /gf  ,ifc /lf  ,ifc /ifc ,ifc /ifc2,ifc /hif )
    print "      inlined2 function call %010.10f %010.10f %010.10f %010.10f %010.10f"%(ifc2/gf  ,ifc2/lf  ,ifc2/ifc ,ifc2/ifc2,ifc2/hif )
    print "  hand inlined function call %010.10f %010.10f %010.10f %010.10f %010.10f"%(hif /gf  ,hif /lf  ,hif /ifc ,hif /ifc2,hif /hif )

import profile
def longt(n):
    for i in range(n):
        g=macro.expand_these(integ_global,f=f2)

def p(n):
    pr = profile.Profile()
    pr.runctx('longt(%d)'%n,globals(),locals())
    pr.print_stats()
