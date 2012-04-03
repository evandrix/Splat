"""Declaration support for Twisted Interfaces"""

__all__ = []

from adapters import *
from api import advise
from interfaces import IOpenProtocol
from weakref import WeakKeyDictionary

































# Twisted uses an approach to __adapt__ that is largely incompatible with
# PEP 246, so we have to jump through some twisty hoops to convince it to work
# for our purposes, without breaking Twisted's test suite.

class TwistedAdaptMethod(object):

    """__adapt__ implementation for Twisted interfaces"""

    __slots__ = 'iface'


    def __init__(self,iface):
        self.iface = iface


    def __call__(self, obj):

        # This is the __adapt__ method that you get
        # for ISomething.__adapt__()...

        if TwistedImplements(obj, self.iface):
            return obj

        # Get Twisted to try and adapt
        return self.iface(obj, None)


    def im_func(self, ob, default):

        # And this is what MetaInterface.__call__ calls when
        # it goes after __adapt__.im_func!

        meth = self.iface.__dict__.get('__adapt__')

        if meth is None:
            return default

        return meth(ob,default)



# Monkeypatch Twisted Interfaces

try:
    from twisted.python.components import \
        implements as TwistedImplements, \
        MetaInterface as TwistedInterfaceClass, \
        getInterfaces as TwistedGetInterfaces

except ImportError:
    TwistedInterfaceTypes = []

else:
    # Force all Twisted interfaces to have an __adapt__ method
    TwistedInterfaceClass.__adapt__ = property(lambda s: TwistedAdaptMethod(s))
    TwistedInterfaceTypes = [TwistedInterfaceClass]


























class TwistedInterfaceAsProtocol(object):

    __slots__ = 'iface'

    advise(
        instancesProvide=[IOpenProtocol],
        asAdapterForTypes=TwistedInterfaceTypes,
    )


    def __init__(self, iface, proto):
        self.iface = iface


    def __adapt__(self, obj):
        return self.iface.__adapt__(obj)


    def registerImplementation(self,klass,adapter=NO_ADAPTER_NEEDED,depth=1):

        oldImplements = TwistedGetInterfaces(klass)

        if adapter is NO_ADAPTER_NEEDED:
            klass.__implements__ = self.iface, tuple(oldImplements)

        elif adapter is DOES_NOT_SUPPORT:
            if self.iface in oldImplements:
                oldImplements.remove(self.iface)
                klass.__implements__ = tuple(oldImplements)

        else:
            raise TypeError(
                "Twisted interfaces can only declare support, not adapters",
                self.iface, klass, adapter
            )






    def addImpliedProtocol(self, proto, adapter=NO_ADAPTER_NEEDED, depth=1):

        iface = self.iface

        # XXX need to ensure 'proto' is usable w/Twisted!
        self.iface.adaptWith(lambda o: adapter(o, iface), proto)

        # XXX is the above sufficient?
        # XXX What are Twisted's adapter override semantics?

        listeners = iface.__dict__.get('_Protocol__listeners',{})

        for listener in listeners.keys():    # Must use keys()!
            listener.newProtocolImplied(self, proto, adapter, depth)


    def registerObject(self, ob, adapter=NO_ADAPTER_NEEDED, depth=1):

        oldImplements = TwistedGetInterfaces(ob)

        if adapter is NO_ADAPTER_NEEDED:
            ob.__implements__ = self.iface, tuple(oldImplements)

        elif adapter is DOES_NOT_SUPPORT:
            if self.iface in oldImplements:
                oldImplements.remove(self.iface)
                ob.__implements__ = tuple(oldImplements)

        else:
            raise TypeError(
                "Twisted interfaces can only declare support, not adapters",
                self.iface, ob, adapter
            )


    def addImplicationListener(self, listener):
        listeners = self.iface.__dict__.setdefault(
            '_Protocol__listeners',WeakKeyDictionary()
        )
        listeners[listener] = True

