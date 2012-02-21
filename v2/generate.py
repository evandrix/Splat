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
