#include "Python.h"
#include "opcode.h"

#include "JIT/PyBytecodeDispatch.h"
#include "JIT/llvm_fbuilder.h"

#include "JIT/opcodes/attributes.h"
#include "JIT/opcodes/binops.h"
#include "JIT/opcodes/block.h"
#include "JIT/opcodes/call.h"
#include "JIT/opcodes/closure.h"
#include "JIT/opcodes/cmpops.h"
#include "JIT/opcodes/container.h"
#include "JIT/opcodes/control.h"
#include "JIT/opcodes/globals.h"
#include "JIT/opcodes/locals.h"
#include "JIT/opcodes/loop.h"
#include "JIT/opcodes/name.h"
#include "JIT/opcodes/slice.h"
#include "JIT/opcodes/stack.h"
#include "JIT/opcodes/unaryops.h"

#include "llvm/BasicBlock.h"

using llvm::BasicBlock;

namespace py {

PyBytecodeDispatch::PyBytecodeDispatch(LlvmFunctionBuilder *fbuilder) :
    fbuilder_(fbuilder)
{
}

void
PyBytecodeDispatch::LOAD_CONST(int index)
{
    OpcodeLocals locals(fbuilder_);
    locals.LOAD_CONST(index);
}

void
PyBytecodeDispatch::LOAD_GLOBAL(int name_index)
{
    OpcodeGlobals globals(fbuilder_);
    globals.LOAD_GLOBAL(name_index);
}

void
PyBytecodeDispatch::STORE_GLOBAL(int name_index)
{
    OpcodeGlobals globals(fbuilder_);
    globals.STORE_GLOBAL(name_index);
}

void
PyBytecodeDispatch::DELETE_GLOBAL(int name_index)
{
    OpcodeGlobals globals(fbuilder_);
    globals.DELETE_GLOBAL(name_index);
}

void
PyBytecodeDispatch::LOAD_NAME(int index)
{
    OpcodeName name(fbuilder_);
    name.LOAD_NAME(index);
}

void
PyBytecodeDispatch::STORE_NAME(int index)
{
    OpcodeName name(fbuilder_);
    name.STORE_NAME(index);
}

void
PyBytecodeDispatch::DELETE_NAME(int index)
{
    OpcodeName name(fbuilder_);
    name.DELETE_NAME(index);
}

void
PyBytecodeDispatch::LOAD_ATTR(int names_index)
{
    OpcodeAttributes attr(fbuilder_);
    attr.LOAD_ATTR(names_index);
}

void
PyBytecodeDispatch::LOAD_METHOD(int names_index)
{
    OpcodeAttributes attr(fbuilder_);
    attr.LOAD_METHOD(names_index);
}

void
PyBytecodeDispatch::STORE_ATTR(int names_index)
{
    OpcodeAttributes attr(fbuilder_);
    attr.STORE_ATTR(names_index);
}

void
PyBytecodeDispatch::DELETE_ATTR(int index)
{
    OpcodeAttributes attr(fbuilder_);
    attr.DELETE_ATTR(index);
}

void
PyBytecodeDispatch::LOAD_FAST(int index)
{
    OpcodeLocals locals(fbuilder_);
    locals.LOAD_FAST(index);
}

void
PyBytecodeDispatch::WITH_CLEANUP()
{
    OpcodeBlock block(fbuilder_);
    block.WITH_CLEANUP();
}

void
PyBytecodeDispatch::LOAD_CLOSURE(int freevars_index)
{
    OpcodeClosure closure(fbuilder_);
    closure.LOAD_CLOSURE(freevars_index);
}

void
PyBytecodeDispatch::MAKE_CLOSURE(int num_defaults)
{
    OpcodeClosure closure(fbuilder_);
    closure.MAKE_CLOSURE(num_defaults);
}

void
PyBytecodeDispatch::CALL_FUNCTION(int oparg)
{
    OpcodeCall call(fbuilder_);
    call.CALL_FUNCTION(oparg);
}

void
PyBytecodeDispatch::CALL_METHOD(int oparg)
{
    OpcodeCall call(fbuilder_);
    call.CALL_METHOD(oparg);
}

void
PyBytecodeDispatch::CALL_FUNCTION_VAR(int oparg)
{
    OpcodeCall call(fbuilder_);
    call.CALL_FUNCTION_VAR(oparg);
}

void
PyBytecodeDispatch::CALL_FUNCTION_KW(int oparg)
{
    OpcodeCall call(fbuilder_);
    call.CALL_FUNCTION_KW(oparg);
}

void
PyBytecodeDispatch::CALL_FUNCTION_VAR_KW(int oparg)
{
    OpcodeCall call(fbuilder_);
    call.CALL_FUNCTION_VAR_KW(oparg);
}

void
PyBytecodeDispatch::IMPORT_NAME()
{
    OpcodeContainer cont(fbuilder_);
    cont.IMPORT_NAME();
}

void
PyBytecodeDispatch::LOAD_DEREF(int index)
{
    OpcodeClosure closure(fbuilder_);
    closure.LOAD_DEREF(index);
}

void
PyBytecodeDispatch::STORE_DEREF(int index)
{
    OpcodeClosure closure(fbuilder_);
    closure.STORE_DEREF(index);
}

void
PyBytecodeDispatch::JUMP_FORWARD(llvm::BasicBlock *target,
                                 llvm::BasicBlock *fallthrough)
{
    OpcodeControl control(fbuilder_);
    control.JUMP_FORWARD(target, fallthrough);
}

void
PyBytecodeDispatch::JUMP_ABSOLUTE(llvm::BasicBlock *target,
                                  llvm::BasicBlock *fallthrough)
{
    OpcodeControl control(fbuilder_);
    control.JUMP_ABSOLUTE(target, fallthrough);
}

void
PyBytecodeDispatch::POP_JUMP_IF_FALSE(unsigned target_idx,
                                      unsigned fallthrough_idx,
                                      BasicBlock *target,
                                      BasicBlock *fallthrough)
{
    OpcodeControl control(fbuilder_);
    control.POP_JUMP_IF_FALSE(target_idx, fallthrough_idx,
                              target, fallthrough);
}

void
PyBytecodeDispatch::POP_JUMP_IF_TRUE(unsigned target_idx,
                                     unsigned fallthrough_idx,
                                     BasicBlock *target,
                                     BasicBlock *fallthrough)
{
    OpcodeControl control(fbuilder_);
    control.POP_JUMP_IF_TRUE(target_idx, fallthrough_idx,
                             target, fallthrough);
}

void
PyBytecodeDispatch::JUMP_IF_FALSE_OR_POP(unsigned target_idx,
                                         unsigned fallthrough_idx,
                                         BasicBlock *target,
                                         BasicBlock *fallthrough)
{
    OpcodeControl control(fbuilder_);
    control.JUMP_IF_FALSE_OR_POP(target_idx, fallthrough_idx,
                                 target, fallthrough);
}

void
PyBytecodeDispatch::JUMP_IF_TRUE_OR_POP(unsigned target_idx,
                                        unsigned fallthrough_idx,
                                        BasicBlock *target,
                                        BasicBlock *fallthrough)
{
    OpcodeControl control(fbuilder_);
    control.JUMP_IF_TRUE_OR_POP(target_idx, fallthrough_idx,
                                target, fallthrough);
}

void
PyBytecodeDispatch::STORE_FAST(int index)
{
    OpcodeLocals locals(fbuilder_);
    locals.STORE_FAST(index);
}

void
PyBytecodeDispatch::DELETE_FAST(int index)
{
    OpcodeLocals locals(fbuilder_);
    locals.DELETE_FAST(index);
}

void
PyBytecodeDispatch::SETUP_LOOP(llvm::BasicBlock *target,
                               int target_opindex,
                               llvm::BasicBlock *fallthrough)
{
    OpcodeBlock block(fbuilder_);
    block.SETUP_LOOP(target, target_opindex, fallthrough);
}

void
PyBytecodeDispatch::GET_ITER()
{
    OpcodeLoop loop(fbuilder_);
    loop.GET_ITER();
}

void
PyBytecodeDispatch::FOR_ITER(llvm::BasicBlock *target,
                             llvm::BasicBlock *fallthrough)
{
    OpcodeLoop loop(fbuilder_);
    loop.FOR_ITER(target, fallthrough);
}

void
PyBytecodeDispatch::POP_BLOCK()
{
    OpcodeBlock block(fbuilder_);
    block.POP_BLOCK();
}

void
PyBytecodeDispatch::SETUP_EXCEPT(llvm::BasicBlock *target,
                                 int target_opindex,
                                 llvm::BasicBlock *fallthrough)
{
    OpcodeBlock block(fbuilder_);
    block.SETUP_EXCEPT(target, target_opindex, fallthrough);
}

void
PyBytecodeDispatch::SETUP_FINALLY(llvm::BasicBlock *target,
                                  int target_opindex,
                                  llvm::BasicBlock *fallthrough)
{
    OpcodeBlock block(fbuilder_);
    block.SETUP_FINALLY(target, target_opindex, fallthrough);
}

void
PyBytecodeDispatch::END_FINALLY()
{
    OpcodeBlock block(fbuilder_);
    block.END_FINALLY();
}

void
PyBytecodeDispatch::CONTINUE_LOOP(llvm::BasicBlock *target,
                                  int target_opindex,
                                  llvm::BasicBlock *fallthrough)
{
    OpcodeLoop loop(fbuilder_);
    loop.CONTINUE_LOOP(target, target_opindex, fallthrough);
}

void
PyBytecodeDispatch::BREAK_LOOP()
{
    OpcodeLoop loop(fbuilder_);
    loop.BREAK_LOOP();
}

void
PyBytecodeDispatch::RETURN_VALUE()
{
    OpcodeControl control(fbuilder_);
    control.RETURN_VALUE();
}

void
PyBytecodeDispatch::YIELD_VALUE()
{
    OpcodeControl control(fbuilder_);
    control.YIELD_VALUE();
}

void
PyBytecodeDispatch::RAISE_VARARGS_ZERO()
{
    OpcodeControl control(fbuilder_);
    control.RAISE_VARARGS_ZERO();
}

void
PyBytecodeDispatch::RAISE_VARARGS_ONE()
{
    OpcodeControl control(fbuilder_);
    control.RAISE_VARARGS_ONE();
}

void
PyBytecodeDispatch::RAISE_VARARGS_TWO()
{
    OpcodeControl control(fbuilder_);
    control.RAISE_VARARGS_TWO();
}

void
PyBytecodeDispatch::RAISE_VARARGS_THREE()
{
    OpcodeControl control(fbuilder_);
    control.RAISE_VARARGS_THREE();
}

void
PyBytecodeDispatch::STORE_SUBSCR()
{
    OpcodeContainer cont(fbuilder_);
    cont.STORE_SUBSCR();
}

void
PyBytecodeDispatch::DELETE_SUBSCR()
{
    OpcodeContainer cont(fbuilder_);
    cont.DELETE_SUBSCR();
}

#define BINOP_METH(OPCODE)              \
void                                    \
PyBytecodeDispatch::OPCODE()            \
{                                       \
    OpcodeBinops binops(fbuilder_);     \
    binops.OPCODE();                    \
}

BINOP_METH(BINARY_ADD)
BINOP_METH(BINARY_SUBTRACT)
BINOP_METH(BINARY_MULTIPLY)
BINOP_METH(BINARY_DIVIDE)
BINOP_METH(BINARY_MODULO)
BINOP_METH(BINARY_SUBSCR)

BINOP_METH(BINARY_TRUE_DIVIDE)
BINOP_METH(BINARY_LSHIFT)
BINOP_METH(BINARY_RSHIFT)
BINOP_METH(BINARY_OR)
BINOP_METH(BINARY_XOR)
BINOP_METH(BINARY_AND)
BINOP_METH(BINARY_FLOOR_DIVIDE)

BINOP_METH(INPLACE_ADD)
BINOP_METH(INPLACE_SUBTRACT)
BINOP_METH(INPLACE_MULTIPLY)
BINOP_METH(INPLACE_TRUE_DIVIDE)
BINOP_METH(INPLACE_DIVIDE)
BINOP_METH(INPLACE_MODULO)
BINOP_METH(INPLACE_LSHIFT)
BINOP_METH(INPLACE_RSHIFT)
BINOP_METH(INPLACE_OR)
BINOP_METH(INPLACE_XOR)
BINOP_METH(INPLACE_AND)
BINOP_METH(INPLACE_FLOOR_DIVIDE)

#undef BINOP_METH

void
PyBytecodeDispatch::BINARY_POWER()
{
    OpcodeBinops binops(fbuilder_);
    binops.BINARY_POWER();
}

void
PyBytecodeDispatch::INPLACE_POWER()
{
    OpcodeBinops binops(fbuilder_);
    binops.INPLACE_POWER();
}

#define UNARYOP_METH(NAME)                              \
void							\
PyBytecodeDispatch::NAME()				\
{							\
    OpcodeUnaryops unary(fbuilder_);                    \
    unary.NAME();                                       \
}

UNARYOP_METH(UNARY_CONVERT)
UNARYOP_METH(UNARY_INVERT)
UNARYOP_METH(UNARY_POSITIVE)
UNARYOP_METH(UNARY_NEGATIVE)
UNARYOP_METH(UNARY_NOT)
#undef UNARYOP_METH

void
PyBytecodeDispatch::POP_TOP()
{
    OpcodeStack stack(fbuilder_);
    stack.POP_TOP();
}

void
PyBytecodeDispatch::DUP_TOP()
{
    OpcodeStack stack(fbuilder_);
    stack.DUP_TOP();
}

void
PyBytecodeDispatch::DUP_TOP_TWO()
{
    OpcodeStack stack(fbuilder_);
    stack.DUP_TOP_TWO();
}

void
PyBytecodeDispatch::DUP_TOP_THREE()
{
    OpcodeStack stack(fbuilder_);
    stack.DUP_TOP_THREE();
}

void
PyBytecodeDispatch::ROT_TWO()
{
    OpcodeStack stack(fbuilder_);
    stack.ROT_TWO();
}

void
PyBytecodeDispatch::ROT_THREE()
{
    OpcodeStack stack(fbuilder_);
    stack.ROT_THREE();
}

void
PyBytecodeDispatch::ROT_FOUR()
{
    OpcodeStack stack(fbuilder_);
    stack.ROT_FOUR();
}

void
PyBytecodeDispatch::COMPARE_OP(int cmp_op)
{
    OpcodeCmpops cmpops(fbuilder_);
    cmpops.COMPARE_OP(cmp_op);
}

void
PyBytecodeDispatch::LIST_APPEND()
{
    OpcodeContainer cont(fbuilder_);
    cont.LIST_APPEND();
}

void
PyBytecodeDispatch::STORE_MAP()
{
    OpcodeContainer cont(fbuilder_);
    cont.STORE_MAP();
}

void
PyBytecodeDispatch::BUILD_LIST(int size)
{
    OpcodeContainer cont(fbuilder_);
    cont.BUILD_LIST(size);
}

void
PyBytecodeDispatch::BUILD_TUPLE(int size)
{
    OpcodeContainer cont(fbuilder_);
    cont.BUILD_TUPLE(size);
}

void
PyBytecodeDispatch::BUILD_MAP(int size)
{
    OpcodeContainer cont(fbuilder_);
    cont.BUILD_MAP(size);
}

void
PyBytecodeDispatch::SLICE_BOTH()
{
    OpcodeSlice slice(fbuilder_);
    slice.SLICE_BOTH();
}

void
PyBytecodeDispatch::SLICE_LEFT()
{
    OpcodeSlice slice(fbuilder_);
    slice.SLICE_LEFT();
}

void
PyBytecodeDispatch::SLICE_RIGHT()
{
    OpcodeSlice slice(fbuilder_);
    slice.SLICE_RIGHT();
}

void
PyBytecodeDispatch::SLICE_NONE()
{
    OpcodeSlice slice(fbuilder_);
    slice.SLICE_NONE();
}

void
PyBytecodeDispatch::STORE_SLICE_BOTH()
{
    OpcodeSlice slice(fbuilder_);
    slice.STORE_SLICE_BOTH();
}

void
PyBytecodeDispatch::STORE_SLICE_LEFT()
{
    OpcodeSlice slice(fbuilder_);
    slice.STORE_SLICE_LEFT();
}

void
PyBytecodeDispatch::STORE_SLICE_RIGHT()
{
    OpcodeSlice slice(fbuilder_);
    slice.STORE_SLICE_RIGHT();
}

void
PyBytecodeDispatch::STORE_SLICE_NONE()
{
    OpcodeSlice slice(fbuilder_);
    slice.STORE_SLICE_NONE();
}

void
PyBytecodeDispatch::DELETE_SLICE_BOTH()
{
    OpcodeSlice slice(fbuilder_);
    slice.DELETE_SLICE_BOTH();
}

void
PyBytecodeDispatch::DELETE_SLICE_LEFT()
{
    OpcodeSlice slice(fbuilder_);
    slice.DELETE_SLICE_LEFT();
}

void
PyBytecodeDispatch::DELETE_SLICE_RIGHT()
{
    OpcodeSlice slice(fbuilder_);
    slice.DELETE_SLICE_RIGHT();
}

void
PyBytecodeDispatch::DELETE_SLICE_NONE()
{
    OpcodeSlice slice(fbuilder_);
    slice.DELETE_SLICE_NONE();
}

void
PyBytecodeDispatch::BUILD_SLICE_TWO()
{
    OpcodeSlice slice(fbuilder_);
    slice.BUILD_SLICE_TWO();
}

void
PyBytecodeDispatch::BUILD_SLICE_THREE()
{
    OpcodeSlice slice(fbuilder_);
    slice.BUILD_SLICE_THREE();
}

void
PyBytecodeDispatch::UNPACK_SEQUENCE(int size)
{
    OpcodeContainer cont(fbuilder_);
    cont.UNPACK_SEQUENCE(size);
}

}
