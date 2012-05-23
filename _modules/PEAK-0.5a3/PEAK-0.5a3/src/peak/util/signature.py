"""Crude introspection of call signatures"""

import protocols; from protocols import adapt, Interface
from inspect import getargspec
from types import FunctionType, MethodType

__all__ = 'ISignature', 'getPositionalArgs'


class ISignature(Interface):
    # XXX There should be a lot more here than this...

    def getPositionalArgs():
        """Return a sequence of positional argument names"""

    def getCallable():
        """Return the callable object"""


class FunctionAsSignature(protocols.Adapter):

    protocols.advise(
        instancesProvide=[ISignature],
        asAdapterForTypes=[FunctionType]
    )

    def getPositionalArgs(self):
        return getargspec(self.subject)[0]

    def getCallable(self):
        return self.subject










class MethodAsSignature(FunctionAsSignature):

    protocols.advise(
        instancesProvide=[ISignature],
        asAdapterForTypes=[MethodType]
    )

    def __init__(self, ob, proto):
        self.funcSig = adapt(ob.im_func, ISignature)
        self.offset = ob.im_self is not None
        self.subject = ob

    def getPositionalArgs(self):
        return self.funcSig.getPositionalArgs()[self.offset:]


def getPositionalArgs(ob):
    return adapt(ob,ISignature).getPositionalArgs()























