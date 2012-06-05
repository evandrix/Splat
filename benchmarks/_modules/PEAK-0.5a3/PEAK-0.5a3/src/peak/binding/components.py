"""Basic binding tools"""

from __future__ import generators
from peak.api import *

from once import *
from interfaces import *
from types import ModuleType
from peak.naming.names import toName, AbstractName, COMPOUND_KIND, IName
from peak.naming.syntax import PathSyntax
from peak.util.EigenData import AlreadyRead
from peak.config.interfaces import IConfigKey, IPropertyMap, \
    IConfigurationRoot, NullConfigRoot
from peak.config.registries import ImmutableConfig
from peak.util.imports import importString


__all__ = [
    'Base', 'Component', 'whenAssembled', 'Obtain', 'Require', 'Delegate',
    'bindTo', 'requireBinding', 'bindSequence', 'bindToParent', 'bindToSelf',
    'getRootComponent', 'getParentComponent', 'lookupComponent',
    'acquireComponent', 'notifyUponAssembly', 'PluginsFor', 'PluginKeys',
    'bindToUtilities', 'bindToProperty', 'Constant', 'delegateTo',
    'getComponentName', 'getComponentPath', 'Acquire', 'ComponentName',
]

from _once import BaseDescriptor

class _proxy(BaseDescriptor):

    def __init__(self,attrName):
        self.attrName = attrName

    def usageError(self):
        raise AttributeError, self.attrName

    def computeValue(self,ob,d,a): raise AttributeError, a




def getComponentPath(component, relativeTo=None):

    """Get 'ComponentName' that would traverse from 'relativeTo' to 'component'

    If 'relativeTo' is 'None' or not supplied, the path returned is relative
    to the root component of 'component'.  Note that if supplied, 'relativeTo'
    must be an ancestor (parent, parent's parent, etc.) of 'component'."""

    path = []; root=None

    if relativeTo is None:
        root = getRootComponent(component)

    c = component

    while 1:

        if c is root:
            path.append(''); break

        elif c is relativeTo:
            break

        path.append(getComponentName(c) or '*')

        c = getParentComponent(c)

        if c is None:
            break

    path.reverse()
    return ComponentName(path)









def Constant(value, **kw):
    """DEPRECATED: Use 'Make(lambda: value)' instead"""
    return Make(lambda: value, **kw)


class ModuleAsNode(object):

    protocols.advise(
        instancesProvide=[IBindingNode],
        asAdapterForTypes=[ModuleType],
    )

    def __init__(self,ob,protocol):
        self.module = ob

    def getParentComponent(self):
        m = '.'.join(self.module.__name__.split('.')[:-1])
        if m: return importString(m)
        return None

    def getComponentName(self):
        return self.module.__name__.split('.')[-1]


    # XXX it's not clear if we really need the below, since
    # XXX they are not currently used with an adaptation

    def _getConfigData(self, forObj, configKey):
        return NOT_FOUND

    def notifyUponAssembly(self,child):
        child.uponAssembly()









def getParentComponent(component):

    """Return parent of 'component', or 'None' if root or non-component"""

    try:
        gpc = component.getParentComponent

    except AttributeError:

        component = adapt(component,IBindingNode,None)

        if component is not None:
            return component.getParentComponent()

    else:
        return gpc()


def getComponentName(component):

    """Return name of 'component', or 'None' if root or non-component"""

    try:
        gcn = component.getComponentName

    except AttributeError:

        component = adapt(component,IBindingNode,None)

        if component is not None:
            return component.getComponentName()

    else:
        return gcn()







def getRootComponent(component):

    """Return the root component of the tree 'component' belongs to"""

    next = component

    while next is not None:
        component = next
        next = getParentComponent(component)

    return component




