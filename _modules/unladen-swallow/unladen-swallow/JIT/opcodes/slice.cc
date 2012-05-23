#include "Python.h"

#include "JIT/opcodes/slice.h"
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

OpcodeSlice::OpcodeSlice(LlvmFunctionBuilder *fbuilder) :
    fbuilder_(fbuilder), state_(fbuilder->state())
{
}

void
OpcodeSlice::AssignSlice(Value *seq, Value *start, Value *stop,
                                 Value *source)
{
    Function *assign_slice = this->state_->GetGlobalFunction<
        int (PyObject *, PyObject *, PyObject *, PyObject *)>(
            "_PyEval_AssignSlice");
    Value *result = this->state_->CreateCall(
        assign_slice, seq, start, stop, source, "ApplySlice_result");
    this->state_->XDecRef(source);
    this->state_->XDecRef(stop);
    this->state_->XDecRef(start);
    this->state_->DecRef(seq);
    this->fbuilder_->PropagateExceptionOnNonZero(result);
}

void
OpcodeSlice::ApplySlice(Value *seq, Value *start, Value *stop)
{
    Function *build_slice = this->state_->GetGlobalFunction<
        PyObject *(PyObject *, PyObject *, PyObject *)>("_PyEval_ApplySlice");
    Value *result = this->state_->CreateCall(
        build_slice, seq, start, stop, "ApplySlice_result");
    this->state_->XDecRef(stop);
    this->state_->XDecRef(start);
    this->state_->DecRef(seq);
    this->fbuilder_->PropagateExceptionOnNull(result);
    this->fbuilder_->Push(result);
}

void
OpcodeSlice::SLICE_BOTH()
{
    Value *stop = this->fbuilder_->Pop();
    Value *start = this->fbuilder_->Pop();
    Value *seq = this->fbuilder_->Pop();
    this->ApplySlice(seq, start, stop);
}

void
OpcodeSlice::SLICE_LEFT()
{
    Value *stop = this->state_->GetNull<PyObject*>();
    Value *start = this->fbuilder_->Pop();
    Value *seq = this->fbuilder_->Pop();
    this->ApplySlice(seq, start, stop);
}

void
OpcodeSlice::SLICE_RIGHT()
{
    Value *stop = this->fbuilder_->Pop();
    Value *start = this->state_->GetNull<PyObject*>();
    Value *seq = this->fbuilder_->Pop();
    this->ApplySlice(seq, start, stop);
}

void
OpcodeSlice::SLICE_NONE()
{
    Value *stop = this->state_->GetNull<PyObject*>();
    Value *start = this->state_->GetNull<PyObject*>();
    Value *seq = this->fbuilder_->Pop();
    this->ApplySlice(seq, start, stop);
}

void
OpcodeSlice::STORE_SLICE_BOTH()
{
    Value *stop = this->fbuilder_->Pop();
    Value *start = this->fbuilder_->Pop();
    Value *seq = this->fbuilder_->Pop();
    Value *source = this->fbuilder_->Pop();
    this->AssignSlice(seq, start, stop, source);
}

void
OpcodeSlice::STORE_SLICE_LEFT()
{
    Value *stop = this->state_->GetNull<PyObject*>();
    Value *start = this->fbuilder_->Pop();
    Value *seq = this->fbuilder_->Pop();
    Value *source = this->fbuilder_->Pop();
    this->AssignSlice(seq, start, stop, source);
}

void
OpcodeSlice::STORE_SLICE_RIGHT()
{
    Value *stop = this->fbuilder_->Pop();
    Value *start = this->state_->GetNull<PyObject*>();
    Value *seq = this->fbuilder_->Pop();
    Value *source = this->fbuilder_->Pop();
    this->AssignSlice(seq, start, stop, source);
}

void
OpcodeSlice::STORE_SLICE_NONE()
{
    Value *stop = this->state_->GetNull<PyObject*>();
    Value *start = this->state_->GetNull<PyObject*>();
    Value *seq = this->fbuilder_->Pop();
    Value *source = this->fbuilder_->Pop();
    this->AssignSlice(seq, start, stop, source);
}

void
OpcodeSlice::DELETE_SLICE_BOTH()
{
    Value *stop = this->fbuilder_->Pop();
    Value *start = this->fbuilder_->Pop();
    Value *seq = this->fbuilder_->Pop();
    Value *source = this->state_->GetNull<PyObject*>();
    this->AssignSlice(seq, start, stop, source);
}

void
OpcodeSlice::DELETE_SLICE_LEFT()
{
    Value *stop = this->state_->GetNull<PyObject*>();
    Value *start = this->fbuilder_->Pop();
    Value *seq = this->fbuilder_->Pop();
    Value *source = this->state_->GetNull<PyObject*>();
    this->AssignSlice(seq, start, stop, source);
}

void
OpcodeSlice::DELETE_SLICE_RIGHT()
{
    Value *stop = this->fbuilder_->Pop();
    Value *start = this->state_->GetNull<PyObject*>();
    Value *seq = this->fbuilder_->Pop();
    Value *source = this->state_->GetNull<PyObject*>();
    this->AssignSlice(seq, start, stop, source);
}

void
OpcodeSlice::DELETE_SLICE_NONE()
{
    Value *stop = this->state_->GetNull<PyObject*>();
    Value *start = this->state_->GetNull<PyObject*>();
    Value *seq = this->fbuilder_->Pop();
    Value *source = this->state_->GetNull<PyObject*>();
    this->AssignSlice(seq, start, stop, source);
}

void
OpcodeSlice::BUILD_SLICE_TWO()
{
    Value *step = this->state_->GetNull<PyObject*>();
    Value *stop = this->fbuilder_->Pop();
    Value *start = this->fbuilder_->Pop();
    Function *build_slice = this->state_->GetGlobalFunction<
        PyObject *(PyObject *, PyObject *, PyObject *)>("PySlice_New");
    Value *result = this->state_->CreateCall(
        build_slice, start, stop, step, "BUILD_SLICE_result");
    this->state_->DecRef(start);
    this->state_->DecRef(stop);
    this->fbuilder_->PropagateExceptionOnNull(result);
    this->fbuilder_->Push(result);
}

void
OpcodeSlice::BUILD_SLICE_THREE()
{
    Value *step = this->fbuilder_->Pop();
    Value *stop = this->fbuilder_->Pop();
    Value *start = this->fbuilder_->Pop();
    Function *build_slice = this->state_->GetGlobalFunction<
        PyObject *(PyObject *, PyObject *, PyObject *)>("PySlice_New");
    Value *result = this->state_->CreateCall(
        build_slice, start, stop, step, "BUILD_SLICE_result");
    this->state_->DecRef(start);
    this->state_->DecRef(stop);
    this->state_->DecRef(step);
    this->fbuilder_->PropagateExceptionOnNull(result);
    this->fbuilder_->Push(result);
}

}
