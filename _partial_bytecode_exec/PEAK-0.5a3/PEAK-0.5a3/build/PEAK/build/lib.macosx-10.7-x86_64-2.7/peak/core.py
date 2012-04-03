"""PEAK's Core API

 This module provides easy access to PEAK's core API's and modules.

 For each of the 'binding', 'config', 'model', and 'naming' packages, this
 module exports that package's 'api' module under the corresponding name, using
 a lazy import.  Thus 'from peak.core import binding' will give you a lazily
 imported version of the 'peak.binding.api' module.  This allows you to get
 quick, easy access to the PEAK core API, without complex import patterns, but
 also without a lot of namespace pollution.

 In addition to the lazily-imported modules, 'peak.core' also exports
 the following objects for convenience in interacting with PEAK's APIs:

    'NOT_GIVEN' and 'NOT_FOUND' -- Singleton values used for convenience
        in dealing with non-existent parameters or dictionary/cache entries

    'Items()' -- a convenience function that produces a 'dict.items()'-style
        list from a mapping and/or keyword arguments.

    'PropertyName' -- a string subclass with restricted syntax, that's useful
        for creating configuration keys.  Using property names as configuration
        keys makes it easy to create hierarchical configuration namespaces and
        define them in .ini files (similar to 'peak.ini').

    'adapt()' -- the PEP 246 'adapt()' function.

    'protocols' -- the PyProtocols 'protocols' module.
"""

from __future__ import generators
import protocols
from protocols import adapt

__all__ = [
    'adapt', 'protocols', 'NOT_GIVEN', 'NOT_FOUND', 'Items',    # Primitives
    'PropertyName', 'binding', 'config', 'model', 'naming',     # Core
    'exceptions',
]


from peak.util.imports import lazyModule, whenImported

binding     = lazyModule('peak.binding.api')
config      = lazyModule('peak.config.api')
model       = lazyModule('peak.model.api')
naming      = lazyModule('peak.naming.api')
exceptions  = lazyModule('peak.exceptions')

from peak.util.symbols import NOT_GIVEN, NOT_FOUND
































def Items(mapping=None, **kwargs):

    """Convert 'mapping' and/or 'kwargs' into a list of '(key,val)' items

        Key/value item lists are often easier or more efficient to manipulate
        than mapping objects, so PEAK API's will often use such lists as
        a preferred parameter format.  Sometimes, however, the syntactic sugar
        of keyword items, possibly in combination with an existing mapping
        object, is desired.  In those cases, the 'Items()' function can be
        used .

        'Items()' takes an optional mapping and optional keyword arguments, and
        returns a key/value pair list that contains the items from both the
        mapping and keyword arguments, with the keyword arguments taking
        precedence over (i.e. being later in the list than) the mapping items.
    """

    if mapping:

        i = mapping.items()

        if kwargs:
            i.extend(kwargs.items())

        return i

    elif kwargs:
        return kwargs.items()

    else:
        return []










import re
pnameValidChars = re.compile( r"([-+*?!:._a-z0-9]+)", re.I ).match

class PropertyName(str):

    """Name of a configuration property, usable as a configuration key"""

    def __new__(klass, value, protocol=None):

        self = super(PropertyName,klass).__new__(klass,value)
        valid = pnameValidChars(self)
        vend = valid and valid.end() or 0
        if vend<len(self):
            raise exceptions.InvalidName(
                "Invalid characters in property name", self
            )

        parts = self.split('.')

        if '' in parts or not parts:
            raise exceptions.InvalidName("Empty part in property name", self)

        if '*' in self:
            if '*' not in parts or parts.index('*') < (len(parts)-1):
                raise exceptions.InvalidName(
                    "'*' must be last part of wildcard property name", self
                )


        if '?' in self:
            if '?' in parts or self.index('?') < (len(self)-1):
                    raise exceptions.InvalidName(
                        "'?' must be at end of a non-empty part", self
                    )

        return self





    def isWildcard(self):
        return self.endswith('*')

    def isDefault(self):
        return self.endswith('?')

    def isPlain(self):
        return self[-1:] not in '?*'


    def lookupKeys(self):

        yield self

        if not self.isPlain():
            return

        name = self

        while '.' in name:
            name = name[:name.rindex('.')]
            yield name+'.*'

        yield '*'
        yield self
        yield self+'?'


    def registrationKeys(self,depth=0):
        return (self,depth),











    def parentKeys(self):

        name = self

        if '.' in name:
            yield name[:self.rindex('.')]       # foo.bar.baz -> foo.bar

        while '.' in name:
            name = name[:name.rindex('.')]      # foo.bar.XXX -> foo.bar.*
            yield name+'.*'

        yield '*'


    def asPrefix(self):

        p = self

        if not self.isPlain():
            p=p[:-1]

        if p and not p.endswith('.'):
            p=p+'.'

        return p


    def __call__(self, forObj=None, default=NOT_GIVEN):
        from peak.config.api import lookup
        return lookup(forObj, self, default)


    def of(self, forObj):
        from peak.config.config_components import Namespace
        return Namespace(self, forObj)


    def __repr__(self):
        return 'PropertyName(%s)' % super(PropertyName,self).__repr__()


    def fromString(klass, value, keep_wildcards=False, keep_empties=False):

        value = str(value)

        if not keep_wildcards:
            value = value.replace('?','_').replace('*','_')

        if not keep_empties:
            value = '.'.join(filter(None,value.split('.')))

        while 1:
            valid = pnameValidChars(value)
            vend = valid and valid.end() or 0
            if vend<len(value):
                # Force-fit the character and loop
                value = value[:vend] + '_'+ value[vend+1:]
            else:
                break
        return klass(value)

    fromString = classmethod(fromString)


# If/when we use 'peak.config', declare that PropertyName supports IConfigKey
# and that it adapts strings to IConfigKey

whenImported('peak.config.interfaces',

    lambda interfaces:  (
        protocols.declareImplementation(
            PropertyName, instancesProvide=[interfaces.IConfigKey]
        ),

        protocols.declareAdapter(
            PropertyName,
            provides=[interfaces.IConfigKey],
            forTypes=[str]
        )
    )
)

