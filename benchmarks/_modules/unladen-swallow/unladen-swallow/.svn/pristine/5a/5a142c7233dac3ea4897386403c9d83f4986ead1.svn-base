// -*- C++ -*-
#ifndef OPCODE_LOCALS_H_
#define OPCODE_LOCALS_H_

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

// This class includes all opcodes used to access locals.
class OpcodeLocals
{
public:
    OpcodeLocals(LlvmFunctionBuilder *fbuilder);

    void LOAD_CONST(int index);
    void LOAD_FAST(int index);
    void STORE_FAST(int index);
    void DELETE_FAST(int index);

private:
    typedef llvm::IRBuilder<true, llvm::TargetFolder> BuilderT;

    // A safe version that always works, and a fast version that omits NULL
    // checks where we know the local cannot be NULL.
    void LOAD_FAST_fast(int index);
    void LOAD_FAST_safe(int index);

    // Replaces a local variable with the PyObject* stored in
    // new_value.  Decrements the original value's refcount after
    // replacing it.
    void SetLocal(int locals_index, llvm::Value *new_value);

    LlvmFunctionBuilder *fbuilder_;
    LlvmFunctionState *state_;
    BuilderT &builder_;
};

}

#endif /* OPCODE_LOCALS_H_ */

