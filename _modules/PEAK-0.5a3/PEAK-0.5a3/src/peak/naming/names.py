from __future__ import generators

"""Name, Syntax, and Reference Objects"""

from peak.api import *

import re
from types import StringTypes
from urllib import unquote

from interfaces import *
from syntax import *
from arithmetic import *

from peak.binding.once import Activator, Make
from peak.util.imports import importObject
from peak.binding.interfaces import IComponentKey


__all__ = [
    'AbstractName', 'toName', 'CompositeName', 'CompoundName',
    'NNS_NAME', 'URLMatch', 'Reference', 'Indirect',
    'LinkRef', 'NNS_Reference', 'isBoundary', 'crossesBoundaries',
]


def isBoundary(name):
    return name and name.nameKind==COMPOSITE_KIND and len(name)<3 \
           and not name[-1]

def crossesBoundaries(name):
    return name and name.nameKind==COMPOSITE_KIND and ( len(name)>1
        or name and not name[0] )








class Indirect(object):

    """Indirect lookup via another IComponentKey

    Use this in e.g. 'binding.Obtain' to look up something indirectly, like::

        class MyClass(binding.Component):

            socketURL = "fd:0"

            socket = binding.Obtain(
                naming.Indirect('socketURL'), adaptTo=[IListeningSocket]
            )

    Instances of the above class will have a 'socket' attribute that is the
    result of looking up the URL provided by the instance's 'socketURL'
    attribute at runtime."""

    protocols.advise(
        instancesProvide = [IComponentKey]
    )

    __slots__ = 'key', 'default'

    def __init__(self, key, default=NOT_GIVEN):
        """Set up an 'Indirect' instance.  'key' must provide 'IComponentKey'
        """
        self.key = adapt(key,IComponentKey)
        self.default = default

    def findComponent(self, component, default=NOT_GIVEN):
        realKey = self.key.findComponent(component, self.default)
        return adapt(realKey,IComponentKey).findComponent(component,default)








class NameClass(type):

    """Support for name subclasses to adapt from strings"""

    def __adapt__(klass, ob):
        if isinstance(ob,StringTypes):
            return klass.mdl_fromString(ob)

    __adapt__ = protocols.metamethod(__adapt__)
































class AbstractName(tuple):

    __metaclass__ = NameClass

    protocols.advise(
        instancesProvide = [IPath]
    )

    nameKind    = None

    def __new__(klass, *args):

        if args:

            s = args[0]

            if isinstance(s,klass):
                return s

            elif isinstance(s,StringTypes):
                return klass.parse(s)

        return super(AbstractName,klass).__new__(klass,*args)

    def __str__(self):
        return self.format()

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, list(self))

    __add__  = name_add
    __sub__  = name_sub
    __radd__ = name_radd
    __rsub__ = name_rsub

    def __getslice__(self, *args):
        return self.__class__(
            super(AbstractName,self).__getslice__(*args)
        )


    # syntax-based methods

    syntax = UnspecifiedSyntax

    def format(self):
        return self.syntax.format(self)

    def parse(klass, name):
        return klass(klass.syntax.parse(name))

    parse = classmethod(parse)


    # IType methods

    def mdl_fromString(klass,aString):
        return klass.parse(aString)

    mdl_fromString = classmethod(mdl_fromString)


    def mdl_normalize(klass, value):
        return klass(value)

    mdl_normalize = classmethod(mdl_normalize)


    def findComponent(self, component, default=NOT_GIVEN):

        """Look the name up in context of component"""

        from api import lookup

        return lookup(
            component, self, default=default, creationParent=component
        )

    mdl_typeCode = None



