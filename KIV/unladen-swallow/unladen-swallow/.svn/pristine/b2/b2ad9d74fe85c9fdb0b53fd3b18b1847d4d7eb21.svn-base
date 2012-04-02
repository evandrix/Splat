//===----------------------------------------------------------------------===//
//
// This file defines C wrappers for an llvm::SmallPtrSet<PyObject *>
//
//===----------------------------------------------------------------------===//

#ifndef UTIL_PYSMALLPTRSET_H
#define UTIL_PYSMALLPTRSET_H

#ifdef __cplusplus
extern "C" {
#endif

#include "Python.h"


typedef struct PySmallPtrSet PySmallPtrSet;
typedef void(*PySmallPtrSetCallback)(PyObject *, void *);


// C'tors, d'tors
PySmallPtrSet *PySmallPtrSet_New(void);
void PySmallPtrSet_Del(PySmallPtrSet *);

/// Insert - This returns 1 if the pointer was new to the set, 0 if it
/// was already in the set.
int PySmallPtrSet_Insert(PySmallPtrSet *, PyObject *);

/// Erase - If the set contains the specified pointer, remove it and return
/// 1, otherwise return 0.
int PySmallPtrSet_Erase(PySmallPtrSet *, PyObject *);

/// Get the size of the set.
unsigned PySmallPtrSet_Size(PySmallPtrSet *);

/// Count - Return 1 if the specified pointer is in the set.
int PySmallPtrSet_Count(PySmallPtrSet *, PyObject *);

// Iterating over a C++ collection from C is a major pain in the ass, so we do
// this: given a function pointer, call it once for each element in the set.
// An optional void * can be given, which will be provided as a second
// argument to the callback.
void PySmallPtrSet_ForEach(PySmallPtrSet *, PySmallPtrSetCallback, void *);


#ifdef __cplusplus
}
#endif

#endif  // UTIL_PYSMALLPTRSET_H
