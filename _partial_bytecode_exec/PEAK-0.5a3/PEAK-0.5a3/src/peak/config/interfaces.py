from peak.api import protocols, exceptions, PropertyName, NOT_GIVEN
from protocols import Interface, Attribute

__all__ = [
    'IConfigKey', 'IConfigurable', 'IConfigSource', 'IConfigurationRoot',
    'ISmartProperty', 'IRule', 'IPropertyMap', 'ISettingLoader',
    'IIniParser', 'ISettingParser', 'NullConfigRoot', 'IConfigMap',
    'IServiceArea',
]


class IConfigKey(Interface):

    """Configuration data key, used for 'config.lookup()' et al

    Configuration keys may be polymorphic at registration or lookup time.
    IOW, when looking up a configuration key, you can search multiple values
    that would imply the key being looked for.  And, when registering a value
    for a configuration key, the key can supply alternate keys that it should
    be registered under.  Thus, an 'IConfigKey' is never itself directly used
    as a key, only the values supplied by its 'registrationKeys()' and
    'lookupKeys()' methods are used.  (However, those values must themselves
    be adaptable to 'IConfigKey', and they must be usable as dictionary keys.)
    """

    def registrationKeys(depth=0):
        """Iterate over (key,depth) pairs to be used when registering"""

    def lookupKeys():
        """Iterate over keys that should be used for lookup"""

    def parentKeys():
        """Iterate over keys that are containing namespaces for this key"""








class IConfigSource(Interface):

    """Something that can be queried for configuration data"""

    def _getConfigData(forObj, configKey):

        """Return a value of 'configKey' for 'forObj' or 'NOT_FOUND'

        Note that 'configKey' is an 'IConfigKey' instance and may therefore be
        a 'PropertyName' or an 'Interface' object.

        Also note that 'binding.Component' implements this method by simply
        returning 'NOT_FOUND', and that is a perfectly acceptable
        implementation for many purposes."""


class IConfigurable(IConfigSource):

    """Object which can be configured with rules for configuration keys"""

    def registerProvider(configKey, ruleObj):

        """Register 'IRule' 'ruleObj' as a provider for 'configKey'

        'configKey' must be adaptable to 'IConfigKey'.  'ruleObj' will be
        registered as a provider of the specified key.

        If a provider has already been registered for the given key, the
        new provider will replace it, provided that it has not yet been
        used.  (If it has, 'AlreadyRead' should be raised.)

        If the key is an 'Interface' with bases (or any other type of
        configuration key that supports registering implied keys), the provider
        will also be registered for any keys implied by the supplied key,
        unless a provider was previously registered under the implied key.
        """





class IServiceArea(IConfigSource):
    """A component that acts as a home for services and their configuration"""

    def getService(ruleKey, factory):
        """Return service for 'ruleKey', creating w/'factory' if needed"""


class IConfigurationRoot(IServiceArea):
    """A root component that acknowledges its configuration responsibilities"""

    def noMoreValues(root,configKey,forObj):
        """A value search has completed"""

    def noMoreUtilities(root,configKey,forObj):
        """DEPRECATED: Use 'noMoreValues()' method instead"""

    def nameNotFound(root,name,forObj,bindName):
        """A (non-URL) component name was not found"""


class _NullConfigRoot(object):
    """Adapter to handle missing configuration root"""

    def noMoreValues(self,root,configKey,forObj):
        raise exceptions.InvalidRoot(
            "Root component %r does not implement 'IConfigurationRoot'"
            " (was looking up %s for %r)" % (root, configKey, forObj)
        )

    def nameNotFound(self,root,name,forObj):
        raise exceptions.NameNotFound(
            remainingName = name, resolvedObj = root
        )

    def noMoreUtilities(self,root,configKey,forObj):
        """DEPRECATED: Use 'noMoreValues()' method instead"""
        return self.noMoreValues(root,configKey,forObj)

NullConfigRoot = _NullConfigRoot()


class IIniParser(Interface):

    """Parser object passed to 'ISettingParser' instances"""

    def add_setting(section, name, value, lineInfo):
        """Define a configuration rule for 'section'+'name' = value
        Note that when this method is called by the IIniParser itself,
        'section' already has the 'prefix' attribute added to it, and it
        is already formatted as a property prefix.  So, for a section like::

            [foo]
            bar = baz

        and a parser 'prefix' of '"some.prefix."', this method gets called
        with '("some.prefix.foo.", "bar", "baz", ...)'."""


    def add_global(name,value):
        """Add/update a global variable for rules evaluation

        This creates a new 'globalDict' attribute, so that rules
        parsed before this global was added, will still be using
        the globals that were in effect when the rule was parsed."""


    prefix = Attribute("""Prefix that should be added to all property names""")
    pMap   = Attribute("""'IConfigMap' that the parser is loading""")

    globalDict = Attribute("""Globals dictionary used for eval()ing rules""")












