"""API functions and classes for the peak.naming package"""

from interfaces import *
from syntax     import *
from names      import *
from contexts   import *
import spi

from peak.util.imports import lazyModule
URL = lazyModule(__name__,'../URL')
del lazyModule

def InitialContext(parent, componentName=None, **options):

    """Get an initial naming context, based on 'parent' and keyword options

    'parent' is the component which will be used as the naming context's
    parent component, to obtain any required configuration data.  The
    'componentName' argument and 'options' keyword arguments are used
    to set up the context's name and attributes, just as with a normal
    PEAK component constructor.

    This function implements the 'binding.IComponentFactory' interface, and
    thus can be used as a factory for a 'binding.Make()' attribute.  That
    is, you can do this::

        myInitCtx = binding.Make(naming.InitialContext)

    in a class to create a 'myInitCtx' attribute.  This can be useful if
    you will be using naming functions a lot and would like to hang onto
    an initial context.
    """

    return spi.getInitialContext(parent, componentName, **options)

from peak.binding.interfaces import IComponentFactory
from protocols import adviseObject

adviseObject(InitialContext, provides=[IComponentFactory])
del IComponentFactory, adviseObject

from peak.api import NOT_GIVEN

def lookup(parent, name, default=NOT_GIVEN, **options):

    """Look up 'name' in the default initial context for 'parent', w/'options'

    This is just a shortcut for calling::

        naming.InitialContext(parent,**options)[name]
    """

    return InitialContext(parent, **options).lookup(name,default)

del NOT_GIVEN   # don't pollute the namespace

def parseURL(parent, name):

    """Return a parsed URL for 'name', based on schemes available to 'parent'

    If a parser for the URL scheme isn't available, or 'name' is not a
    valid URL, 'exceptions.InvalidName' will be raised.  Note that 'name'
    must include a URL scheme, (e.g. '"ldap:"'), or it will be considered
    invalid.
    """

    url = toName(name)

    if url.nameKind != URL_KIND:
        from peak.exceptions import InvalidName
        raise InvalidName("Not a URL", name)

    scheme, body = url.scheme, url.body

    ctx = spi.getURLContext(parent, scheme, IResolver)

    if ctx is None:
        from peak.exceptions import InvalidName
        raise InvalidName("Unknown scheme", scheme)

    return ctx.schemeParser(scheme, body)

