from elements import PrimitiveType, Immutable, Type
from features import structField
from enumerations import Enumeration, enum
from peak.api import binding

__all__ = [
    'TCKind', 'TypeCode', 'Short', 'Long', 'UShort', 'ULong', 'Float', 'Double',
    'Integer','UnlimitedInteger','Boolean','String','Name', 'WString', 'Char',
    'WChar', 'LongLong', 'ULongLong', 'LongDouble', 'PrimitiveTC', 'SimpleTC',
    'Fixed','basicTypes', 'Any', 'Repr'
]

class PrimitiveTC(Enumeration):

    """Primitive CORBA typecode kinds"""

    tk_short = enum()
    tk_long  = enum()
    tk_ushort = enum()
    tk_ulong = enum()
    tk_float = enum()
    tk_double = enum()
    tk_boolean = enum()
    tk_char = enum()
    tk_wchar = enum()
    tk_octet = enum()

    tk_longlong = enum()
    tk_ulonglong = enum()
    tk_longdouble = enum()

class SimpleTC(PrimitiveTC):

    """Simple (i.e. atomic/unparameterized) CORBA typecode kinds"""

    tk_any   = enum()
    tk_TypeCode = enum()
    tk_Principal = enum()
    tk_null = enum()
    tk_void = enum()

class TCKind(SimpleTC):

    """The full set of CORBA TypeCode kinds"""

    tk_alias = enum()       # content_type

    tk_struct = enum()      # member names + types

    tk_sequence = enum()    # length + content_type
    tk_array = enum()

    tk_objref = enum()

    tk_enum = enum()        # member names
    tk_union = enum()       # member names + types + discriminator
    tk_except = enum()      # member names + types

    tk_string = enum()      # length
    tk_wstring = enum()

    tk_fixed = enum()       # digits + scale



    # J2SE also defines these...  presumably they come from a newer CORBA
    # spec than XMI 1.0 uses?  Or maybe they just aren't useful for XMI?
    #
    # tk_abstract_interface
    # tk_native
    # tk_value
    # tk_value_box










class Any(PrimitiveType):
    pass

class Integer(PrimitiveType):
    mdl_fromString = int

class Short(Integer):
    pass

class Long(Integer):
    mdl_fromString = long

class UShort(Integer):
    pass

class ULong(Long):
    pass

class Float(PrimitiveType):
    mdl_fromString = float

class Double(Float):
    pass


class String(PrimitiveType):

    length = 0

    def mdl_fromString(klass,value):
        return value

    mdl_typeKind = TCKind.tk_string

    def mdl_typeCode(klass):
        return TypeCode(kind = klass.mdl_typeKind, length=klass.length)

    mdl_typeCode = binding.classAttr( binding.Make(mdl_typeCode) )



class WString(String):
    mdl_typeKind = TCKind.tk_wstring

class Char(String):
    mdl_typeKind = TCKind.tk_char
    length = 1

class WChar(WString):
    mdl_typeKind = TCKind.tk_wchar
    length = 1


class LongLong(Integer):
    pass

class ULongLong(Integer):
    pass

class LongDouble(Float):
    pass

class Boolean(Enumeration):
    true = enum(True)
    false = enum(False)


class Fixed(Float):

    fixed_digits = 1
    fixed_scale  = 0

    def mdl_typeCode(klass):
        return TypeCode(kind = TCKind.Fixed,
            fixed_digits = klass.fixed_digits,
            fixed_scale  = klass.fixed_scale
        )

    mdl_typeCode = binding.classAttr( binding.Make(mdl_typeCode) )



class UnlimitedInteger(Integer):

    UNBOUNDED = -1

    def mdl_fromString(klass, value):
        if value=='*': return klass.UNBOUNDED
        return int(value)


class Repr(String):

    def mdl_fromString(klass,value):
        return eval(value)  # XXX should really use tokenize, for safety

    def mdl_toString(klass,value):
        return `value`


class Name(String):
    pass


