from peak.api import *
import ZConfig.loader
from peak.running.commands import AbstractInterpreter
from peak.naming.factories.openable import FileURL
import os

class BaseLoader(binding.Component, ZConfig.loader.BaseLoader):

    def openResource(self, url):
        url = str(url)
        try:
            factory = adapt(naming.lookup(self, url), naming.IStreamFactory)
            file = factory.open('t')
        except (IOError, OSError), e:
            # Python 2.1 raises a different error from Python 2.2+,
            # so we catch both to make sure we detect the situation.
            error = ZConfig.ConfigurationError("error opening resource %s: %s"
                                               % (url, str(e)))
            error.url = url
            raise error
        return self.createResource(file, url)


    def normalizeURL(self, url):
        url = naming.parseURL(self, url)
        if getattr(url,'fragment',None) is not None:
            raise ZConfig.ConfigurationError(
                "fragment identifiers are not supported")
        return str(url)












class SchemaLoader(BaseLoader, ZConfig.loader.SchemaLoader):

    registry = binding.Make(ZConfig.datatypes.Registry)
    _cache   = binding.Make(dict)
    __init__ = binding.Component.__init__.im_func

class ConfigRunner(AbstractInterpreter,BaseLoader,ZConfig.loader.ConfigLoader):

    """Config-file interpreter"""

    usage="""
Usage: peak SCHEMA_URL ZCONFIG_FILE arguments...

SCHEMA_URL should be a 'zconfig.schema:' URL referring to the schema used
for the config file.  ZCONFIG_FILE should be the URL of a ZConfig configuration
file that follows the schema specified by SCHEMA_URL.  The object that results
from loading ZCONFIG_FILE should implement or be adaptable to
to 'running.ICmdLineAppFactory'.  It will be run with the remaining
command-line arguments.
"""

    schema = binding.Require("ZConfig schema to use")

    def interpret(self, filename):
        url = naming.toName(filename, FileURL.fromFilename)
        factory = adapt(self.lookupComponent(url), naming.IStreamFactory)
        ob, handler = self.loadFile(factory.open('t'), str(url))
        binding.suggestParentComponent(self.getCommandParent(),None,ob)
        return self.getSubcommand(ob)

    def loadResource(self, resource):
        sm = self.createSchemaMatcher()
        self._parse_resource(sm, resource,
            # lowercase version of os.environ; ZConfig lowercases its lookups
            dict([(k.lower(),v) for k,v in os.environ.items()])
        )
        result = sm.finish(), ZConfig.loader.CompositeHandler(
            sm.handlers, self.schema
        )
        return result

class ZConfigSchemaURL(naming.URL.Base):

    """'zconfig.schema:' URL scheme - loads body as a schema

    Note that the body of this URL can be any other type of URL, but
    if no URL scheme is present in the body, then the body is interpreted
    as a 'file:' URL.
    """

    supportedSchemes = 'zconfig.schema',


class ZConfigSchemaContext(naming.AddressContext):

    schemeParser = ZConfigSchemaURL

    def _get(self, name, retrieve=1):

        url = naming.toName(name.body, FileURL.fromFilename)
        ob = adapt(naming.lookup(self,url), naming.IStreamFactory)

        loader = SchemaLoader(self.creationParent).loadFile(
            ob.open('t'), str(url)
        )
        parent = self.creationParent

        def factory(**kw):
            kw.setdefault('schema', loader)
            kw.setdefault('parentComponent', parent)
            return ConfigRunner(**kw)

        protocols.adviseObject(factory, provides=[running.ICmdLineAppFactory])

        return factory







