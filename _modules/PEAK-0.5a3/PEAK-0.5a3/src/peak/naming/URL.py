"""URL parsing and formatting tools"""

from types import StringTypes
from urllib import unquote

from peak.api import exceptions, NOT_GIVEN, adapt, protocols
from peak.binding.once import classAttr, Make
from peak.binding.components import Obtain
from peak.model.elements import Struct
from peak.model.features import structField
from peak.model.datatypes import String, Integer
from peak.model.interfaces import IType
from interfaces import *
from arithmetic import *
from names import CompoundName, URLMatch

__all__ = [
    'Base', 'Field', 'RequiredField', 'IntField', 'NameField', 'Collection',
    'ParseError', 'MissingData', 'Rule', 'Sequence', 'Repeat', 'Optional',
    'Tuple', 'Named', 'ExtractString', 'Conversion', 'Alternatives',
    'Set', 'MatchString', 'parse', 'format', 'ExtractQuoted', 'StringConstant'
]

from peak.util.fmtparse import *

















class ExtractQuoted(Rule):

    """Return matched subrule as a string, possibly handling quote/unquote"""

    __slots__ = 'rule', 'unquote', 'terminators'

    def __init__(self, rule=MatchString(), unquote=True, terminators=''):
        self.rule = adapt(rule,IRule)
        self.unquote = unquote
        self.terminators = terminators

    def parse(self, inputStr, produce, startAt):
        out = []
        pos = inputStr.parse(self.rule, out.append, startAt)
        if isinstance(pos,ParseError):
            return pos

        if self.unquote:
            produce(unquote(inputStr[startAt:pos]))
        else:
            produce(inputStr[startAt:pos])
        return pos


    def withTerminators(self,terminators,memo):
        return self.__class__(
            self.rule.withTerminators(terminators,memo), self.unquote, terminators
        )

    def getOpening(self,closing,memo):
        return self.rule.getOpening(closing,memo)

    def format(self,data,write):
        if self.unquote:
            for t in self.terminators:
                data = data.replace(t, '%'+hex(256+ord(t))[-2:].upper())
        write(data)




class Field(structField):

    referencedType = String
    defaultValue = None
    unquote = True

    def _syntax(feature):

        syntax = feature.syntax

        if syntax is None:
            syntax = getattr(feature.typeObject, 'mdl_syntax', None)

        if syntax is None:
            syntax = Conversion(
                ExtractQuoted(unquote = feature.unquote),
                converter = feature.fromString,
                formatter = feature.toString,
                defaultValue = feature._defaultValue,
                canBeEmpty = feature.canBeEmpty
            )

        if feature.isMany:
            syntax = Repeat(
                syntax,
                minCt = feature.lowerBound,
                maxCt = feature.upperBound,
                separator = feature.separator,
                sepMayTerm = feature.sepMayTerm
            )

        return Named( feature.attrName, syntax )

    _syntax = classAttr(Make(_syntax))







class Collection(Field):
    upperBound = None
    separator  = ''


class RequiredField(Field):
    lowerBound = 1
    defaultValue = NOT_GIVEN


class IntField(Field):
    referencedType = Integer


class NameField(RequiredField):
    unquote = False

























class Base(Struct):

    """Basic scheme/body URL"""

    protocols.advise(
        instancesProvide=[IAddress],
        classProvides=[IAddressFactory]
    )

    nameKind         = URL_KIND
    nameAttr         = None
    supportedSchemes = ()

    def supportsScheme(klass, scheme):
        return scheme in klass.supportedSchemes or not klass.supportedSchemes

    supportsScheme = classmethod(supportsScheme)


    def __init__(self, scheme=None, body='', **__kw):

        scheme = scheme or self.__class__.defaultScheme

        if body:
            data = self.parse(scheme,str(body))
            data.update(__kw)
            __kw = data

        __kw['scheme']=scheme
        __kw['body']=body

        for f in self.__class__.mdl_features:
            if f.isRequired and not f.attrName in __kw:
                raise exceptions.InvalidName(
                    "Missing %s field in %r" % (f.attrName, __kw)
                )

        super(Base,self).__init__(**__kw)
        self.__class__.body._setup(self, self.getCanonicalBody())


    class scheme(RequiredField):

        _defaultValue = classAttr(Obtain('defaultScheme'))

        def _onLink(feature,element,item,posn):
            # delegate scheme validation to element class
            if not element.supportsScheme(item):
                raise exceptions.InvalidName(
                    "Unsupported scheme %r for %r" % (item, element.__class__)
                )


    class body(NameField):
        defaultValue = ''
        unquote = False
        canBeEmpty = True

    syntax = body._syntax   # default syntax is just to parse the body


    def mdl_fromString(klass, aName):
        m = URLMatch(aName)
        if m:
            return klass( m.group(1), aName[m.end():] )
        else:
            return klass( None, aName)


    def __str__(self):
        return "%s:%s" % (self.scheme, self.body)

    # "inherit" findComponent() method from names
    findComponent = CompoundName.findComponent.im_func








    __add__  = name_add
    __sub__  = name_sub
    __radd__ = name_radd
    __rsub__ = name_rsub


    def addName(self,other):

        if not other:
            return self

        name = adapt(other,IName,None)

        if name is None:
            raise TypeError(
                "Only names can be added to URLs", self, other
            )

        other = name
        if other.nameKind==URL_KIND:
            return other

        na = self.nameAttr

        if not na:
            raise TypeError(
                "Addition not supported for pure address types", self, other
            )

        d = dict(self._hashAndCompare)
        d['body'] = None    # before the below in case 'na' is "body"
        d[na] = getattr(self,na,CompoundName(())) + other

        res = self.__class__(**d)
        return res






    def __split(self):

        d = dict(self._hashAndCompare)
        na = self.nameAttr

        if na:
            if na in d:
                nic = d[na]; del d[na]
            else:
                nic = getattr(self,na)
        else:
            nic = CompoundName(())

        d['body'] = ''
        auth = self.__class__(**d)
        return auth, nic

    __split = Make(__split)

    def getAuthorityAndName(self):
        return self.__split


    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__,
            ','.join(
                ['%s=%r' % (k,v) for (k,v) in self._hashAndCompare]
            )
        )

    def _hashAndCompare(self):
        klass = self.__class__
        omitBody = len(klass.mdl_featureNames)!=2   # ('scheme','body')
        return tuple(
            [(f,getattr(self,f)) for f in self.__class__.mdl_featureNames
                if (not omitBody or f!='body')
            ]
        )

    _hashAndCompare = Make(_hashAndCompare)

    def parse(klass,scheme,body):
        if klass.syntax is not None:
            return parse(body, klass.syntax)

        return {}

    parse = classmethod(parse)

    def getCanonicalBody(self):
        if self.__class__.syntax is not None:
            return format(dict(self._hashAndCompare),self.__class__.syntax)
        return self.body

    defaultScheme = classAttr(
        Make(
            lambda self: self.supportedSchemes and self.supportedSchemes[0]
                or None
        )
    )


    def getURLContext(klass,parent,scheme,iface,componentName=None,**options):
        if klass.supportsScheme(scheme):
            from contexts import AddressContext
            return AddressContext(
                parent, componentName, schemeParser=klass, **options
            )

    getURLContext = classmethod(getURLContext)


    def __adapt__(klass, ob):
        """Allow address classes to be used as protocols"""
        if isinstance(ob,str):
            return klass.mdl_fromString(ob)

    __adapt__ = classAttr(protocols.metamethod(__adapt__))




