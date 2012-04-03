"""Interfaces, constants, property names, etc. for peak.naming"""

from protocols import Interface, Attribute
from peak.api import PropertyName, NOT_GIVEN
from peak.binding.interfaces import IComponentKey

__all__ = [

    'IName', 'IAddress', 'IInitialContextFactory', 'IResolver', 'IPath',
    'IURLContextFactory', 'IAddressFactory', 'IObjectFactory', 'IState',
    'IBasicContext', 'IReadContext', 'IWriteContext', 'IReferenceable',
    'COMPOUND_KIND', 'COMPOSITE_KIND', 'URL_KIND', 'IState', 'IReference',
    'IStreamFactory',

    'CREATION_PARENT', 'SCHEMES_PREFIX', 'FACTORY_PREFIX',
    'INIT_CTX_FACTORY', 'SCHEME_PARSER',

]


INIT_CTX_FACTORY = PropertyName('peak.naming.initialContextFactory')

CREATION_PARENT  = PropertyName('peak.naming.creationParent')
SCHEME_PARSER    = PropertyName('peak.naming.schemeParser')

SCHEMES_PREFIX   = PropertyName('peak.naming.schemes')
FACTORY_PREFIX   = PropertyName('peak.naming.factories')














COMPOUND_KIND  = 1
COMPOSITE_KIND = 2
URL_KIND       = 3

class IName(IComponentKey):

    """Abstract name object"""

    nameKind = Attribute("One of COMPOUND_KIND, COMPOSITE_KIND, or URL_KIND")

    def __add__(other):
        """Add 'other' to name, composing a name that is relative to this one"""

    def __radd__(other):
        """Add name to 'other', using this name as a relative name to it"""

    def __sub__(other):
        """Subtract 'other' from name, returning 'None' if not a prefix"""

    def __rsub__(other):
        """Subtract name from 'other', returning 'None' if not a prefix"""

    def __hash__():
        """Should be usable as a dictionary key"""

    def __eq__():
        """Should be usable as a dictionary key"""














class IPath(IName):

    """A path-like name (COMPOUND_KIND or COMPOSITE_KIND)"""

    def __iter__():
        """Iterate over path segments"""

    def __getitem__(pos):
        """Return a designated segment"""

    def __len__():
        """Return path length"""

    def __getslice__(start,end):
        """Return a slice of the path as a path of the same type"""


























class IResolver(Interface):

    """Thing which can participate in name resolution"""

    def resolveToInterface(name,iface):
        """Find nearest context to 'name' that supports 'iface'

        Return a tuple of the form '(context, remainingName)', where 'context'
        is the context nearest to 'name' that supports interface 'iface', and
        'remainingName' is the portion of 'name' that is relative to
        'context'.  That is, 'remainingName' interpreted relative to 'context'
        should be the same name as 'name' relative to the context this method
        is called on.
        """



























class IBasicContext(IResolver):

    """Basic naming context; supports only name retrieval"""

    def lookup(name, default=NOT_GIVEN):
        """Lookup 'name' and return object, 'default', or raise 'NameNotFound'

        If 'default' is 'NOT_GIVEN', this method should behave identically to
        '__getitem__()'.  Otherwise, it should behave like 'get()'."""

    def __getitem__(name):
        """Lookup 'name' and return an object, or raise 'NameNotFound'"""

    def get(name, default=None):
        """Lookup 'name' and return an object, or 'default' if not found"""

    def __contains__(name):
        """Return a true value if 'name' has a binding in context"""

    def has_key(name):
        """Synonym for __contains__"""

    def close():
        """Close the context"""

    def lookupLink(name):
        """Return terminal LinkRef of 'name', if it's a link"""














class IReadContext(IBasicContext):

    """Context that supports iteration/inspection of contents"""

    def keys():
        """Return a sequence of the names present in the context"""

    def __iter__():
        """Return an iterator of the names present in the context"""

    def items():
        """Return a sequence of (name,boundItem) pairs"""

    def info():
        """Return a sequence of (name,boundState) pairs"""

    # XXX search, getAttributes
























class IWriteContext(IBasicContext):

    """Context that supports adding/changing its contents"""

    def rename(oldName,newName):
        """Rename 'oldName' to 'newName'"""

    def __setitem__(name,ob):
        """Bind 'ob' under 'name'"""

    def __delitem__(name):
        """Remove any binding associated with 'name'"""

    def bind(name,ob):
        """Synonym for __setitem__"""

    def unbind(name,ob):
        """Synonym for __delitem__"""

    def mksub(name):
        """Create a subcontext of the same kind under 'name'"""

    def rmsub(name):
        """Remove sub-context 'name'"""

    # XXX modifyAttributes