class ISettingParser(Interface):

    """Handler for name=value settings in an .ini file section"""

    def __call__(parser, section, name, value, lineInfo):
        """Act on 'name' = 'value' in section 'section'

        'parser' is an 'IIniParser' for the file being parsed, and 'lineInfo'
        is a tuple of '(filename, lineNumber, lineContents)'.  Typically,
        a setting parser will perform some operation(s) on 'parser.pMap' in
        response to each setting it receives.

        If you want to use the standard parser's interpretation of the name
        and value, you can call 'parser.add_setting()', but be sure to
        provide compatible arguments, as 'add_setting()' expects its 'section'
        argument to be a valid, ready-to-use prefix for its 'name' argument.
        """


class IRule(Interface):

    """Rule to compute a property value for a target object"""

    def __call__(propertyMap, configKey, targetObject):

        """Retrieve 'configKey' for 'targetObject' or return 'NOT_FOUND'

        The rule object is allowed to call any 'IConfigMap' methods on the
        'propertyMap' that is requesting computation of this rule.

        What an IRule must *not* do, however, is return different results over
        time for the same input parameters.  If it cannot guarantee this
        algorithmically, it must cache its results keyed by the parameters it
        used, and not compute the results a second time."""







class ISmartProperty(Interface):

    """An property value that itself should be treated as a rule

    Objects that implement this interface will have their 'computeProperty()'
    method called when they are used as the return value of an .ini-file
    property definition.  For example:

        [myapp.settings]
        foo.* = SomeRuleObject()

    If 'SomeRuleObject()' implements 'ISmartProperty', the return value of its
    'computeProperty()' method is returned as the value of any properties
    requested from the 'myapp.settings.foo.*' property namespace."""

    def computeProperty(propertyMap, name, prefix, suffix, targetObject):
        """Retrieve property 'rulePrefix+propertySuffix' from 'propertyMap'

        This is basically the same as 'IRule.__call__', except that the key
        must be a property name ('name'), and it is also broken into a 'prefix'
        for the name under which the rule was defined, and the 'suffix',
        if any."""



















class ISettingLoader(Interface):

    """Callable used to load configuration data"""

    def __call__(propertyMap, *args, **kw):
        """Load settings into 'propertyMap'

        Loading functions can require whatever arguments are useful or desired.
        The value of each "Load Settings From" config file entry will be
        interpreted as part of a call to the loader.  For example, this entry::

            [Load Settings From]
            mapping = importString('os.environ'), prefix='environ.*'

        will be interpereted as::

            loader(propertyMap, importString('os.environ'), prefix='environ.*')

        So it's up to the author of the loader to choose and document the
        arguments to be used in configuration files.

        However, one keyword argument which all 'ISettingLoader' functions
        must accept is 'includedFrom'.  This is an implementation-defined
        object which represents the state of the 'ISettingLoader' which is the
        caller.  Currently, this argument is only supplied by the default
        'config.loadConfigFile()' loader, and the value passed is a
        'ConfigReader' instance.
        """













class IConfigMap(IConfigurable):

    """Configurable component that allows iteration over keys"""

    def _configKeysMatching(configKey):
        """Iterable over defined keys that match 'configKey'

        A key 'k' in the map is considered to "match" 'configKey' if any of
        'k.parentKeys()' are listed as keys in 'configKey.registrationKeys()'.
        You must not change the configuration map while iterating over the
        keys.  Also, keep in mind that only explicitly-registered keys are
        returned; for instance, load-on-demand rules will only show up as
        wildcard keys.

        Implementations may yield keys in any order, but must not yield the
        same key more than once."""


class IPropertyMap(IConfigMap):

    """DEPRECATED: Use 'IConfigMap' instead"""

    def setDefault(propName, ruleObj):
        """DEPRECATED"""

    def setRule(propName, ruleObj):
        """DEPRECATED"""

    def setValue(configKey, value):
        """DEPRECATED"""

    def getValueFor(forObj, propName):
        """DEPRECATED"""








