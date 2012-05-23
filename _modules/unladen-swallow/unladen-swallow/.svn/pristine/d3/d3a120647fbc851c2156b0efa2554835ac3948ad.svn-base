// -*- C++ -*-
#ifndef OPCODE_BINOPS_H_
#define OPCODE_BINOPS_H_

#ifndef __cplusplus
#error This header expects to be included only in C++ source
#endif

#include "Python.h"

namespace py {

class LlvmFunctionBuilder;
class LlvmFunctionState;

// This class includes all opcodes involving binary operators.
class OpcodeBinops
{
public:
    OpcodeBinops(LlvmFunctionBuilder *fbuilder);

    void BINARY_ADD();
    void BINARY_SUBTRACT();
    void BINARY_MULTIPLY();
    void BINARY_TRUE_DIVIDE();
    void BINARY_DIVIDE();
    void BINARY_MODULO();
    void BINARY_POWER();
    void BINARY_LSHIFT();
    void BINARY_RSHIFT();
    void BINARY_OR();
    void BINARY_XOR();
    void BINARY_AND();
    void BINARY_FLOOR_DIVIDE();
    void BINARY_SUBSCR();

    void INPLACE_ADD();
    void INPLACE_SUBTRACT();
    void INPLACE_MULTIPLY();
    void INPLACE_TRUE_DIVIDE();
    void INPLACE_DIVIDE();
    void INPLACE_MODULO();
    void INPLACE_POWER();
    void INPLACE_LSHIFT();
    void INPLACE_RSHIFT();
    void INPLACE_OR();
    void INPLACE_XOR();
    void INPLACE_AND();
    void INPLACE_FLOOR_DIVIDE();

#ifdef Py_WITH_INSTRUMENTATION
    static void IncStatsOptimized();
    static void IncStatsOmitted();
    static void IncStatsTotal();
#else
    static void IncStatsOptimized() {}
    static void IncStatsOmitted() {}
    static void IncStatsTotal() {}
#endif /* Py_WITH_INSTRUMENTATION */

private:
    // Helper methods for binary and unary operators, passing the name
    // of the Python/C API function that implements the operation.
    // GenericBinOp's apifunc is "PyObject *(*)(PyObject *, PyObject *)"
    void GenericBinOp(const char *apifunc);
    // Like GenericBinOp(), but uses an optimized version if available.
    void OptimizedBinOp(const char *apifunc);
    // GenericPowOp's is "PyObject *(*)(PyObject *, PyObject *, PyObject *)"
    void GenericPowOp(const char *apifunc);

    LlvmFunctionBuilder *fbuilder_;
    LlvmFunctionState *state_;
};

}

#endif /* OPCODE_BINOPS_H_ */
