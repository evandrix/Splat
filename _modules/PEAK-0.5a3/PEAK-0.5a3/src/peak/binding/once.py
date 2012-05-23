"""'Once' objects and classes"""

from __future__ import generators
from peak.api import NOT_FOUND, protocols, adapt
from peak.util.imports import importObject, importString
from peak.util.signature import ISignature, getPositionalArgs
from interfaces import IAttachable, IActiveDescriptor, IRecipe
from peak.config.interfaces import IConfigKey
from _once import *
from protocols import IOpenProvider, IOpenImplementor, NO_ADAPTER_NEEDED
from protocols.advice import metamethod, getMRO
from warnings import warn
from types import ClassType

__all__ = [
    'Make', 'Once', 'New', 'Copy', 'Activator', 'ActiveClass',
    'getInheritedRegistries', 'classAttr', 'Singleton', 'metamethod',
    'Attribute', 'ComponentSetupWarning', 'suggestParentComponent'
]

class ComponentSetupWarning(UserWarning):
    """Large iterator passed to suggestParentComponent"""

def supertype(supertype,subtype):

    """Workaround for 'super()' not handling metaclasses well

    Note that this will *skip* any classic classes in the MRO!
    """

    mro = iter(subtype.__mro__)

    for cls in mro:
        if cls is supertype:
            for cls in mro:
                if hasattr(cls,'__mro__'):
                    return cls
            break

    raise TypeError("Not sub/supertypes:", supertype, subtype)

class Descriptor(BaseDescriptor):

    """Attribute descriptor with lazy initialization and caching

    A 'Descriptor' (or subclass) instance is a Python attribute descriptor,
    similar to the ones created using the Python 'property' built-in type.
    However, where 'property' instances invoke a function on every access to
    the attribute, 'binding.Descriptor' instances only call their
    'computeValue()' method once, caching the result in the containing object's
    dictionary.  Thereafter, the value in the dictionary is reused, instead of
    calling the function each time.  If the attribute is deleted (e.g. via
    'del anObj.anAttr') or the value is cleared from the dictionary, the
    'computeValue()' method will be called again, the next time that the
    attribute is retrieved.

    Because the instance dictionary is used to store the attribute value, a
    'Descriptor' needs to know its name, so that it knows what key to store its
    value under.  Unfortunately, Python does not provide a way for descriptors
    to know what name(s) they are accessible under in a class, so you must
    explicitly provide an 'attrName' value, either as a constructor keyword
    argument, or by defining it in a subclass.  Many 'Descriptor' subclasses
    have the ability to guess or detect what 'attrName' should be used, but you
    must still explicitly provide it if they are unable to do so automatically.
    Failure to supply a correct 'attrName' will result in a 'TypeError' when
    the attribute is used.

    'Descriptor' instances have the following attributes which may be set by
    keyword arguments to the class' constructor:

        'attrName' -- sets the name which the descriptor will use to get/set
        its value in the instance dictionary.  Ordinarily this should be the
        same as the name given to the descriptor in its containing class, but
        you may occasionally wish it to be something else.


        'computeValue(obj, instDict, attrName)' -- a function that will be
        called whenever the attribute is accessed and no value for the
        attribute is present in the object's instance dictionary.  The function
        will be passed three arguments: the object that owns the attribute, the
        object's instance dictionary, and the descriptor's 'attrName'.

         The value returned will be treated as the attribute's value.  It will
         also be cached in the object's instance dictionary to avoid repeat
         calls, unless the descriptor's 'noCache' attribute is 'True'.

         Note that the default implementation of 'computeValue()' simply raises
         an 'AttributeError'.  Also note that the call signature of
         'computeValue()' is the same as that of 'binding.IRecipe'.  That is,
         any object that provides 'IRecipe' may be used as a 'computeValue'
         attribute.  'Descriptor' does not perform any adaptation, however, so
         if your desired object must be adapted to 'IRecipe', you should do so
         before assigning it to the 'computeValue' attribute.


        'noCache' -- if set to 'True', the descriptor will not cache its
        'computeValue()' results in the owning object's instance dictionary.
        This makes the descriptor's behavior more similar to the Python
        'property' type.  But, 'computeValue()' will not be called when the
        attribute is currently set (i.e., a value is in the object's instance
        dictionary under 'attrName'), so the behavior is still quite different
        from the 'property' type.


        'onSet(obj, attrName, value)' -- a function that will be called
        whenever the attribute is set, or when the result of 'computeValue()'
        is to be cached.  The function will be passed three arguments: the
        object that owns the attribute, the descriptor's 'attrName', and the
        'value' that is to be set.  The function may return the passed-in
        value, or change it by returning a different value.  To prevent the
        value from being set, the function should raise an exception.  If you
        do not set this attribute, its default implementation simply returns
        the value unmodified.


        'ofClass(attrName, klass)' -- a function that will be called whenever
        the descriptor is retrieved from its class.  The default implementation
        simply returns the descriptor.


        'permissionNeeded' -- a 'peak.security.IAbstractPermission', or 'None'.
        This is a convenience feature for use with the 'peak.security' package.

    You can override the methods described above in subclasses.  Keep in mind,
    however, that you will then need to add a 'self' parameter in addition to
    the ones described above.  The 'self' argument will refer to the
    'Descriptor' instance.

    The 'Descriptor' class is rarely used directly; normally you will use one
    of its subclasses, which have many additional features for more convenient
    use.  However, many of those subclasses themselves use 'Descriptor'
    instances as part of their definition.  That's why this exists as a
    separate base class: to make it possible to use descriptors as part of the
    definition of descriptor classes."""

    permissionNeeded = None    # IGuardedDescriptor; declared in peak.security

    def __init__(self,**kw):

        """Create a descriptor from keyword arguments

        You may pass any keyword arguments, as long as they represent existing
        attributes defined by the 'Descriptor' class (or subclass, if
        this constructor is used by the subclass)."""

        klass = self.__class__

        for k,v in kw.items():
            if hasattr(klass,k):
                setattr(self,k,v)
            else:
                raise TypeError("%r has no keyword argument %r" % (klass,k))