def notifyUponAssembly(parent,child):

    """Call 'child.uponAssembly()' as soon as 'parent' knows all its parents"""

    try:
        nua = parent.notifyUponAssembly

    except AttributeError:

        parent = getParentComponent(parent)

        if parent is None:
            child.uponAssembly()
        else:
            notifyUponAssembly(parent,child)

    else:
        nua(child)








def acquireComponent(component, name):

    """Acquire 'name' relative to 'component', w/fallback to naming.lookup()

    'name' is looked for as an attribute of 'component'.  If not found,
    the component's parent will be searched, and so on until the root component
    is reached.  If 'name' is still not found, and the root component
    implements 'config.IConfigurationRoot', the name will be looked up in the
    default naming context, if any.  Otherwise, a 'NameNotFound' error will be
    raised."""

    prev = target = component

    while target is not None:

        ob = getattr(target, name, NOT_FOUND)

        if ob is not NOT_FOUND:
            return ob

        prev = target
        target = getParentComponent(target)

    else:
        return adapt(
            prev, IConfigurationRoot, NullConfigRoot
        ).nameNotFound(
            prev, name, component
        )












class ComponentName(AbstractName):

    """Path between components

    Component Path Syntax

        Paths are '"/"' separated attribute names.  Path segments of '"."' and
        '".."' mean the same as they do in URLs.  A leading '"/"' (or a
        compound name beginning with an empty path segment), will be treated
        as an "absolute path" relative to the component's root component.

        Paths beginning with anything other than '"/"', '"./"', or '"../"' are
        acquired, which means that the first path segment will be looked
        up using 'acquireComponent()' before processing the rest of the path.
        (See 'acquireComponent()' for more details.)  If you do not want
        a name to be acquired, simply prefix it with './' so it is relative
        to the starting object.

        All path segments after the first are interpreted as attribute names
        to be looked up, beginning at the component referenced by the first
        path segment.  '.' and '..' are interpreted the same as for the first
        path segment.
    """

    nameKind = COMPOUND_KIND

    syntax = PathSyntax(
        direction = 1,
        separator = '/',
    )

    protocols.advise(
        instancesProvide=[IComponentKey]
    )







    def findComponent(self, component, default=NOT_GIVEN):

        if not self:  # empty name refers to self
            return component

        parts = iter(self)
        attr = parts.next()                 # first part
        pc = _getFirstPathComponent(attr)


        if pc:  ob = pc(component)
        else:   ob = acquireComponent(component, attr)

        resolved = []
        append = resolved.append

        try:
            for attr in parts:
                pc = _getNextPathComponent(attr)
                if pc:  ob = pc(ob)
                else:   ob = getattr(ob,attr)
                append(attr)

        except AttributeError:

            if default is not NOT_GIVEN:
                return default

            raise exceptions.NameNotFound(
                resolvedName = ComponentName(resolved),
                remainingName = ComponentName([attr] + [a for a in parts]),
                resolvedObj = ob
            )

        return ob






_getFirstPathComponent = dict( (
    ('',   getRootComponent),
    ('.',  lambda x:x),
    ('..', getParentComponent),
) ).get


_getNextPathComponent = dict( (
    ('',   lambda x:x),
    ('.',  lambda x:x),
    ('..', getParentComponent),
) ).get


def lookupComponent(component, name, default=NOT_GIVEN, adaptTo=None,
    creationName=None, suggestParent=True):

    """Lookup 'name' as a component key relative to 'component'

    'name' can be any object that implements or is adaptable to 'IComponentKey'.
    Such objects include 'peak.naming' names, interface objects, property
    names, and any custom objects you may create that implement 'IComponentKey'.
    Strings will be converted to a URL, or to a 'ComponentName' if they have
    no URL prefix.  If the key cannot be found, an 'exceptions.NameNotFound'
    error will be raised unless a 'default' other than 'NOT_GIVEN' is provided.
    """

    result = adapt(name, IComponentKey).findComponent( component, default )

    if adaptTo is not None:
        result = adapt(result,adaptTo)

    if suggestParent:
        suggestParentComponent(component,creationName,result)

    return result





