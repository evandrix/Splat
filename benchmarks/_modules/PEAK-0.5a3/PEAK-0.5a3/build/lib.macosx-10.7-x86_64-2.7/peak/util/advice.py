from new import instancemethod
from peak.util.signature import ISignature, getPositionalArgs
import protocols






































class advice(object):

    """advice(func) -- "around advice" wrapper base class

        This wrapper is a base class for "around" advice on a method.  Just
        redefine the '__call__' method to have the desired semantics.  E.g.::

            class loggedMethod(advice):

                __slots__ = ()

                def __call__(self,*__args,**__kw):
                    print "Entering", self._func, __args, __kw
                    self._func(*__args,**__kw)
                    print "Leaving",self._func

            class someObject(object):

                def aMethod(self,foobly):
                    print foobly

                aMethod = loggedMethod(aMethod)

        If your advice needs parameters, you'll probably want to override
        '__init__()' as well, and add some slots as appropriate.  Note that
        the 'self' parameter to '__call__' is the *advice object*, not the
        'self' that will be passed through to the underlying function (which
        is the first item in '__args'.

        The 'advice' class tries to transparently emulate a normal Python
        method, and to be indistinguishable from such a method to inspectors
        like 'help()' and ZPublisher's 'mapply()'.  Because of this, if
        callers of a method need to know that it is being "advised", you
        should document this in your method's docstring.  There isn't any
        other way someone can tell, apart from reading your source or checking
        the 'type()' or '__class__' of the retrieved method's 'im_func'.

        Advice objects can be transparently stacked, so you can do things like
        'aMethod = loggedMethod( lockedMethod(aMethod) )' safely."""


    __slots__ = '_func'

    extraArgs = 0

    protocols.advise(instancesProvide = [ISignature])

    def __init__(self, func):
        self._func = func

    def getPositionalArgs(self):
        """Return a sequence of positional argument names"""
        return getPositionalArgs(self._func)[self.extraArgs:]

    def getCallable(self):
        return self

    def __get__(self,ob,typ):
        if typ is None: typ = ob.__class__
        return instancemethod(self, ob, typ)


    def __call__(self,*__args,**__kw):
        return self._func(*__args,**__kw)


    def __repr__(self):
        return `self._func`


    # Pass through any attribute requests to the wrapped object;
    # this will make us "smell right" to ZPublisher's 'mapply()' function.

    def __getattr__(self, attr):
        return getattr(self._func,attr)

    # __doc__ is a special case; our class wants to supply it, and so won't
    # let __getattr__ near it.

    __doc__ = property(lambda s: s._func.__doc__)










