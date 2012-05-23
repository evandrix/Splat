// -*- C++ -*-
#ifndef OPCODE_CLOSURE_H_
#define OPCODE_CLOSURE_H_

#ifndef __cplusplus
#error This header expects to be included only in C++ source
#endif

#include "llvm/Support/IRBuilder.h"
#include "llvm/Support/TargetFolder.h"

namespace py {

class LlvmFunctionBuilder;
class LlvmFunctionState;

// This class contains all opcodes related to closures.
class OpcodeClosure
{
public:
    OpcodeClosure(LlvmFunctionBuilder *fbuilder);

    void LOAD_CLOSURE(int freevar_index);
    void MAKE_CLOSURE(int num_defaults);
    void LOAD_DEREF(int index);
    void STORE_DEREF(int index);

private:
    typedef llvm::IRBuilder<true, llvm::TargetFolder> BuilderT;

    LlvmFunctionBuilder *fbuilder_;
    LlvmFunctionState *state_;
    BuilderT &builder_;
    PyGlobalLlvmData *const llvm_data_;
};

}

#endif /* OPCODE_CLOSURE_H_ */
