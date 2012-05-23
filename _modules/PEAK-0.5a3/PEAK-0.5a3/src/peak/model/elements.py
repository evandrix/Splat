"""Basic implementation of a domain metamodel (minus enumerations)

    This module implements base classes for "Elements" and "Features"
    in the sense of the "Service-Element-Feature" pattern.  By subclassing
    from them, you get a wide variety of services automatically provided,
    ranging from automatic generation of getter/setter/mutator methods,
    metadata such as ordered lists of features provided by a class,
    well-defined hookpoints for "event" trapping, persistence support,
    and more.
"""

from peak.api import *
from interfaces import *
from peak.util.hashcmp import HashAndCompare
from types import FunctionType

from peak.persistence import Persistent
from peak.storage.lazy_loader import LazyLoader
from peak.binding.components import _Base
from peak.util import fmtparse

__all__ = [
    'Type', 'PrimitiveType', 'Immutable', 'Struct', 'Element',
]

















class Namespace(_Base):

    """Abstract base class for packages and types -- DEPRECATED

    This class currently exists only to mix in an '_XMIMap' registry.  It
    may not exist for long; don't use it directly or rely on its presence."""

    def _XMIMap(self):

        xm = {}

        for m in binding.getInheritedRegistries(self,'_XMIMap'):
            xm.update(m)

        for k,v in self.__class_descriptors__.iteritems():

            for n in getattr(v,'_XMINames',()):

                xm[n] = k

                while '.' in n:
                    n = n.split('.',1)[1]
                    xm[n]=k

        return xm

    _XMIMap = binding.classAttr(binding.Make(_XMIMap))














class TypeClass(Namespace.__class__):

    """Basis for all flavors"""

    def __new__(meta, name, bases, cdict):
        for k,v in cdict.items():
            if k.startswith('mdl_') and isinstance(v,FunctionType):
                cdict[k]=classmethod(v)
        return super(TypeClass,meta).__new__(meta,name,bases,cdict)

    def mdl_featuresDefined(self,instDict,attrName):

        """Sorted tuple of feature objects defined/overridden by this class"""

        mine = [adapt(v,IFeature,None) for (k,v) in instDict.items()]
        mine = filter(None,mine)
        mine.sort()
        return tuple(mine)

    mdl_featuresDefined = binding.Make(mdl_featuresDefined)


    def mdl_featureNames(self):
        """Names of all features, in monotonic order (see 'mdl_features')"""
        return tuple([f.attrName for f in self.mdl_features])

    mdl_featureNames = binding.Make(mdl_featureNames)


    mdl_isAbstract = binding.Make(
        lambda: False, doc =
        """Is this an abstract class?  Defaults to 'False'.

            To make a 'model.Type' subclass abstract, set this
            to 'True' in the class definition.  Note that you don't
            ever need to set this to 'False', since it will default
            to that value in every new subclass, even the subclasses of
            abstract classes.
        """
    )

    def mdl_features(self):
        """All feature objects of this type, in monotonic order

        The monotonic order of features is equivalent to the concatenation of
        'mdl_featuresDefined' for all classes in the type's MRO, in
        reverse MRO order, with duplicates (i.e. overridden features)
        eliminated.  That is, if a feature named 'x' exists in more than one
        class in the MRO, the most specific definition of 'x' will be used
        (i.e. the first definition in MRO order), but it will be placed in the
        *position* reserved by the *less specific* definition.  The idea is
        that, once a position has been defined for a feature name, it will
        continue to be used by all subclasses, if possible.  For example::

            class A(model.Type):
                class foo(model.Attribute): pass

            class B(A):
                class foo(model.Attribute): pass
                class bar(model.Attribute): pass

        would result in 'B' having a 'mdl_features' order of '(foo,bar)',
        even though its 'mdl_featuresDefined' would be '(bar,foo)' (because
        features without a sort priority define are ordered by name).

        The purpose of using a monotonic ordering like this is that it allows
        subtypes to use a serialized format that is a linear extension of
        their supertype, at least in the case of single inheritance.  It may
        also be useful for GUI layouts, where it's also desirable to have a
        subtype's display look "the same" as a base type's display, except for
        those features that it adds to the supertype."""

        out  = []
        posn = {}
        add  = out.append
        get  = posn.get

        all  = list(
            binding.getInheritedRegistries(self,'mdl_features')
        )
        all.append(self.mdl_featuresDefined)

        for nf in all:
            for f in nf:
                n = f.attrName
                p = get(n)
                if p is None:
                    posn[n] = len(out)
                    add(f)
                else:
                    out[p] = f

        return tuple(out)

    mdl_features = binding.Make(mdl_features)


    def mdl_sortedFeatures(self):

        """All feature objects of this type, in sorted order"""

        fl = list(self.mdl_features)
        fl.sort()
        return tuple(fl)

    mdl_sortedFeatures = binding.Make(mdl_sortedFeatures)


    mdl_compositeFeatures = binding.Make(
        lambda self: tuple([f for f in self.mdl_features if f.isComposite]),
        doc="""Ordered subset of 'mdl_features' that are composite"""
    )

    mdl_subclassNames = binding.Make(
        lambda: (), doc =
        """Sequence of component keys to find an abstact class' subclasses"""
    )

    def findComponent(self,component,default=NOT_GIVEN):
        return self



