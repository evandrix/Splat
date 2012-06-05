"""Use 'zope.publisher' to publish 'peak.web' apps"""

from peak.api import *
from interfaces import *
from places import Traversal
from errors import NotFound, NotAllowed

__all__ = [
    'Interaction', 'NullAuthenticationService', 'InteractionPolicy',
    'CGIPublisher', 'DefaultExceptionHandler',
    'TraversalPath', 'TestInteraction',
]


class DefaultExceptionHandler(binding.Singleton):

    def handleException(self, interaction, thrower, exc_info, retry_allowed=1):
        try:
            storage.abort(interaction.app)

            # XXX note that the following assumes exc_info is available as
            # XXX sys.exc_info; will this always be the case?
            interaction.log.exception("ERROR:")

            # XXX Maybe the following should be in a method on interaction?
            interaction.response.reset()
            interaction.response.setCharsetUsingRequest(interaction.request)
            interaction.response.handleException(exc_info)

        finally:
            # Don't allow exc_info to leak, even if the above resulted in
            # an error
            exc_info = None








class TraversalPath(naming.CompoundName):

    """Name that knows how to do 'IWebTraversable' traversal"""

    syntax = naming.PathSyntax(
        direction=1,
        separator='/'
    )

    def traverse(self, ob, getRoot = lambda ctx: ctx):

        path = iter(self)
        part = path.next()

        if not part:
            ob = getRoot(ob)
        else:
            # reset to beginning
            path = iter(self)

        for part in path:
            if part:
                ob = ob.contextFor(part)

        return ob



class NullAuthenticationService:

    protocols.advise(
        instancesProvide=[IAuthService]
    )

    def getUser(self, interaction):
        return None





class InteractionPolicy(binding.Component, protocols.StickyAdapter):

    protocols.advise(
        instancesProvide = [IInteractionPolicy],
        asAdapterForProtocols = [binding.IComponent],
        factoryMethod = 'fromComponent',
    )

    def fromComponent(klass, ob, proto):
        ip = klass(ob)
        protocols.StickyAdapter.__init__(ip, ob, proto)
        return ip

    fromComponent = classmethod(fromComponent)

    app            = binding.Obtain('./subject')
    log            = binding.Obtain(APPLICATION_LOG)
    errorProtocol  = binding.Obtain(ERROR_PROTOCOL)
    pathProtocol   = binding.Obtain(PATH_PROTOCOL)
    pageProtocol   = binding.Obtain(PAGE_PROTOCOL)
    defaultMethod  = binding.Obtain(DEFAULT_METHOD)
    resourcePrefix = binding.Obtain(RESOURCE_PREFIX)

    _authSvc       = binding.Make(IAuthService, adaptTo=IAuthService)
    _skinSvc       = binding.Make(ISkinService, adaptTo=ISkinService)
    _layerSvc      = binding.Make(ILayerService, adaptTo=ILayerService)
    _mkInteraction = binding.Obtain(config.FactoryFor(IWebInteraction))

    root = binding.Make(
        lambda self: adapt(self.app, self.pathProtocol)
    )

    getSkin = binding.Delegate('_skinSvc')
    getLayer = binding.Delegate('_layerSvc')
    getUser  = binding.Delegate('_authSvc')

    def newInteraction(self,request):
        return self._mkInteraction(self,None,policy=self,request=request)



class Interaction(security.Interaction):

    """Base publication policy/interaction implementation"""

    policy   = binding.Obtain('..', adaptTo=IInteractionPolicy)
    request  = binding.Require("Request object")
    response = binding.Delegate("request")

    app = log = root = \
    defaultMethod = resourcePrefix = \
    errorProtocol = pathProtocol = pageProtocol = \
        binding.Delegate("policy")


    skinName = "default"

    user = binding.Make(lambda self: self.policy.getUser(self) )
    skin = binding.Make(lambda self: self.policy.getSkin(self.skinName))

    getResource = getResourceURL = resources = \
        binding.Delegate("skin")


    def beforeTraversal(self, request):
        """Begin transaction before traversal"""
        storage.beginTransaction(self.app)

    def getApplication(self,request):
        return Traversal(self.skin, interaction=self)

    def callTraversalHooks(self, request, ob):
        ob.checkPreconditions()

    def traverseName(self, request, ob, name, check_auth=1):
        return ob.contextFor(name)

    def afterTraversal(self, request, ob):
        # Let the found object know it's being traversed
        ob.checkPreconditions()


    def getDefaultTraversal(self, request, ob):

        """Find default method if object isn't renderable"""

        default = self.defaultMethod

        if default and ob.renderable is None:

            # Not renderable, try for default method

            try:
                ob.contextFor(default)
            except NotFound:
                # Default method doesn't exist, try for direct rendering
                return ob, ()
            except NotAllowed:
                pass

            # Traversal will succeed (or be unauthorized), so tell the
            # request to proceed
            return ob, (default,)

        # object is renderable or no default is in use: just render
        # the object directly
        return ob, ()


    def callObject(self, request, ob):
        return ob.render()

    def afterCall(self, request):
        """Commit transaction after successful hit"""

        storage.commitTransaction(self.app)
        if request.method=="HEAD":
            # XXX this doesn't handle streaming; there really should be
            # XXX a different response class for HEAD; Zope 3 should
            # XXX probably do it that way too.
            request.response.setBody('')


    def handleException(self, object, request, exc_info, retry_allowed=1):

        """Convert exception to a handler, and invoke it"""

        try:
            handler = adapt(
                exc_info[1], self.errorProtocol, DefaultExceptionHandler
            )
            return handler.handleException(
                self, object, exc_info, retry_allowed
            )
        finally:
            # Don't allow exc_info to leak, even if the above resulted in
            # an error
            exc_info = None


    appURL = binding.Make(lambda self: self.request.getApplicationURL())

    def getAbsoluteURL(self, resource=None):
        base = self.appURL
        if resource is None:
            return base
        path = adapt(resource,self.pathProtocol).resourcePath   # XXX borken
        return '%s/%s' % (base, path)

    def clientHas(self, lastModified=None, ETag=None):
        return False    # XXX













