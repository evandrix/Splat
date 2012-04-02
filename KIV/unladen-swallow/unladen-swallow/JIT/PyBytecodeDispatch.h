// -*- C++ -*-
#ifndef UTIL_PYBYTECODEDISPATCH_H
#define UTIL_PYBYTECODEDISPATCH_H

#ifndef __cplusplus
#error This header expects to be included only in C++ source
#endif

namespace llvm {
    class BasicBlock;
}

namespace py {

class LlvmFunctionBuilder;

// This class handles dispatching opcodes by calling their
// implementations in JIT/opcodes/*.  If you want to replace a opcode
// implementation, subclass PyBytecodeDispatch and override the
// corresponding method.
//
// The opcode methods are not yet virtualized for performance reasons.
class PyBytecodeDispatch {
public:
    PyBytecodeDispatch(LlvmFunctionBuilder *fbuilder);

    /// The following methods operate like the opcodes with the same
    /// name.
    void LOAD_CONST(int index);
    void LOAD_FAST(int index);
    void STORE_FAST(int index);
    void DELETE_FAST(int index);

    void SETUP_LOOP(llvm::BasicBlock *target, int target_opindex,
                    llvm::BasicBlock *fallthrough);
    void GET_ITER();
    void FOR_ITER(llvm::BasicBlock *target,
                  llvm::BasicBlock *fallthrough);
    void POP_BLOCK();

    void SETUP_EXCEPT(llvm::BasicBlock *target, int target_opindex,
                      llvm::BasicBlock *fallthrough);
    void SETUP_FINALLY(llvm::BasicBlock *target, int target_opindex,
                       llvm::BasicBlock *fallthrough);
    void END_FINALLY();
    void WITH_CLEANUP();

    void JUMP_FORWARD(llvm::BasicBlock *target,
                      llvm::BasicBlock *fallthrough);
    void JUMP_ABSOLUTE(llvm::BasicBlock *target,
                       llvm::BasicBlock *fallthrough);

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
    void CONTINUE_LOOP(llvm::BasicBlock *target,
                       int target_opindex,
                       llvm::BasicBlock *fallthrough);

    void BREAK_LOOP();
    void RETURN_VALUE();
    void YIELD_VALUE();

    void POP_TOP();
    void DUP_TOP();
    void DUP_TOP_TWO();
    void DUP_TOP_THREE();
    void ROT_TWO();
    void ROT_THREE();
    void ROT_FOUR();

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

    void UNARY_CONVERT();
    void UNARY_INVERT();
    void UNARY_POSITIVE();
    void UNARY_NEGATIVE();
    void UNARY_NOT();

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
    void STORE_SUBSCR();
    void DELETE_SUBSCR();
    void STORE_MAP();
    void LIST_APPEND();
    void IMPORT_NAME();

    void COMPARE_OP(int cmp_op);

    void CALL_FUNCTION(int num_args);
    void CALL_METHOD(int num_args);
    void CALL_FUNCTION_VAR(int num_args);
    void CALL_FUNCTION_KW(int num_args);
    void CALL_FUNCTION_VAR_KW(int num_args);

    void BUILD_TUPLE(int size);
    void BUILD_LIST(int size);
    void BUILD_MAP(int size);
    void BUILD_SLICE_TWO();
    void BUILD_SLICE_THREE();
    void UNPACK_SEQUENCE(int size);

    void LOAD_GLOBAL(int index);
    void STORE_GLOBAL(int index);
    void DELETE_GLOBAL(int index);

    void LOAD_NAME(int index);
    void STORE_NAME(int index);
    void DELETE_NAME(int index);

    void LOAD_ATTR(int index);
    void LOAD_METHOD(int index);
    void STORE_ATTR(int index);
    void DELETE_ATTR(int index);

    void LOAD_CLOSURE(int freevar_index);
    void MAKE_CLOSURE(int num_defaults);
    void LOAD_DEREF(int index);
    void STORE_DEREF(int index);

    void RAISE_VARARGS_ZERO();
    void RAISE_VARARGS_ONE();
    void RAISE_VARARGS_TWO();
    void RAISE_VARARGS_THREE();

private:
    LlvmFunctionBuilder *fbuilder_;
};

}

#endif  // UTIL_PYBYTECODEDISPATCH_H
