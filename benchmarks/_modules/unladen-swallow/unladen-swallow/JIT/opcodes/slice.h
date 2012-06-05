// -*- C++ -*-
#ifndef OPCODE_SLICE_H_
#define OPCODE_SLICE_H_

#ifndef __cplusplus
#error This header expects to be included only in C++ source
#endif

namespace llvm {
    class Value;
}

namespace py {

class LlvmFunctionBuilder;
class LlvmFunctionState;

// This class contains all opcodes related to slices.
class OpcodeSlice
{
public:
    OpcodeSlice(LlvmFunctionBuilder *fbuilder);

    void SLICE_NONE();
    void SLICE_LEFT();
    void SLICE_RIGHT();
    void SLICE_BOTH();
    void STORE_SLICE_NONE();
    void STORE_SLICE_LEFT();
    void STORE_SLICE_RIGHT();
    void STORE_SLICE_BOTH();
    void DELETE_SLICE_NONE();
    void DELETE_SLICE_LEFT();
    void DELETE_SLICE_RIGHT();
    void DELETE_SLICE_BOTH();

    void BUILD_SLICE_TWO();
    void BUILD_SLICE_THREE();

private:
    // Apply a classic slice to a sequence, pushing the result onto the
    // stack.  'start' and 'stop' can be Value*'s representing NULL to
    // indicate missing arguments, and all references are stolen.
    void ApplySlice(llvm::Value *seq, llvm::Value *start, llvm::Value *stop);
    // Assign to or delete a slice of a sequence. 'start' and 'stop' can be
    // Value*'s representing NULL to indicate missing arguments, and
    // 'source' can be a Value* representing NULL to indicate slice
    // deletion. All references are stolen.
    void AssignSlice(llvm::Value *seq, llvm::Value *start, llvm::Value *stop,
                     llvm::Value *source);

    LlvmFunctionBuilder *fbuilder_;
    LlvmFunctionState *state_;
};

}

#endif /* OPCODE_SLICE_H_ */
