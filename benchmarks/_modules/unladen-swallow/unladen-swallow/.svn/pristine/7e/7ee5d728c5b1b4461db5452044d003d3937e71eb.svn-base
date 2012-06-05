#include "Python.h"

#include "JIT/opcodes/name.h"
#include "JIT/llvm_fbuilder.h"

#include "llvm/BasicBlock.h"
#include "llvm/Function.h"
#include "llvm/Instructions.h"

using llvm::BasicBlock;
using llvm::ConstantInt;
using llvm::Function;
using llvm::Type;
using llvm::Value;

namespace py {

OpcodeName::OpcodeName(LlvmFunctionBuilder *fbuilder) :
    fbuilder_(fbuilder), state_(fbuilder->state())
{
}

void
OpcodeName::LOAD_NAME(int index)
{
    Value *result = this->state_->CreateCall(
        this->state_->GetGlobalFunction<PyObject *(PyFrameObject*, int)>(
            "_PyEval_LoadName"),
        this->fbuilder_->frame(),
        ConstantInt::get(
            PyTypeBuilder<int>::get(this->fbuilder_->context()), index));
    this->fbuilder_->PropagateExceptionOnNull(result);
    this->fbuilder_->Push(result);
}

void
OpcodeName::STORE_NAME(int index)
{
    Value *to_store = this->fbuilder_->Pop();
    Value *err = this->state_->CreateCall(
        this->state_->GetGlobalFunction<int(PyFrameObject*, int, PyObject*)>(
            "_PyEval_StoreName"),
        this->fbuilder_->frame(),
        ConstantInt::get(
            PyTypeBuilder<int>::get(this->fbuilder_->context()), index),
        to_store);
    this->fbuilder_->PropagateExceptionOnNonZero(err);
}

void
OpcodeName::DELETE_NAME(int index)
{
    Value *err = this->state_->CreateCall(
        this->state_->GetGlobalFunction<int(PyFrameObject*, int)>(
            "_PyEval_DeleteName"),
        this->fbuilder_->frame(),
        ConstantInt::get(
            PyTypeBuilder<int>::get(this->fbuilder_->context()), index));
    this->fbuilder_->PropagateExceptionOnNonZero(err);
}

}
