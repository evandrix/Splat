// -*- C++ -*-
#ifndef OPCODE_CONTROL_H_
#define OPCODE_CONTROL_H_

#ifndef __cplusplus
#error This header expects to be included only in C++ source
#endif

#include "llvm/Support/IRBuilder.h"
#include "llvm/Support/TargetFolder.h"

namespace llvm {
    class BasicBlock;
    class Value;
}

namespace py {

class LlvmFunctionBuilder;
class LlvmFunctionState;

// This class contains most control flow opcodes.
// break and continue can be found in OpcodeLoop.
class OpcodeControl
{
public:
    OpcodeControl(LlvmFunctionBuilder *fbuilder);

    void RAISE_VARARGS_ZERO();
    void RAISE_VARARGS_ONE();
    void RAISE_VARARGS_TWO();
    void RAISE_VARARGS_THREE();

    void RETURN_VALUE();
    void YIELD_VALUE();

    void JUMP_FORWARD(llvm::BasicBlock *target, llvm::BasicBlock *fallthrough) {
        this->JUMP_ABSOLUTE(target, fallthrough);
    }
    void JUMP_ABSOLUTE(llvm::BasicBlock *target, llvm::BasicBlock *fallthrough);

    void POP_JUMP_IF_FALSE(unsigned target_idx,
                           unsigned fallthrough_idx,
                           llvm::BasicBlock *target,
                           llvm::BasicBlock *fallthrough);
    void POP_JUMP_IF_TRUE(unsigned target_idx,
                          unsigned fallthrough_idx,
                          llvm::BasicBlock *target,
                          llvm::BasicBlock *fallthrough);
    void JUMP_IF_FALSE_OR_POP(unsigned target_idx,
                              unsigned fallthrough_idx,
                              llvm::BasicBlock *target,
                              llvm::BasicBlock *fallthrough);
    void JUMP_IF_TRUE_OR_POP(unsigned target_idx,
                             unsigned fallthrough_idx,
                             llvm::BasicBlock *target,
                             llvm::BasicBlock *fallthrough);

private:
    typedef llvm::IRBuilder<true, llvm::TargetFolder> BuilderT;

    // Set exception information and jump to exception handling. The
    // arguments can be Value*'s representing NULL to implement the
    // four forms of the 'raise' statement. Steals all references.
    void DoRaise(llvm::Value *exc_type, llvm::Value *exc_inst,
                 llvm::Value *exc_tb);

    // Helper function for the POP_JUMP_IF_{TRUE,FALSE} and
    // JUMP_IF_{TRUE,FALSE}_OR_POP, used for omitting untake branches.
    // If sufficient data is availble, we made decide to omit one side of a
    // conditional branch, replacing that code with a jump to the interpreter.
    // If sufficient data is available:
    //      - set true_block or false_block to a bail-to-interpreter block.
    //      - set bail_idx and bail_block to handle bailing.
    // If sufficient data is available or we decide not to optimize:
    //      - leave true_block and false_block alone.
    //      - bail_idx will be 0, bail_block will be NULL.
    //
    // Out parameters: true_block, false_block, bail_idx, bail_block.
    void GetPyCondBranchBailBlock(unsigned true_idx,
                                  llvm::BasicBlock **true_block,
                                  unsigned false_idx,
                                  llvm::BasicBlock **false_block,
                                  unsigned *bail_idx,
                                  llvm::BasicBlock **bail_block);

    // Helper function for the POP_JUMP_IF_{TRUE,FALSE} and
    // JUMP_IF_{TRUE,FALSE}_OR_POP. Fill in the bail block for these opcodes
    // that was obtained from GetPyCondBranchBailBlock().
    void FillPyCondBranchBailBlock(llvm::BasicBlock *bail_to,
                                   unsigned bail_idx);

    LlvmFunctionBuilder *fbuilder_;
    LlvmFunctionState *state_;
    BuilderT &builder_;
};

}

#endif /* OPCODE_CONTROL_H_ */