# XXX Set up noCache to set the 'isVolatile' attribute inherited from
# BaseDescriptor.  This should be changed by changing BaseDescriptor to define
# noCache instead of isVolatile, but doing it this way ensures backward
# compatibility.  In alpha 4, this kludge should be removed.

Descriptor.noCache = Descriptor(
    attrName = 'noCache',
    onSet = lambda o,a,v: setattr(o,'isVolatile',v and 1 or 0) or v,
    computeValue = lambda o,d,a: False
)

def getInheritedRegistries(klass, registryName):

    """Minimal set of 'registryName' registries in reverse MRO order"""

    bases = klass.__bases__

    if len(bases)==1:
        reg = getattr(bases[0],registryName,NOT_FOUND)
        if reg is not NOT_FOUND:
            yield reg

    else:
        mro = list(getMRO(klass))
        bases = [(-mro.index(b),b) for b in bases]
        bases.sort()
        for (b,b) in bases:
            reg = getattr(b,registryName,NOT_FOUND)
            if reg is not NOT_FOUND:
                yield reg


def suggestParentComponent(parent,name,child):

    """Suggest to 'child' that it has 'parent' and 'name'

    If 'child' does not support 'IAttachable' and is a container that derives
    from 'tuple' or 'list', all of its elements that support 'IAttachable'
    will be given a suggestion to use 'parent' and 'name' as well.  Note that
    this means it would not be a good idea to use this on, say, a 10,000
    element list (especially if the objects in it aren't components), because
    this function has to check all of them."""

    ob = adapt(child,IAttachable,None)

    if ob is not None:
        # Tell it directly
        ob.setParentComponent(parent,name,suggest=True)




