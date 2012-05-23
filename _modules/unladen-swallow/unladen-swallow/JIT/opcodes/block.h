// -*- C++ -*-
#ifndef OPCODE_BLOCK_H_
#define OPCODE_BLOCK_H_

#ifndef __cplusplus
#error This header expects to be included only in C++ source
#endif

#include "llvm/Support/IRBuilder.h"
#include "llvm/Support/TargetFolder.h"

namespace llvm {
    class BasicBlock;
}

namespace py {

class LlvmFunctionBuilder;
class LlvmFunctionState;

// This class contains all opcodes which manipulate the blockstack.
class OpcodeBlock
{
public:
    OpcodeBlock(LlvmFunctionBuilder *fbuilder);

    void SETUP_LOOP(llvm::BasicBlock *target, int target_opindex,
                    llvm::BasicBlock *fallthrough);

    void POP_BLOCK();

    void SETUP_EXCEPT(llvm::BasicBlock *target, int target_opindex,
                      llvm::BasicBlock *fallthrough);
    void SETUP_FINALLY(llvm::BasicBlock *target, int target_opindex,
                       llvm::BasicBlock *fallthrough);
    void END_FINALLY();
    void WITH_CLEANUP();
    
private:
    typedef llvm::IRBuilder<true, llvm::TargetFolder> BuilderT;

    // Adds handler to the switch for unwind targets and then sets up
    // a call to PyFrame_BlockSetup() with the block type, handler
    // index, and current stack level.
    void CallBlockSetup(int block_type,
                        llvm::BasicBlock *handler, int handler_opindex);

    LlvmFunctionBuilder *fbuilder_;
    LlvmFunctionState *state_;
    BuilderT &builder_;
    PyGlobalLlvmData *const llvm_data_;
};

}

#endif /* OPCODE_BLOCK_H_ */
