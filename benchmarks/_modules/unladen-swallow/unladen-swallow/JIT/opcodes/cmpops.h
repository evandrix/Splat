// -*- C++ -*-
#ifndef OPCODE_CMPOPS_H_
#define OPCODE_CMPOPS_H_

#ifndef __cplusplus
#error This header expects to be included only in C++ source
#endif

#include "llvm/Support/IRBuilder.h"
#include "llvm/Support/TargetFolder.h"

namespace llvm {
    class Value;
}

namespace py {

class LlvmFunctionBuilder;
class LlvmFunctionState;

// This class includes all code to implement the compare opcode.
class OpcodeCmpops
{
public:
    OpcodeCmpops(LlvmFunctionBuilder *fbuilder);

    void COMPARE_OP(int cmp_op);

private:
    typedef llvm::IRBuilder<true, llvm::TargetFolder> BuilderT;

    bool COMPARE_OP_fast(int cmp_op,
                         const PyTypeObject *lhs_type,
                         const PyTypeObject *rhs_type);
    void COMPARE_OP_safe(int cmp_op);

    // Call PyObject_RichCompare(lhs, rhs, cmp_op), pushing the result
    // onto the stack. cmp_op is one of Py_EQ, Py_NE, Py_LT, Py_LE, Py_GT
    // or Py_GE as defined in Python/object.h. Steals both references.
    void RichCompare(llvm::Value *lhs, llvm::Value *rhs, int cmp_op);

    // Call PySequence_Contains(seq, item), returning the result as an i1.
    // Steals both references.
    llvm::Value *ContainerContains(llvm::Value *seq, llvm::Value *item);

    // Check whether exc (a thrown exception) matches exc_type
    // (a class or tuple of classes) for the purpose of catching
    // exc in an except clause. Returns an i1. Steals both references.
    llvm::Value *ExceptionMatches(llvm::Value *exc, llvm::Value *exc_type);

    LlvmFunctionBuilder *fbuilder_;
    LlvmFunctionState *state_;
    BuilderT &builder_;
};

}

#endif /* OPCODE_CMPOPS_H_ */
