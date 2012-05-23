from __future__ import generators
from peak.api import *
from interfaces import *
from peak.util.imports import whenImported
from protocols.advice import getMRO
from types import ClassType

__all__ = [
    'MultiKey', 'UnionOf', 'ProviderOf', 'FactoryFor',
]


def permuteLookup(seq, prev=None):
    if prev is None:
        for inner in seq:
            yield inner,
    else:
        seq = list(seq)
        for outer in prev:
            for inner in seq:
                yield outer+(inner,)


def permuteReg(seq, prev=None):
    if prev is None:
        for inner,d in seq:
            yield (inner,),d
    else:
        seq = list(seq)
        for outer,d1 in prev:
            for inner,d2 in seq:
                yield outer+(inner,), d1+d2









class Wrapper(object):

    __slots__ = 'subject','protocol'

    def __init__(self, ob, proto):
        self.subject = ob
        self.protocol = proto

    def __hash__(self):
        return hash(self.subject)

    def __cmp__(self,other):
        return cmp(self.subject,other)

    def __nonzero__(self):
        return self.subject and True or False

    def __repr__(self):
        return repr(self.subject)


class ClassAsConfigKey(Wrapper):

    """Adapt classes to configuration keys"""

    __slots__ = ()

    protocols.advise(
        instancesProvide=[IConfigKey],
        asAdapterForTypes=[type,ClassType],
    )

    def registrationKeys(self, depth=0):
        yield self.subject, depth

    def lookupKeys(self):
        return getMRO(self.subject)

    def parentKeys(self):
        return ()   # XXX maybe use modules?

class UnionOf(object):

    """Key that matches any of its subkeys"""

    __slots__ = 'keys'

    protocols.advise(
        instancesProvide=[IConfigKey],
    )

    def __new__(klass,*keys):
        if len(keys)==1:
            return adapt(keys[0],IConfigKey)
        return super(UnionOf,klass).__new__(klass,*keys)

    def __init__(self,*keys):
        self.keys = tuple([adapt(key,IConfigKey) for key in keys])

    def registrationKeys(self, depth=0):
        for key in self.keys:
            for k in key.registrationKeys(depth):
                yield k

    def lookupKeys(self):
        for key in self.keys:
            for k in key.lookupKeys():
                yield k

    def parentKeys(self):
        return ()

    def __repr__(self):
        return 'config.UnionOf'+repr(self.subject)








class MultiKey(Wrapper):

    __slots__ = ()

    protocols.advise(
        instancesProvide=[IConfigKey],
    )

    def __init__(self,*keys):
        self.subject = tuple([adapt(key,IConfigKey) for key in keys])

    def registrationKeys(self, depth=0):
        i = None
        for k in self.subject:
            i = permuteReg(k.registrationKeys(depth), i)
        for k,d in i:
            yield MultiKey(*k), d

    def lookupKeys(self):
        i = None
        for k in self.subject:
            i = permuteLookup(k.lookupKeys(), i)
        for k in i:
            yield MultiKey(*k)

    def parentKeys(self):
        return ()

    def __repr__(self):
        return 'config.MultiKey'+repr(self.subject)











def ProviderOf(iface, *classes):

    """Configuration key based on interface+class(es)

    Usage::

        key = config.ProviderOf(ISomething, Class1, Class2, ...)

    The example is equivalent to::

        key = config.MultiKey(ISomething, config.UnionOf(Class1, Class2, ...))

    In other words, the returned key is a two-element configuration key that
    matches the combination of the given interface and any of the given
    classes."""

    return config.MultiKey(iface, config.UnionOf(*classes))


def FactoryFor(iface):

    """Config key for an 'IComponentFactory' that returns 'iface' objects

    Usage::

        key = config.FactoryFor(ISomething)

    The example is equivalent to::

        key = config.MultiKey(binding.IComponentFactory, ISomething)
    """

    return config.MultiKey(binding.IComponentFactory,iface)








class InterfaceAsConfigKey(Wrapper):

    """Adapt interfaces to configuration keys"""

    __slots__ = ()

    protocols.advise(
        instancesProvide=[IConfigKey],
        asAdapterForTypes=[protocols.Interface.__class__],
    )

    def registrationKeys(self, depth=0):
        """Iterate over (key,depth) pairs to be used when registering"""

        yielded = {self.subject: 1}
        yield self.subject, depth

        depth += 1
        for base in self.subject.getBases():
            for item in adapt(base,IConfigKey).registrationKeys(depth):
                if item[0] not in yielded:
                    yield item
                    yielded[item[0]]=True

    def lookupKeys(self):
        """Iterate over keys that should be used for lookup"""
        return self.subject,

    def parentKeys(self):
        return ()

whenImported('zope.interface',
    lambda interface: (
        protocols.declareAdapter(
            InterfaceAsConfigKey, provides=[IConfigKey],
            forTypes = [interface.Interface.__class__]
        )
    )
)


class ImmutableConfig(object):

    def __init__(self, baseMaps=(), items=()):

        self.depth = depths = {}
        self.keysIndex = keysIndex = {}
        self.data = data = {}

        for base in baseMaps:
            adapt(base,ImmutableConfig)
            for key, depth in base.depth.items():
                old = depths.get(key,depth)
                if old>=depth:
                    data[key] = base.data[key]
                    depths[key] = depth

            for ns,keysMap in base.keysIndex.items():
                keysIndex.setdefault(ns,{}).update(keysMap)

        for configKey,value in items:

            for key,depth in adapt(configKey,IConfigKey).registrationKeys():

                if depths.get(key,depth)>=depth:

                    ckey = adapt(key, IConfigKey)

                    for k in ckey.parentKeys():
                        keysIndex.setdefault(k,{})[ckey] = True

                    data[key]=value
                    depths[key] = depth









    def lookup(self, configKey, failObj=None):
        data = self.data
        for key in configKey.lookupKeys():
            if key in data:
                return data[key]
        return failObj


    def _configKeysMatching(self, configKey):

        index = self.keysIndex

        if not index:
            return

        for key,depth in adapt(configKey,IConfigKey).registrationKeys():
            for k in index.get(key,()):
                yield k























