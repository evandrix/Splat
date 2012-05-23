import closure

g1 = g2 = g3 = g4 = g5 = 0

def func0(x):
    return x + 0 + 0 + 0 + 0 + 0

def func01(x):
    return x

def func1(x, g1=g1, g2=g2, g3=g3, g4=g4, g5=g5):
    return x + g1 + g2 + g3 + g4 + g5
    
def func2(x):
    return x + g1 + g2 + g3 + g4 + g5

func3 = closure.bind_now(func2)

def timing(func, args, n=1, **keywords) :
	import time
	time=time.time
	appl=apply
	if type(args) != type(()) : args=(args,)
	rep=range(n)
	before=time()
	for i in rep: res=appl(func, args, keywords)
	return round(time()-before,4), res

def test():
    res = [0,0,0,0,0]
    for i in range(10):
        res[0]=res[0]+timing(func0, 42, 100000)[0]
        res[1]=res[1]+timing(func01, 42, 100000)[0]
        res[2]=res[2]+timing(func1, 42, 100000)[0]
        res[3]=res[3]+timing(func2, 42, 100000)[0]
        res[4]=res[4]+timing(func3, 42, 100000)[0]
    print res
    
result = """
>>> test()
func1 (1.54, 42)
func2 (1.98, 42)
func2 (1.59, 42)
"""
