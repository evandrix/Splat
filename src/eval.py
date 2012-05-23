from math import *
user_func = raw_input("type a function: y = ")
for x in xrange(10):
	print "x = ", x , ", y = ", eval(user_func)
