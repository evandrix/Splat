cdef extern from "Python.h":
    int PyType_Check(object o)
    object PyDict_New()
    void *PyDict_GetItem(object dict,object key)
    struct _object:
        void *ob_type

cdef extern object GET_DICTIONARY(object o)

cdef void *_lockType
cdef object Py_None     # Avoid dictionary lookups for 'None'

from peak.util.threads import get_ident


cdef class bindingLock:

    cdef int id

    def __new__(self):
        self.id = get_ident()


_lockType = <void *> bindingLock
Py_None   = None        # Avoid dictionary lookups for 'None'


cdef int isLock(void *obj):
    return (<_object *>obj).ob_type == _lockType


cdef int isOurs(void *obj):
    cdef int id
    cdef bindingLock lock
    id = get_ident()
    lock = <bindingLock> obj
    return lock.id == id




cdef class BaseDescriptor:

    """Data descriptor base class for 'Once' bindings"""

    cdef public object attrName
    cdef public int isVolatile


    def __set__(self, obj, value):
        d = GET_DICTIONARY(obj)
        d[self.attrName] = self.onSet(obj, self.attrName, value)

    def __delete__(self, obj):
        d = GET_DICTIONARY(obj)
        del d[self.attrName]

    def onSet(self, obj, attrName, value):
        return value

    def ofClass(self, attrName, klass):
        return self


    def __get__(self, ob, typ):
        # Compute the attribute value and cache it

        # Note: fails if attribute name not supplied or doesn't reference
        # this descriptor!

        cdef void *obj

        if ob is Py_None:
            return self.ofClass(self.attrName, typ)

        n = self.attrName
        if not n: # or getattr(ob.__class__, n, None) is not self:
            self.usageError()

        d = GET_DICTIONARY(ob)
        obj = PyDict_GetItem(d, n)

        if obj:

            if (<_object *>obj).ob_type == _lockType:

                if isOurs(obj):
                    raise AttributeError(
                        "Recursive attempt to compute attribute", n
                    )

            else:
                return <object> obj

        else:
            # claim our spot
            d[n] = bindingLock()

        try:
            value = self.computeValue(ob, d, n)
            if not self.isVolatile:
                value = self.onSet(ob, n, value)

        except:
            # We can only remove the guard if it was put in
            # place by this thread, and another thread hasn't
            # already finished the computation

            obj = PyDict_GetItem(d, n)
            if obj and isLock(obj) and isOurs(obj):
                del d[n]
            raise

        if self.isVolatile:
            del d[n]
        else:
            d[n] = value

        return value




    def usageError(self):
        raise TypeError(
            "%s was used in a type which does not support active bindings,"
            " but a valid attribute name was not supplied"
            % self
        )


    def computeValue(self, ob, idict, attrName):
        raise AttributeError, attrName


__all__ = ['BaseDescriptor']




























