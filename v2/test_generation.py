#!/usr/bin/env python
# -*- coding: utf-8 -*-
from headers   import *
#############################################################################
# Collect minimal (lazy) list of instances
print ">> Generating test context..."
context = []
for label, klass in classes:
    obj = params = None
    while True:
        try:
            obj = apply(klass, params)
        except TypeError, te:
            # try the empty class constructor first
            # then augment with None's
            if params is None:
                params = []
            else:
                params.append(None)
        else:
            # store complete object
            tobj = type('dummy', (object,), {}) # TestObject class
            tobj.ref_object      = obj
            tobj.num_ctor_params = len(params)
            context.append(tobj)
            break
assert len(context) == len(classes), \
    "Not all classes instantiated (lazily)!"
for cls in context:
    print "\t", [user_attribute for user_attribute in getmembers(cls)] 
print
#############################################################################
# Generating unit test suite
print ">> Writing out unit test suite to file..."
import simplejson
import pyparsing    # S-Expr
import pystache

class tmplObj:
    def __init__(self, idx):
        self.n = idx
objs = [ todict(tmplObj(i)) for i in xrange(3) ]
tmpl_context = {
    'a': context[0].ref_object,
    'b': objs
}

template_file = open("test_template.mustache", "r")
tmpl = template_file.read()
template_file.close()
rendered = pystache.render(tmpl, tmpl_context)
print rendered
fout = open("test_%s.py" % MODULE_UNDER_TEST.__name__, "w")
print >> fout, rendered
fout.close()
del fout
print ">> ...done!"