class _SequenceAsAttachable(protocols.Adapter):

    """Set parent component for all members of a list/tuple"""

    protocols.advise(
        instancesProvide = [IAttachable],
        asAdapterForTypes = [list, tuple],
    )

    def setParentComponent(self,parentComponent,componentName=None,suggest=False):

        ct = 0

        for ob in self.subject:

            ob = adapt(ob,IAttachable,None)

            if ob is not None:
                ob.setParentComponent(parentComponent,componentName,suggest)
            else:
                ct += 1
                if ct==100:
                    warn(
                        ("Large iterator for %s; if it will never"
                         " contain components, this is wasteful.  (You may"
                         " want to set 'suggestParent=False' on the attribute"
                         " binding or lookupComponent() call, if applicable.)"
                         % componentName),
                        ComponentSetupWarning, 3
                    )











def Copy(obj, **kw):

    """DEPRECATED: Use 'Make(lambda: copy(obj))' or 'Make(lambda: expr)'"""

    from copy import copy
    return Make(
        lambda s,d,a: copy(obj), **kw
    )


class AttributeClass(type):

    """Help attribute classes keep class docs separate from instance docs"""

    def __new__(meta, name, bases, cdict):
        classDoc = cdict.get('__doc__')
        cdict['__doc__'] = Descriptor(
            attrName = '__doc__',
            computeValue = lambda s,d,a: s.doc,
            ofClass = lambda a,k: classDoc
        )
        return supertype(AttributeClass,meta).__new__(meta,name,bases,cdict)



















