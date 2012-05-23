// -*- C++ -*-
#ifndef OPCODE_CALL_H_
#define OPCODE_CALL_H_

#ifndef __cplusplus
#error This header expects to be included only in C++ source
#endif

#include "llvm/Support/IRBuilder.h"
#include "llvm/Support/TargetFolder.h"

namespace py {

class LlvmFunctionBuilder;
class LlvmFunctionState;

// This class contains the implementation of all CALL_FUNCTION* opcodes.
class OpcodeCall
{
public:
    OpcodeCall(LlvmFunctionBuilder *fbuilder);

    void CALL_FUNCTION(int num_args);
    void CALL_METHOD(int num_args);
    void CALL_FUNCTION_VAR(int num_args);
    void CALL_FUNCTION_KW(int num_args);
    void CALL_FUNCTION_VAR_KW(int num_args);

private:
    typedef llvm::IRBuilder<true, llvm::TargetFolder> BuilderT;

    // Helper method for CALL_FUNCTION_(VAR|KW|VAR_KW); calls
    // _PyEval_CallFunctionVarKw() with the given flags and the current
    // stack pointer.
    void CallVarKwFunction(int num_args, int call_flag);

    // CALL_FUNCTION comes in two flavors: CALL_FUNCTION_safe is guaranteed to
    // work, while CALL_FUNCTION_fast takes advantage of data gathered while
    // running through the eval loop to omit as much flexibility as possible.
    void CALL_FUNCTION_safe(int num_args);
    bool CALL_FUNCTION_fast(int num_args);

    // Specialized version of CALL_FUNCTION for len() on certain types.
    void CALL_FUNCTION_fast_len(llvm::Value *actual_func,
                                llvm::Value *stack_pointer,
                                llvm::BasicBlock *invalid_assumptions,
                                const char *function_name);

    LlvmFunctionBuilder *fbuilder_;
    LlvmFunctionState *state_;
    BuilderT &builder_;
    PyGlobalLlvmData *const llvm_data_;
};

}

#endif /* OPCODE_CALL_H_ */
