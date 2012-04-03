"""Delegate hashes and comparisons to a (possibly computed) attribute"""

__all__ = ['HashAndCompare']

class HashAndCompare(object):

    """Mixin that allows 'hash' and 'cmp' operations on a delegate value

        'model.Immutable', 'model.Struct', and 'model.Enumeration' all use
        this mixin so that their instances can be hashed and compared according
        to a delegate value.  For enumerations, it's the "value" of the
        enumeration, and for the others it's a tuple of attribute values.

        You only need to use this mixin if you *aren't* using one of the
        immutable element base classes such as 'model.Immutable' or
        'model.Struct', but you want to be able to have your instances
        implement '__hash__', '__cmp__', and '__nonzero__' based on a delegate
        value in the same way.

        To use this mixin, just add it to your base class list, and ensure
        that your '_hashAndCompare' attribute is always the desired delegate
        value.  If your instances are to be used as dictionary keys, the
        value of the '_hashAndCompare' attribute must be hashable, immutable,
        and must never vary.  That is, every access of the '_hashAndCompare'
        value should return the same or an equivalent object.
    """

    def __hash__(self):
        return hash(self._hashAndCompare)

    def __cmp__(self,other):
        return cmp(self._hashAndCompare,other)

    def __nonzero__(self):
        return self._hashAndCompare and True or False