# Declare that strings should be converted to names (with a default class
# of ComponentName), in order to use them as component keys
#
protocols.declareAdapter(
    lambda ob, proto: toName(ob, ComponentName, 1),
    provides = [IComponentKey],
    forTypes = [str, unicode],
)


class ConfigFinder(object):

    """Look up utilities or properties"""

    __slots__ = 'ob'

    protocols.advise(
        instancesProvide = [IComponentKey],
        asAdapterForProtocols = [IConfigKey]
    )

    def __init__(self, ob, proto):
        self.ob = ob

    def findComponent(self, component, default=NOT_GIVEN):
        return config.lookup(component, self.ob, default)

    def __repr__(self):
        return repr(self.ob)












class PluginKeys(object):
    """Component key that finds the keys of plugins matching a given key

    Usage::

        # get a sorted list of the keys to all 'foo.bar' plugins
        pluginNames = binding.Obtain( binding.PluginKeys('foo.bar') )

        # get an unsorted list of the keys to all 'foo.bar' plugins
        pluginNames = binding.Obtain(
            binding.PluginKeys('foo.bar', sortBy=None)
        )

    'sortBy' is either a false value or a callable that will be applied to
    each key to get a value for sorting purposes.  If set to a false value,
    the keys will be in the same order as yielded by 'config.iterKeys()'.
    'sortBy' defaults to 'str', which means the keys will be sorted based
    on their string form.
    """

    protocols.advise(
        instancesProvide = [IComponentKey],
    )

    def __init__(self, configKey, sortBy=str):
        self.configKey = adapt(configKey, IConfigKey)
        self.sortBy = sortBy


    def findComponent(self, component, default=NOT_GIVEN):

        keys = config.iterKeys(component, self.configKey)

        if self.sortBy:
            sortBy = self.sortBy
            keys = [(sortBy(k),k) for k in keys]
            keys.sort()
            return [k for (sortedBy,k) in keys]

        return list(keys)

class PluginsFor(PluginKeys):

    """Component key that finds plugins matching a configuration key

    Usage::

        # get a list of 'my.plugins.X' plugins, sorted by property name
        myPlugins = binding.Obtain( binding.PluginsFor('my.plugins') )

        # get an unsorted list of all 'foo.bar' plugins
        myPlugins = binding.Obtain(
            binding.PluginsFor('foo.bar', sortKeys=False)
        )

    This key type works similarly to 'PluginKeys()', except that it returns the
    plugins themselves, rather than their configuration keys.

    'sortBy' is either a false value or a callable that will be applied to
    each plugin's key to get a value for sorting purposes.  If set to a false
    value,  plugins will be in the same order as their keys are yielded by
    'config.iterKeys()'.  'sortBy' defaults to 'str', which means the plugins
    will be sorted based on the string form of the keys used to retrieve them.
    """

    def findComponent(self, component, default=NOT_GIVEN):
        keys = super(PluginsFor,self).findComponent(component)
        return [adapt(k,IComponentKey).findComponent(component) for k in keys]














class Obtain(Attribute):
    """'Obtain(componentKey,[default=value])' - finds/caches a needed component

    Usage examples::

        class someClass(binding.Component):

            thingINeed = binding.Obtain("path/to/service")
            otherThing = binding.Obtain(IOtherThing)
            aProperty  = binding.Obtain(PropertyName('some.prop'), default=42)

    'someClass' instances can then refer to their attributes, such as
    'self.thingINeed', instead of repeatedly calling
    'self.lookupComponent(someKey)'.

    The initial argument to the 'Obtain' constructor must be adaptable to
    'binding.IComponentKey'.  If a 'default' keyword argument is supplied,
    it will be used as the default in case the specified component key is not
    found.

    XXX need to document IComponentKey translations somewhere... probably
        w/IComponentKey"""

    default = NOT_GIVEN
    targetName = None

    def __init__(self,targetName,**kw):
        self.targetName = adapt(targetName, IComponentKey)
        super(Obtain,self).__init__(**kw)

    def computeValue(self, obj, instanceDict, attrName):
        return self.targetName.findComponent(obj, self.default)

    def __repr__(self):
        if self.__doc__:
            return "binding.Obtain(%r):\n\n%s" % (self.targetName,self.__doc__)
        else:
            return "binding.Obtain(%r)" % (self.targetName,)

