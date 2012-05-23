#include "Python.h"

#include "JIT/opcodes/locals.h"
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

OpcodeLocals::OpcodeLocals(LlvmFunctionBuilder *fbuilder) :
    fbuilder_(fbuilder),
    state_(fbuilder->state()),
    builder_(fbuilder->builder())
{
}

void
OpcodeLocals::LOAD_CONST(int index)
{
    PyObject *co_consts = this->fbuilder_->code_object()->co_consts;
    Value *const_ = this->builder_.CreateBitCast(
        this->state_->GetGlobalVariableFor(PyTuple_GET_ITEM(co_consts, index)),
        PyTypeBuilder<PyObject*>::get(this->fbuilder_->context()));
    this->state_->IncRef(const_);
    this->fbuilder_->Push(const_);
}

// TODO(collinwinter): we'd like to implement this by simply marking the load
// as "cannot be NULL" and let LLVM's constant propgation optimizers remove the
// conditional branch for us. That is currently not supported, so we do this
// manually.
void
OpcodeLocals::LOAD_FAST(int index)
{
    // Simple check: if DELETE_FAST is never used, function parameters cannot
    // be NULL.
    if (!this->fbuilder_->uses_delete_fast() &&
        index < this->fbuilder_->GetParamCount())
        this->LOAD_FAST_fast(index);
    else
        this->LOAD_FAST_safe(index);
}

void
OpcodeLocals::LOAD_FAST_fast(int index)
{
    Value *local = this->builder_.CreateLoad(
        this->fbuilder_->GetLocal(index), "FAST_loaded");
#ifndef NDEBUG
    Value *frame_local_slot = this->builder_.CreateGEP(
        this->fbuilder_->fastlocals(),
        ConstantInt::get(Type::getInt32Ty(this->fbuilder_->context()),
                         index));
    Value *frame_local = this->builder_.CreateLoad(frame_local_slot);
    Value *sane_locals = this->builder_.CreateICmpEQ(frame_local, local);
    this->state_->Assert(sane_locals, "alloca locals do not match frame locals!");
#endif  /* NDEBUG */
    this->state_->IncRef(local);
    this->fbuilder_->Push(local);
}

void
OpcodeLocals::LOAD_FAST_safe(int index)
{
    BasicBlock *unbound_local =
        this->state_->CreateBasicBlock("LOAD_FAST_unbound");
    BasicBlock *success =
        this->state_->CreateBasicBlock("LOAD_FAST_success");

    Value *local = this->builder_.CreateLoad(
        this->fbuilder_->GetLocal(index), "FAST_loaded");
#ifndef NDEBUG
    Value *frame_local_slot = this->builder_.CreateGEP(
        this->fbuilder_->fastlocals(),
        ConstantInt::get(Type::getInt32Ty(this->fbuilder_->context()),
                         index));
    Value *frame_local = this->builder_.CreateLoad(frame_local_slot);
    Value *sane_locals = this->builder_.CreateICmpEQ(frame_local, local);
    this->state_->Assert(sane_locals,
                         "alloca locals do not match frame locals!");
#endif  /* NDEBUG */
    this->builder_.CreateCondBr(this->state_->IsNull(local),
                                unbound_local, success);

    this->builder_.SetInsertPoint(unbound_local);
    Function *do_raise =
        this->state_->GetGlobalFunction<void(PyFrameObject*, int)>(
            "_PyEval_RaiseForUnboundLocal");
    this->state_->CreateCall(do_raise, this->fbuilder_->frame(),
                             this->state_->GetSigned<int>(index));
    this->fbuilder_->PropagateException();

    this->builder_.SetInsertPoint(success);
    this->state_->IncRef(local);
    this->fbuilder_->Push(local);
}

void
OpcodeLocals::STORE_FAST(int index)
{
    this->SetLocal(index, this->fbuilder_->Pop());
}

void
OpcodeLocals::SetLocal(int locals_index, llvm::Value *new_value)
{
    // We write changes twice: once to our LLVM-visible locals, and again to the
    // PyFrameObject. This makes vars(), locals() and dir() happy.
    Value *frame_local_slot = this->builder_.CreateGEP(
        this->fbuilder_->fastlocals(), 
        ConstantInt::get(Type::getInt32Ty(this->fbuilder_->context()),
                         locals_index));
    this->fbuilder_->llvm_data()->tbaa_locals.MarkInstruction(frame_local_slot);
    this->builder_.CreateStore(new_value, frame_local_slot);

    Value *llvm_local_slot = this->fbuilder_->GetLocal(locals_index);
    Value *orig_value =
        this->builder_.CreateLoad(llvm_local_slot,
                                  "llvm_local_overwritten");
    this->builder_.CreateStore(new_value, llvm_local_slot);
    this->state_->XDecRef(orig_value);
}

void
OpcodeLocals::DELETE_FAST(int index)
{
    BasicBlock *failure =
        this->state_->CreateBasicBlock("DELETE_FAST_failure");
    BasicBlock *success =
        this->state_->CreateBasicBlock("DELETE_FAST_success");
    Value *local_slot = this->fbuilder_->GetLocal(index);
    Value *orig_value = this->builder_.CreateLoad(
        local_slot, "DELETE_FAST_old_reference");
    this->builder_.CreateCondBr(this->state_->IsNull(orig_value),
                                failure, success);

    this->builder_.SetInsertPoint(failure);
    Function *do_raise = this->state_->GetGlobalFunction<
        void(PyFrameObject *, int)>("_PyEval_RaiseForUnboundLocal");
    this->state_->CreateCall(
        do_raise, this->fbuilder_->frame(),
        ConstantInt::getSigned(
            PyTypeBuilder<int>::get(this->fbuilder_->context()), index));
    this->fbuilder_->PropagateException();

    /* We clear both the LLVM-visible locals and the PyFrameObject's locals to
       make vars(), dir() and locals() happy. */
    this->builder_.SetInsertPoint(success);
    Value *frame_local_slot = this->builder_.CreateGEP(
        this->fbuilder_->fastlocals(),
        ConstantInt::get(Type::getInt32Ty(this->fbuilder_->context()),
                         index));
    this->builder_.CreateStore(this->state_->GetNull<PyObject*>(),
                               frame_local_slot);
    this->builder_.CreateStore(this->state_->GetNull<PyObject*>(),
                               local_slot);
    this->state_->DecRef(orig_value);
}

}
