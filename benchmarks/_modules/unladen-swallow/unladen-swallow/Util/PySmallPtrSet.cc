#include "Util/PySmallPtrSet.h"

#include "llvm/ADT/SmallPtrSet.h"
#include "llvm/ADT/SmallVector.h"


typedef llvm::SmallPtrSet<PyObject *, 8> PySmallPtrSet_Impl;

typedef struct PySmallPtrSet {
    PySmallPtrSet_Impl llvm_set;
} PySmallPtrSet;


// C'tors, d'tors
PySmallPtrSet *
PySmallPtrSet_New()
{
    PySmallPtrSet *set = PyMem_New(PySmallPtrSet, 1);
    if (set == NULL)
        return NULL;
    new(set)PySmallPtrSet();

    return set;
}

void
PySmallPtrSet_Del(PySmallPtrSet *set)
{
    set->~PySmallPtrSet();
    PyMem_Free(set);
}

int
PySmallPtrSet_Insert(PySmallPtrSet *set, PyObject *obj)
{
    return set->llvm_set.insert(obj);
}

int
PySmallPtrSet_Erase(PySmallPtrSet *set, PyObject *obj)
{
    return set->llvm_set.erase(obj);
}

unsigned
PySmallPtrSet_Size(PySmallPtrSet *set)
{
    return set->llvm_set.size();
}

int
PySmallPtrSet_Count(PySmallPtrSet *set, PyObject *obj)
{
    return set->llvm_set.count(obj);
}

void
PySmallPtrSet_ForEach(PySmallPtrSet *set, PySmallPtrSetCallback callback,
                      void *callback_arg)
{
    // Copy the original set in case the callback modifies the set.
    llvm::SmallVector<PyObject *, 8> contents(set->llvm_set.begin(),
                                              set->llvm_set.end());
    for (llvm::SmallVector<PyObject *, 8>::iterator i = contents.begin(),
            end = contents.end(); i != end; ++i) {
        callback(*i, callback_arg);
    }
}
