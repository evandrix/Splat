from __future__ import generators

from peak.api import *
from peak.util.imports import importString, importObject, whenImported
from peak.binding.components import Component, Make, getParentComponent
from peak.binding.interfaces import IAttachable, IRecipe
from peak.util.EigenData import EigenCell,AlreadyRead
from peak.util.FileParsing import AbstractConfigParser
from registries import FactoryFor
from interfaces import *
from protocols.advice import getMRO, determineMetaclass

__all__ = [
    'ConfigMap', 'PropertyMap', 'LazyRule', 'PropertySet', 'fileNearModule',
    'iterParents','findUtilities','findUtility', 'Value', 'iterKeys',
    'provideInstance', 'instancePerComponent', 'Namespace', 'iterValues',
    'CreateViaFactory', 'parentsProviding', 'parentProviding', 'lookup',
    'ServiceArea',
]


def _setCellInDict(d,key,value):

    cell = d.get(key)

    if cell is None:
        cell = d[key] = EigenCell()

    cell.set(value)

_emptyRuleCell = EigenCell()
_emptyRuleCell.set(lambda *args: NOT_FOUND)
_emptyRuleCell.exists()


def fileNearModule(moduleName,filename):
    filebase = importString(moduleName+':__file__')
    import os; return os.path.join(os.path.dirname(filebase), filename)



def iterParents(component):

    """Iterate over all parents of 'component'"""

    last = component

    while component is not None:

        yield component

        component = getParentComponent(component)


def iterValues(component, configKey):

    """Return iterator over all values of'configKey' for 'component'"""

    forObj = component
    configKey = adapt(configKey,IConfigKey)

    for component in iterParents(component):

        try:
            gcd = component._getConfigData
        except AttributeError:
            continue

        value = gcd(forObj, configKey)
        if value is not NOT_FOUND:
            yield value

    adapt(
        component,IConfigurationRoot,NullConfigRoot
    ).noMoreUtilities(component, configKey, forObj)


def findUtilities(component, iface):
    """DEPRECATED: Use 'config.iterValues()' instead"""
    return iterValues(component,iface)


def lookup(component, configKey, default=NOT_GIVEN):

    """Return value for 'configKey' in context of 'component', or 'default'"""

    for value in iterValues(component, configKey):
        return value

    if default is NOT_GIVEN:
        raise exceptions.NameNotFound(configKey, resolvedObj = component)

    return default


def findUtility(component, configKey, default=NOT_GIVEN):
    """DEPRECATED: use 'config.lookup()' instead"""
    return lookup(component, configKey, default)


def parentsProviding(component, protocol):

    """Iterate over all parents of 'component' that adapt to 'protocol'"""

    for parent in iterParents(component):
        c = adapt(parent,protocol,None)
        if c is not None:
            yield c


def parentProviding(component, protocol, default=NOT_GIVEN):
    """Return first parent providing 'protocol' for 'component', or 'default'"""

    for u in parentsProviding(component, protocol):
        return u

    if default is NOT_GIVEN:
        raise exceptions.NameNotFound(protocol, resolvedObj = component)

    return default



def iterKeys(component, configKey):

    """Iterate sub-keys of 'configKey' that are available from 'component'"""

    yielded = {}

    for ob in parentsProviding(component,IConfigMap):
        for key in ob._configKeysMatching(configKey):
            if key in yielded:
                continue
            yielded[key] = 1
            yield key





























class CreateViaFactory(object):

    """'IRule' for one-time creation of target interface using FactoryFor()"""

    protocols.advise(
        classProvides=[IRule]
    )

    __slots__ = 'configKey'


    def __init__(self,configKey):
        self.configKey = adapt(configKey,IConfigKey)


    def __call__(self, propertyMap, configKey, targetObj):

        serviceArea = parentProviding(targetObj, IServiceArea)

        def create():
            factory = lookup(serviceArea, FactoryFor(self.configKey))

            if factory is NOT_FOUND:
                return factory

            instance = factory()
            binding.suggestParentComponent(serviceArea, None, instance)
            return instance

        return serviceArea.getService(self.configKey, create)