bindTo = Obtain     # XXX DEPRECATED

def bindSequence(*targetNames, **kw):
    """DEPRECATED: use binding.Obtain([key1,key2,...])"""
    return Obtain(targetNames, **kw)


class SequenceFinder(object):

    """Look up sequences of component keys"""

    __slots__ = 'ob'

    protocols.advise(
        instancesProvide = [IComponentKey],
        asAdapterForProtocols = [protocols.sequenceOf(IComponentKey)]
    )

    def __init__(self, ob, proto):
        self.ob = ob

    def findComponent(self, component, default=NOT_GIVEN):
        return tuple([ob.findComponent(component, default) for ob in self.ob])


def whenAssembled(func, **kw):
    """DEPRECATED: use 'Make(func, uponAssembly=True)'"""
    kw['uponAssembly'] = True
    return Make(func, **kw)














class Delegate(Make):

    """Delegate attribute to the same attribute of another object

    Usage::

        class PasswordFile(binding.Component):
            shadow = binding.Obtain('config:etc.shadow/')
            checkPwd = changePwd = binding.Delegate('shadow')

    The above is equivalent to this longer version::

        class PasswordFile(binding.Component):
            shadow = binding.Obtain('config:etc.shadow/')
            checkPwd = binding.Obtain('shadow/checkPwd')
            changePwd = binding.Obtain('shadow/changePwd')

    Because 'Delegate' uses the attribute name being looked up, you do not
    need to create a separate binding for each attribute that is delegated,
    as you do when using 'Obtain()'."""

    delegateAttr = None

    def __init__(self, delegateAttr, **kw):
        def delegate(s,d,a):
            return getattr(getattr(s,delegateAttr),a)
        super(Delegate,self).__init__(delegate,delegateAttr=delegateAttr,**kw)

    def __repr__(self):
        if self.__doc__:
            return "binding.Delegate(%r):\n\n%s" % (
                self.delegateAttr,self.__doc__
            )
        else:
            return "binding.Delegate(%r)" % (self.delegateAttr,)


delegateTo = Delegate   # XXX DEPRECATED; backward compat.



def Acquire(key, **kw):
    """DEPRECATED: use Obtain(key, offerAs=[key])"""
    key = adapt(key,IConfigKey)
    kw['offerAs'] = [key]   # XXX should check that kwarg wasn't supplied
    return Obtain(key,**kw)

def bindToParent(level=1, **kw):
    """DEPRECATED: use binding.Obtain('..')"""
    return Obtain('/'.join(['..']*level), **kw)

def bindToSelf(**kw):
    """DEPRECATED: use binding.Obtain('.')"""
    return Obtain('.', **kw)

def bindToProperty(propName, default=NOT_GIVEN, **kw):
    """DEPRECATED: use binding.Obtain(PropertyName(propName))"""
    kw['default'] = default
    return binding.Obtain(PropertyName(propName), **kw)























class Require(Attribute):

    """Placeholder for a binding that should be (re)defined by a subclass"""

    description = ''

    def __init__(self, description="", **kw):
        kw['description'] = description
        super(Require,self).__init__(**kw)


    def computeValue(self, obj, instanceDict, attrName):
        raise NameError("Class %s must define %s; %s"
            % (obj.__class__.__name__, attrName, self.description)
        )

    def __repr__(self):
        if self.__doc__:
            return "binding.Require(%r):\n\n%s" % (
                self.description,self.__doc__
            )
        else:
            return "binding.Require(%r)" % (self.description,)

