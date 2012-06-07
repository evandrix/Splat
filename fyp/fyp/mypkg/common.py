import sys
import time
import opcode
import decorator
import inspect

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
# fixed width binary representation (@goo.gl/7udcK)
def bin(x, width):
    return ''.join(str((x>>i)&1) for i in xrange(width-1,-1,-1))

@decorator.decorator
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
@decorator.decorator
def aspect_timer(f, *args, **kwargs):
    """ adds timing aspect to function """
    t0 = time.clock()
    f(*args, **kwargs)
    print >> sys.stderr, \
        "\r\n*** Total time: %.3f seconds ***" % (time.clock()-t0)
    return f

from blessings import Terminal
term = Terminal()
term_colors = {
    'black': term.black,
    'red': term.red,
    'green': term.green,
    'yellow': term.yellow,
    'blue': term.blue,
    'magenta': term.magenta,
    'cyan': term.cyan,
    'white': term.white,
}
def recursive_print(v, lvl):
    if isinstance(v, dict):
        print '{'
        counter = 0
        for _k,_v in v.iteritems():
            if counter <= 3:
                if inspect.isclass(_k):
                    print '\t'*lvl+term.bold_blue_on_bright_green(_k.__name__)+':',
                else:
                    print '\t'*lvl+term.bold_blue_on_bright_green(str(_k))+':',
                if any(map(lambda cls: isinstance(_v, cls), [list,set,dict])) and len(_v) > 1:
                    recursive_print(_v, lvl+1)
                else:
                    print _v
                counter += 1
            else:
                print '\t'*lvl+'...','['+str(len(v))+']'
                break
        print '\t'*(max(0,lvl-1))+'}'
    elif isinstance(v, set):
        print list(v)[0],'...','['+str(len(v))+']'
    elif isinstance(v, list):
        print v[0],'...','['+str(len(v))+']'
    else:
        print '<hidden>'
def debug(GLOBALS):
    if term.is_a_tty:
        print '===',term.underline('GLOBALS'), '==='
        for k,v in sorted(GLOBALS.iteritems()):
#            if k not in ['graph_fn_cfg']: continue
            if isinstance(v, basestring):
                print term.bold_cyan_on_bright_green(k) + ':',v
            else:
                print term.bold_cyan_on_bright_green(k) + ':',
                recursive_print(v,1)

