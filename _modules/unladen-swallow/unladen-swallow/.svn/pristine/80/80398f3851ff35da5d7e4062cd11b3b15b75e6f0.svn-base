// -*- C++ -*-
#ifndef OPCODE_GLOBALS_H_
#define OPCODE_GLOBALS_H_

#ifndef __cplusplus
#error This header expects to be included only in C++ source
#endif

#include "llvm/Support/IRBuilder.h"
#include "llvm/Support/TargetFolder.h"

namespace py {

class LlvmFunctionBuilder;
class LlvmFunctionState;

// This class includes all opcodes used to access globals.
class OpcodeGlobals
{
public:
    OpcodeGlobals(LlvmFunctionBuilder *fbuilder);

    void LOAD_GLOBAL(int index);
    void STORE_GLOBAL(int index);
    void DELETE_GLOBAL(int index);

private:
    typedef llvm::IRBuilder<true, llvm::TargetFolder> BuilderT;

    /* LOAD_GLOBAL comes in two flavors: the safe version (a port of the eval
       loop that's guaranteed to work) and a fast version, which uses dict
       versioning to cache pointers as immediates in the generated IR. */
    void LOAD_GLOBAL_fast(int index);
    void LOAD_GLOBAL_safe(int index);

    LlvmFunctionBuilder *fbuilder_;
    LlvmFunctionState *state_;
    BuilderT &builder_;
};

}

#endif /* OPCODE_GLOBALS_H_ */