protocols.declareAdapter(
    lambda o,p: o.mdl_asSyntax(),
    provides=[fmtparse.IRule], forTypes=[TypeClass]
)


class Type(Namespace):

    __metaclass__ = TypeClass

    protocols.advise( classProvides = [ITypeInfo] )

    mdl_defaultValue = NOT_GIVEN
    mdl_isAbstract   = True   # 'model.Type' itself is abstract
    mdl_syntax       = None   # Syntax rule for parsing/formatting

    def __new__(klass,*__args,**__kw):

        """Don't allow instantiation if this is an abstract class"""

        if klass.mdl_isAbstract:
            raise TypeError, "Can't instantiate an abstract class!"
        return super(Type,klass).__new__(klass,*__args,**__kw)


    def mdl_fromFields(klass,fieldSeq):
        """Return a new instance from a sequence of fields"""
        return klass(**dict(zip(klass.mdl_featureNames,fieldSeq)))


    def mdl_fromString(klass, value):
        if klass.mdl_syntax is not None:
            return klass(**fmtparse.parse(value, klass.mdl_syntax))
        raise NotImplementedError


    def mdl_normalize(klass, value):
        return value



    def __init__(self,parentComponent=NOT_GIVEN,componentName=None,**__kw):

        klass = self.__class__

        for k,v in __kw.items():

            try:
                f = getattr(klass,k)
                s = f._setup    # XXX we should only check this for immutables

            except AttributeError:
                raise TypeError(
                    "%s constructor has no keyword argument %s" %
                    (klass, k)
                )

        for f in klass.mdl_features:
            if f.attrName in __kw:
                f._setup(self,__kw[f.attrName])

        if parentComponent is not NOT_GIVEN or componentName is not None:
            self.setParentComponent(parentComponent,componentName)


    def setParentComponent(self, parentComponent, componentName=None):
        if parentComponent is not None or componentName is not None:
            raise TypeError("Data values are not components")

    def getParentComponent(self):
        return None

    def getComponentName(self):
        return None








    def mdl_toString(klass, value):
        return str(value)

    def mdl_asSyntax(klass):
        if klass.mdl_isAbstract and klass.mdl_subclassNames:
            return fmtparse.Alternatives(
                *tuple(
                    [binding.lookupComponent(klass,n)
                        for n in klass.mdl_subclassNames
                    ]
                )
            )
        elif klass.mdl_syntax is not None:
            return fmtparse.Conversion(
                fmtparse.Tuple(klass.mdl_syntax),
                converter=lambda x: klass(**dict(x)),
                formatter=klass.mdl_toString,
            )

    def __str__(self):
        if self.__class__.mdl_syntax is not None:
            return fmtparse.format(
                self._mdl_toDict(), self.__class__.mdl_syntax
            )
        else:
            return super(Type,self).__str__()


    def _mdl_toDict(self):
        d = {}
        for f in self.__class__.mdl_featureNames:
            try:
                d[f] = getattr(self,f)
            except AttributeError:
                continue
        return d





class ImmutableClass(TypeClass):

    def __init__(klass,name,bases,dict):

        for f in klass.mdl_features:

            if f.isChangeable:
                raise TypeError(
                    "Immutable class with changeable feature",
                    klass, f
                )

            if f.referencedEnd:
                raise TypeError(
                    "Immutable class with bidirectional association",
                    klass, f
                )

        super(ImmutableClass,klass).__init__(name,bases,dict)






















