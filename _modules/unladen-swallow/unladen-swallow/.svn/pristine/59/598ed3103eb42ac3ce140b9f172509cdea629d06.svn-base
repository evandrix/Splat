#include "Python.h"

#include "JIT/opcodes/globals.h"
#include "JIT/llvm_fbuilder.h"

#include "llvm/BasicBlock.h"
#include "llvm/Function.h"
#include "llvm/Instructions.h"

using llvm::BasicBlock;
using llvm::Function;
using llvm::Value;

namespace py {

OpcodeGlobals::OpcodeGlobals(LlvmFunctionBuilder *fbuilder) :
    fbuilder_(fbuilder),
    state_(fbuilder->state()),
    builder_(fbuilder->builder())
{
}

void OpcodeGlobals::LOAD_GLOBAL(int index)
{
    // A code object might not have co_watching set if
    // a) it was compiled by setting co_optimization, or
    // b) we couldn't watch the globals/builtins dicts.
    PyObject **watching = this->fbuilder_->code_object()->co_watching;
    if (watching && watching[WATCHING_GLOBALS] && watching[WATCHING_BUILTINS])
        this->LOAD_GLOBAL_fast(index);
    else
        this->LOAD_GLOBAL_safe(index);
}

void OpcodeGlobals::LOAD_GLOBAL_fast(int index)
{
    PyCodeObject *code = this->fbuilder_->code_object();
    assert(code->co_watching != NULL);
    assert(code->co_watching[WATCHING_GLOBALS]);
    assert(code->co_watching[WATCHING_BUILTINS]);

    PyObject *name = PyTuple_GET_ITEM(code->co_names, index);
    PyObject *obj = PyDict_GetItem(code->co_watching[WATCHING_GLOBALS], name);
    if (obj == NULL) {
        obj = PyDict_GetItem(code->co_watching[WATCHING_BUILTINS], name);
        if (obj == NULL) {
            /* This isn't necessarily an error: it's legal Python
               code to refer to globals that aren't yet defined at
               compilation time. Is it a bad idea? Almost
               certainly. Is it legal? Unfortunatley. */
            this->LOAD_GLOBAL_safe(index);
            return;
        }
    }
    this->fbuilder_->WatchDict(WATCHING_GLOBALS);
    this->fbuilder_->WatchDict(WATCHING_BUILTINS);

    BasicBlock *keep_going =
        this->state_->CreateBasicBlock("LOAD_GLOBAL_keep_going");
    BasicBlock *invalid_assumptions =
        this->state_->CreateBasicBlock("LOAD_GLOBAL_invalid_assumptions");

#ifdef WITH_TSC
    this->state_->LogTscEvent(LOAD_GLOBAL_ENTER_LLVM);
#endif
    this->builder_.CreateCondBr(this->fbuilder_->GetUseJitCond(),
                                keep_going,
                                invalid_assumptions);

    /* Our assumptions about the state of the globals/builtins no longer hold;
       bail back to the interpreter. */
    this->builder_.SetInsertPoint(invalid_assumptions);
    this->fbuilder_->CreateBailPoint(_PYFRAME_FATAL_GUARD_FAIL);

    /* Our assumptions are still valid; encode the result of the lookups as an
       immediate in the IR. */
    this->builder_.SetInsertPoint(keep_going);
    Value *global = this->state_->EmbedPointer<PyObject*>(obj);
    this->state_->IncRef(global);
    this->fbuilder_->Push(global);

#ifdef WITH_TSC
    this->state_->LogTscEvent(LOAD_GLOBAL_EXIT_LLVM);
#endif
}

void OpcodeGlobals::LOAD_GLOBAL_safe(int index)
{
    this->fbuilder_->SetOpcodeArguments(0);
    BasicBlock *global_missing =
            this->state_->CreateBasicBlock("LOAD_GLOBAL_global_missing");
    BasicBlock *global_success =
            this->state_->CreateBasicBlock("LOAD_GLOBAL_global_success");
    BasicBlock *builtin_missing =
            this->state_->CreateBasicBlock("LOAD_GLOBAL_builtin_missing");
    BasicBlock *builtin_success =
            this->state_->CreateBasicBlock("LOAD_GLOBAL_builtin_success");
    BasicBlock *done = this->state_->CreateBasicBlock("LOAD_GLOBAL_done");
#ifdef WITH_TSC
    this->state_->LogTscEvent(LOAD_GLOBAL_ENTER_LLVM);
#endif
    Value *name = this->fbuilder_->LookupName(index);
    Function *pydict_getitem = this->state_->GetGlobalFunction<
        PyObject *(PyObject *, PyObject *)>("PyDict_GetItem");
    Value *global = this->state_->CreateCall(
        pydict_getitem, this->fbuilder_->globals(), name, "global_variable");
    this->builder_.CreateCondBr(this->state_->IsNull(global),
                                global_missing, global_success);

    this->builder_.SetInsertPoint(global_success);
    this->state_->IncRef(global);
    this->fbuilder_->SetOpcodeResult(0, global);
    this->builder_.CreateBr(done);

    this->builder_.SetInsertPoint(global_missing);
    // This ignores any exception set by PyDict_GetItem (and similarly
    // for the builtins dict below,) but this is what ceval does too.
    Value *builtin = this->state_->CreateCall(
        pydict_getitem, this->fbuilder_->builtins(), name, "builtin_variable");
    this->builder_.CreateCondBr(this->state_->IsNull(builtin),
                                builtin_missing, builtin_success);

    this->builder_.SetInsertPoint(builtin_missing);
    Function *do_raise = this->state_->GetGlobalFunction<
        void(PyObject *)>("_PyEval_RaiseForGlobalNameError");
    this->state_->CreateCall(do_raise, name);
    this->fbuilder_->PropagateException();

    this->builder_.SetInsertPoint(builtin_success);
    this->state_->IncRef(builtin);
    this->fbuilder_->SetOpcodeResult(0, builtin);
    this->builder_.CreateBr(done);

    this->builder_.SetInsertPoint(done);
#ifdef WITH_TSC
    this->state_->LogTscEvent(LOAD_GLOBAL_EXIT_LLVM);
#endif
}

void OpcodeGlobals::STORE_GLOBAL(int index)
{
    Value *name = this->fbuilder_->LookupName(index);
    Value *value = this->fbuilder_->Pop();
    Function *pydict_setitem = this->state_->GetGlobalFunction<
        int(PyObject *, PyObject *, PyObject *)>("PyDict_SetItem");
    Value *result = this->state_->CreateCall(
        pydict_setitem, this->fbuilder_->globals(), name, value,
        "STORE_GLOBAL_result");
    this->state_->DecRef(value);
    this->fbuilder_->PropagateExceptionOnNonZero(result);
}

void OpcodeGlobals::DELETE_GLOBAL(int index)
{
    BasicBlock *failure =
        this->state_->CreateBasicBlock("DELETE_GLOBAL_failure");
    BasicBlock *success =
        this->state_->CreateBasicBlock("DELETE_GLOBAL_success");
    Value *name = this->fbuilder_->LookupName(index);
    Function *pydict_setitem = this->state_->GetGlobalFunction<
        int(PyObject *, PyObject *)>("PyDict_DelItem");
    Value *result = this->state_->CreateCall(
        pydict_setitem, this->fbuilder_->globals(), name, "STORE_GLOBAL_result");
    this->builder_.CreateCondBr(this->state_->IsNonZero(result),
                                failure, success);

    this->builder_.SetInsertPoint(failure);
    Function *do_raise = this->state_->GetGlobalFunction<
        void(PyObject *)>("_PyEval_RaiseForGlobalNameError");
    this->state_->CreateCall(do_raise, name);
    this->fbuilder_->PropagateException();

    this->builder_.SetInsertPoint(success);
}

}