class Attribute(Descriptor):
    """Descriptor for Component Attribute Bindings

    'Attribute' is a 'Descriptor' with additional features to make component
    interconnection easier.  Specifically, 'Attribute' adds the ability to
    automatically adapt computed or assigned values to a specific interface,
    and the ability to automatically "suggest" to an assigned value that the
    containing object should become its parent component.  In addition,
    'Attribute' has various metadata attributes that can be read by a
    containing class, to enable various features such as "offering" the
    attribute as a supplier of a particular interface or configuration key.

    In addition, if an 'Attribute' is placed in a 'binding.Component' subclass
    (or any class whose metaclass derives from 'binding.Activator'), it will
    automatically discover its 'attrName' from the class, so that you don't
    have to explicitly supply it.

    'Attribute' is primarily an abstract base class; you will ordinarily use
    'Make', 'Obtain', 'Require', or 'Delegate' instead.  However, all of those
    subclasses accept the same keyword arguments, and have the same basic
    lazy initialization and caching behavior.  They differ only in *how* they
    compute the attribute value, and in their constructors' positional arguments.

    In addition to the attributes defined by the 'Descriptor' base class,
    'Attribute' instances also have the following attributes, which may be
    overridden in subclasses, or by supplying constructor keyword arguments:

        'offerAs' -- A sequence of configuration keys under which the attribute
        should be registered.  This tells the containing 'Component' class
        to offer the attribute's value to child components when they look up
        any of the specified configuration keys.  Values in the supplied
        sequence will be adapted to the 'config.IConfigKey' interface.  Default
        value: an empty list.  (Note that this attribute has no effect unless
        the 'Attribute' is placed in a 'binding.Component' subclass.)

        'uponAssembly' -- A flag indicating whether the attribute should be
        initialized as soon as its containing component is part of a complete
        component hierarchy.  Default value: False.  (Note that this attribute
        has no effect unless the 'Attribute' is placed in a 'binding.Component'
        subclass.)

        'doc' -- A docstring, used to give an appropriate representation of the
        attribute when it's rendered by 'pydoc' or the Python 'help()'
        function.

        'adaptTo' -- the interface that values of this attribute should be
        adapted to, or 'None'.  If not 'None', then whenever the attribute is
        set (or its 'computeValue()' result is cached), the value will be
        adapted to this interface before being stored.  If adaptation fails,
        a 'NotImplementedError' will be raised.  (Note that this behavior is
        implemented by 'Attribute.onSet()'; if you override the default
        'onSet()', this adaptation will not take place unless your replacement
        does it.)

        'suggestParent' -- should assigned values be informed that they are
        being attached to the containing component?  This value defaults to
        'True', so you should set it to 'False' if you do not want the
        attachment to happen.  If 'True', then whenever the attribute is set
        (or its 'computeValue()' result is cached), 'suggestParentComponent()'
        will be called to let the value know that the containing component may
        be the value's parent component, and what attribute name it is being
        referenced by.  Note that this call happens *after* the value is first
        adapted to the 'adaptTo' interface, if applicable, and is also
        performed by 'Attribute.onSet()', so the same warning about overriding
        'onSet()' applies here.
    """

    __metaclass__ = AttributeClass

    protocols.advise(
        instancesProvide = [IActiveDescriptor]
    )   # also IGuardedDescriptor; declared in peak.security

    # XXX Set up 'activateUponAssembly' to set the 'uponAssembly' attribute
    # XXX This is for backward compatibility only, and should go away in a4

    activateUponAssembly = Descriptor(
        attrName = 'activateUponAssembly',
        onSet = lambda o,a,v: setattr(o,'uponAssembly',v and 1 or 0) or v,
        computeValue = lambda o,d,a: False
    )

    offerAs = ()
    uponAssembly = False
    doc = None
    adaptTo = None
    suggestParent = True


    def activateInClass(self,klass,attrName):
        setattr(klass, attrName, self._copyWithName(attrName))
        return self


    def _copyWithName(self, attrName):
        return Descriptor(
            attrName     = attrName,
            computeValue = self.computeValue,
            ofClass      = self.ofClass,
            onSet        = self.onSet,
            noCache      = self.noCache,
            permissionNeeded = self.permissionNeeded
        )


    def __repr__(self):
        if self.__doc__:
            return "binding.Attribute:\n\n%s" % self.__doc__
        else:
            return "binding.Attribute()"


    def onSet(self, obj, attrName, value):

        if self.adaptTo is not None:
            value = adapt(value, self.adaptTo)

        if self.suggestParent:
            suggestParentComponent(obj, attrName, value)
        return value



    # The following methods only get called when an instance of this class is
    # used as a descriptor in a classic class or other class that doesn't
    # support active descriptors.  So, we will use the invocation of these
    # methods to bootstrap our activation.  Once activated, these methods won't
    # be called any more.

    def __get__(self, ob, typ=None):
        if ob is None:
            return self
        return self._installedDescr(ob.__class__).__get__(ob,typ)


    def __set__(self,ob,value):
        self._installedDescr(ob.__class__).__set__(ob,value)


    def __delete__(self,ob,value):
        self._installedDescr(ob.__class__).__delete__(ob)


    def _installedDescr(self, klass):
        # Return a newly installed descriptor proxy to use, or raise a usage
        # error if self doesn't know its own right name.

        from protocols.advice import getMRO
        name = self.attrName

        for cls in getMRO(klass):
            if name in cls.__dict__:
                if cls.__dict__[name] is self:
                    # Install a proxy, so we don't have to do this again!
                    descr = self._copyWithName(name)
                    setattr(cls, name, descr)
                    return descr
                else:
                    break

        # If we get here, we were not found under the name we were given
        self.usageError()


class _MultiRecipe:

    """ADAPTER: Sequence(IRecipe) --> IRecipe"""

    protocols.advise(
        instancesProvide = [IRecipe],
        asAdapterForProtocols = [protocols.sequenceOf(IRecipe)]
    )

    def __init__(self,ob,proto):
        self.subject = ob
        self.__doc__ = getattr(ob,'__doc__',None)

    def __repr__(self):
        return repr(self.subject)

    def __call__(self, component, instDict, attrName):
        return tuple([ob(component,instDict,attrName) for ob in self.subject])


class _TypeAsRecipe:

    """ADAPTER: type | class --> IRecipe"""

    protocols.advise(
        instancesProvide = [IRecipe],
        asAdapterForTypes = [type, ClassType]
    )

    def __init__(self,ob,proto):
        self.subject = ob
        self.__doc__ = None   # Don't use the type's docstring as our docstring

    def __call__(self, component, instDict, attrName):
        return self.subject()

    def __repr__(self):
        return "%s.%s" % (self.subject.__module__, self.subject.__name__)