class IStreamFactory(Interface):

    """A stream resource

    Naming and storage systems use the IStreamFactory interface to access
    streams such as files, TCP/IP protocol connections, pipes, etc.

    There are three basic ways to open a stream: to read an "existing"
    stream (via 'open()'), to create a new stream, overwriting any existing
    data (via 'create()'), and to update/append a (possibly existing)
    stream (via 'update()').

    Each method provides some options.  The 'mode' argument, required by
    all methods, must be '"b"', '"t"', or '"U"', indicating the text/binary
    mode for Python to use in interpreting stream contents.  The 'seek'
    argument, if set to true, requests that the opened stream be seekable.
    The 'readable' and 'writable' arguments request that the stream be
    capable of that operation in addition to the normal behavior for that
    opening method.

    The 'autocommit' option indicates whether autocommit behavior (i.e. a
    separate transaction just for that operation) is desired.  Note that if
    the 'autocommit' option is set, changes to an existing resource may be
    visible to other threads or processes before the opened stream is
    closed.

    For all options, if the requested option is unsupported, an exception
    will be raised.  Ommitting 'autocommit' when a particular stream
    factory requires autocommitting, will also result in an exception."""


    def open(mode,seek=False,writable=False,autocommit=False):

        """Open an existing stream resource for reading (like '"r"' mode)

        The resource must exist and be readable.  It is not created if
        it does not exist."""




    def create(mode,seek=False,readable=False,autocommit=False):

        """Create/replace a stream resource for writing (like '"w"' mode)

        Always creates the resource, whether it exists or not, erasing any
        previously existing contents if applicable."""


    def update(mode,seek=False,readable=False,append=False,autocommit=False):

        """Update or append to a stream resource (like '"w+"' or '"a"' mode)

        Opens the resource for modification; if it doesn't exist, it's
        created empty.  The 'append' flag controls whether the stream
        is opened for writing at the end of the existing resource.  Note
        that in append mode, some operating systems will send *all* writes
        to the end of a file, regardless of seek position (according to
        the Python manual)."""


    def exists():
        """Return true if the resource exists (i.e. if 'open()' would succeed)

        For remote resources, this should verify the resource's existence
        without actually downloading it.  However, this should include
        authentication if the protocol requires it.

        This method is specifically intended to be able to be used to verify
        that a remote service is up and running."""


    def delete(autocommit=False):
        """Delete the resource"""








# Framework interfaces

class IAddress(IName):

    """URL/Name that supports in-context self-retrieval (URL_KIND)"""

    def getAuthorityAndName():
        """Return an 'authority,name' tuple"""

    defaultFactory = Attribute(
        """Name of default object factory for this address"""
    )


class IInitialContextFactory(Interface):
    """Get access to an initial naming context"""

    def getInitialContext(parentComponent, componentName=None, **options):
        """Return a naming context for 'parentComponent' with 'options'"""


class IReferenceable(Interface):
    """Thing that can return a reference to itself, for binding in a context"""

    def getReference():
        """Return a '(IReference,attrs)' pair for saving in a naming context"""

class IState(Interface):
    """Thing that stores an object's state in a naming context"""

    def restore(context, name):
        """Return the object that this is the state for"""

class IReference(IState):
    """A reference to an object, described as a factory name + addresses"""

    factoryName = Attribute("Dotted name of an 'IObjectFactory'")
    addresses = Attribute("Sequence of strings or parsed address objects")



class IObjectFactory(Interface):

    """Convert data in a naming system into a useful retrieved object"""

    def getObjectInstance(context, refInfo, name, attrs=None):

        """Return the object that should be constructed from 'refInfo'

        This function or method should return the object which is referenced
        by 'refInfo', or 'None' if it does not know how or does not wish to
        interpret 'refInfo'.

        'refInfo' is an 'IReference' representing an object found in 'context'
        under 'name', with attributes 'attrs'.  The specific contents of
        'refInfo', 'name', and 'attrs', are entirely dependent upon the
        implementation details of the 'context' object.

        (Note: the official semantics of the 'attrs' parameter is not yet
        defined; it is reserved for implementing JNDI 'DirContext'-style
        operations.  Currently 'None' is the only correct value for 'attrs'.)
        """




















class IURLContextFactory(Interface):

    """Obtain a context implementation for a URL scheme"""

    def getURLContext(parent,scheme,iface,componentName=None,**options):

        """Return a context that can provide 'iface' for 'scheme' URLs

        'scheme' is a URL scheme as defined by RFC 1738.  The trailing ':'
        should *not* be included.  Per RFC 1738, the '-', '+', and '.'
        characters are allowed.  Also per the RFC, any implementation of
        this interface should use the lowercase form of any scheme name
        supplied.

        This function or method should return a context implementation bound
        to 'parent', with name 'componentName' and providing '**options'.
        If no context implementation supporting 'iface' can be found, return
        'None'.

        'IURLContextFactory' is not normally used as a utility; naming context
        implementations should use the primary 'naming.spi.getURLContext()'
        function to obtain URL context providers when needed.  But, it is
        possible to register implementations of this interface under part
        of the 'peak.naming.schemes' property space, and they will then be
        used to find a more specific URL context.

        For example, if you have a set of schemes 'foo.bar', 'foo.baz',
        and 'foo.spam', you could register the following in an application
        configuration file::

            [peak.naming.schemes]
            foo.* = "some.module"

        and put this in 'some.module'::

            from peak.api import *

            moduleProvides(naming.IURLContextFactory)

            def getURLContext(parent,scheme,iface,componentName,**options):
                # code to pick between 'foo.bar', 'foo.baz', etc. and
                # return a context implementation

        Of course, the only reason to do this is if the contexts are created
        dynamically in some fashion, otherwise it would suffice to register
        'foo.bar', etc. directly in your application's configuration.

        Alternately, you could register your context factory under
        'peak.naming.schemes.*', in which case it would be used as a default
        for any schemes not specifically defined or registered.
        """


class IAddressFactory(IURLContextFactory):

    """Class for creating parsed URLs from scheme and body"""

    def __call__(scheme,body):
        """Return a new address object for scheme and body"""

    def supportsScheme(scheme):
        """Is URL scheme 'scheme' supported by this factory?"""




















