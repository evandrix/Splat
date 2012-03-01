    # case 2: Custom wrapper parameter objects
    def f_noarg():
        return
    def f_varg(*args, **kwargs):
        return

    param_value_seq = [ None, 0, 0.0, '', f_noarg, f_varg ]
    #pprint([(i+1,x) for i,x in enumerate(param_value_seq)])
    #print    
    param_states = {}
    param_instantiated = set()
    arglist = [create_param_obj(index) for index,_ in enumerate(args)]

    def decorator(target):
        def wrapper(*args, **kwargs):
            #kwargs.update({'debug': True})
            #print '%s(args=%s, kwargs=%s)' % (target.__name__,args,kwargs)

            from cStringIO import StringIO
            import sys
            try:
                sys.stdout = mystdout = StringIO()
                target(*args, **kwargs)
            except Exception as e:
                raise e
            else:
                print >> sys.__stdout__, '\nProgram output:'
                #print >> sys.__stderr__, mystdout.getvalue()
            finally:
                sys.stdout = writer(sys.__stdout__)
            return target(*args, **kwargs)
        return wrapper

    fn = decorator(fn)
    num_iterations = 0
    while num_iterations < MAX_ITERATIONS:
        try:
            num_iterations+=1
            fn(*arglist)
        except TypeError as e:
            assert 'last_instantiated' in param_states
            obj, attr, index = param_states['last_instantiated']
            #print '>> ' + OKGREEN + 'TypeError' + ENDC + ':', e, (obj,attr,index,param_value_seq[index])
            err_param = re.split('^%d format: a number is required, not MyParam([0-9]+)$', e.message)[1:-1]
            if len(err_param):
                # TypeError encountered with this specific error message
                assert len(err_param) == 1
                err_param = int(err_param[0])
                sz_err_param = 'MyParam%d' % err_param
                
                if sz_err_param != obj.__class__.__name__:
                    # done instantiating old object
                    param_instantiated.add(obj)

                    param_instantiated.add(arglist[err_param-1])
                    for i,x in enumerate(param_value_seq):
                        if isinstance(x, int):
                            break
                    param_states[sz_err_param] = i
                    param_states['last_instantiated'] = (arglist[err_param-1], None, i)
                    arglist[err_param-1] = -1
                    continue

            exception_type, exception_value, tb = sys.exc_info()
            code = py.code.Traceback(tb)[-1]
            fn_name = code.name
            fn_frame = code.frame
            fn_code = fn_frame.code
            fn_lineno = code.lineno + 1
            #print code.getfirstlinesource(), code.locals, code.relline
            try:
                code = Code.from_code(obj.__dict__[attr].func_code)
                #pprint(code.code)
            except:
                pass
            del obj.__dict__[attr]  # retry with next argument in list
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
        else:
            print
            break

    print ">> Discovered parameters in %d / %d iterations..." % (num_iterations,MAX_ITERATIONS)
    print param_states
    print arglist
    print param_instantiated
    print
