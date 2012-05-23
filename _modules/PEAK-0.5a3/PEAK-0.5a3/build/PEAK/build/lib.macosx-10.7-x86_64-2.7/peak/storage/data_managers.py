from peak.api import binding, model, protocols
from interfaces import *
from transactions import TransactionComponent
from peak.persistence import Persistent, isGhost
from peak.util.ListProxy import ListProxy


__all__ = [
    'FacadeDM', 'QueryDM', 'EntityDM', 'PersistentQuery', 'QueryLink',
    'StorableDM',
]






























class FacadeDM(binding.Component):

    """DM that just returns objects from other DM(s) via a different key"""

    protocols.advise(
        instancesProvide=[IKeyableDM]
    )

    def __getitem__(self, oid, state=None):

        ob = self.cache.get(oid,self)

        if ob is not self:

            # double-check identity
            if oid==self.oidFor(ob):
                return ob

            # Oops, key no longer valid, drop it
            del self.cache[oid]

        ob = self._retrieve(oid, state)

        if ob is not None:
            self.cache[oid] = ob
            return ob

        raise KeyError, oid

    preloadState = __getitem__

    cache = binding.Make('peak.storage.caches:WeakCache')

    def _retrieve(self, oid, state=None):
        """Look up 'oid' in underlying storage and return it, or 'None'"""
        raise NotImplementedError

    def oidFor(self, ob):
        """Return this DM's OID for 'ob'; used to validate consistency"""
        raise NotImplementedError

class PersistentQuery(Persistent, ListProxy):

    """An immutable, persistent ListProxy for query results"""

    __slots__ = 'data', '__weakref__'

    def __getstate__(self):
        return self.data

    def __setstate__(self,state):
        self.data = list(state)






























class QueryLink(ListProxy):

    """PersistentQuery proxy for use in Collection or Sequence

    QueryLinks are designed primarily for use with relational databases and
    other systems that implement one-to-many relationships via a pointer on
    the "one" side, and a query on the "many" side. The QueryLink is used on
    the "many" side, while the "one" side is implemented via a
    straightforward load/save on the "pointer" (foreign key).

    A QueryLink is a proxy for use in an object's loaded state, to reference
    a persistent query whose contents represent the value of a collection or
    sequence property.  Using a QueryLink keeps changes to the object from
    affecting the underlying query, and they also prevent execution of the
    query if the object is modified without actually looking at the results
    of the query.

    In this way, if you have a collection with 10,000 things in it
    ("virtually"), it isn't necessary to load the list of 10,000 things to
    add an item to it.  What happens is that if the query hasn't already
    executed, the QueryLink ignores the modification attempts (under the
    assumption that if you look at the collection later, the query will
    execute and be up-to-date). If the query has executed, the QueryLink
    makes a copy of the query results, and modifies the copy.

    Last, but not least, whenever any operation (whether read or write) is
    performed on a QueryLink, it checks whether the data in the underlying
    query has been refreshed since the QueryLink made a copy of it, and if
    so, discards its local copy.

    Normal usage looks like this (in a DM's '_load()' method)::

        return {'someCollection': QueryLink(aQueryDM[foreignKey]), ..."""

    __cacheData = None
    __localData = None

    def __init__(self, query):
        self.__query = query


    def data(self):
        # Discard cached form of query data when underlying query reloaded
        if self.__cacheData is not self.__query.data:
            self.__cacheData = self.__query.data
            self.__localData = self.__cacheData[:]

        return self.__localData

    data = property(data)


    def __isActive(self):
        return not isGhost(self.__query)


    def __setitem__(self, i, item):
        if self.__isActive():
            self.data[i]=item

    def __delitem__(self, i):
        if self.__isActive():
            del self.data[i]


    def __setslice__(self, i, j, other):
        if self.__isActive():
            i = max(i, 0); j = max(j, 0)
            self.data[i:j] = self._cast(other)


    def __delslice__(self, i, j):
        if self.__isActive():
            i = max(i, 0); j = max(j, 0)
            del self.data[i:j]


    def __iadd__(self, other):
        if self.__isActive():
            self.data += self._cast(other)
        return self

    def append(self, item):
        if self.__isActive():
            self.data.append(item)


    def insert(self, i, item):
        if self.__isActive():
            self.data.insert(i, item)


    def remove(self, item):
        if self.__isActive():
            self.data.remove(item)


    def extend(self, other):
        if self.__isActive():
            self.data.extend(self._cast(other))























