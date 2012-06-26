import sys
import time
import decorator
import inspect
import itertools
import operator

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
        print >> sys.stderr, "Module %s cannot be imported" \
            % settings.MODULE_UNDER_TEST
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
                if any(map(lambda cls: isinstance(_v, cls), [list,set,dict])) \
                    and len(_v) > 1:
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

# itertools recipes
# @ http://docs.python.org/library/itertools.html
def take(n, iterable):
    "Return first n items of the iterable as a list"
    return list(islice(iterable, n))

def tabulate(function, start=0):
    "Return function(0), function(1), ..."
    return imap(function, count(start))

def consume(iterator, n):
    "Advance the iterator n-steps ahead. If n is none, consume entirely."
    # Use functions that consume iterators at C speed.
    if n is None:
        # feed the entire iterator into a zero-length deque
        collections.deque(iterator, maxlen=0)
    else:
        # advance to the empty slice starting at position n
        next(islice(iterator, n, n), None)

def nth(iterable, n, default=None):
    "Returns the nth item or a default value"
    return next(islice(iterable, n, None), default)

def quantify(iterable, pred=bool):
    "Count how many times the predicate is true"
    return sum(imap(pred, iterable))

def padnone(iterable):
    """Returns the sequence elements and then returns None indefinitely.

    Useful for emulating the behavior of the built-in map() function.
    """
    return chain(iterable, repeat(None))

def ncycles(iterable, n):
    "Returns the sequence elements n times"
    return itertools.chain.from_iterable(repeat(tuple(iterable), n))

def dotproduct(vec1, vec2, sum=sum, imap=itertools.imap, mul=operator.mul):
    return sum(imap(mul, vec1, vec2))

def flatten(listOfLists):
    "Flatten one level of nesting"
    return itertools.chain.from_iterable(listOfLists)

def repeatfunc(func, times=None, *args):
    """Repeat calls to func with specified arguments.

    Example:  repeatfunc(random.random)
    """
    if times is None:
        return starmap(func, repeat(args))
    return starmap(func, repeat(args, times))

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)

def grouper(n, iterable, fillvalue=None):
    "grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return izip_longest(fillvalue=fillvalue, *args)

def roundrobin(*iterables):
    "roundrobin('ABC', 'D', 'EF') --> A D E B F C"
    # Recipe credited to George Sakkis
    pending = len(iterables)
    nexts = cycle(iter(it).next for it in iterables)
    while pending:
        try:
            for next in nexts:
                yield next()
        except StopIteration:
            pending -= 1
            nexts = cycle(islice(nexts, pending))

def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return itertools.chain.from_iterable(itertools.combinations(s, r) for r in range(len(s)+1))

def unique_everseen(iterable, key=None):
    "List unique elements, preserving order. Remember all elements ever seen."
    # unique_everseen('AAAABBBCCDAABBB') --> A B C D
    # unique_everseen('ABBCcAD', str.lower) --> A B C D
    seen = set()
    seen_add = seen.add
    if key is None:
        for element in ifilterfalse(seen.__contains__, iterable):
            seen_add(element)
            yield element
    else:
        for element in iterable:
            k = key(element)
            if k not in seen:
                seen_add(k)
                yield element

def unique_justseen(iterable, key=None):
    "List unique elements, preserving order. Remember only the element just seen."
    # unique_justseen('AAAABBBCCDAABBB') --> A B C D A B
    # unique_justseen('ABBCcAD', str.lower) --> A B C A D
    return imap(next, imap(itemgetter(1), groupby(iterable, key)))

def iter_except(func, exception, first=None):
    """ Call a function repeatedly until an exception is raised.

    Converts a call-until-exception interface to an iterator interface.
    Like __builtin__.iter(func, sentinel) but uses an exception instead
    of a sentinel to end the loop.

    Examples:
        bsddbiter = iter_except(db.next, bsddb.error, db.first)
        heapiter = iter_except(functools.partial(heappop, h), IndexError)
        dictiter = iter_except(d.popitem, KeyError)
        dequeiter = iter_except(d.popleft, IndexError)
        queueiter = iter_except(q.get_nowait, Queue.Empty)
        setiter = iter_except(s.pop, KeyError)

    """
    try:
        if first is not None:
            yield first()
        while 1:
            yield func()
    except exception:
        pass

def random_product(*args, **kwds):
    "Random selection from itertools.product(*args, **kwds)"
    pools = map(tuple, args) * kwds.get('repeat', 1)
    return tuple(random.choice(pool) for pool in pools)

def random_permutation(iterable, r=None):
    "Random selection from itertools.permutations(iterable, r)"
    pool = tuple(iterable)
    r = len(pool) if r is None else r
    return tuple(random.sample(pool, r))

def random_combination(iterable, r):
    "Random selection from itertools.combinations(iterable, r)"
    pool = tuple(iterable)
    n = len(pool)
    indices = sorted(random.sample(xrange(n), r))
    return tuple(pool[i] for i in indices)

def random_combination_with_replacement(iterable, r):
    "Random selection from itertools.combinations_with_replacement(iterable, r)"
    pool = tuple(iterable)
    n = len(pool)
    indices = sorted(random.randrange(n) for i in xrange(r))
    return tuple(pool[i] for i in indices)
