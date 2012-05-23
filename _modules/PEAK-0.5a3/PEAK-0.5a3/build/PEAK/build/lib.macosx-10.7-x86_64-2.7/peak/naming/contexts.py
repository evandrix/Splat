"""Base classes for naming contexts"""

from peak.api import *

from interfaces import *
from names import *

import spi

from peak.binding.components import Component, Make, Obtain, Require



__all__ = [
    'NameContext', 'AddressContext',
]

























class NameContext(Component):

    protocols.advise(
        instancesProvide = [IBasicContext],
        classProvides    = [IURLContextFactory]
    )

    parseURLs       = True
    creationParent  = Obtain(CREATION_PARENT, offerAs=[CREATION_PARENT])
    schemeParser    = Obtain(SCHEME_PARSER,   offerAs=[SCHEME_PARSER])

    compoundParser  = CompoundName
    compositeParser = CompositeName

    namingAuthority = Make( lambda self: self.schemeParser() )
    nameInContext   = Make( lambda self: self.compoundParser(()) )

    serializationProtocol = Require(
        "Protocol to adapt objects to before storing them"
    )

    def getURLContext(klass, parent, scheme, iface, componentName, **options):
        if klass.schemeParser.supportsScheme(scheme):
            return adapt(klass(parent, componentName, **options), iface, None)

    getURLContext = classmethod(getURLContext)















    def _resolveComposite(self, name, iface):

        # You should override this method if you want dynamic weak NNS
        # support; that is, if you want to mix composite names and compound
        # names and figure out dynamically when you've crossed over into
        # another naming system.

        if not name:
            # convert to compound (local) empty name
            return self._resolveLocal(self.compoundParser(()), iface)

        else:

            if isBoundary(name):    # /, x/
                return self._checkSupported(name, iface)

            local = toName(name[0], self.compoundParser, self.parseURLs)

            if len(name)==1:    # 'x'
                # Single element composite name doesn't change namespaces
                return self.resolveToInterface(local,iface)


            # '/y', 'x/y' -- lookup the part through the '/' and continue

            ctx = self[CompositeName((local,''))]
            res = adapt(ctx,IResolver,None)

            if res is not None:
                return res.resolveToInterface(name[1:], iface)

            raise exceptions.NotAContext(
                "Unsupported interface", iface,
                resolvedObj=ctx, remainingName=name[1:]
            )






    def _checkSupported(self, name, iface):

        ctx = adapt(self, iface, None)

        if ctx is not None:
            return ctx, name

        raise exceptions.NotAContext(
            "Unsupported interface", iface,
            resolvedObj=self, remainingName=name
        )






























    def _resolveLocal(self, name, iface):

        if len(name)<2:
            return self._checkSupported(name, iface)

        try:
            ctx = self[name[:1]]
            res = adapt(ctx,IResolver,None)
            if res is not None:
                return res.resolveToInterface(name[1:],iface)

        except exceptions.NotAContext:
            pass

        # It wasn't a resolver, or didn't support the target interface,
        # so fall back to self and name, if possible.

        return self._checkSupported(name, iface)




    def _resolveURL(self, name, iface):

        auth, nic = name.getAuthorityAndName()
        diff = nic - self.nameInContext

        if self.namingAuthority == auth and diff is not None:
            return self.resolveToInterface(diff, iface)

        else:
            ctx = self.__class__(self, namingAuthority=auth)
            return ctx.resolveToInterface(nic, iface)








    def resolveToInterface(self, name, iface=IBasicContext):

        name = toName(name, self.compositeParser, self.parseURLs)

        if name.nameKind == COMPOSITE_KIND:
            return self._resolveComposite(name, iface)

        elif name.nameKind == COMPOUND_KIND:
            name = self.compoundParser(name)        # ensure syntax is correct
            return self._resolveLocal(name,iface)   # resolve locally


        # else name.nameKind == URL_KIND

        parser = self.schemeParser

        if parser:

            if isinstance(name, parser):
                return self._resolveURL(name,iface)

            elif parser.supportsScheme(name.scheme):
                return self._resolveURL(
                    parser(name.scheme, name.body), iface
                )

        # Delegate to the appropriate URL context

        ctx = spi.getURLContext(self, name.scheme, iface)

        if ctx is None:
            raise exceptions.InvalidName(
                "Unknown scheme %s in %r" % (name.scheme,name)
            )

        return ctx.resolveToInterface(name,iface)





    def _contextNNS(self):
        return NNS_Reference( self )


    def _get_nns(self, name, retrieve=1):

        if not name:
            return self._contextNNS()

        ob = self._get(name, retrieve)

        if ob is NOT_FOUND or not retrieve:
            return ob

        state = ob

        ob = self._deref(state, name)

        if isinstance(ob, self.__class__):
            # Same or subclass, must not be a junction;
            # so delegate the NNS lookup to it
            return ob._contextNNS()

        else:
            res = adapt(ob, IResolver, None)    # XXX introspection!
            if res is ob:
                # it's a context, so let it go as-is
                return state

        # Otherwise, wrap it in an NNS_Reference
        return NNS_Reference( ob )


    def close(self):
        pass






    def _deref(self, state, name):

        ob = adapt(state, IState, None)

        if ob is not None:
            return ob.restore(self, name)

        return state


    def _mkref(self, obj, name):
        return adapt(obj, self.serializationProtocol)





























    def lookupLink(self, name):

        """Return terminal link for 'name'"""

        ctx, name = self.resolveToInterface(name)
        if ctx is not self: return ctx.lookupLink(name)

        if isBoundary(name):
            state = self._get_nns(self.compoundParser(name[0]))
        else:
            state = self._get(name)

        if state is NOT_FOUND:
            raise exceptions.NameNotFound(
                remainingName=name, resolvedObj=self
            )

        if adapt(state,LinkRef,None) is not None:   # XXX introspection!
            return state

        return self._deref(state, name)


    def __getitem__(self, name):

        """Lookup 'name' and return an object"""

        ctx, name = self.resolveToInterface(name)
        if ctx is not self: return ctx[name]

        obj = self._getOb(name)

        if obj is NOT_FOUND:
            raise exceptions.NameNotFound(
                remainingName=name, resolvedObj=self
            )

        return obj



    def get(self, name, default=None):

        """Lookup 'name' and return an object, or 'default' if not found"""

        ctx, name = self.resolveToInterface(name)
        if ctx is not self: return ctx.get(name,default)

        return self._getOb(name, default)


    def __contains__(self, name):
        """Return a true value if 'name' has a binding in context"""

        ctx, name = self.resolveToInterface(name)

        if ctx is not self:
            return name in ctx

        if isBoundary(name):
            return self._get_nns(self.compoundParser(name[0]), False
                ) is not NOT_FOUND

        return self._get(name, False) is not NOT_FOUND


    def lookup(self, name, default=NOT_GIVEN):
        """Lookup 'name' --> object; synonym for __getitem__"""
        if default is NOT_GIVEN:
            return self[name]
        else:
            return self.get(name,default)

    def has_key(self, name):
        """Synonym for __contains__"""
        return name in self

    def keys(self):
        """Return a sequence of the names present in the context"""
        return [name for name in self]


    def items(self):
        """Return a sequence of (name,boundItem) pairs"""
        return [ (name,self._getOb(name, None)) for name in self ]


    def info(self):
        """Return a sequence of (name,refInfo) pairs"""
        return [ (name,self._get(name,False))
                    for name in self
        ]


    def bind(self, name, object):

        """Synonym for __setitem__, with attribute support"""

        self.__setitem__(name,object)


    def unbind(self, name, object):

        """Synonym for __delitem__"""

        del self[name]


    def _getOb(self, name, default=NOT_FOUND):

        if isBoundary(name):
            state = self._get_nns(self.compoundParser(name[0]))
        else:
            state = self._get(name)

        if state is NOT_FOUND: return default
        return self._deref(state, name)






    def rename(self, oldName, newName):

        """Rename 'oldName' to 'newName'"""

        oldCtx, n1 = self.resolveToInterface(oldName,IResolver)
        newCtx, n2 = self.resolveToInterface(newName,IResolver)

        if oldCtx.namingAuthority <> newCtx.namingAuthority or \
            crossesBoundaries(n1) or crossesBoundaries(n2):
                raise exceptions.InvalidName(
                    "Can't rename across naming systems", oldName, newName
                )

        n1 = oldCtx.nameInContext + n1
        n2 = newCtx.nameInContext + n2

        common = []
        for p1, p2 in zip(n1,n2):
            if p1!=p2: break
            common.append(p1)

        common = self.compoundParser(common)
        n1 = n1 - common
        n2 = n2 - common

        if self.namingAuthority<>oldCtx.namingAuthority or \
            (common-self.nameInContext) is None:

            ctx, base = self.resolveToInterface(
                oldCtx.namingAuthority + common, IWriteContext
            )

            if ctx is not self:
                ctx.rename(base+n1,base+n2)
                return

        else:
            base = common - self.nameInContext

        self._rename(base+n1, base+n2)

    def __setitem__(self, name, object):

        """Bind 'object' under 'name'"""

        ctx, name = self.resolveToInterface(name,IWriteContext)

        if ctx is not self:
            ctx[name]=object

        elif isBoundary(name):
            name = name[0]
            state = self._mkref(object,name)
            self._bind_nns(name, state)

        else:
            state = self._mkref(object,name)
            self._bind(name, state)


    def __delitem__(self, name):
        """Remove any binding associated with 'name'"""

        ctx, name = self.resolveToInterface(name,IWriteContext)

        if ctx is not self:
            del ctx[name]
        elif isBoundary(name):
            self._unbind_nns(name[0])
        else:
            self._unbind(name)











    # The actual implementation....

    def _get(self, name, retrieve=True):

        """Lookup 'name', returning 'NOT_FOUND' if not found

        If 'name' doesn't exist, always return 'NOT_FOUND'.  Otherwise,
        if 'retrieve' is true, return the bound state.

        If 'retrieve' is false, you may return any value other than
        'NOT_FOUND'.  This is for optimization purposes, to allow you to
        skip costly retrieval operations if a simple existence check will
        suffice."""

        raise NotImplementedError


    def __iter__(self):
        """Return an iterator of the names present in the context

        Note: must return names which are directly usable by _get()!  That is,
        ones which have already been passed through 'toName()' and/or
        'self.schemeParser()'.
        """
        raise NotImplementedError

    def _bind(self, name, state):
        raise NotImplementedError

    def _bind_nns(self, name, state):
        raise NotImplementedError

    def _unbind(self, name):
        raise NotImplementedError

    def _unbind_nns(self, name):
        raise NotImplementedError

    def _rename(self, old, new):
        raise NotImplementedError

class EmptyContext(NameContext):

    """A naming context that doesn't contain anything, but can handle URLs"""

    protocols.advise(
        instancesProvide = [IReadContext]
    )

    def _get(self, name, retrieve=True):
        return NOT_FOUND

    def __iter__(self):
        return iter(())




























class AddressContext(NameContext):

    """Handler for address-only URL namespaces"""


    def _get(self, name, retrieve=True):
        # All syntactically valid addresses exist in principle
        if hasattr(name, 'defaultFactory'):
            return Reference(name.defaultFactory, (name,))
        else:
            return name


    def _resolveURL(self, name, iface):

        # Since the URL contains all data needed, there's no need
        # to extract naming authority; just handle the URL directly

        return self._checkSupported(name, iface)



    def _resolveLocal(self, name, iface):

        # Convert compound names to a URL in this context's scheme

        return self.resolveToInterface(
            self.namingAuthority + name, iface
        )















