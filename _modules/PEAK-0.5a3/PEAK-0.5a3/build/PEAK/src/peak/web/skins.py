from peak.api import *
from interfaces import *
from places import Traversable, MultiTraverser, Traversal
from publish import TraversalPath
from resources import Resource

__all__ = [
    'Skin', 'LayerService', 'SkinService',
]


class LayerService(Resource):

    """Service for accessing layers (w/caching and sharing between skins)"""

    protocols.advise(
        instancesProvide=[ILayerService]
    )

    # Our path is /++resources++ or equivalent
    resourcePath = binding.Obtain(RESOURCE_PREFIX)

    layerMap = binding.Make( config.Namespace('peak.web.layers') )

    permissionNeeded = security.Anybody

    def getLayer(self,layerName):
        ob = getattr(self.layerMap,layerName)
        binding.suggestParentComponent(self,layerName,ob)
        return ob

    def traverseTo(self, name, ctx):
        return ctx.interaction.resources.traverseTo(name,ctx)

    def getObject(self,interaction):
        return interaction.resources.getObject(interaction)





class SkinService(binding.Component):

    protocols.advise(
        instancesProvide=[ISkinService]
    )

    app = root = binding.Delegate('policy')

    policy = binding.Obtain('..')

    skinMap = binding.Make( config.Namespace('peak.web.skins') )

    def getSkin(self, name):
        ob = getattr(self.skinMap,name)
        binding.suggestParentComponent(self.policy,name,ob)
        return ob

























class Skin(Traversable):

    """Skins provide a branch-point between the app root and resources"""

    protocols.advise(
        instancesProvide = [ISkin]
    )

    resources  = binding.Make(lambda self: MultiTraverser(items=self.layers))
    cache      = binding.Make(dict)
    policy     = binding.Obtain('..')
    root       = binding.Delegate("policy")

    layerNames = binding.Require("Sequence of layer names")
    layers     = binding.Make(
        lambda self: map(self.policy.getLayer, self.layerNames)
    )

    def dummyInteraction(self):
        interaction = self.policy.newInteraction(None)
        interaction.user = None
        interaction.skin = self
        return interaction

    dummyInteraction = binding.Make(dummyInteraction)


    def traverseTo(self, name, ctx):

        if name == ctx.interaction.resourcePrefix:
            return self.resources

        return self.root.traverseTo(name, ctx)

    resourcePath = ''  # skin is at root


    def getObject(self,interaction):
        return self.root.getObject(interaction)


    def getResource(self, path):

        path = adapt(path,TraversalPath)

        if path in self.cache:
            return self.cache[path]

        interaction = self.dummyInteraction
        start = Traversal(
            self, interaction=interaction
        ).contextFor(interaction.resourcePrefix)   # start at ++resources++

        resourceCtx = path.traverse(start, getRoot = lambda ctx: start)
        self.cache[path] = resourceCtx.subject
        return resourceCtx.subject


    def getResourceURL(self, path, interaction):

        while path.startswith('/'):
            path = path[1:]

        base = interaction.getAbsoluteURL(self.traverser)

        if path:
            return '%s/%s' % (base, path)
        else:
            return base