class QueryDM(TransactionComponent):

    resetStatesAfterTxn = True

    protocols.advise(
        instancesProvide=[IDataManager]
    )

    def __getitem__(self, oid, state=None):

        if self.resetStatesAfterTxn:
            # must always be used in a txn
            self.joinedTxn

        ob = self.cache.get(oid,self)

        if ob is not self:
            return ob

        ob = self._ghost(oid,state)

        if isinstance(ob,Persistent):

            ob._p_jar = self
            ob._p_oid = oid

            if state is None:
                ob._p_deactivate()
            else:
                ob.__setstate__(state)

        self.cache[oid] = ob
        return ob

    preloadState = __getitem__






    # Private abstract methods/attrs

    cache = binding.Make('peak.storage.caches:WeakCache')

    defaultClass = PersistentQuery

    def _ghost(self, oid, state=None):

        klass = self.defaultClass

        if klass is None:
            raise NotImplementedError

        return klass()


    def _load(self, oid, ob):
        raise NotImplementedError


    # Persistence.IPersistentDataManager methods

    def setstate(self, ob):

        if self.resetStatesAfterTxn:
            # must always be used in a txn
            self.joinedTxn

        oid = ob._p_oid
        assert oid is not None
        ob.__setstate__(self._load(oid,ob))


    def mtime(self, ob):
        pass    # return None

    def register(self, ob):
        raise TypeError("Attempt to modify query result", ob)



    # ITransactionParticipant methods

    def finishTransaction(self, txnService, committed):

        if self.resetStatesAfterTxn:

            for oid, ob in self.cache.items():
                if isinstance(ob,Persistent):
                    ob._p_deactivate()

        super(QueryDM,self).finishTransaction(txnService,committed)






























class EntityDM(QueryDM):

    protocols.advise(
        instancesProvide=[IWritableDM]
    )

    def oidFor(self, ob):

        if ob._p_jar is self:

            oid = ob._p_oid

            if oid is None:
                # force it to have an ID by saving it
                ob._p_changed = 1
                self.flush(ob)
                return ob._p_oid

            else:
                return oid

        else:
            return self._thunk(ob)


    def newItem(self,klass=None):

        if klass is None:
            klass = self.defaultClass

        if klass is None:
            raise NotImplementedError

        ob=klass()
        ob.__setstate__(self._defaultState(ob))
        ob._p_jar = self

        self.register(ob)
        return ob


    # Set/state management

    dirty = binding.Make(dict)
    saved = binding.Make(dict)


    def flush(self, ob=None):

        markSaved = self.saved.setdefault
        dirty = self.dirty

        if ob is None:
            obs = dirty.values()
        else:
            obs = [ob]

        for ob in obs:

            if ob._p_oid is None:

                # No oid, it's a new object that needs saving
                oid = ob._p_oid = self._new(ob)
                self.cache[oid]=ob

            else:
                # just save it the ordinary way
                self._save(ob)

            # Update status flags and object sets
            key = id(ob)

            markSaved(key,ob)

            if key in dirty:
                del dirty[key]

            ob._p_changed = False




    # Private abstract methods/attrs

    defaultClass = None

    def _save(self, ob):
        raise NotImplementedError

    def _new(self, ob):
        raise NotImplementedError

    def _defaultState(self, ob):
        return ob.__getstate__()

    def _thunk(self, ob):
        raise NotImplementedError



    # Persistence.IPersistentDataManager methods

    def register(self, ob):

        # Ensure that we have a transaction service and we've joined
        # the transaction in progress...

        self.joinedTxn

        # precondition:
        #   object has been changed since last save

        # postcondition:
        #   ob is in 'dirty' set
        #   DM is registered w/transaction if not previously registered

        key = id(ob)

        # Ensure it's in the 'dirty' set
        self.dirty.setdefault(key,ob)

        return self.joinedTxn

    # ITransactionParticipant methods

    def readyToVote(self, txnService):
        if self.dirty:
            self.flush()
            return False
        else:
            return True


    def voteForCommit(self, txnService):
        # Everything should have been written by now...  If not, it's VERY BAD
        # because the DB we're storing to might've already gotten a tpc_vote(),
        # and won't accept writes any more.  So raise holy hell if we're dirty!
        assert not self.dirty


    def commitTransaction(self, txnService):
        self.saved.clear()


    def abortTransaction(self, txnService):

        for ob in self.dirty.values():
            ob._p_changed = False
            ob._p_deactivate()

        self.dirty.clear()

        for ob in self.saved.values():
            ob._p_deactivate()

        self.saved.clear()








class StorableDMClass(EntityDM.__class__, Persistent.__class__):
    pass

class StorableDM(EntityDM,Persistent):
    __metaclass__ = StorableDMClass




































