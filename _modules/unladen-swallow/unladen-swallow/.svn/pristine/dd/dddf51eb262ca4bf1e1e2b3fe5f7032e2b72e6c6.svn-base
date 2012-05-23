#include "Python.h"

#include "JIT/opcodes/loop.h"
#include "JIT/llvm_fbuilder.h"

#include "llvm/BasicBlock.h"
#include "llvm/Function.h"
#include "llvm/Instructions.h"

using llvm::BasicBlock;
using llvm::ConstantInt;
using llvm::Function;
using llvm::Type;
using llvm::Value;

// Use like "this->GET_GLOBAL_VARIABLE(Type, variable)".
#define GET_GLOBAL_VARIABLE(TYPE, VARIABLE) \
    GetGlobalVariable<TYPE>(&VARIABLE, #VARIABLE)

namespace py {

OpcodeLoop::OpcodeLoop(LlvmFunctionBuilder *fbuilder) :
    fbuilder_(fbuilder),
    state_(fbuilder->state()),
    builder_(fbuilder->builder())
{
}

void
OpcodeLoop::GET_ITER()
{
    Value *obj = this->fbuilder_->Pop();
    Function *pyobject_getiter =
        this->state_->GetGlobalFunction<PyObject*(PyObject*)>(
        "PyObject_GetIter");
    Value *iter = this->state_->CreateCall(pyobject_getiter, obj);
    this->state_->DecRef(obj);
    this->fbuilder_->PropagateExceptionOnNull(iter);
    this->fbuilder_->Push(iter);
}

void
OpcodeLoop::FOR_ITER(llvm::BasicBlock *target,
                     llvm::BasicBlock *fallthrough)
{
    Value *iter = this->fbuilder_->Pop();
    Value *iter_tp = this->builder_.CreateBitCast(
        this->builder_.CreateLoad(
            ObjectTy::ob_type(this->builder_, iter)),
        PyTypeBuilder<PyTypeObject *>::get(this->fbuilder_->context()),
        "iter_type");
    Value *iternext = this->builder_.CreateLoad(
        TypeTy::tp_iternext(this->builder_, iter_tp),
        "iternext");
    Value *next = this->state_->CreateCall(iternext, iter, "next");
    BasicBlock *got_next = this->state_->CreateBasicBlock("got_next");
    BasicBlock *next_null = this->state_->CreateBasicBlock("next_null");
    this->builder_.CreateCondBr(this->state_->IsNull(next),
                                next_null, got_next);

    this->builder_.SetInsertPoint(next_null);
    Value *err_occurred = this->state_->CreateCall(
        this->state_->GetGlobalFunction<PyObject*()>("PyErr_Occurred"));
    BasicBlock *iter_ended = this->state_->CreateBasicBlock("iter_ended");
    BasicBlock *exception = this->state_->CreateBasicBlock("exception");
    this->builder_.CreateCondBr(this->state_->IsNull(err_occurred),
                                iter_ended, exception);

    this->builder_.SetInsertPoint(exception);
    Value *exc_stopiteration = this->builder_.CreateLoad(
        this->state_->GET_GLOBAL_VARIABLE(PyObject*, PyExc_StopIteration));
    Value *was_stopiteration = this->state_->CreateCall(
        this->state_->GetGlobalFunction<int(PyObject *)>("PyErr_ExceptionMatches"),
        exc_stopiteration);
    BasicBlock *clear_err = this->state_->CreateBasicBlock("clear_err");
    BasicBlock *propagate = this->state_->CreateBasicBlock("propagate");
    this->builder_.CreateCondBr(this->state_->IsNonZero(was_stopiteration),
                                clear_err, propagate);

    this->builder_.SetInsertPoint(propagate);
    this->state_->DecRef(iter);
    this->fbuilder_->PropagateException();

    this->builder_.SetInsertPoint(clear_err);
    this->state_->CreateCall(this->state_->GetGlobalFunction<void()>("PyErr_Clear"));
    this->builder_.CreateBr(iter_ended);

    this->builder_.SetInsertPoint(iter_ended);
    this->state_->DecRef(iter);
    this->builder_.CreateBr(target);

    this->builder_.SetInsertPoint(got_next);
    this->fbuilder_->Push(iter);
    this->fbuilder_->Push(next);
}

void
OpcodeLoop::CONTINUE_LOOP(llvm::BasicBlock *target,
                          int target_opindex,
                          llvm::BasicBlock *fallthrough)
{
    // Accept code after a continue statement, even though it's never executed.
    // Otherwise, CPython's willingness to insert code after block
    // terminators causes problems.
    BasicBlock *dead_code = this->state_->CreateBasicBlock("dead_code");
    this->builder_.CreateStore(
        ConstantInt::get(Type::getInt8Ty(this->fbuilder_->context()),
                         UNWIND_CONTINUE),
        this->fbuilder_->unwind_reason_addr());
    Value *unwind_target =
        this->fbuilder_->AddUnwindTarget(target, target_opindex);
    // Yes, store the unwind target in the return value slot. This is to
    // keep the translation from eval.cc as close as possible; deviation will
    // only introduce bugs. The UNWIND_CONTINUE cases in the unwind block
    // (see FillUnwindBlock()) will pick this up and deal with it.
    const Type *long_type =
        PyTypeBuilder<long>::get(this->fbuilder_->context());
    Value *pytarget = this->state_->CreateCall(
            this->state_->GetGlobalFunction<PyObject *(long)>(
                "PyInt_FromLong"),
            this->builder_.CreateZExt(unwind_target, long_type));
    this->builder_.CreateStore(pytarget, this->fbuilder_->retval_addr());
    this->builder_.CreateBr(this->fbuilder_->unwind_block());

    this->builder_.SetInsertPoint(dead_code);
}

void
OpcodeLoop::BREAK_LOOP()
{
    // Accept code after a break statement, even though it's never executed.
    // Otherwise, CPython's willingness to insert code after block
    // terminators causes problems.
    BasicBlock *dead_code = this->state_->CreateBasicBlock("dead_code");
    this->builder_.CreateStore(
        ConstantInt::get(Type::getInt8Ty(this->fbuilder_->context()),
                         UNWIND_BREAK),
        this->fbuilder_->unwind_reason_addr());
    this->builder_.CreateBr(this->fbuilder_->unwind_block());

    this->builder_.SetInsertPoint(dead_code);
}

}