requireBinding = Require    # XXX DEPRECATED



def bindToUtilities(iface, **kw):
    """DEPRECATED: bind list of all 'iface' utilities above the component"""

    return Make(lambda self: list(config.iterValues(self,iface)), **kw)









class _Base(object):

    """Basic attribute management and "active class" support"""

    __metaclass__ = ActiveClass

    protocols.advise(
        instancesProvide = [IBindableAttrs]
    )

    def _setBinding(self, attr, value, useSlot=False):

        self._bindingChanging(attr,value,useSlot)

        if useSlot:
            getattr(self.__class__,attr).__set__(self,value)

        else:
            self.__dict__[attr] = value


    def _getBinding(self, attr, default=None, useSlot=False):

        if useSlot:
            val = getattr(self,attr,default)

        else:
            val = self.__dict__.get(attr,default)

        if val is not default:

            val = self._postGet(attr,val,useSlot)

            if val is NOT_FOUND:
                return default

        return val




    def _getBindingFuncs(klass, attr, useSlot=False):
        if useSlot:
            d = getattr(klass,attr)
        else:
            d = _proxy(attr)
        return d.__get__, d.__set__, d.__delete__

    _getBindingFuncs = classmethod(_getBindingFuncs)


    def _delBinding(self, attr, useSlot=False):

        self._bindingChanging(attr, NOT_FOUND, useSlot)

        if useSlot:
            d = getattr(self.__class__,attr).__delete__

            try:
                d(self)
            except AttributeError:
                pass

        elif attr in self.__dict__:
            del self.__dict__[attr]

    def _hasBinding(self,attr,useSlot=False):

        if useSlot:
            return hasattr(self,attr)
        else:
            return attr in self.__dict__


    def _bindingChanging(self,attr,newval,isSlot=False):
        pass


    def _postGet(self,attr,value,isSlot=False):
        return value


