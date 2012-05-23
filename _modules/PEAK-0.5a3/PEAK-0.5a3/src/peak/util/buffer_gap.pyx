"""Gap-based Mutable Character Buffer"""

cdef extern from "Python.h":
    void* PyMem_Malloc(int n) except NULL
    void* PyMem_Realloc(void *p, int n) except NULL
    void  PyMem_Free(void *p)
    object PyString_FromStringAndSize(char *, int)
    int PyObject_AsReadBuffer(object obj, void **buffer, int *buffer_len) except -1
    int PyObject_Compare(object o1, object o2) except *


cdef extern from "string.h":
    void* memmove(void *DST, void *SRC, int LENGTH)


cdef class Buffer


cdef int _checkIndex(int p, int len, int hi) except -1:

    if p<0:
        p = p + len

    if p<0 or p>=hi:
        raise IndexError, p

    return p


cdef int _fixupIndex(Buffer self, int p) except -1:

    p = _checkIndex(p, self.length, self.length)

    if p>=self.gap:
        p = p+self.gapsize

    return p




cdef void _setGap(Buffer self, int pos):

    cdef char *buf
    cdef int move, after

    if pos != self.gap:

        after = self.gap + self.gapsize

        if pos < self.gap:
            move = self.gap - pos
            memmove(&self.buffer[after-move], &self.buffer[pos], move)

        else:
            move = pos - self.gap
            memmove(&self.buffer[self.gap], &self.buffer[after], move)

        self.gap = pos


cdef int _setGapSize(Buffer self,int size) except -1:

    cdef int count

    if size > self.gapsize:

        _setGap(self, self.length)

        count = min(size, self.alloc)

        self.buffer  = <char *>PyMem_Realloc(self.buffer, self.size + count)

        self.gapsize = self.gapsize + count
        self.size    = self.size + count







cdef class Buffer:

    cdef int gap, gapsize, length, size, alloc
    cdef char *buffer

    def __new__(self, object initializer='', int alloc=512):
        self.size = 0
        self.gap = 0
        self.length = 0
        self.gapsize = 0
        self.buffer = NULL
        self.alloc = alloc

    def __dealloc__(self):
        if self.buffer is not NULL:
            PyMem_Free(self.buffer)

    def __init__(self, object initializer='', int alloc=512):
        self.__setslice__(0, self.length, initializer)

    def __str__(self):
        return self[0:self.length]

    def __repr__(self):
        return repr(str(self))

    def __len__(self):
        return self.length

    def __getitem__(self, int p):
        p = _fixupIndex(self, p)
        return self.buffer[p]

    def __setitem__(self, int p, int x):
        p = _fixupIndex(self, p)
        self.buffer[p] = x

    def __delitem__(self, int p):
        self.__delslice__(p,p+1)


    def insert(self, int p, int x):

        if p<0 or p>self.length:
            raise IndexError, p

        if self.gapsize==0:
            _setGapSize(self, 1)

        _setGap(self, p)

        self.buffer[p] = x

        self.gapsize = self.gapsize - 1
        self.gap     = self.gap     + 1
        self.length  = self.length  + 1


    def append(self, int x):
        self.insert(self.length, x)


    def extend(self, aStr):
        self.__setslice__(self.length, self.length, aStr)


















    def __setslice__(self, int i, int j, x):

        cdef int change, datalen
        cdef void *data

        i = _checkIndex(i, self.length, self.length+1)
        j = _checkIndex(j, self.length, self.length+1)

        # XXX need index chopping ???

        PyObject_AsReadBuffer(x, &data, &datalen)
        change = datalen - (j-i)

        if change>0:
            _setGapSize(self, change)

        _setGap(self, i)

        if datalen:
            memmove(&self.buffer[i], data, datalen)

        self.gapsize = self.gapsize - change
        self.gap     = self.gap     + change
        self.length  = self.length  + change


    def __getslice__(self, int i, int j):

        i = _checkIndex(i, self.length, self.length+1)
        j = _checkIndex(j, self.length, self.length+1)

        if self.gap<j:
            _setGap(self, self.length)

        if (j-i) > 0:
            return PyString_FromStringAndSize(&self.buffer[i], j-i)

        return ''



    def __delslice__(self, int i, int j):

        cdef int change

        i = _checkIndex(i, self.length, self.length+1)
        j = _checkIndex(j, self.length, self.length+1)

        change = i-j    # negative

        _setGap(self, i)

        self.gapsize = self.gapsize - change
        self.gap     = self.gap     + change
        self.length  = self.length  + change


    def __iadd__(self, x):
        self.__setslice__(self.length,self.length,x)
        return self


    def __add__(object x, object y):

        cdef int alloc

        if isinstance(x,Buffer):
            alloc = (<Buffer> x).alloc
        elif isinstance(y,Buffer):
            alloc = (<Buffer> y).alloc
        else:
            alloc = 512

        newBuf = Buffer(x,alloc)
        newBuf.extend(y)
        return newBuf






    def __cmp__(self, ob):
        return PyObject_Compare(str(self), ob)


    def __getreadbuffer__(self, int segment, void **p):

        if segment:
            raise SystemError("Invalid read segment", segment)

        _setGap(self, self.length)
        p[0] = self.buffer
        return self.length


    def __getwritebuffer__(self, int segment, void **p):

        if segment:
            raise SystemError("Invalid write segment", segment)

        _setGap(self, self.length)
        p[0] = self.buffer
        return self.length


    def __getcharbuffer__(self, int segment, char **p):

        if segment:
            raise SystemError("Invalid character segment", segment)

        _setGap(self, self.length)
        p[0] = self.buffer
        return self.length


    def __getsegcount__(self, int *p):

        if p is not NULL:
            p[0] = self.length

        return 1

