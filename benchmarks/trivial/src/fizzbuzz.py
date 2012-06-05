def f1(limit):
    for i in xrange(1,limit+1):print"FizzBuzz"[i*i%3*4:8--i**4%5]or i

def f2(limit):
    print '\n'.join(['Fizz'*(not i%3) + 'Buzz'*(not i%5) or str(i) for i in xrange(1, limit+1)])

def f3(limit):
    for x in xrange(limit): print x%3/2*'Fizz'+x%5/4*'Buzz' or x+1

def f4(limit):
    for i in xrange(1, limit+1):
	    if i%3==0 and i%5==0:
		    print "FizzBuzz"
	    elif i%5==0:
		    print "Buzz"
	    elif i%3==0:
		    print "Fizz"
	    else:
		    print i

def fizzbuzz(n):
    for i in xrange(n):
        if i % 15 == 0:
            print i, "fizzbuzz"
        elif i % 5 == 0:
            print i, "buzz"
        elif i % 3 == 0:
            print i, "fizz"
        else:
            print i

