/* Forward declares some functions using PyGlobalLlvmData so that C
   files can use them.  See global_llvm_data.h for the full C++
   interface. */
#ifndef PYTHON_GLOBAL_LLVM_DATA_FWD_H
#define PYTHON_GLOBAL_LLVM_DATA_FWD_H

#include "Python.h"

#ifdef __cplusplus
extern "C" {
#endif

#ifdef WITH_LLVM
#define PyGlobalLlvmData_GET() (PyThreadState_GET()->interp->global_llvm_data)

struct PyGlobalLlvmData *PyGlobalLlvmData_New(void);
void PyGlobalLlvmData_Clear(struct PyGlobalLlvmData *);
void PyGlobalLlvmData_Free(struct PyGlobalLlvmData *);

#define Py_MIN_LLVM_OPT_LEVEL 0
#define Py_DEFAULT_JIT_OPT_LEVEL 2
#define Py_MAX_LLVM_OPT_LEVEL 3

/* See global_llvm_data.h:PyGlobalLlvmData::Optimize for documentation. */
PyAPI_FUNC(int) PyGlobalLlvmData_Optimize(struct PyGlobalLlvmData *,
                                          _LlvmFunction *, int);
/* See global_llvm_data.h:PyGlobalLlvmData::CollectUnusedGlobals. */
PyAPI_FUNC(void) PyGlobalLlvmData_CollectUnusedGlobals(
    struct PyGlobalLlvmData *);

/* Initializes LLVM and all of the LLVM wrapper types. */
int _PyLlvm_Init(void);

/* Finalizes LLVM. */
void _PyLlvm_Fini(void);

/* Sets LLVM debug output on or off. */
PyAPI_FUNC(int) PyLlvm_SetDebug(int on);
#endif  /* WITH_LLVM */

#ifdef __cplusplus
}
#endif
#endif  /* PYTHON_GLOBAL_LLVM_DATA_FWD_H */