class Component(_Base):

    """Thing that can be composed into a component tree, w/binding & lookups"""

    protocols.advise(
        classProvides = [IComponentFactory],
        instancesProvide = [IComponent]
    )


    def __init__(self, parentComponent=NOT_GIVEN, componentName=None, **kw):

        # Set up keywords first, so state is sensible
        if kw:

            klass = self.__class__

            for k,v in kw.iteritems():
                if hasattr(klass,k):
                    setattr(self,k,v)
                else:
                    raise TypeError(
                        "%s constructor has no keyword argument %s" %
                        (klass, k)
                    )

        # set our parent component and possibly invoke assembly events
        if parentComponent is not NOT_GIVEN or componentName is not None:
            self.setParentComponent(parentComponent,componentName)

    lookupComponent = lookupComponent










    def fromZConfig(klass, section):

        """Classmethod: Create an instance from a ZConfig 'section'"""

        # ZConfig uses unicode for keys and defaults unsupplied values to None
        data = dict([(str(k),v) for k,v in section.__dict__.items()
            if v is not None])

        if not hasattr(klass,'_name') and '_name' in data:
            del data['_name']

        if not hasattr(klass,'_matcher') and '_matcher' in data:
            del data['_matcher']

        return klass(**data)

    fromZConfig = classmethod(fromZConfig)


    def setParentComponent(self, parentComponent, componentName=None,
        suggest=False):

        pc = self.__parentSetting

        if pc is NOT_GIVEN:
            self.__parentSetting = parentComponent
            self.__componentName = componentName
            self.__parentComponent  # lock and invoke assembly events
            return

        elif suggest:
            return

        raise AlreadyRead(
            "Component %r already has parent %r; tried to set %r"
            % (self,pc,parentComponent)
        )

    __parentSetting = NOT_GIVEN
    __componentName = None

    def __parentComponent(self,d,a):

        parent = self.__parentSetting
        if parent is NOT_GIVEN:
            parent = self.__parentSetting = None

        d[a] = parent
        if parent is None:
            self.uponAssembly()
        elif (self.__class__.__attrsToBeAssembled__
            or self._getBinding('__objectsToBeAssembled__')):
                notifyUponAssembly(parent,self)

        return parent

    __parentComponent = Make(__parentComponent, suggestParent=False)


    def getParentComponent(self):
        return self.__parentComponent

    def getComponentName(self):
        return self.__componentName

    __instance_offers__ = Make(
        'peak.config.config_components:PropertyMap', offerAs=[IPropertyMap]
    )














    def _configKeysMatching(self, configKey):

        """Iterable over defined keys that match 'configKey'

        A key 'k' in the map is considered to "match" 'configKey' if any of
        'k.parentKeys()' are listed as keys in 'configKey.registrationKeys()'.
        You must not change the configuration map while iterating over the
        keys.  Also, keep in mind that only explicitly-registered keys are
        returned; for instance, load-on-demand rules will only show up as
        wildcard keys."""

        maps = [self.__class__.__class_offers__]
        attr = self._getBinding('__instance_offers__')

        if attr:
            maps.append(attr)

        yielded = {}

        for cMap in maps:
            for key in cMap._configKeysMatching(configKey):
                if key in yielded:
                    continue
                yield key
                yielded[key] = 1
















    def _getConfigData(self, forObj, configKey):

        attr = self._getBinding('__instance_offers__')

        if attr:
            value = attr.getValueFor(forObj, configKey)

            if value is not NOT_FOUND:
                return value

        attr = self.__class__.__class_offers__.lookup(configKey)

        if attr:
            return getattr(self, attr, NOT_FOUND)

        return NOT_FOUND


    def registerProvider(self, configKey, provider):
        self.__instance_offers__.registerProvider(configKey, provider)


    def notifyUponAssembly(self,child):

        tba = self.__objectsToBeAssembled__

        if tba is None:
            child.uponAssembly()    # assembly has already occurred
        else:
            tba.append(child)       # save reference to child for callback

            if (len(tba)==1 and self.__parentSetting is not NOT_GIVEN
                and len(tba)==1 and not self.__class__.__attrsToBeAssembled__
            ):
                # Make sure our parent calls us, since we need to call a
                # child now, but would not have been registered ourselves.
                notifyUponAssembly(self.getParentComponent(),self)




    def uponAssembly(self):
        """Don't override this unless you can handle the reentrancy issues!"""
        tba = self.__objectsToBeAssembled__

        if tba is None:
            return

        self.__objectsToBeAssembled__ = None

        try:
            while tba:
                ob = tba.pop()
                try:
                    ob.uponAssembly()
                except:
                    tba.append(ob)
                    raise

            for attr in self.__class__.__attrsToBeAssembled__:
                getattr(self,attr)

        except:
            self.__objectsToBeAssembled__ = tba
            raise

    __objectsToBeAssembled__ = Make(list)


    def __attrsToBeAssembled__(klass,d,a):
        aa = {}
        map(aa.update, getInheritedRegistries(klass, '__attrsToBeAssembled__'))

        for attrName, descr in klass.__class_descriptors__.items():
            notify = getattr(descr,'uponAssembly',False)
            if notify: aa[attrName] = True

        return aa

    __attrsToBeAssembled__ = classAttr(Make(__attrsToBeAssembled__))


    def __class_offers__(klass,d,a):

        return ImmutableConfig(
            baseMaps = getInheritedRegistries(klass, '__class_offers__'),
            items = [(adapt(key,IConfigKey), attrName)
                for attrName, descr in klass.__class_descriptors__.items()
                    for key in getattr(descr,'offerAs',())
            ]
        )


    __class_offers__ = classAttr(Make(__class_offers__))





Base = Component    # XXX backward compatibility; deprecated























