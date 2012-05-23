"""Objects that can be written, unless they've been read

Dynamic configuration can be a wonderful thing.  It can also be a nightmare,
if you have configuration values that depend on other configuration values,
and you are using lots of components that are reading and writing those
values.  If you change a value after it has already been used by another
component, how can you be sure what objects were configured in what way?

Different languages and systems approach this issue differently.  In Java,
it's common to have settings which can be set only once.  In Python, one
may use immutables.  Zope 3X has a configuration conflict detection algorithm.
But all of these approaches depend on either a write-once approach or an
atomic configuration phase.

PEAK takes a "quantum physics" approach to immutability instead: treat
configuration data as an opaque box, whose contents you can change at will.
However, once somebody looks in the box, the result is fixed and can no
longer be changed.  You can think of it as a kind of "lazy immutability".

The EigenData module supplies an 'EigenCell' class for storing single
values, and an 'EigenDict' class to be used in place of dictionaries.
Modifying an 'EigenCell' or 'EigenDict' once it has been read results in
an 'AlreadyRead' exception.  Also available: 'CollapsedCell', which is an
empty 'EigenCell' that has already been read and is therefore immutable.

FYI: the module and classes are named after eigenstates in quantum physics;
"one of a finite number of states that a quantum system can be in".  The
famous "Schrodinger's Cat" thought experiment is an analogy for eigenstates:
once the box is opened, its contents are forced to collapse to a single
eigenstate.  'SchrodingDict' and 'SchrodingCell', however, are much more
awkward to say and type!"""

__all__ = [
    'AlreadyRead', 'EigenCell', 'CollapsedCell', 'EigenDict',
]

from protocols import Interface

class AlreadyRead(Exception):
    """Key or value has already been read"""

class EigenCell(object):

    """Hold a value which can be changed as long as it has not been examined

    An EigenCell is used to hold a configuration value that should not be
    changed once it is used.  The value may be 'set()' or 'unset()' at will
    as long as the 'exists()' or 'get()' methods have not been called.  As
    soon as the cell's value has been read or tested for existence, the value
    is locked and an 'AlreadyRead' exception will be thrown if you attempt to
    'set()' or 'unset()' the value after that point.  (Note: 'unset()' is a
    no-op if the value is empty, whether the cell is locked or not, because
    it does not change the value's nonexistence.)"""

    __slots__ = ['value','locked']

    def __init__(self):
        """Create an (empty and unread) EigenCell"""
        self.locked = False


    def get(self, setdefault=None):
        """Return the cell's value, or raise AttributeError if empty

        A function may be supplied to set a default value, if the cell has not
        yet been read and no value is currently assigned.  The return value
        of the function will be used.  For example::

            aCell.get(lambda: someObj())

        will set the value of 'aCell' to 'someObj()' if 'aCell' has not been
        read and has no value currently assigned.  Notice that you must pass
        a function, not a value.  The simplest way to do this is with 'lambda'
        as shown above."""

        if not self.locked and not hasattr(self,'value') and setdefault:
            self.value = setdefault()

        self.locked = True
        return self.value


    def exists(self):
        """Return true if the cell contains a value."""
        self.locked = True
        return hasattr(self,'value')

    def set(self,value):
        """Set the cell's value, or raise AlreadyRead"""
        if self.locked: raise AlreadyRead
        self.value = value

    def unset(self):
        """Remove the cell's value (reset to non-existence)"""
        if hasattr(self,'value'):
            if self.locked: raise AlreadyRead
            del self.value


























class EigenDict(object):

    """Mapping whose entries can be changed as long as they are unread

    An EigenDict is used to hold a set of configuration values that should not
    be changed once they are read.  It offers essentially the same interface
    as a standard Python dictionary, with the following twists:

     * Operations on individual entries are delegated to EigenCell objects,
       so a given entry cannot be written to or deleted once it has been
       read, or its existence inspected by 'has_key()', 'get()', etc.

     * Operations on the dictionary as a whole, such as 'keys()', 'values()',
       'copy()', '__cmp__()', '__repr__()', etc., will lock the entire
       dictionary and no further modifications will be allowed.

     * '__len__()' and 'popitem()' methods are not available.

     * '.copy()' returns a standard Python dictionary, not an EigenDict

    """

    def __init__(self, dict=None):
        self.data = {}
        if dict is not None: self.update(dict)

    def keys(self):
        self.lock(); return self.data.keys()

    def items(self):
        self.lock(); return [(k,v.get()) for (k,v) in self.data.items()]

    def values(self):
        self.lock(); return [v.get() for v in self.data.values()]

    def copy(self):
        return dict(self.items())




    def iteritems(self):
        return iter(self.items())

    def iterkeys(self):
        return iter(self.keys())

    def itervalues(self):
        return iter(self.values())


    def update(self, dict):
        sc = self._setCell
        for k, v in dict.items():
            sc(k).set(v)

    def clear(self):
        for v in self.data.values():
            v.unset()


    def __repr__(self):
        return `self.copy()`

    def __cmp__(self, dict):
        return cmp(self.copy(), dict.copy())

    def __iter__(self):
        return self.iterkeys()













    locked = False

    def lock(self):
        """Lock the dictionary, ensuring that its contents cannot change

            This method locks all the dictionary's cells, and sets a flag
            to ensure that no new cells will be created.  It also discards
            empty cells, for the convenience of routines that operate on
            the dictionary as a whole, like 'keys()' and 'values()'.
        """

        if self.locked:
            return

        self.locked = True
        data = self.data

        for k,v in data.items():
            if not v.exists():
                del data[k]


    def _setCell(self, key):
        """Return a new or existing EigenCell for 'key'

            If there is no EigenCell stored under 'key', return a new
            EigenCell and store it.  If the dictionary is locked, return
            an empty, locked EigenCell instead of creating a new one.  This
            ensures that no new entries can be created if locked."""

        cell = self.data.get(key)

        if cell is None:

            if self.locked:
                return CollapsedCell

            cell = self.data[key] = EigenCell()

        return cell

    def __getitem__(self, key):

        cell = self._setCell(key)

        if cell.exists():
            return cell.get()

        raise KeyError, key


    def get(self, key, failobj=None, factory=None):

        cell = self._setCell(key)

        try:
            return cell.get(factory)
        except AttributeError:
            return failobj


    def setdefault(self, key, failobj=None):
        if not self.data.has_key(key):
            self[key] = failobj
        return self[key]


    def has_key(self, key):
        return self._setCell(key).exists()

    def __contains__(self, key):
        return self._setCell(key).exists()

    def __setitem__(self, key, item):
        self._setCell(key).set(item)

    def __delitem__(self, key):
        self._setCell(key).unset()




# CollapsedCell is an empty (but read and locked) EigenCell

CollapsedCell = EigenCell()
CollapsedCell.exists()  # force locking





