class ConfigMap(Component):

    rules = depth = keyIndex = lockedNamespaces = Make(dict)

    protocols.advise(
        instancesProvide=[IPropertyMap]     # XXX make just IConfigMap later
    )

    def setRule(self, propName, ruleObj):
        """DEPRECATED - use registerProvider(propName,ruleObj)"""
        self.registerProvider(propName, ruleObj)

    def setDefault(self, propName, defaultRule):
        """DEPRECATED - use registerProvider(propName+'?',defaultRule)"""
        self.registerProvider(propName+'?', defaultRule)

    def setValue(self, propName, value):
        """DEPRECATED - use registerProvider(propName,config.Value(value))"""
        self.registerProvider(propName, Value(value))


    def registerProvider(self, configKey, provider):
        """Register 'provider' under 'configKey'"""

        for key,depth in adapt(configKey, IConfigKey).registrationKeys():

            if self.depth.get(key,depth)>=depth:
                # The new provider is at least as good as the one we have
                lockedNamespaces = self.lockedNamespaces
                ckey = adapt(key, IConfigKey)
                for k in ckey.parentKeys():
                    if k in lockedNamespaces:
                        raise AlreadyRead(
                            "A namespace containing %r "
                            "has already been examined" % (configKey,)
                        )
                for k in ckey.parentKeys():
                    self.keyIndex.setdefault(k,{})[ckey] = True
                _setCellInDict(self.rules, key, provider)
                self.depth[key]=depth

    def _configKeysMatching(self, configKey):

        """Iterable over defined keys that match 'configKey'

        A key 'k' in the map is considered to "match" 'configKey' if any of
        'k.parentKeys()' are listed as keys in 'configKey.registrationKeys()'.
        You must not change the configuration map while iterating over the
        keys.  Also, keep in mind that only explicitly-registered keys are
        returned; for instance, load-on-demand rules will only show up as
        wildcard keys."""

        index = self._getBinding('keyIndex')

        if not index:
            return

        for key,depth in adapt(configKey,IConfigKey).registrationKeys():
            self.lockedNamespaces[key] = True
            for k in index.get(key,()):
                yield k





















    def _getConfigData(self, forObj, configKey):

        """Look up the requested value"""

        rules      = self._getBinding('rules')
        value      = NOT_FOUND

        if not rules:
            return value

        xRules     = []

        for name in configKey.lookupKeys():

            rule = rules.get(name)

            if rule is None:
                xRules.append(name)     # track unspecified rules

            elif rule is not _emptyRuleCell:

                value = rule.get()(self, configKey, forObj)

                if value is not NOT_FOUND:
                    break

        # ensure that unspecified rules stay that way, if they
        # haven't been replaced in the meanwhile by a higher-level
        # wildcard rule

        for name in xRules:
            rules.setdefault(name,_emptyRuleCell)

        return value

    getValueFor = _getConfigData    # DEPRECATED


PropertyMap = ConfigMap             # DEPRECATED


def Value(v):
    """Return an 'IRule' that always returns 'v'"""
    return lambda *args: v


class LazyRule(object):

    loadNeeded = True

    def __init__(self, loadFunc, prefix='*', **kw):
        self.load = loadFunc
        self.prefix = prefix
        self.__dict__.update(kw)


    def __call__(self, propertyMap, propName, targetObj):

        if self.loadNeeded:

            try:
                self.loadNeeded = False
                return self.load(propertyMap, self.prefix, propName)

            except:
                del self.loadNeeded
                raise

        return NOT_FOUND













from peak.naming.interfaces import IState

class NamingStateAsSmartProperty(protocols.Adapter):

    protocols.advise(
        instancesProvide = [ISmartProperty],
        asAdapterForProtocols = [IState],
    )

    def computeProperty(self, propertyMap, name, prefix, suffix, targetObject):

        from peak.naming.factories.config_ctx import PropertyPath
        from peak.naming.factories.config_ctx import PropertyContext

        ctx = PropertyContext(targetObject,
            creationParent = targetObject,
            nameInContext = PropertyPath(prefix[:-1]), # strip any trailing '.'
        )

        result = self.subject.restore(ctx, PropertyPath(suffix))

        rule = adapt(result, ISmartProperty, None)
        if rule is not None:
            result = rule.computeProperty(
                propertyMap, name, prefix, suffix, targetObject
            )

        return result













class ServiceArea(Component):

    """Component that acts as a home for "global"-ish services"""

    protocols.advise(instancesProvide=[IServiceArea])

    __services = binding.Make('peak.util.EigenData:EigenDict')

    def getService(self,ruleKey,factory):
        return self.__services.get(ruleKey,NOT_FOUND,factory=factory)































class ConfigurationRoot(ServiceArea):

    """Default implementation for a configuration root.

    If you think you want to subclass this, you're probably wrong.  Note that
    you can have whatever setup code you want, called automatically from .ini
    files loaded by this class.  We recommend you try that approach first."""

    protocols.advise(instancesProvide=[IConfigurationRoot])

    def __instance_offers__(self,d,a):
        pm = d[a] = PropertyMap(self)
        self.setupDefaults(pm)
        return pm

    __instance_offers__ = Make(__instance_offers__,
        offerAs=[IPropertyMap], uponAssembly = True
    )

    iniFiles = ( ('peak','peak.ini'), )

    def setupDefaults(self, propertyMap):
        """Set up 'propertyMap' with default contents loaded from 'iniFiles'"""

        for file in self.iniFiles:
            if isinstance(file,tuple):
                file = fileNearModule(*file)
            config.loadConfigFile(propertyMap, file)


    def noMoreValues(self,root,configKey,forObj): pass

    def noMoreUtilities(self,root,configKey,forObj):
        """DEPRECATED: Use 'noMoreValues()' method instead"""
        return self.noMoreValues(root,configKey,forObj)

    def nameNotFound(self,root,name,forObj):
        return naming.lookup(forObj, name, creationParent=forObj)



