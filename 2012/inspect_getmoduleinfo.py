#!/usr/bin/env python

import imp
import inspect
import sys

# Module #
filename = sys.argv[1] if len(sys.argv) >= 2 else 'sample_module.pyc'
try:
    (name, suffix, mode, mtype) = inspect.getmoduleinfo(filename)
except TypeError:
    print 'Could not determine module type of %s' % filename
else:
    mtype_name = { imp.PY_SOURCE:'source',
                   imp.PY_COMPILED:'compiled',
                   }.get(mtype, mtype)
    mode_description = { 'rb':'(read-binary)',
                         'U':'(universal newline)',
                         }.get(mode, '')
    print 'NAME   :', name
    print 'SUFFIX :', suffix
    print 'MODE   :', mode, mode_description
    print 'MTYPE  :', mtype_name

print
import inspect
import sample_module
for name, data in inspect.getmembers(sample_module):
    if name != '__builtins__':
        print '%s :' % name, repr(data)

print
# or, for only classes
for name, data in inspect.getmembers(sample_module, inspect.isclass):
    print '%s :' % name, repr(data)

# Class #
print
import inspect
from pprint import pprint
import sample_module

# not found => NameError
# no filtering => shows the attributes, methods, slots, and other members of the class
pprint(inspect.getmembers(sample_module.A))

# interrogate methods
pprint(inspect.getmembers(sample_module.A, inspect.ismethod))
pprint(inspect.getmembers(sample_module.B, inspect.ismethod))

# documentation strings
import inspect
import sample_module

print 'B.__doc__:'
print sample_module.B.__doc__
print
print 'getdoc(B):'
# getdoc(): __doc__ attribute with tabs expanded to spaces and with indentation made uniform
print inspect.getdoc(sample_module.B)

##############################################################################
# disabled: only if source is available
##############################################################################
# comments
print inspect.getcomments(sample_module.B.do_something)
# returns first comment in module 
print inspect.getcomments(sample_module)
# retrieving source
try:
    print inspect.getsource(sample_module.A.get_name)
    # pass in class => all methods of class included in output
    pprint.pprint(inspect.getsourcelines(sample_module.A.get_name))
except IOError, e:
    print e
##############################################################################

# module and function arguments
# complete specification of the arguments the callable takes, including default values
# getargspec(): returns list of positional argument names, the name of any variable positional arguments (e.g., *args), names of any variable named arguments (e.g., **kwds), and default values for the arguments.
# If there are default values, they match up with the end of the positional argument list.
arg_spec = inspect.getargspec(sample_module.module_level_function)
print 'NAMES   :', arg_spec[0]
print '*       :', arg_spec[1]
print '**      :', arg_spec[2]
print 'defaults:', arg_spec[3]

# first argument, arg1, does not have a default value. The single default therefore is matched up with arg2
args_with_defaults = arg_spec[0][-len(arg_spec[3]):]
print 'args & defaults:', zip(args_with_defaults, arg_spec[3])

# class hierarchies
import inspect
import sample_module

class C(sample_module.B):
    pass
class D(C, sample_module.A):
    pass
def print_class_tree(tree, indent=-1):
    if isinstance(tree, list):
        for node in tree:
            print_class_tree(node, indent+1)
    else:
        print '  ' * indent, tree[0].__name__
    return

if __name__ == '__main__':
    print 'A, B, C, D:'
    print_class_tree(inspect.getclasstree([sample_module.A, sample_module.B, C, D]))
    print_class_tree(inspect.getclasstree([sample_module.A, sample_module.B, C, D], unique=True,))

# method resolution order (MRO)
# demonstrates the "depth-first" nature of the MRO search
# For B_First, A also comes before C in the search order, because B is derived from A
import inspect
import sample_module
class C(object):
    pass
class C_First(C, sample_module.B):
    pass
class B_First(sample_module.B, C):
    pass
print 'B_First:'
for c in inspect.getmro(B_First):
    print '\t', c.__name__
print
print 'C_First:'
for c in inspect.getmro(C_First):
    print '\t', c.__name__

# inspect (code obj +) RTE
# work with call stack
# operate on call frames
# each frame record in the stack is:
#   (frame obj, filename, line no., fn name, context list, context index)
# used to build tracebacks during exceptions raised
# or during debugging, to interrogate argument values
import inspect
def recurse(limit):
    local_variable = '.' * limit
    # getargvalues(): returns (arg name, varargs, local frame values)
    # currentframe(): frame @ stack top, for current function
    print limit, inspect.getargvalues(inspect.currentframe())
    if limit <= 0:
        return
    recurse(limit - 1)
    return
if __name__ == '__main__':
    recurse(3)

# stack(): access all stack frames from current frame -> first caller
# prints stack information at end of recursion
import inspect

def recurse(limit):
    local_variable = '.' * limit
    if limit <= 0:
        for frame, filename, line_num, func, source_code, source_index in inspect.stack():
            print '%s[%d]\n  -> %s' % (filename, line_num, source_code[source_index].strip())
            print inspect.getargvalues(frame)
            print
        return
    recurse(limit - 1)
    return

if __name__ == '__main__':
    recurse(3)

# others: trace(), getouterframes(), and getinnerframes()