class Immutable(Type, HashAndCompare):

    __metaclass__  = ImmutableClass

    mdl_isAbstract = True   # Immutable itself is abstract

    def _hashAndCompare(self):
        return tuple([
            getattr(self,n,None) for n in self.__class__.mdl_featureNames
        ])

    _hashAndCompare = binding.Make(_hashAndCompare)


    def __setattr__(self,attr,value):
        raise TypeError("Immutable object", self)

    def __delattr__(self,attr,value):
        raise TypeError("Immutable object", self)


    def __repr__(self):

        klass = self.__class__

        return "%s(%s)" % (klass.__name__,
            ','.join(
                ['%s=%r' % (f.attrName,f.get(self))
                    for f in klass.mdl_features
                        if f.includeInRepr and hasattr(self,f.attrName)
                ]
            )
        )








class PrimitiveTypeClass(TypeClass):

    def __init__(klass,name,bases,cDict):

        super(PrimitiveTypeClass,klass).__init__(name,bases,cDict)

        if klass.mdl_features:
            raise TypeError(
                "Primitive types can't have features", klass
            )

    # Primitive types are not instantiable; they stand in for
    # a type that isn't derived from model.Type

    mdl_isAbstract = binding.Make(lambda: True)


class PrimitiveType(Type):

    """A primitive type (e.g. Boolean, String, etc.)"""

    __metaclass__ = PrimitiveTypeClass

    def mdl_fromFields(klass,fieldSeq):
        # primitive types don't have fields...
        raise NotImplementedError

    def mdl_asSyntax(klass):
        if klass.mdl_syntax is not None:
            return fmtparse.Conversion(
                klass.mdl_syntax,
                converter=klass.mdl_fromString,
                formatter=klass.mdl_toString,
            )
        return Type.mdl_asSyntax.im_func(klass)






class Struct(Immutable):

    """An immutable data structure type"""

    protocols.advise(classProvides=[ITypeInfo, IStructType])

    def mdl_typeCode(klass):

        """TypeCode for Struct classes is a 'tk_struct' w/appropriate fields"""

        from peak.model.datatypes import TCKind, TypeCode

        return TypeCode(
            kind = TCKind.tk_struct,
            member_names = klass.mdl_featureNames,
            member_types = [
                f.typeObject.mdl_typeCode for f in klass.mdl_features
            ]

        )

    mdl_typeCode = binding.classAttr( binding.Make(mdl_typeCode) )



















class ElementClass(TypeClass, Persistent.__class__):
    pass


class Element(Type, Persistent):

    """A persistent domain element"""

    __metaclass__  = ElementClass

    def setParentComponent(self, parentComponent, componentName=None,
        suggest=False):

        if suggest:
            return  # don't accept suggestions

        if parentComponent is not None:
            self._p_jar = parentComponent

        self._p_oid = componentName


    def getParentComponent(self):
        return self._p_jar

    def getComponentName(self):
        return self._p_oid














    def _getBindingFuncs(klass, attr, useSlot=False):

        oldGet, oldSet, oldDel = super(Element,klass)._getBindingFuncs(
            attr,useSlot
        )

        def _doGet(ob):
            value = oldGet(ob)
            if isinstance(value,LazyLoader):
                oldDel(ob)
                value.load(ob,attr)
                return oldGet(ob)
            return value

        def _doSet(ob,value):
            try:
                old = _doGet(ob)
            except AttributeError:
                ob._p_changed = True
            else:
                if old is not value or not isinstance(value,Persistent):
                    ob._p_changed = True
            oldSet(ob,value)

        def _doDel(ob):
            try:
                old = _doGet(ob)
            except AttributeError:
                pass
            else:
                ob._p_changed = True
                oldDel(ob)

        return _doGet, _doSet, _doDel


    _getBindingFuncs = classmethod(_getBindingFuncs)




    def _bindingChanging(self, attr, value=NOT_FOUND, isSlot=False):

        old = self._getBinding(attr,NOT_FOUND,isSlot)

        if old is not value or not isinstance(value,Persistent):
            self._p_changed = True


    def _postGet(self,attr,value,isSlot=False):

        if isinstance(value,LazyLoader):
            if isSlot:
                getattr(self.__class__,attr).__delete__(self)
            else:
                del self.__dict__[attr]

            value.load(self,attr)   # XXX
            return self._getBinding(attr,NOT_FOUND)

        return value





















