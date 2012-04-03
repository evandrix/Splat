"""Support for inheritance of metaclass constraints

    This module exports a 'makeClass' function that can be used as a
    '__metaclass__' value in class definitions to provide enhanced metaclass
    capabilities, such as specifying multiple metaclasses, and automatic
    generation of a satisfactory metaclass based on the information provided.

    PEAK automatically uses this function to build your classes when
    you use 'config.setupModule()', so you don't usually need to use this
    directly.  But if you want to know more about what it does and how it
    works, or have a special need, this is the right place to look.
"""

from weakref import WeakValueDictionary
from types import ClassType
from protocols.advice import minimalBases

__all__ = ['makeClass']























### Metaclass Derivation Code

metaReg = WeakValueDictionary()     # Weak, so unused metaclasses can die off

def derivedMeta(metaclasses):
    derived = metaReg.get(metaclasses)

    if derived is None:
        normalized = normalizeBases(metaclasses)
        derived = metaReg.get(normalized)

        if derived is None:
            if len(normalized)==1:
                derived = normalized[0]
            else:
                derived = metaFromBases(normalized)(
                    '_'.join([n.__name__ for n in normalized]),
                    metaclasses, {}
                )
            try: metaReg[normalized] = derived
            except TypeError: pass  # Some metatypes can't be weakref'd

        try: metaReg[metaclasses] = derived
        except TypeError: pass

    return derived


def normalizeBases(allBases):
    return minimalBases([b for b in allBases if b is not makeClass])


def metaFromBases(bases):
    meta = tuple([getattr(b,'__class__',type(b)) for b in bases])
    if meta==bases: raise TypeError("Incompatible root metatypes",bases)
    return derivedMeta(meta)





def makeClass(name,bases,dict):

    """makeClass(name, bases, dict) - enhanced class creation

    Automatically generates a metaclass that satisfies metaclass constraints
    inherited from the supplied base classes, and then calls it to create a
    new class.  It can be used as a '__metaclass__' value, or can be directly
    called as a substitute to using 'new.classobject()' to dynamically create
    classes.

    If the supplied dictionary contains a '__metaclasses__' entry, it will be
    taken to be a sequence of metaclasses which should take first priority in
    the base classes of the generated metaclass.  The next highest priority is
    given to the dictionary's '__metaclass__' entry, if any, and then priority
    is according to the order of the base classes which introduce the metaclass
    constraints.

    'ClassType' (the "classic" class type) is automatically excluded from the
    constraints, as is the 'makeClass' function itself (just in case you used
    the function as an explicit metaclass).  'makeClass()' will only return
    a "classic" class if all the base classes are classic, and no
    '__metaclass__' or '__metaclasses__' entries supply any non-classic
    types.  Effectively, 'makeClass()' fully supports the three most popular
    Python metatypes: "classic classes", "new-style types", and
    'ExtensionClass'.  You cannot, however, combine ExtensionClasses with
    new-style types, because their root metatypes are different.  That is,
    'type(type) is type', and 'type(ExtensionClass) is ExtensionClass'.  There
    may be other ways to create illegal metatype combinations, but they should
    be detected and result in a TypeError.

    Generated metaclasses are cached for reuse, and they are automatically
    given classnames which are the concatenation of their base metaclasses'
    names.  So if you set '__metaclasses__' to 'ThreadSafe, Persistent'
    (or if your bases are instances of 'ThreadSafe' and 'Persistent'), the
    derived metaclass will be called 'ThreadSafe_Persistent'.  That is,
    the return from 'makeClass()' will be of type (have a '__class__' of)
    'ThreadSafe_Persistent'.

    Metaclasses are derived according to the algorithm in the book "Putting
    Metaclasses to Work", by Ira R. Forman and Scott H. Danforth.  It, and
    Guido's metaclass tutorial for Python 2.2, are highly recommended reading
    for making the best use of this capability.  But a brief word to the wise:

        * Write your metaclasses co-operatively!  Don't assume that your
          metaclass will be the first or last one to handle a particular
          method call.

        * In general, when programming with new-style classes, don't assume
          you know what the inheritance order is.  Always use 'super()';
          'super()' is your friend.  :)  Remember that your immediate base
          class today, may have other classes sandwiched between you and it
          tomorrow, if one of your subclasses so desires!
    """

    # Create either a "classic" Python class, an ExtensionClass, or a new-style
    # class with autogenerated metaclass, based on the nature of the base
    # classes involved

    name = str(name)  # De-unicode

    metaclasses = [getattr(b,'__class__',type(b)) for b in bases]

    if dict.has_key('__metaclass__'):
        metaclasses.insert(0,dict['__metaclass__'])

    if dict.has_key('__metaclasses__'):
        metaclasses[0:0] = list(dict['__metaclasses__'])

    metaclasses = normalizeBases(metaclasses)

    if metaclasses:

        # If we have metaclasses, it's not a classic class, so derive a
        # single metaclass, and ask it to create the class.

        if len(metaclasses)==1:
            metaclass = metaclasses[0]
        else:
            metaclass = derivedMeta(metaclasses)

        return metaclass(name,bases,dict)

    # No metaclasses, it's a classic class, so use 'new.classobj'

    from new import classobj; return classobj(name,bases,dict)






































if __name__=='__main__':

    class MMM2(type):
        pass

    class MM1(type):
        pass

    class MM2(type):
        __metaclass__ = MMM2

    class M1(type):
        __metaclass__ = MM1

    class M2(type):
        __metaclass__ = MM2

    class C1:
        __metaclass__ = M1

    class C2:
        __metaclass__ = M2

    class C3(C1,C2):
        __metaclass__ = makeClass

    from ExtensionClass import Base

    class X:
        __metaclass__ = makeClass

    class Foo(Base):
        __metaclass__ = makeClass

    class Y(X,Foo):
        __metaclass__ = makeClass

    #The below would fail with a TypeError - can't combine ExtCls and 'type'
    #class Z(Y,C3):
    #    __metaclass__ = makeClass

