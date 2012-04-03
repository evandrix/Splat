import logging
import shelve

SAVE_FILE = ".pyregres.db"
mode = "train"

class TestResult(object):
	def __init__(self, name, result, args, kwargs):
		self.name = name
		self.args = args
		self.kwargs = kwargs
		self.result = result
		
	def __eq__(self, other):
		return self.name == other.name and \
			   self.params == other.params and \
			   self.result == other.result and \
			   self.args == other.args and \
			   self.kwargs == other.kwargs
	
	def __repr__(self):
		return "Name: " + self.name  + ", Result " + self.result

def _store(func, res, args, kwargs):
	test_result = TestResult(func.__name__, res, args, kwargs)
	func_name = func.__name__
	results = shelve.open(SAVE_FILE)
	if results.has_key(func_name):
		results[func_name].append(test_result)
	else:
		results[func_name] = [test_result]
	results.close()
	
def _retrieve(func, args, kwargs):
	results = shelve.open(SAVE_FILE)
	func_name = func.__name__
	if not results.has_key(func_name):
		raise Exception, "No results stored for this function"
	data = results[func_name]
	results.close()
	found = False
	for d in data:
		if args == d.args and kwargs == d.kwargs:
			return d
	if not found:
		raise Exception, "No results stored for function with these arguments"
		
def _process(func, res, args, kwargs):
	if mode == "train":
		_store(func, res, args, kwargs)
	else:
		old = _retrieve(func, args, kwargs)
		if old.result != res:
			raise Exception, "Value from %s differs from orginal run %s now is %s" % (func.__name__, old.result, res) 

def regres(func, *args, **kwargs):
	def wrapper(*args, **kwargs):
		res = func(*args, **kwargs)
		_process(func, res, args, kwargs)
		return res
	return wrapper

def run_regression(func, *args, **kwargs):
	global mode
	mode = "test"
	return func(*args, **kwargs)

#TODO:kwargs
def args_repr(args, kwargs):
	out = ""
	for arg in args:
		arg = arg.replace('\n', '\\n').replace('\r', '\\r')
		if isinstance(arg, str):
			out += "\"" + arg + "\""
		else:
			out += arg
	return out
	
def write_tests(filename):
	results = shelve.open(SAVE_FILE)
	output = "import unittest\n\n"
	for res in results.keys():
		saved_results = results[res]
		count = 1
		for res in saved_results:
			print res.args, res.kwargs
			output += "class Test" + res.name + str(count) + "(unittest.TestCase):\n\t"
			output += "def test_" + res.name + "(self):\n\t\t"
			output += "self.assertEquals(" + res.result + ", " 
			output += res.name + "("
			output += args_repr(res.args, res.kwargs) + "))"
			count += 1
	output += "\nif __name__ == \"__main__\":\n"
	output += "\tunittest.main()"
	print output
	results.close()
	
if __name__ == "__main__":
	write_tests("outtests.py")