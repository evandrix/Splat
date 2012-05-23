"""Enumeration support"""

from peak.api import *

from interfaces import *
from elements import PrimitiveTypeClass, PrimitiveType
from peak.util.hashcmp import HashAndCompare

__all__ = [
    'enum', 'enumDict', 'enums', 'Enumeration', 'ExtendedEnum'
]






























class enum(object):

    """Define an enumeration literal

    Place 'enum' instances in an Enumeration class to define the values
    of the enumeration's instances.  Example::

        class RGB(model.Enumeration):
            red = model.enum("R")
            green = model.enum("G")
            blue = model.enum("B")

    In the example above, 'RGB.red' will become an enumeration instance
    whose value hashes and compares the same as the string '"R"'.

    You may use any object as an enumeration literal, but typically you
    will use an integer, string, boolean, or similar primitive type.
    Note that you can also omit the value when creating a literal, in
    which case the value will be the same string as the name of the literal,
    e.g.::

        class FooBar(model.Enumeration)
            foo = model.enum()
            bar = model.enum()

    In the example above, 'FooBar.foo' will be an enumeration instance whose
    value hashes and compares the same as the string '"foo"'.

    Note, by the way, that a 'model.enum()' literal is *not* the same object
    as the enumeration instance whose value it defines!  'model.enum(1)'
    does not hash or compare the same as '1', and it is not an instance of
    'model.Enumeration' or any subclass thereof.  'model.enum()' is only
    used to define literals in the body of an enumeration class."""

    __slots__ = 'value'

    def __init__(self,*value):
        if len(value)>1:
            raise TypeError("enum() takes at most one argument",value)
        self.value = value

    def __call__(self,name):
        """Return dict of enumeration literals in context of 'name'

        This method is used by Enumeration classes to set up their instances;
        you do not need to call this yourself."""

        if self.value:
            return {name:self.value[0]}
        else:
            return {name:name}































class enumDict(enum):

    """Define a dictionary of enumeration literals

    This is used in place of 'model.enum()' to specify an assortment of
    enumeration literals from a sequence of '(name,value)' pairs or
    a dictionary.  It's useful in circumstances where a literal's
    name is a Python keyword or an illegal value for an identifier, e.g.::

        from keyword import kwlist

        class PythonKeyword(model.Enumeration):

            __whatever = model.enumDict(
                [(k,k) for k in kwlist]
            )

    The above defines an enumeration type, 'PythonKeyword', such that
    'PythonKeyword.class' is an enumeration instance that hashes and
    compares equal to the string '"class"', and so on for all Python
    keywords.  (As an extra benefit, the expression 'aString in PythonKeyword'
    will evaluate true if 'aString' is a python keyword.)

    Note that it doesn't matter what name you give the 'enumDict()' in the
    enumeration class definition; the name will not be used to name an
    enumeration instance.  It is suggested, however, that you use a "private"
    attribute name (as in the example above) to avoid namespace pollution."""

    __slots__ = ()

    def __init__(self, fromDict):
        self.value = dict(fromDict)

    def __call__(self,name):
        """Return dict of enumeration literals in context of 'name'

        This method is used by Enumeration classes to set up their instances;
        you do not need to call this yourself."""
        return self.value


def enums(*values):

    """A sequence of enumeration literals

    This function is a shortcut for creating a series of 'model.enum()'
    instances.  Examples::

        class RGB(model.Enumeration):
            red, green, blue = model.enums("R","G","B")

        class Binary(model.Enumeration):
            zero, one = model.enums(range(2))

        class FooBar(model.Enumeration):
            foo, bar = model.enums(2)

    'model.enums()' accepts a series of arguments, and creates a 'model.enum()'
    for each one, returning the list ('RGB' example).  If only one argument is
    supplied, and it's iterable, it is used as the input list.  Finally, if
    only one argument is supplied, and it's not iterable, it is treated as a
    count of empty 'model.enum()' objects to be returned.  In the 'FooBar'
    example, this is equivalent to saying
    'foo, bar = model.enum(), model.enum()'."""


    if len(values)==1:

        values = values[0]

        try:
            iter(values)
        except:
            return [enum()] * values

    return map(enum,values)






class EnumerationClass(PrimitiveTypeClass):

    """Metaclass for enumeration types"""

    def __init__(klass,name,bases,cDict):

        super(EnumerationClass,klass).__init__(name,bases,cDict)

        values = {}

        map(values.update,
            binding.getInheritedRegistries(
                klass,'_EnumerationClass__enumeration_values'
            )
        )

        for k,v in cDict.items():
            if isinstance(v,enum):
                values.update(v(k))

        klass.__enumeration_values = values

        sorted = []

        for k in values.iterkeys():
            inst = klass(k)
            setattr(klass,k,inst)
            sorted.append(inst)

        sorted.sort()
        klass.__sorted = tuple(sorted)

    __enumsByName = __enumsByValue = binding.Make(dict)


    # Enumeration classes are never abstract and must always be
    # instantiable

    mdl_isAbstract = binding.Make(lambda: False)


    def __new__(meta, name, bases, cDict):

        # By default, ensure new enumeration classes don't get a dictionary
        if '__slots__' not in cDict:
            cDict['__slots__'] = ()

        return super(EnumerationClass,meta).__new__(meta, name, bases, cDict)


    def __getitem__(klass, nameOrValue, default=NOT_GIVEN):

        inst = NOT_FOUND

        if isinstance(nameOrValue,(str,unicode)):
            inst = klass.__enumsByName.get(nameOrValue, NOT_FOUND)

        if inst is NOT_FOUND:
            inst = klass.__enumsByValue.get(nameOrValue, NOT_FOUND)

        if inst is not NOT_FOUND:
            return inst

        if default is NOT_GIVEN:
            raise exceptions.EnumerationError(
                "Invalid name or value for enumeration",
                klass, nameOrValue
            )

        return default


    def get(klass, nameOrValue, default=None):
        return klass.__getitem__(nameOrValue, default)

    def __contains__(klass,value):
        return klass.get(value,NOT_FOUND) is not NOT_FOUND

    def __iter__(klass):
        return iter(klass.__sorted)


    def _setupInst(klass, inst, name):

        value = klass.__enumeration_values.get(
            name, NOT_GIVEN
        )

        if value is NOT_GIVEN:
            raise exceptions.EnumerationError(
                "Invalid name or value for enumeration",
                klass, name
            )

        klass.name.__set__(inst,name)
        klass._hashAndCompare.__set__(inst,value)

        klass.__enumsByName[name]   = inst
        klass.__enumsByValue[value] = inst


    def mdl_typeCode(klass):

        from peak.model.datatypes import TCKind, TypeCode

        return TypeCode(
            kind = TCKind.tk_enum,
            member_names = [e.name for e in klass]
        )

    mdl_typeCode = binding.Make(mdl_typeCode)












