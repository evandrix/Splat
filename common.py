#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import settings
from decorator import decorator

def todict(obj, classkey=None):
    """ Serialise object to dictionary, with optional 'classkey' """

    if isinstance(obj, dict):
        for k in obj.keys():
            obj[k] = todict(obj[k], classkey)
        return obj
    elif callable(obj):
        return obj.func_name
    elif hasattr(obj, "__iter__"):
        return [todict(v, classkey) for v in obj]
    elif hasattr(obj, "__dict__"):
        data = dict([(key, todict(value, classkey))
            for key, value in obj.__dict__.iteritems()])
        if classkey is not None and hasattr(obj, "__class__"):
            data[classkey] = obj.__class__.__name__
        return data
    else:
        return obj

# fixed width binary representation
# credits @ goo.gl/7udcK
def _bin(x, width):
    return ''.join(str((x>>i)&1) for i in xrange(width-1,-1,-1))

@decorator
def aspect_import_mut(f, *args, **kwargs):
    """ import module & adds it into the keyword arg namespace """
    try:
        if args:
            module = args[0].strip()
            if module.endswith(".pyc"):
                module = module[:-len(".pyc")]
            settings.MODULE_UNDER_TEST = module
        kwargs['module'] = __import__(settings.MODULE_UNDER_TEST)
    except ImportError as e:
        print >> sys.stderr, "Module %s cannot be imported" % settings.MODULE_UNDER_TEST
    return f(*args, **kwargs)

@decorator
def aspect_timer(f, *args, **kwargs):
    """ adds timing aspect to function """
    t0 = time.time()
    f(*args, **kwargs)
    print >> sys.stderr, \
        ("*** Total time: %.3f seconds ***" % (time.time()-t0))
    return f
