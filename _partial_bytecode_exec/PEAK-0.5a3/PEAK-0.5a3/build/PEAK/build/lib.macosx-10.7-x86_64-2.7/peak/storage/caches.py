from peak.api import binding, protocols
from interfaces import *
from weakref import WeakValueDictionary


__all__ = [
    'WeakCache', 'PermanentCache', 'NullCache',
]


class CacheBase(binding.Component):
    protocols.advise(
        instancesProvide=[ICache]
    )


class WeakCache(CacheBase, WeakValueDictionary):

    """Keeps items in cache as long as they are in use elsewhere"""

    def __init__(self, *args, **kw):
        super(WeakCache,self).__init__(*args, **kw)
        WeakValueDictionary.__init__(self)


class PermanentCache(CacheBase, dict):

    """Keeps items in cache until explicitly cleared"""

    def __new__(klass, parent=None):
        return super(PermanentCache,klass).__new__(klass)










class NullCache(CacheBase):

    """Never keeps anything in cache"""

    def get(self, key, default=None):
        return default

    def __setitem__(self, key, value):
        pass

    def clear(self):
        pass

    def values(self):
        return ()


























