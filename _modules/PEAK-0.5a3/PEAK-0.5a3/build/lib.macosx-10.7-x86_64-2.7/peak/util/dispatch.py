"""Closest-match rule-based dispatching, generic functions, and multimethods"""

from __future__ import generators
from types import ClassType
from peak.util.EigenData import EigenDict
from protocols import Interface, advise

__all__ = [
    'Dispatch', 'IRule', 'Signature', 'GenericFunction', 'MultiMethod',
    'DispatchError', 'NoMatchError', 'AmbiguousRulesError',
]


class DispatchError(TypeError):
    "Any method resolution error"

class NoMatchError(DispatchError,KeyError):
    "No match found"

class AmbiguousRulesError(DispatchError):
    "Ambiguous rules found"


class IRule(Interface):

    """Stylesheet-like matching rule"""

    def __contains__(value):
        """Return true if rule "matches" value"""

    def includesRule(otherRule):
        """Return true if values matching 'otherRule' match this one"""

    def __hash__():
        """Rules must be hashable, so they can be dictionary keys"""

    def __eq__(other):
        """Rules must be comparable, so they can be dictionary keys"""



def compareMatches((r1,res1),(r2,res2)):

    """Compare a pair of (rule,result) tuples in "most-specific first" order

    Designed primarily for use as a list.sort() "compare function", this
    function returns 1, 0, or -1, according to the order that the
    '(rule,result)' pairs should be ordered in.  Zero indicates that the
    rules are overlapping or equivalent, and therefore have no discernible
    ordering.  Note that this may cause problems when sorting rules which
    are disjoint (non-overlapping), if the sorting algorithm assumes equality
    is transitive!  For its use in this module, however, it is always sorting
    a list of rules that have all matched the same value, which means that
    none of the rules are disjoint (since they must at least overlap in the
    area of the matched value).  Therefore, either all rules are overlapping
    (and thus equal) or one or more rules are "more specific" than any of
    the overlapping rules.  This suffices for sorting matches, since we
    want all the unambiguous matches first, followed by the ambiguous ones.
    (There may also be some "less specific" rules that encompass the
    ambiguous ones, but since we fail at the first ambiguity, this is
    unimportant."""

    # A lot of doc for such a simple function!
    return cmp(r1.includesRule(r2), r2.includesRule(r1))

    # Truth table:
    #
    # r1 includes r2  r2 includes r1    Result
    # --------------  --------------    ------
    #     False          False           0 (disjoint or overlapping)
    #     False           True          -1 (r1 is more specific and goes first)
    #      True          False           1 (r2 is more specific and goes first)
    #      True           True           0 (r1 and r2 are equal)









def iterMatches(matches):
    """Iterate over sorted list of matches; fail at first ambiguity"""

    count = len(matches)
    last = count - 1

    p = 0
    while p<count:
        m = matches[p]
        if p<last and compareMatches(m, matches[p+1])==0:
            raise AmbiguousRulesError(
                "Overlapping rules", m[0], matches[p+1][0],
            )
        yield m[1]
        p += 1


