class CompositeName(AbstractName):

    """A name whose parts may belong to different naming systems

        Composite name strings consist of name parts separated by forward
        slashes.  URL-encoding (%2F) is used to quote any slashes in each
        part.  Subclasses of 'CompositeName' may define a different
        'separator' attribute instead of '"/"', to use a different syntax."""

    nameKind = COMPOSITE_KIND
    separator = '/'

    def format(self):
        sep = self.separator
        enc = "%%%02X" % ord(sep)
        n = [str(s).replace(sep,enc) for s in self]

        if not filter(None,n):
            n.append('')

        return '/'.join(n)


    def parse(klass, name, firstPartType=None):

        # XXX Should we unescape anything besides separator?
        sep = klass.separator
        en1 = "%%%02X" % ord(sep)
        en2 = en1.lower()
        parts = [p.replace(en1,sep).replace(en2,sep) for p in name.split(sep)]

        if not filter(None,parts):
            parts.pop()

        if parts and firstPartType is not None:
            parts[0] = firstPartType(parts[0])
            if len(parts)==1: return parts[0]
        return klass(parts)

    parse = classmethod(parse)

class CompoundName(AbstractName):

    """A multi-part name with all parts in the same naming system"""

    nameKind = COMPOUND_KIND
    syntax   = FlatSyntax

    def asCompositeType(klass):

        """Get a 'CompositeName' subclass using this as first-element parser"""

        class _CompositeName(CompositeName):

            def mdl_fromString(_CNClass,aString):
                # Parse plain composite name, using this as compound parser
                name = CompositeName.parse(aString, klass)
                if isinstance(name, klass):
                    return CompositeName([name])
                return name

            mdl_fromString = classmethod(mdl_fromString)


            def mdl_normalize(_CNClass, value):
                if isinstance(value, klass):
                    # normalize compound as part of Composite
                    return CompositeName([value])
                return CompositeName(value)

            mdl_normalize = classmethod(mdl_normalize)


        return _CompositeName


    asCompositeType = classmethod(asCompositeType)





URLMatch = re.compile('([-+.a-z0-9]+):',re.I).match

def toName(aName, nameClass=CompoundName, acceptURL=1):

    """Convert 'aName' to a Name object

        If 'aName' is already a 'Name', return it.  If it's a string or
        Unicode object, attempt to parse it.  Returns an 'OpaqueURL' if
        'acceptURL' is set and the string is a URL (per RFC 1738).  Otherwise,
        use 'nameClass' to construct a Name object from the string.

        If 'aName' is neither a Name nor a string/Unicode object, an
        'exceptions.InvalidName' is raised.
    """

    if isinstance(aName,StringTypes):

        if acceptURL and URLMatch(aName):
            import URL
            return URL.Base.mdl_fromString(aName)

        return nameClass(aName)

    else:
        name = adapt(aName,IName,None)

        if name is not None:
            return name

    raise exceptions.InvalidName(aName)


NNS_NAME = CompositeName.parse('/',CompoundName)








class Reference(object):

    protocols.advise(
        instancesProvide = [IReference]
    )

    __slots__ = 'factoryName', 'addresses'

    def __init__(self, factoryName, addresses=()):
        self.factoryName = factoryName
        self.addresses = addresses

    def restore(self, context, name):
        factory = importObject(FACTORY_PREFIX.of(context)[self.factoryName])
        factory = adapt(factory, IObjectFactory)
        return factory.getObjectInstance(context, self, name)

    def __repr__(self):
        return "Reference(%r,%r)" % (self.factoryName, self.addresses)


class LinkRef(object):

    """Symbolic link"""

    protocols.advise(
        instancesProvide = [IState]
    )

    __slots__ = 'linkName'

    def __init__(self, linkName):
        self.linkName = linkName

    def __repr__(self):
        return "LinkRef(%s)" % `self.linkName`

    def restore(self, context, name):
        return context[self.linkName]


class NNS_Reference(object):

    """Next Naming System reference"""

    protocols.advise(
        instancesProvide = [IState]
    )

    __slots__ = 'relativeTo'

    def __init__(self, relativeTo):
        self.relativeTo = relativeTo

    def __repr__(self):
        return "NNS_Reference(%r)" % self.relativeTo

    def restore(self, context, name):
        # default is to treat the object as its own NNS
        return self.relativeTo






