def _callableAsRecipe(func, protocol):
    args, func = func.getPositionalArgs(), func.getCallable()
    if len(args)==3:
        return func
    elif len(args)==1:
        f = lambda s,d,a: func(s)
    elif not args:
        f = lambda s,d,a: func()
    f.__doc__ = getattr(func,'__doc__',None)
    return f

protocols.declareAdapter(
    _callableAsRecipe, provides = [IRecipe], forProtocols = [ISignature]
)

class _StringAsRecipe(_TypeAsRecipe):

    """ADAPTER: string (import spec) --> IRecipe"""

    protocols.advise(
        instancesProvide = [IRecipe],
        asAdapterForTypes = [str]
    )

    def __call__(self, component, instDict, attrName):
        return adapt(importString(self.subject), IRecipe)(
            component, instDict, attrName
        )

    def __repr__(self):
        return self.subject

def _configKeyAsRecipe(ob,proto):
    from peak.api import config; from components import lookupComponent
    return lambda self,d,a: \
        lookupComponent(self,config.FactoryFor(ob),adaptTo=IRecipe)(self,d,a)

protocols.declareAdapter(
    _configKeyAsRecipe, provides=[IRecipe], forProtocols = [IConfigKey]
)

class Make(Attribute):

    """'Make(recipe)' - Construct a value and cache it

    Usage examples::

        class MyComponent(binding.Component):

            # this makes a new dictionary in each MyComponent instance
            aDict = binding.Make(dict)

            # this makes an instance of 'thing.Thing' in each MyComponent
            aThing = binding.Make("things.Thing")

            # 1-argument functions are called with the MyComponent instance
            someAttr = binding.Make(lamdba self: self.otherAttr * 2)

            # Types and no-argument functions are just called
            otherAttr = binding.Make(lambda: 42)

    'Make' accepts a 'binding.IRecipe' (or object that's adaptable to one), and
    uses it to compute the attribute's value.  See the docs for 'Descriptor'
    and 'Attribute' for the remaining semantics of this attribute type.

    XXX need more docs for adaptations to 'IRecipe'
    """

    def __init__(self, recipe, **kw):
        kw.setdefault('attrName',
            getattr(recipe, '__name__', None)
        )
        recipe = self.computeValue = adapt(recipe, IRecipe)
        kw.setdefault('doc',
            getattr(recipe,'__doc__',None)
        )
        super(Make,self).__init__(**kw)





    def __repr__(self):
        if self.__doc__:
            return "binding.Make(%r):\n\n%s" % (self.computeValue,self.__doc__)
        else:
            return "binding.Make(%r)" % self.computeValue

Once = New = Make   # XXX DEPRECATED, backward compatibility


































class classAttr(object):

    """Class attribute binding

    This wrapper lets you create bindings which apply to a class, rather than
    to its instances.  This can be useful for creating bindings in a base
    class that will summarize metadata about subclasses.  Usage example::

        class SomeClass(binding.Component):

            CLASS_NAME = binding.classAttr(
                binding.Make(
                    lambda self: self.__name__.upper()
                )
            )

        class aSubclass(SomeClass):
            pass

        assert SomeClass.CLASS_NAME == "SOMECLASS"
        assert aSubclass.CLASS_NAME == "ASUBCLASS"

    Class attributes will only work in subclasses of classes like
    'binding.Component', whose metaclass derives from 'binding.Activator'.

    Implementation note: class attributes actually cause a new metaclass to
    be created on-the-fly to contain them.  The generated metaclass is named
    for the class that contained the class attributes, and has the same
    '__module__' attribute value.  So continuing the above example::

        assert SomeClass.__class__.__name__ == 'SomeClassClass'
        assert aSubClass.__class__.__name__ == 'SomeClassClass'

    Notice that the generated metaclass is reused for subsequent
    subclasses, as long as they don't define any new class attributes."""

    __slots__ = 'binding'

    def __init__(self, binding): self.binding = binding