class TestInteraction(Interaction):

    """Convenient interaction to use for tests, experiments, etc."""

    request = binding.Make('peak.web.requests:TestRequest')

    appURL = 'http://127.0.0.1'    # prevent use of request unless necessary

    def simpleTraverse(self, path, run=True):

        path = adapt(path, TraversalPath)
        ob = self.getApplication(None)

        for part in path:
            ob = self.traverseName(None, ob, part)

        if run:
            return self.callObject(None, ob)

        return ob





















class CGIPublisher(binding.Component):

    """Use 'zope.publisher' to run an application as CGI/FastCGI

    For basic use, this just needs an 'app' parameter, and it will publish
    that application using 'BaseInteraction' as its interaction class,
    'IWebTraversable' and 'IWebPage' as its path and page protocols,
    and the default request classes supplied by 'zope.publisher'.

    Three HTTP variants are supported: "generic" HTTP, "browser" HTTP, and
    XML-RPC.  They are distinguished from one another by the CGI
    'REQUEST_METHOD' and 'CONTENT_TYPE' environment variables.  A "POST"
    of 'text/xml' is considered XML-RPC, while all other "POST", "GET",
    and "HEAD" methods are considered "browser" HTTP.  Any other methods
    ("PUT", "DELETE", etc.) are considered "generic" HTTP (e.g. WebDAV).

    You can override specific request types as follows::

        HTTP Variant    KW for Request Class    Property Name
        ------------    --------------------    -----------------------
        "Generic"       mkHTTP                  peak.web.HTTPRequest
        "XML-RPC"       mkXMLRPC                peak.web.XMLRPCRequest
        "Browser"       mkBrowser               peak.web.BrowserRequest

    So, for example, to change the XML-RPC request class, you might do this::

        myPublisher = CGIPublisher( mkXMLRPC = MyXMLRPCRequestClass )

    In practice, you're more likely to want to change the interaction class,
    since the default request classes are likely to suffice for most
    applications.  (It's also easier to change the properties in an application
    .ini file than to supply the classes as keyword arguments.)

    'CGIPublisher' is primarily intended as a base adapter class for creating
    web applications.  To use it, you can simply subclass it, replacing the
    'app' binding with an instance of your application, and replacing any other
    parameters as needed.  The resulting class can be invoked with 'peak CGI'
    to run as a CGI or FastCGI application."""



    protocols.advise(
        instancesProvide=[running.IRerunnableCGI],
    )


    # The fromApp method is registered as an adapter factory for
    # arbitrary components to IRerunnableCGI, in peak.running.interfaces.
    # If we registered it here, it wouldn't be usable unless peak.web
    # was already imported, which leads to bootstrap problems, at least
    # with very trivial web apps (like examples/trivial_web).

    def fromApp(klass, app, protocol):
        return klass(app, app=app)

    fromApp = classmethod(fromApp)


    app              = binding.Require("Application root to publish")
    policy           = binding.Obtain('app', adaptTo = IInteractionPolicy)


    # items to (potentially) replace in subclasses

    publish   = binding.Obtain('import:zope.publisher.publish:publish')

    mkXMLRPC  = binding.Obtain(PropertyName('peak.web.XMLRPCRequest'))
    mkBrowser = binding.Obtain(PropertyName('peak.web.BrowserRequest'))
    mkHTTP    = binding.Obtain(PropertyName('peak.web.HTTPRequest'))

    _browser_methods = binding.Make(lambda: {'GET':1, 'POST':1, 'HEAD':1} )











    def runCGI(self, input, output, errors, env, argv=()):

        """Process one request"""

        method = env.get('REQUEST_METHOD', 'GET').upper()

        if method in self._browser_methods:
            if (method == 'POST' and
                env.get('CONTENT_TYPE', '').lower().startswith('text/xml')
                ):
                request = self.mkXMLRPC(input, output, env)
            else:
                request = self.mkBrowser(input, output, env)
        else:
            request = self.mkHTTP(input, output, env)

        request.setPublication(
            self.policy.newInteraction(request)
        )
        return self.publish(request) or 0





