class Namespace(object):
    """Traverse to another property namespace

    Use this in .ini files (e.g. '__main__.* = config.Namespace("environ.*")')
    to create a rule that looks up undefined properties in another property
    namespace.

    Or, use this as a way to treat a property namespace as a mapping object::

        myNS = config.Namespace("some.prefix", aComponent)
        myNS['spam.bayes']              # property 'some.prefix.spam.bayes'
        myNS.get('something',default)   # property 'some.prefix.something'

    Or use this in a component class to allow traversing to a property space::

        class MyClass(binding.Component):

            appConfig = binding.Make(
                config.Namespace('MyClass.conf')
            )

            something = binding.Obtain('appConfig/foo.bar.baz')

    In the example above, 'something' will be the component's value for the
    property 'MyClass.conf.foo.bar.baz'.  Note that you may not traverse to
    names beginning with an '_', and traversing to the name 'get' will give you
    the namespace's 'get' method, not the 'get' property in the namespace.  To
    obtain the 'get' property, or properties beginning with '_', you must use
    the mapping style of access, as shown above."""

    def __init__(self, prefix, target=NOT_GIVEN, cacheAttrs=True):
        self._prefix = PropertyName(prefix).asPrefix()
        self._target = target
        self._cache = cacheAttrs

    def __call__(self, suffix):
        """Return a sub-namespace for 'suffix'"""
        return self.__class__(
            PropertyName.fromString(self._prefix+suffix),self._target
        )

    def __getattr__(self, attr):
        if not attr.startswith('_'):
            ob = self.get(attr, NOT_FOUND)
            if ob is not NOT_FOUND:
                if self._cache:
                    setattr(self,attr,ob)   # Cache for future use
                return ob
        raise AttributeError,attr


    def __getitem__(self, key):
        """Return the value of property 'key' within this namespace"""
        ob = self.get(key,NOT_FOUND)
        if ob is not NOT_FOUND:
            return ob
        raise KeyError,key


    def get(self,key,default=None):
        """Return property 'key' within this namespace, or 'default'"""
        if self._target is not NOT_GIVEN:
            return lookup(
                self._target,PropertyName.fromString(self._prefix+key),default
            )
        return default


    def __repr__(self):
        return "config.Namespace(%r,%r)" % (self._prefix,self._target)












    def keys(self):

        items = []

        if self._target is not NOT_GIVEN:

            prel = len(self._prefix)
            append = items.append
            yielded = {}

            for key in iterKeys(self._target,self._prefix+'*'):
                key = key[prel:]
                if key.endswith('?'):
                    key = key[:-1]
                elif key.endswith('*'):
                    continue
                if key not in yielded:
                    append(key)
                    yielded[key]=1

        return items




















class __NamespaceExtensions(protocols.Adapter):

    protocols.advise(
        instancesProvide = [ISmartProperty, IAttachable, IRecipe],
        asAdapterForTypes = [Namespace]
    )

    def computeProperty(self, propertyMap, name, prefix, suffix, targetObject):
        return config.lookup(
            propertyMap, self.subject._prefix+suffix, default=NOT_FOUND
        )

    def setParentComponent(self, parentComponent, componentName=None,
        suggest=False
    ):

        pc = self.subject._target

        if pc is NOT_GIVEN:
            self.subject._target = parentComponent
            return

        elif suggest:
            return

        raise AlreadyRead(
            "%r already has target %r; tried to set %r"
                % (self.subject,pc,parentComponent)
        )


    def __call__(self,client,instDict,attrName):
        subject = self.subject
        return subject.__class__(subject._prefix[:-1], client, subject._cache)







class PropertySet(object):

    """DEPRECATED"""

    def __init__(self, targetObj, prefix):
        self.prefix = PropertyName(prefix).asPrefix()
        self.target = targetObj

    def __getitem__(self, key, default=NOT_GIVEN):
        return config.lookup(self.target,self.prefix+key,default)

    def get(self, key, default=None):
        return config.lookup(self.target,self.prefix+key,default)

    def __getattr__(self,attr):
        return self.__class__(self.target, self.prefix+attr)

    def of(self, target):
        return self.__class__(target, self.prefix[:-1])

    def __call__(self, default=None, forObj=NOT_GIVEN):

        if forObj is NOT_GIVEN:
            forObj = self.target

        return config.lookup(forObj, self.prefix[:-1], default)















def instancePerComponent(factorySpec):
    """DEPRECATED: use factory mechanisms instead"""
    return lambda foundIn, configKey, forObj: importObject(factorySpec)(forObj)


def provideInstance(factorySpec):
    """DEPRECATED, use 'CreateViaFactory(key)' instead"""
    _ob = []
    def rule(foundIn, configKey, forObj):
        if not _ob:
            _ob.append(importObject(factorySpec)(
                binding.getParentComponent(foundIn))
            )
        return _ob[0]
    return rule


























