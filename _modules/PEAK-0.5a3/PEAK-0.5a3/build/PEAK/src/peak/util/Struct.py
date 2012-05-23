"""It's a tuple...  it's a dictionary...  it's super struct!"""

from types import StringTypes

__all__ = [
    'structType', 'struct', 'makeStructType'
]


































class structType(type):

    """Sets up __fieldmap__ and field properties"""

    classmethods = (
        'fromArgs', 'fromOther', 'fromString',
        'fromMapping', 'extractFromMapping',
    )

    def __new__(meta, name, bases, cdict):

        cdict = cdict.copy()
        cdict['__slots__']=[]

        for cm in meta.classmethods:
            if cm in cdict:
                cdict[cm] = classmethod(cdict[cm])

        if '__fields__' in cdict:
            cdict['__fields__'] = list(cdict['__fields__'])

        return super(structType,meta).__new__(meta, name, bases, cdict)

    def __init__(klass, name, bases, cdict):

        fields = getattr(klass,'__fields__', ())
        baseMap = getattr(super(klass,klass), '__fieldmap__', {})
        fzip = zip(fields, range(len(fields)))
        fieldMap = klass.__fieldmap__ = dict(fzip)

        # No change in schema? leave properties alone
        if baseMap==fieldMap: return

        for fieldName, fieldNum in fzip:
            if fieldName in cdict or baseMap.get(fieldName)==fieldNum:
                # don't override any explicitly supplied properties
                # or inherited ones based on the same field number
                continue

            setattr(klass, fieldName, makeFieldProperty(fieldName, fieldNum))

    def addField(klass, fieldName):

        """Add field 'fieldName' to an existing struct class"""

        fm = klass.__fieldmap__

        if fieldName not in fm:

            fm[fieldName] = fieldNum = len(fm)
            setattr(klass, fieldName, makeFieldProperty(fieldName,fieldNum))
            klass.__fields__.append(fieldName)






























class struct(tuple):

    """Typed, immutable, multi-field object w/sequence and mapping interfaces

    Usage::

        class myRecord(struct):
            __fields__ = 'first', 'second', 'third'

        # the following will now all produce identical objects
        # and they'll all compare equal to the tuple (1,2,3):

        r = myRecord([1,2,3])
        r = myRecord(first=1, second=2, third=3)
        r = myRecord({'first':1, 'second':2, 'third':3})
        r = myRecord.fromMapping({'first':1, 'second':2, 'third':3})
        r = myRecord.extractFromMapping(
            {'first':1, 'second':2, 'third':3, 'blue':'lagoon'}
        )
        r = myRecord.fromMapping( myRecord([1,2,3]) )

        # the following will all print the same thing for any 'r' above:

        print r
        print (r.first, r.second, r.third)
        print (r[0], r[1], r[2])
        print (r['first'], r['second'], r['third'])

    If you want to define your own properties in place of the automagically
    generated ones, just include them in your class.  Your defined properties
    will be inherited by subclasses, as long as the field of that name is at
    the same position in the record.  If a subclass changes the field order,
    the inherited property will be overridden by a generated one, unless the
    subclass supplies a replacement as part of the class dictionary.

    Note: if you define custom properties, they only determine the *attributes*
    of the instance.  All other behaviors including string representation,
    iteration, item retrieval, etc., will be unaffected.  It's probably best
    to redefine the 'fromArgs' classmethod to manage the initial construction
    of the fields instead."""

    __metaclass__ = structType

    __fields__ = __converters__ = __defaults__ = ()


    def __new__(klass, *__args, **__kw):

        if len(__args)==1 and not __kw:

            arg = __args[0]

            if isinstance(arg,StringTypes):
                return klass.fromString(arg)

            elif isinstance(arg,dict):
                return klass.fromMapping(arg)

            return klass.fromOther(arg)


        elif __kw and not __args:
            return klass.fromMapping(__kw)

        return klass.fromArgs(*__args, **__kw)


    def fromString(klass, arg):

        """Override this classmethod to enable parsing from a string"""

        raise NotImplementedError










    def fromArgs(klass, *__args, **__kw):

        """Create from arguments

            By default, this classmethod is where all the other creation
            methods "call down" to, so that you can do any validation or
            conversions.  The default implementation just calls
            'tuple.__new__' on the '*__args' tuple.  You should override
            this with a classmethod that takes the arguments you want, in
            the same order as your '__fields__' definition, supplying
            defaults if desired.

            The default version of this method will accept input sequences
            with more items than there are fields to fill.  The extra data
            isn't lost, it's just unavailable except via sequence methods.
            If you want different behavior, such as truncating the sequence
            or raising an exception, you'll need to override this method.
        """

        if __kw:
            raise TypeError("Invalid keyword arguments for " + klass.__name__)

        return tuple.__new__(klass, __args)


















    def fromOther(klass, arg):

        """Create from a single argument

            You can define a classmethod here, to be used in place of
            'tuple.__new__' when the struct is being created from a single
            argument that is not a dictionary, keywords, or a string.

            The default simply hands the argument through to the
            'fromArgs()' method, where it will be treated as being the
            first field of the struct.
        """
        return klass.fromArgs(arg)


    def fromMapping(klass, arg):

        """Create a struct from a mapping

            This method checks that the mapping doesn't contain any field names
            the struct won't accept.  This prevents silent unintentional loss
            of information during conversions.  If you want extra data in the
            mapping to be ignored, you should use 'extractFromMapping' instead.

            Note that although this method will raise 'ValueError' for fields
            that would be dropped, it uses a default value of 'None' for any
            fields which are missing from the mapping.  If you want a stricter
            policy, you'll need to override this.
        """

        fm = klass.__fieldmap__; nfm = fm.copy(); nfm.update(arg)

        if len(nfm)>len(fm):
            raise ValueError(
                ("Mapping contains keys which are not fields of %s"
                 % klass.__name__), arg
            )

        return klass.fromArgs(*tuple(map(arg.get, klass.__fields__)))


    def extractFromMapping(klass, arg):
        """Fast extraction from a mapping; ignores undefined fields"""
        return klass.fromArgs(*tuple(map(arg.get, klass.__fields__)))


    def __getitem__(self, key):

        if isinstance(key,StringTypes):

            # will raise KeyError for us if it's not found
            i = self.__fieldmap__[key]

            if i>=len(self):
                raise KeyError,key
            else:
                key = i

        # this will raise IndexError instead of KeyError, which we want
        # if it was a number...
        return tuple.__getitem__(self,key)


    def get(self, key, default=None):
        try:
            return self[key]
        except (KeyError,IndexError):
            return default


    def copy(self):         return dict(self.items())
    def keys(self):         return list(self.__fields__[:len(self)])
    def iterkeys(self):     return iter(self.__fields__[:len(self)])
    def items(self):        return zip(self.__fields__,self)
    def iteritems(self):    return iter(self.items())
    def values(self):       return list(self)
    def itervalues(self):   return iter(self)





    __safe_for_unpickling__ = True

    def __reduce__(self):   return self.__class__, (tuple(self),)

    def __contains__(self, key):
        myLen = len(self)
        return self.__fieldmap__.get(key,myLen) < myLen

    has_key = __contains__



def makeFieldProperty(fieldName, fieldNum):

    def get(self):
        try:
            return tuple.__getitem__(self,fieldNum)
        except IndexError:
            return None

    return property(get)


def makeStructType(name, fields, baseType=struct, **kw):
    kw['__fields__'] = fields
    return structType(name or 'anonymous_struct', (baseType,), kw)