class _tcField(structField):

    """TypeCode field that only allows itself to be set when relevant"""

    allowedKinds = ()

    sortPosn = 1    # all fields must sort *after* 'kind'

    def _onLink(feature,element,item,posn):
        if element.kind not in feature.allowedKinds:
            raise TypeError(
                "%s may not be set for TypeCode of kind %r" %
                (feature.attrName, element.kind)
            )





class TypeCode(Immutable):

    # XXX name, id ???

    class kind(structField):
        referencedType = TCKind
        sortPosn = 0
        allowedKinds = TCKind

    class length(_tcField):     # xmi.tcLength

        allowedKinds = (
            TCKind.tk_array, TCKind.tk_sequence, TCKind.tk_string,
            TCKind.tk_wstring,
        )

        referencedType = Integer


    class content_type(_tcField):
        allowedKinds = (
            TCKind.tk_array, TCKind.tk_sequence, TCKind.tk_alias,
        )
        referencedType = 'TypeCode'


    class member_names(_tcField):   # XMI.CorbaTcEnumLabel/XMI.CorbaTcField
        allowedKinds = (
            TCKind.tk_enum, TCKind.tk_struct, TCKind.tk_except, TCKind.tk_union
        )
        upperBound = None   # sequence
        referencedType = Name


    class member_types(_tcField):   # XMI.CorbaTcField
        allowedKinds = (
            TCKind.tk_struct, TCKind.tk_except, TCKind.tk_union
        )
        upperBound = None   # sequence
        referencedType = 'TypeCode'

    class discriminator_type(_tcField):
        allowedKinds = TCKind.tk_union,
        referencedType = 'TypeCode'

    class member_labels(_tcField):
        allowedKinds = TCKind.tk_union,
        referencedType = 'Any'

    class fixed_digits(_tcField):   # xmi.tcDigits
        allowedKinds = TCKind.tk_fixed,
        referencedType = Integer

    class fixed_scale(fixed_digits):    # xmi.tcScale
        pass


    def __repr__(self):

        kind = self.kind
        info = [
            '%s=%r' % (f.attrName,f.get(self))
            for f in self.__class__.mdl_features
                if kind in f.allowedKinds and hasattr(self,f.attrName)
        ]

        return 'TypeCode(%s)' % (', '.join(info))


    def unaliased(self):
        if self.kind == TCKind.tk_alias:
            return self.content_type.unaliased()
        return self









basicTypes = {

    TCKind.tk_short: Short,
    TCKind.tk_long : Long,
    TCKind.tk_ushort: UShort,
    TCKind.tk_ulong: ULong,
    TCKind.tk_float: Float,
    TCKind.tk_double: Double,

    TCKind.tk_boolean: Boolean,
    TCKind.tk_char: Char,
    TCKind.tk_wchar: WChar,

    # TCKind.tk_octet: Octet,

    TCKind.tk_longlong: LongLong,
    TCKind.tk_ulonglong: ULongLong,
    TCKind.tk_longdouble: LongDouble,

    TCKind.tk_any: Any,
    TCKind.tk_TypeCode: TypeCode,

    # TCKind.tk_Principal: Principal,
    # TCKind.tk_null: Null,
    # TCKind.tk_void: Void,

    TCKind.tk_objref: Type,

    TCKind.tk_string: String,
    TCKind.tk_wstring: WString,

    TCKind.tk_fixed: Fixed,
}








# Bootstrap basic types

for kind, klass in basicTypes.items():

    if kind in TypeCode.length.allowedKinds:
        klass.mdl_typeCode = TypeCode(kind=kind,length=klass.length)

    elif kind in TypeCode.fixed_digits.allowedKinds:
        klass.mdl_typeCode = TypeCode(
            kind = kind,
            fixed_digits = klass.fixed_digits,
            fixed_scale  = klass.fixed_scale,
        )

    else:
        klass.mdl_typeCode = TypeCode(kind=kind)

Integer.mdl_typeCode       = TypeCode(kind=TCKind.tk_long)
PrimitiveType.mdl_typeCode = TypeCode(kind=TCKind.tk_any)






















