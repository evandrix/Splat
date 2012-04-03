"""Declaration support for Zope Interfaces"""

__all__ = []

from types import ClassType

from adapters import *
from api import declareImplementation, advise, adapt
from interfaces import IOpenProtocol, Protocol
from advice import metamethod, supermeta


# Monkeypatch Zope Interfaces

try:
    import zope.interface as zi

except ImportError:
    ZopeInterfaceTypes = []
    zi = None

else:

    def __adapt__(self, obj):
        return adapt(self,IOpenProtocol).__adapt__(obj)

    zi.Interface.__class__.__adapt__ = __adapt__
    ZopeInterfaceTypes = [zi.Interface.__class__]

    del __adapt__











# Adapter for Zope X3 Interfaces

class ZopeInterfaceAsProtocol(StickyAdapter, Protocol):

    advise(
        instancesProvide=[IOpenProtocol],
        asAdapterForTypes=ZopeInterfaceTypes,
    )

    attachToProtocols = IOpenProtocol,


    def __init__(self, ob, proto):
        StickyAdapter.__init__(self,ob, proto)
        Protocol.__init__(self)


    def __adapt__(self, obj):
        if self.subject.isImplementedBy(obj):
            return obj
        return supermeta(ZopeInterfaceAsProtocol,self).__adapt__(obj)


    def registerImplementation(self,klass,adapter=NO_ADAPTER_NEEDED,depth=1):

        if adapter is NO_ADAPTER_NEEDED:
            zi.classImplements(klass, self.subject)

        elif adapter is DOES_NOT_SUPPORT:
            ifaces = zi.Declaration(
                [i.__iro__ for i in zi.implementedBy(klass)]
            ) - self.subject
            zi.classImplementsOnly(klass, ifaces)

        return supermeta(ZopeInterfaceAsProtocol,self).registerImplementation(
            klass,adapter,depth
        )

    registerImplementation = metamethod(registerImplementation)


    def registerObject(self, ob, adapter=NO_ADAPTER_NEEDED, depth=1):

        if adapter is NO_ADAPTER_NEEDED:
            zi.directlyProvides(ob,self.subject)

        elif adapter is DOES_NOT_SUPPORT:
            zi.directlyProvides(ob, zi.directlyProvidedBy(ob)-self.subject)

        return supermeta(ZopeInterfaceAsProtocol,self).registerObject(
            ob, adapter, depth
        )

    registerObject = metamethod(registerObject)


    def getImpliedProtocols(self):
        protos = super(ZopeInterfaceAsProtocol,self).getImpliedProtocols()
        return list(protos) + [
            (i,(NO_ADAPTER_NEEDED,1)) for i in self.subject.__bases__
                if i is not zi.Interface
        ]


    def __getstate__(self):
        state = self.__dict__.copy()
        del state['_Protocol__lock']        # locks can't be pickled
        del state['_Protocol__listeners']   # and neither can weakref dict
        return state

    def __hash__(self):
        return hash(self.subject)

    def __cmp__(self,other):
        return cmp(self.subject, other)





