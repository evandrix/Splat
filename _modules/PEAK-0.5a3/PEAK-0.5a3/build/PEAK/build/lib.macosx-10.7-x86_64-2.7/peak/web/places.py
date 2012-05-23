from peak.api import *
from interfaces import *
from types import FunctionType, MethodType
import posixpath
from errors import NotFound, NotAllowed, WebException

__all__ = [
    'Traversable', 'Decorator', 'ContainerAsTraversable',
    'MultiTraverser', 'TraversalContext', 'Traversal',
]































class TraversalContext(binding.Component):

    protocols.advise(
        instancesProvide = [ITraversalContext]
    )

    previous    = binding.Obtain('..')
    interaction = binding.Obtain(IWebInteraction, offerAs=[IWebInteraction])
    traversable = binding.Require("Traversable being traversed")

    subject = binding.Make(
        lambda self: self.traversable.getObject(self.interaction),
        suggestParent=False
    )

    renderable = binding.Make(
        lambda self: adapt(self.subject, self.interaction.pageProtocol, None)
    )

    def checkPreconditions(self):
        """Invoked before traverse by web requests"""
        self.traversable.preTraverse(self)

    def subcontext(self, name, ob):
        ob = adapt(ob, self.interaction.pathProtocol)
        binding.suggestParentComponent(self.traversable, name, ob)
        return self.__class__.newCtx(self, name, traversable = ob)

    # newCtx = "this class"
    newCtx = binding.classAttr(binding.Obtain('.'))

    def substituteContext(self, ob):
        """Clone this context, but using 'ob' as the subject"""
        ob = adapt(ob, self.interaction.pathProtocol)
        return self.__class__(
            self.getParentComponent(),self.getComponentName(),
            traversable=ob, interaction=self.interaction,
        )



    def contextFor(self, name):
        """Return a new traversal context for 'name'"""

        if name == '..':
            if self.previous is None:
                return self
            return self.previous

        elif name=='.' or not name:
            return self

        try:
            ob = self.traversable.traverseTo(name, self)
        except WebException,v:
            v.traversedName = name
            raise
        return self.subcontext(name, ob)


    def render(self):
        """Return rendered value for context object"""

        page = self.renderable

        if page is None:
            # Render the found object directly
            return self.subject

        return page.render(self)












    absoluteURL = binding.Make(
        lambda self: self.traversable.getURL(self),
        doc = "Absolute URL of the current object"
    )

    def traversedURL(self):
        """Parent context's absolute URL + current context's name"""

        base = self.getParentComponent().absoluteURL
        name = self.getComponentName()
        return posixpath.join(base, name)   # handles empty parts OK

    traversedURL = binding.Make(traversedURL)


class Traversal(TraversalContext):

    """Root traversal context"""

    # We're the root, so our URL is that of the interaction
    absoluteURL = binding.Make(
        lambda self: self.interaction.getAbsoluteURL()
    )

    # We haven't gone anywhere yet, so traversed URL = absolute URL
    traversedURL = binding.Obtain('absoluteURL')

    # And you can't go to '..' from here:
    previous = None

    # Traversal start point is always the skin
    traversable = binding.Obtain('interaction/skin')

    # Subcontexts are non-root traversal context
    newCtx = binding.classAttr(TraversalContext)






class Traversable(binding.Component):

    """Basic traversable object; uses self as its subject and for security"""

    protocols.advise(
        instancesProvide = [IWebTraversable]
    )

    def getObject(self, interaction):
        return self

    def traverseTo(self, name, ctx):

        interaction = ctx.interaction
        ob = self.getObject(interaction)
        loc = getattr(ob, name, NOT_FOUND)

        if loc is not NOT_FOUND:

            result = interaction.allows(ob, name)

            if result:
                return loc

            raise NotAllowed(ctx,getattr(result,'message',"Permission Denied"))

        raise NotFound(ctx)


    def preTraverse(self, ctx):
        pass    # Should do any traversal requirements checks

    def getURL(self,ctx):
        return ctx.traversedURL







class Decorator(Traversable):

    """Traversal adapter whose local attributes add/replace the subject's"""

    protocols.advise(
        instancesProvide = [IWebTraversable],
        factoryMethod = 'asTraversableFor',
        asAdapterForTypes = [object],
    )

    ob = None

    def asTraversableFor(klass, ob, proto):
        return klass(ob = ob)

    asTraversableFor = classmethod(asTraversableFor)


    def getObject(self, interaction):
        return self.ob

    def traverseTo(self, name, ctx):

        loc = getattr(self, name, NOT_FOUND)

        if loc is not NOT_FOUND:

            result = ctx.interaction.allows(self, name)
            if result:
                return loc

            # Access failed, see if attribute is private
            guard = adapt(self,security.IGuardedObject,None)

            if guard is not None and guard.getPermissionForName(name):
                # We have explicit permissions defined, so reject access
                raise NotAllowed(ctx, result.message)

        # attribute is absent or private, fall through to underlying object
        return super(Decorator,self).traverseTo(name, ctx)

class ContainerAsTraversable(Decorator):

    """Traversal adapter for container components"""

    protocols.advise(
        instancesProvide = [IWebTraversable],
        factoryMethod = 'asTraversableFor',
        asAdapterForProtocols = [naming.IBasicContext, storage.IDataManager],
        asAdapterForTypes = [dict],
    )

    def traverseTo(self, name, ctx):

        if name.startswith('@@'):
            return super(ContainerAsTraversable,self).traverseTo(
                name[2:], ctx
            )

        try:
            ob = self.ob[name]
        except KeyError:
            return super(ContainerAsTraversable,self).traverseTo(
                name, ctx
            )

        result = ctx.interaction.allows(ob)
        if result:
            return ob

        raise NotAllowed(ctx, result.message)











class MultiTraverser(Traversable):

    """Aggregate traversal across a sequence of delegate traversables"""

    items = binding.Require("traversables to traversed")

    def getObject(self, interaction):
        # Return the first item
        for item in self.items:
            return item.getObject(interaction)

    def preTraverse(self, ctx):
        for item in self.items:
            item.preTraverse(ctx)

    def traverseTo(self, name, ctx):

        newItems = []

        for item in self.items:
            try:
                loc = item.traverseTo(name, ctx)
            except NotFound:
                continue
            else:
                # we should suggest the parent, since our caller won't
                binding.suggestParentComponent(item, name, loc)
                newItems.append(loc)

        if not newItems:
            raise NotFound(ctx)

        if len(newItems)==1:
            loc = newItems[0]
        else:
            loc = self._subTraverser(self, name, items = newItems)
        return loc

    _subTraverser = lambda self, *args, **kw: self.__class__(*args,**kw)


class CallableAsWebPage(protocols.Adapter):

    """Make functions/methods callable"""

    protocols.advise(
        instancesProvide = [IWebPage],
        asAdapterForTypes = [FunctionType, MethodType]
    )

    def render(self, context):
        request = context.interaction.request
        from zope.publisher.publish import mapply
        return mapply(self.subject, request.getPositionalArguments(), request)




