class Activator(type):

    """Descriptor metadata management"""

    __name__ = 'Activator'    # trick to make instances' __name__ writable


    def __new__(meta, name, bases, cdict):

        classAttrs = [
            (k,v.binding) for (k, v) in cdict.items()
                if adapt(v,classAttr,not v) is v
        ]

        if classAttrs:

            cdict = cdict.copy(); d = {}
            d = dict(classAttrs)
            map(cdict.__delitem__, d.keys())

            d['__module__'] = cdict.get('__module__')

            meta = Activator( name+'Class', (meta,), d )

            # The new metaclass' __new__ will finish up for us...
            return meta(name,bases,cdict)

        klass = supertype(Activator,meta).__new__(meta, name, bases, cdict)
        klass.__name__ = name

        cd = klass.__class_descriptors__ = {}

        for k,v in cdict.items():
            v = adapt(v, IActiveDescriptor, None)
            if v is not None:
                cd[k]=v.activateInClass(klass,k)

        return klass



    def __all_descriptors__(klass):
        ad = {}
        map(ad.update, getInheritedRegistries(klass, '__all_descriptors__'))
        ad.update(klass.__class_descriptors__)
        return ad

    __all_descriptors__ = Make(__all_descriptors__, suggestParent=False)


































class ActiveClass(Activator):

    """Metaclass for classes that are themselves components"""

    protocols.advise(
        instancesProvide = [IActiveDescriptor]
    )

    def activateInClass(self,klass,attrName):

        if klass.__module__ == self.__module__:

            if '__parent__' not in self.__dict__ and attrName!='__metaclass__':
                # We use a tuple, so that if our parent is a descriptor,
                # it won't interfere when our instance tries to set *its*
                # parent!
                self.__parent__ = klass,

        return self


    def getParentComponent(self):
        return self.__parent__[0]

    getParentComponent = metamethod(getParentComponent)


    def getComponentName(self):
        return self.__cname__

    getComponentName = metamethod(getComponentName)


    def _getConfigData(self, forObj, configKey):
        return NOT_FOUND

    _getConfigData = metamethod(_getConfigData)




    def __parent__(self,d,a):

        parent = self.__module__
        name = self.__name__

        if '.' in name:
            name = '.'.join(name.split('.')[:-1])
            parent = '%s:%s' % (parent,name)

        return importString(parent),

    __parent__ = Make(__parent__, suggestParent=False)


    def __cname__(self,d,a):
        return self.__name__.split('.')[-1]

    __cname__ = Make(__cname__, suggestParent=False)























_ignoreNames = {'__name__':1, '__new__':1, '__module__':1, '__return__':1}

class SingletonClass(Activator):

    def __new__(meta, name, bases, cdict):
        for k in cdict.keys():
            if k not in _ignoreNames:
                cdict[k] = classAttr(cdict[k])

        return supertype(SingletonClass,meta).__new__(meta,name,bases,cdict)


class Singleton(object):

    """Class whose instances are itself, with all attributes at class level

    Subclass 'binding.Singleton' to create true (per-interpreter) singleton
    objects.  Any attribute bindings defined will apply to the class itself,
    rather than to its instances.  Any attempt to create an instance of a
    singleton class will simply return the class itself.  The 'self' of all
    methods will also be the class.

    This actually works by redefining all the singleton class' attributes
    as 'binding.classAttr()' objects, causing them to be placed in a new
    metaclass created specifically for the singleton class.  So, if you would
    otherwise find yourself using 'classmethod' or 'binding.classAttr()' on
    all the contents of a class, just subclass 'binding.Singleton' instead.

    Note that if you define special methods like '__new__()' or '__init__()',
    these will also be promoted to the metaclass.  This means, for example,
    that if you define an '__init__' method, it will be called with the
    singleton class object (or a subclass) when the class is created."""

    __metaclass__ = SingletonClass

    def __new__(klass):
        return klass

del _ignoreNames['__new__']     # we want this to be promoted, for subclasses


