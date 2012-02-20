#!/usr/bin/env python
# -*- coding: utf-8 -*-
from headers         import *
from part2_auxiliary import *
#############################################################################
def test_function(fn):
    print '\t%s.%s()...' % (MODULE_UNDER_TEST.__name__,name)
    print '\t', getargspec(fn)
    print
    args, varargs, keywords, defaults = getargspec(fn)

    # case 1: Nones
    arglist = [None] * len(args)    # correct # of args
    try:
        fn(*arglist)
    except (AttributeError) as ae:
        print OKGREEN + 'Missing field on argument' + ENDC + ':', ae
        generate_tests(arglist, ae)
    print

    # case 2: Custom wrapper parameter objects
    def f():
        return
    def g(a):
        print a
    def h(a,b,c):
        print a,b,c
    
    param_value_seq = [ None, 0, 0.0, '', f,g,h ]
    pprint([(i+1,x) for i,x in enumerate(param_value_seq)])
    print    
    param_states = {}
    param_instantiated = set()
    arglist = [create_param_obj(index) for index,_ in enumerate(args)]

    num_iterations = 0
    while num_iterations < 20:
        try:
            fn(*arglist)
        except TypeError as e:
            assert 'last_instantiated' in param_states
            obj, attr, index = param_states['last_instantiated']
            print '>> ' + OKGREEN + 'TypeError' + ENDC + ':', e, (obj,attr,index,param_value_seq[index])

            exception_type, exception_value, tb = sys.exc_info()
            code = py.code.Traceback(tb)[-1]
            fn_name = code.name
            fn_frame = code.frame
            fn_code = fn_frame.code
            fn_lineno = code.lineno + 1
            print code.getfirstlinesource(), code.locals, code.relline
            try:
                code = Code.from_code(obj.__dict__[attr].func_code)
                pprint(code.code)
            except:
                pass

            del obj.__dict__[attr]  # retry with next argument in list
            
            print
        except AttrError as e:
            lookup_key, obj, attr = str(e), e.target_object, e.missing_attr
            next_param_index = param_states.setdefault(lookup_key, 0);            
            if next_param_index >= len(param_value_seq):
                print ">> Exhausted possible arguments list for %s" % lookup_key
                break
            else:
                next_param = param_value_seq[next_param_index]
                param_states[lookup_key] += 1            
                param_states['last_instantiated'] = (obj, attr, next_param_index)
                setattr(obj, attr, next_param)
                param_instantiated.add(obj)
        except Exception as e:
            print "Unhandled exception:", e
        num_iterations+=1

    print
    print param_states, arglist, param_instantiated
#############################################################################
if __name__ == "__main__":
    try:
        MODULE_UNDER_TEST = __import__(MODULE_UNDER_TEST)
    except ImportError, ie:
        print >> sys.stderr, "Module %s cannot be imported" % MODULE_UNDER_TEST
    print ">> Testing global functions..."
    functions = getmembers(MODULE_UNDER_TEST, isfunction)
    test_function([fn for name,fn in functions if name == 'foo'][0])
    del MODULE_UNDER_TEST   # cleanup
    sys.exit(0)