class Dispatch(object):

    """Mapping from rules to objects (slow, but simple)

    This is a generic rule-driven lookup table that finds the "closest matches"
    based on whether a supplied key matches rules in the table, returning
    results for the most-specific rules first.  It can be used to
    implement business rules, stylesheets, generic functions, multimethods,
    or anything else you can think of that needs prioritized rule-driven
    matching.  All you need are objects that implement the 'IRule' interface
    to act as rules, and the 'Dispatch' class automatically handles issues
    like overlapping rules.

    Note that 'Dispatch' objects are "write until read", so once you use
    a dispatch table to process an object, you can no longer change its rules.

    Usage::

        # Dispatcher that doesn't hold references to looked-up objects
        dispatcher = Dispatch(WeakKeyDictionary())
        dispatcher[aBusinesRule] = actionToTake

        # Retrieve action for closest match -- error if none found or ambiguous
        actionToTake = dispatcher[aBusinessObject].next()

    Performance

        The principal drawback of this class is speed.  Although lookups are
        cached, each new uncached lookup requires a loop over all the rules in
        the table, with each rule being asked to match the key being looked up.
        Then, the matching rules are sorted to put them in "closest-match-first"
        order, and this uses many function calls per comparison.

        However, for many simple applications of rule-based dispatching (such
        as multiple-dispatch of generic functions), where there aren't too many
        rules and even fewer that match on any given lookup, performance should
        be acceptable.  For more complex applications, you'll want a more
        sophisticated dispatcher that has internal indexes for its rules.  But,
        you can always use this dispatcher as a prototype to get the rest of
        your system figured out first."""

    newCache = dict

    def __init__(self, items=(), cache=None):

        """Create dispatcher from 'items', optionally supplying a lookup cache

        The default cache type for 'Dispatch' objects is a dictionary, so
        all values looked up are cached permanently - not a good idea for
        many applications.  You can change this by supplying a cache object
        of your choice.  The cache must provide '__getitem__' and
        '__setitem__' methods.

        The 'items' parameter, if supplied, should be a sequence of
        '(rule,result)' tuples to initially populate the dispatcher."""

        if cache is None:
            cache = self.newCache()

        self.cache = cache
        self.rules = rules = EigenDict()

        for rule,result in items:
            rules[rule] = result


    def __setitem__(self, rule, result):
        """Store 'result' as output for 'rule'"""
        self.rules[rule] = result













    def __getitem__(self, key):

        """Return an iterator over the results for rules matching 'key'

        Raises 'NoMatchError' if no rules match 'key'.  The iterator will
        raise 'AmbiguousRulesError' if it is advanced to a point where match
        precedence is ambiguous.  This may be as early as the very first match,
        if there is no match which is unambiguously "closest" to 'key'."""

        try:
            matches = self.cache[key]

        except KeyError:

            matches = [
                (rule, result)
                for rule, result in self.rules.items()
                    if key in rule
            ]

            matches.sort(compareMatches)   # force sort by signatures
            self.cache[key] = matches

        if not matches:
            raise NoMatchError("No match found", key)

        return iterMatches(matches)














class Signature(tuple):

    """A rule that matches positional type signatures based on 'issubclass'

    A 'Signature' is a tuple of types or classes (i.e. "new-style" or
    "classic" classes) that represent the types of positional arguments
    to a function.  It implements the 'IRule' interface and can therefore
    be used as a rule in a 'Dispatch' instance (such as a 'GenericFunction'
    or 'MultiMethod').  A 'Signature' "matches" keys that are a sequence
    of the same length as itself, with every member of the sequence being
    the same as, or a subclass of, the corresponding member of the 'Signature'.

    Note that because signatures are tuples of classes, 'MultiMethod' and
    'GenericFunction' objects must always be called with a fixed number of
    positional arguments, although keyword arguments may optionally be
    supplied as well.  If you wish to support default arguments or want to
    supply keyword arguments that will be used as part of the dispatching,
    you'll need to create a wrapper function that supplies the defaults
    and accepts the keywords, then calls the 'MultiMethod' or 'GenericFunction'
    with the fixed positional arguments and any additional keyword arguments.
    """

    advise(
        instancesProvide=[IRule]
    )

    def __new__(klass, *typesOrClasses):

        """Signature(*typesOrClasses) -- create a new signature"""

        for t in typesOrClasses:
            if not isinstance(t,(type,ClassType)):
                raise DispatchError(
                    "Signatures must be made of types or classes", t
                )

        # Create a tuple-subclass instance from 'typesOrClasses'
        return super(Signature,klass).__new__(klass, typesOrClasses)



    def __contains__(self, value):

        """Does 'value' (a types tuple or 'Signature') match this signature?"""

        if len(value)<>len(self):
            raise DispatchError(
                "Can't compare signatures of different lengths", self, value
            )

        for (tS,tV) in zip(self,value):
            if tS is not tV and not issubclass(tV,tS):
                return False
        return True

    includesRule = __contains__


























