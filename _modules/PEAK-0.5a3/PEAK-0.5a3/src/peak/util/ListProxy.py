class ListProxy(object):

    """Abstract base for UserList-like, read-only list proxy objects"""

    def __repr__(self): return repr(self.data)
    def __lt__(self, other): return self.data <  self._cast(other)
    def __le__(self, other): return self.data <= self._cast(other)
    def __eq__(self, other): return self.data == self._cast(other)
    def __ne__(self, other): return self.data != self._cast(other)
    def __gt__(self, other): return self.data >  self._cast(other)
    def __ge__(self, other): return self.data >= self._cast(other)
    def __cmp__(self, other): return cmp(self.data, self._cast(other))

    def _cast(self, other):
        if isinstance(other, ListProxy):
            return other.data
        elif isinstance(other,list):
            return other
        else:
            return list(other)

    def __contains__(self, item): return item in self.data
    def __len__(self): return len(self.data)
    def __getitem__(self, i): return self.data[i]
    def count(self, item): return self.data.count(item)
    def index(self, item): return self.data.index(item)

    def __getslice__(self, i, j):
        i = max(i, 0); j = max(j, 0)
        return self.data[i:j]

    def __add__(self, other):   return self.data + self._cast(other)
    def __radd__(self, other):  return self._cast(other) + self.data

    def __mul__(self, n):
        return self.data*n

    __rmul__ = __mul__