class Enumeration(PrimitiveType, HashAndCompare):
    """An enumeration type

    Defining an enumeration lets you specify a set of acceptable values
    of some other primitive type, each with its own name and representation.
    You can think of Python 2.3's new boolean type as an enumeration whose
    values are the integers 0 and 1, with names of 'False' and 'True'.
    PEAK 'model.Enumeration' classes work similarly.  For example::

        >>> class ThreeWay(model.Enumeration):
                Yes   = model.enum(1)
                No    = model.enum(0)
                Maybe = model.enum(-1)

        >>> print ThreeWay.Yes
        ThreeWay.Yes

        >>> print `ThreeWay.Yes.name`
        'Yes'

        >>> if ThreeWay.Yes == 1: print "yes!"
        yes!

        >>> print ThreeWay['No']
        ThreeWay.No

        >>> if 'Maybe' in ThreeWay: print "maybe!"
        maybe!

        >>> [e for e in ThreeWay]
        [ThreeWay.Maybe, ThreeWay.No, ThreeWay.Yes]

    The above class will have attributes 'Yes', 'No', and 'Maybe', each
    of which is 'ThreeWay' instance that hashes and compares equal to
    the specified literal (1,0, or -1).  The 'str()' and 'repr()' of these
    instances is the enumeration class and instance names, separated by '.'.

    Note: Enumeration values may be of any type.  See the docs on
    'model.enum()', 'model.enums()' and 'model.enumDict()' for various ways to
    specify the literals of an enumeration.

    Enumeration Class Methods

        Notice that the example 'ThreeWay' class itself offers some useful
        methods, such as '__getitem__', 'get', '__contains__', and '__iter__'.
        The first three methods work as if the class were a dictionary whose
        keys were all the names and values of the enumeration instances, mapped
        to the instances themselves.  '__iter__' iterates over all the
        instances sorted in order of their values.  All of these methods are
        available from any 'model.Enumeration' subclass you define.

    Subclassing and Instantiating Enumerations

        It is not necessary to specifically create an instance of an
        enumeration class.  The mere act of defining an enumeration class
        causes the instances to come into existence, and be available as
        attributes of the class.  There is only ever a fixed number of
        instances of an enumeration class, and even if you try to create
        a new instance, you will just get back one of the original ones.

        You can, however, subclass an enumeration class to add more values::

            >>> class FourWay(ThreeWay):
                    Dunno = model.enum("wha?")

            >>> FourWay.No  # values are inherited, but not the instances
            FourWay.No

            >>> if FourWay.Yes == ThreeWay.Yes: print "equal!"
            equal!

            >>> if FourWay.Yes is not ThreeWay.Yes: print "but not identical!"
            but not identical!

        The subclass will inherit all the same literals as its superclass,
        but will have new instances encapsulating them.  Thus, 'FourWay.Yes'
        is equal to, but not the same object as, 'ThreeWay.Yes'.  The subclass
        and superclass instances will 'repr()' with their respective class
        names, even though they will hash and compare the same."""

    __metaclass__ = EnumerationClass

    protocols.advise(
        classProvides=[IEnumType],
        instancesProvide=[IEnumValue]
    )

    __slots__ = 'name', '_hashAndCompare'

    def __new__(klass,nameOrValue):

        inst = klass.get(nameOrValue,NOT_FOUND)

        if inst is not NOT_FOUND:
            return inst

        inst = super(Enumeration,klass).__new__(klass)
        klass._setupInst(inst, nameOrValue)
        return inst

    def __init__(self,name):
        pass

    def __repr__(self):
        return "%s.%s" % (self.__class__.__name__,self.name)

    def mdl_fromString(klass, value):
        """Return an enumeration instance for string 'value'"""
        return klass[value]

    mdl_fromString = classmethod(mdl_fromString)

    def __reduce__(self):
        return self.__class__, (self._hashAndCompare,)









class ExtendedEnum(Enumeration):

    """Enumeration that also parses integers"""

    def mdl_toString(klass,x):
        if x in klass: return klass[x].name
        return str(int(x))

    def mdl_fromString(klass,x):
        if x.lower() in klass:
            return klass[x.lower()]
        return klass._convert(x)

    def _convert(klass,x):
        return int(x)

    _convert = classmethod(_convert)

    def __int__(self):
        return self._hashAndCompare





