class MultiMethod(Dispatch):

    """Callable dispatcher with support for chaining to "next closest" matches

    Usage::
        from peak.util.dispatch import MultiMethod, Signature

        class Foo: pass
        class Bar(Foo): pass
        class Baz(Foo): pass

        spam = MultiMethod()
        spam[Signature(Foo,Bar)] = lambda next,x,y: "foobar, "+next()(next,x,y)
        spam[Signature(Foo,Foo)] = lambda next,x,y: "foofoo"

        print spam(Foo(),Bar())    # prints "foobar, foofoo"
        print spam(Baz(),Baz())    # prints "foofoo"

    'MultiMethod' calls the function whose 'Signature' is closest to the
    classes of the supplied arguments, inserting an extra 'next' argument at
    the front of the arguments.  The 'next' argument can be called to retrieve
    the "next closest" function matching the signature, in much the way that
    'super' can be used to find a superclass method.  Note that this extra
    argument must be included in the definition of the functions used
    with the 'MultiMethod', but should *not* included as part of the
    'Signature()' rules or supplied in the call to the 'MultiMethod' itself.
    """

    def __call__(self, *args, **kw):
        types = tuple([arg.__class__ for arg in args])
        next = self[types].next
        return next()(next, *args, **kw)









class GenericFunction(Dispatch):

    """Callable dispatcher that dispatches based on argument types

    Usage::

        from peak.util.dispatch import GenericFunction, Signature

        class Foo: pass
        class Bar(Foo): pass
        class Baz(Foo): pass

        floob = GenericFunction()
        floob[Signature(Foo,Bar)] = lambda x,y: "foo, bar"
        floob[Signature(Foo,Foo)] = lambda x,y: "foo, foo"

        print floob(Foo(),Bar())    # closest match is Foo, Bar
        print floob(Baz(),Baz())    # closes match is Foo, Foo

    'GenericFunction' calls the function whose 'Signature' is closest
    to the classes of the supplied arguments.  There is no way to
    call the "next closest" function.  (Note that although keyword
    arguments are passed through to the function, they cannot be
    used for dispatching.)
    """

    def __call__(self, *args, **kw):
        types = tuple([arg.__class__ for arg in args])
        return self[types].next()(*args, **kw)












if __name__ == '__main__':
    class Foo:      pass
    class Bar(Foo): pass
    class Baz(Foo): pass

    g = MultiMethod()
    g[Signature(Foo,Foo)] = lambda n,a,b: 'foofoo'
    g[Signature(Foo,Bar)] = lambda n,a,b: 'foobar'
    g[Signature(Bar,Foo)] = lambda n,a,b: 'barfoo'
    try:
        print 'Argtypes ', 'Result'
        print 'Foo, Foo:', g(Foo(), Foo())
        print 'Foo, Bar:', g(Foo(), Bar())
        print 'Bar, Foo:', g(Bar(), Foo())
        print 'Bar, Bar:', g(Bar(), Bar())
    except AmbiguousRulesError:
        print "Failed due to AmbiguousRulesError"
    print '\nAdding new method with signature (Bar, Bar)...'

    g = Dispatch()
    g[Signature(Foo,Foo)] = 'foofoo'
    g[Signature(Foo,Bar)] = 'foobar'
    g[Signature(Bar,Foo)] = 'barfoo'
    g[Signature(Bar,Bar)] = 'barbar'
    print 'Bar, Bar:', g[Bar, Bar].next()

    floob = GenericFunction()
    floob[Signature(Foo,Bar)] = lambda x,y: "foo, bar"
    floob[Signature(Foo,Foo)] = lambda x,y: "foo, foo"

    print floob(Foo(),Bar())    # closest match is Foo, Bar
    print floob(Baz(),Baz())    # closes match is Foo, Foo

    spam = MultiMethod()
    spam[Signature(Foo,Bar)] = lambda next,x,y: "foobar, " + next()(next,x,y)
    spam[Signature(Foo,Foo)] = lambda next,x,y: "foofoo"

    print spam(Foo(),Bar())    # prints "foobar, foofoo"
    print spam(Baz(),Baz())    # prints "foofoo"


