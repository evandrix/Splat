#!/usr/bin/env python
# -*- coding: utf-8 -*-
from headers   import *
#############################################################################
# Import Python module bytecode
try:
    MODULE_UNDER_TEST = __import__(MODULE_UNDER_TEST)
except ImportError, ie:
    print >> sys.stderr, "Module %s cannot be imported" % MODULE_UNDER_TEST
#############################################################################
# Class definitions
print ">> Scanning for class definitions..."
classes = getmembers(MODULE_UNDER_TEST, isclass)
# methods within classes
for label, klass in classes:
    print "\t", label, klass
    for item in getmembers(klass, ismethod):
        print "\t\t", item
print
#############################################################################
# Top level functions
functions = getmembers(MODULE_UNDER_TEST, isfunction)
print ">> Scanning for top level functions..."
print "\t",
pprint(functions)
print
#############################################################################
# Type sanity checking
print ">> Verifying class types..."
for label, klass in classes:
    if type(klass) is types.TypeType:
        print "\tNEW-STYLE:", klass
    elif type(klass) is types.ClassType:
        print "\tOLD-STYLE:", klass
print
#############################################################################
print >> sys.stderr, FAIL + \
    ("*** Total time: %.3f seconds ***" % (time.time() - t0)) + ENDC
del MODULE_UNDER_TEST   # cleanup
sys.exit(0)
#############################################################################
# Unused functions
"""
    isinstance()
        - works on old-style classes
        - need to know type before calling
        - legit type-checking against a known class
    __class__
        - works on old-style classes
        - no need to know type before calling
        - use for debugging: no idea what class the instance is
    issubclass()
"""
"""
    keywords = re.split('\.', code)
    arg = None
    for idx, keyword in enumerate(keywords):
        if fn_name in keyword:
            arg = keywords[idx-1]
    pos = [ i for i,x in enumerate(args) if x == arg ][0]
    for name, fragment in classes:
        if hasattr(fragment, fn_name):
            for class_name in context:
                if isinstance(class_name, fragment):
                    arglist[pos] = class_name
"""
#############################################################################
