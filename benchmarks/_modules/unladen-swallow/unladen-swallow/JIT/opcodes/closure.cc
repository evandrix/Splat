#include "Python.h"

#include "JIT/opcodes/closure.h"
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

OpcodeClosure::OpcodeClosure(LlvmFunctionBuilder *fbuilder) :
    fbuilder_(fbuilder),
    state_(fbuilder->state()),
    builder_(fbuilder->builder()),
    llvm_data_(fbuilder->llvm_data())
{
}

void
OpcodeClosure::LOAD_CLOSURE(int freevars_index)
{
    Value *cell = this->builder_.CreateLoad(
        this->builder_.CreateGEP(
            this->fbuilder_->freevars(),
            ConstantInt::get(Type::getInt32Ty(this->fbuilder_->context()),
                             freevars_index)));
    this->state_->IncRef(cell);
    this->fbuilder_->Push(cell);
}

void
OpcodeClosure::MAKE_CLOSURE(int num_defaults)
{
    Value *code_object = this->fbuilder_->Pop();
    Function *pyfunction_new = this->state_->GetGlobalFunction<
        PyObject *(PyObject *, PyObject *)>("PyFunction_New");
    Value *func_object = this->state_->CreateCall(
        pyfunction_new, code_object, this->fbuilder_->globals(),
        "MAKE_CLOSURE_result");
    this->state_->DecRef(code_object);
    this->fbuilder_->PropagateExceptionOnNull(func_object);
    Value *closure = this->fbuilder_->Pop();
    Function *pyfunction_setclosure = this->state_->GetGlobalFunction<
        int(PyObject *, PyObject *)>("PyFunction_SetClosure");
    Value *setclosure_result = this->state_->CreateCall(
        pyfunction_setclosure, func_object, closure,
        "MAKE_CLOSURE_setclosure_result");
    this->state_->DecRef(closure);
    this->fbuilder_->PropagateExceptionOnNonZero(setclosure_result);
    if (num_defaults > 0) {
        // Effectively inline BuildSequenceLiteral and
        // PropagateExceptionOnNull so we can DecRef func_object on error.
        BasicBlock *failure =
            this->state_->CreateBasicBlock("MAKE_CLOSURE_failure");
        BasicBlock *success =
            this->state_->CreateBasicBlock("MAKE_CLOSURE_success");

        Value *tupsize = ConstantInt::get(
            PyTypeBuilder<Py_ssize_t>::get(this->fbuilder_->context()),
            num_defaults);
        Function *pytuple_new = this->state_
              ->GetGlobalFunction<PyObject *(Py_ssize_t)>("PyTuple_New");
        Value *defaults = this->state_->CreateCall(pytuple_new, tupsize,
                                                   "MAKE_CLOSURE_defaults");
        this->builder_.CreateCondBr(this->state_->IsNull(defaults),
                                    failure, success);

        this->builder_.SetInsertPoint(failure);
        this->state_->DecRef(func_object);
        this->fbuilder_->PropagateException();

        this->builder_.SetInsertPoint(success);
        // XXX(twouters): do this with a memcpy?
        while (--num_defaults >= 0) {
            Value *itemslot = this->state_->GetTupleItemSlot(defaults,
                                                             num_defaults);
            this->builder_.CreateStore(this->fbuilder_->Pop(), itemslot);
        }
        // End of inlining.
        Function *pyfunction_setdefaults = this->state_->GetGlobalFunction<
            int(PyObject *, PyObject *)>("PyFunction_SetDefaults");
        Value *setdefaults_result = this->state_->CreateCall(
            pyfunction_setdefaults, func_object, defaults,
            "MAKE_CLOSURE_setdefaults_result");
        this->state_->DecRef(defaults);
        this->fbuilder_->PropagateExceptionOnNonZero(setdefaults_result);
    }
    this->fbuilder_->Push(func_object);
}

void
OpcodeClosure::LOAD_DEREF(int index)
{
    BasicBlock *failed_load =
        this->state_->CreateBasicBlock("LOAD_DEREF_failed_load");
    BasicBlock *unbound_local =
        this->state_->CreateBasicBlock("LOAD_DEREF_unbound_local");
    BasicBlock *error =
        this->state_->CreateBasicBlock("LOAD_DEREF_error");
    BasicBlock *success =
        this->state_->CreateBasicBlock("LOAD_DEREF_success");

    Value *cell = this->builder_.CreateLoad(
        this->builder_.CreateGEP(
            this->fbuilder_->freevars(),
            ConstantInt::get(Type::getInt32Ty(this->fbuilder_->context()),
                             index)));
    Function *pycell_get = this->state_->GetGlobalFunction<
        PyObject *(PyObject *)>("PyCell_Get");
    Value *value = this->state_->CreateCall(
        pycell_get, cell, "LOAD_DEREF_cell_contents");
    this->builder_.CreateCondBr(this->state_->IsNull(value),
                                failed_load, success);

    this->builder_.SetInsertPoint(failed_load);
    Function *pyerr_occurred =
        this->state_->GetGlobalFunction<PyObject *()>("PyErr_Occurred");
    Value *was_err =
        this->state_->CreateCall(pyerr_occurred, "LOAD_DEREF_err_occurred");
    this->builder_.CreateCondBr(this->state_->IsNull(was_err),
                                unbound_local, error);

    this->builder_.SetInsertPoint(unbound_local);
    Function *do_raise =
        this->state_->GetGlobalFunction<void(PyFrameObject*, int)>(
            "_PyEval_RaiseForUnboundFreeVar");
    this->state_->CreateCall(
        do_raise, this->fbuilder_->frame(),
        ConstantInt::get(PyTypeBuilder<int>::get(this->fbuilder_->context()),
                         index));

    this->fbuilder_->FallThroughTo(error);
    this->fbuilder_->PropagateException();

    this->builder_.SetInsertPoint(success);
    this->fbuilder_->Push(value);
}

void
OpcodeClosure::STORE_DEREF(int index)
{
    Value *value = this->fbuilder_->Pop();
    Value *cell = this->builder_.CreateLoad(
        this->builder_.CreateGEP(
            this->fbuilder_->freevars(),
            ConstantInt::get(Type::getInt32Ty(this->fbuilder_->context()),
                             index)));
    Function *pycell_set = this->state_->GetGlobalFunction<
        int(PyObject *, PyObject *)>("PyCell_Set");
    Value *result = this->state_->CreateCall(
        pycell_set, cell, value, "STORE_DEREF_result");
    this->state_->DecRef(value);
    // eval.cc doesn't actually check the return value of this, I guess
    // we are a little more likely to do things wrong.
    this->fbuilder_->PropagateExceptionOnNonZero(result);
}

}
