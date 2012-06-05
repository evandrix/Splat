#include "Python.h"

#include "JIT/opcodes/binops.h"
#include "JIT/opcodes/container.h"
#include "JIT/llvm_fbuilder.h"

#include "llvm/BasicBlock.h"
#include "llvm/Function.h"
#include "llvm/Instructions.h"
#include "llvm/Support/ManagedStatic.h"
#include "llvm/Support/raw_ostream.h"

using llvm::BasicBlock;
using llvm::ConstantInt;
using llvm::Function;
using llvm::Type;
using llvm::Value;
using llvm::errs;

#ifdef Py_WITH_INSTRUMENTATION
class ImportNameStats {
public:
    ImportNameStats()
        : total(0), optimized(0) {
    }

    ~ImportNameStats() {
        errs() << "\nIMPORT_NAME opcodes:\n";
        errs() << "Total: " << this->total << "\n";
        errs() << "Optimized: " << this->optimized << "\n";
    }

    // Total number of IMPORT_NAME opcodes compiled.
    unsigned total;
    // Number of imports successfully optimized.
    unsigned optimized;
};

static llvm::ManagedStatic<ImportNameStats> import_name_stats;

#define IMPORT_NAME_INC_STATS(field) import_name_stats->field++
#else
#define IMPORT_NAME_INC_STATS(field)
#endif  /* Py_WITH_INSTRUMENTATION */

namespace py {

OpcodeContainer::OpcodeContainer(LlvmFunctionBuilder *fbuilder) :
    fbuilder_(fbuilder),
    state_(fbuilder->state()),
    builder_(fbuilder->builder())
{
}

void
OpcodeContainer::BuildSequenceLiteral(
    int size, const char *createname,
    Value *(LlvmFunctionState::*getitemslot)(Value*, int))
{
    const Type *IntSsizeTy =
        PyTypeBuilder<Py_ssize_t>::get(this->fbuilder_->context());
    Value *seqsize = ConstantInt::getSigned(IntSsizeTy, size);

    Function *create =
        this->state_->GetGlobalFunction<PyObject *(Py_ssize_t)>(createname);
    Value *seq = this->state_->CreateCall(create, seqsize, "sequence_literal");
    this->fbuilder_->PropagateExceptionOnNull(seq);

    // XXX(twouters): do this with a memcpy?
    while (--size >= 0) {
        Value *itemslot = (this->state_->*getitemslot)(seq, size);
        this->builder_.CreateStore(this->fbuilder_->Pop(), itemslot);
    }
    this->fbuilder_->Push(seq);
}

void
OpcodeContainer::BUILD_LIST(int size)
{
   this->BuildSequenceLiteral(size, "PyList_New",
                              &LlvmFunctionState::GetListItemSlot);
}

void
OpcodeContainer::BUILD_TUPLE(int size)
{
   this->BuildSequenceLiteral(size, "PyTuple_New",
                              &LlvmFunctionState::GetTupleItemSlot);
}

void
OpcodeContainer::BUILD_MAP(int size)
{
    Value *sizehint = ConstantInt::getSigned(
        PyTypeBuilder<Py_ssize_t>::get(this->fbuilder_->context()), size);
    Function *create_dict = this->state_->GetGlobalFunction<
        PyObject *(Py_ssize_t)>("_PyDict_NewPresized");
    Value *result = this->state_->CreateCall(create_dict, sizehint,
                                             "BULD_MAP_result");
    this->fbuilder_->PropagateExceptionOnNull(result);
    this->fbuilder_->Push(result);
}

void
OpcodeContainer::UNPACK_SEQUENCE(int size)
{
    // TODO(twouters): We could do even better by combining this opcode and the
    // STORE_* ones that follow into a single block of code circumventing the
    // stack altogether. And omitting the horrible external stack munging that
    // UnpackIterable does.
    Value *iterable = this->fbuilder_->Pop();
    Function *unpack_iterable = this->state_->GetGlobalFunction<
        int(PyObject *, int, PyObject **)>("_PyLlvm_FastUnpackIterable");
    Value *new_stack_pointer = this->builder_.CreateGEP(
        this->builder_.CreateLoad(this->fbuilder_->stack_pointer_addr()),
        ConstantInt::getSigned(
            PyTypeBuilder<Py_ssize_t>::get(this->fbuilder_->context()), size));
    this->fbuilder_->llvm_data()->tbaa_stack.MarkInstruction(new_stack_pointer);

    Value *result = this->state_->CreateCall(
        unpack_iterable, iterable,
        ConstantInt::get(
            PyTypeBuilder<int>::get(this->fbuilder_->context()), size, true),
        // _PyLlvm_FastUnpackIterable really takes the *new* stack pointer as
        // an argument, because it builds the result stack in reverse.
        new_stack_pointer);
    this->state_->DecRef(iterable);
    this->fbuilder_->PropagateExceptionOnNonZero(result);
    // Not setting the new stackpointer on failure does mean that if
    // _PyLlvm_FastUnpackIterable failed after pushing some values onto the
    // stack, and it didn't clean up after itself, we lose references.  This
    // is what eval.cc does as well.
    this->builder_.CreateStore(new_stack_pointer,
                               this->fbuilder_->stack_pointer_addr());
}

#define INT_OBJ_OBJ_OBJ int(PyObject*, PyObject*, PyObject*)

void
OpcodeContainer::STORE_SUBSCR_list_int()
{
    BasicBlock *success =
        this->state_->CreateBasicBlock("STORE_SUBSCR_success");
    BasicBlock *bailpoint =
        this->state_->CreateBasicBlock("STORE_SUBSCR_bail");

    Value *key = this->fbuilder_->Pop();
    Value *obj = this->fbuilder_->Pop();
    Value *value = this->fbuilder_->Pop();
    Function *setitem =
        this->state_->GetGlobalFunction<INT_OBJ_OBJ_OBJ>(
            "_PyLlvm_StoreSubscr_List");

    Value *result = this->state_->CreateCall(setitem, obj, key, value,
                                             "STORE_SUBSCR_result");
    this->builder_.CreateCondBr(this->state_->IsNonZero(result),
                                bailpoint, success);

    this->builder_.SetInsertPoint(bailpoint);
    this->fbuilder_->Push(value);
    this->fbuilder_->Push(obj);
    this->fbuilder_->Push(key);
    this->fbuilder_->CreateGuardBailPoint(_PYGUARD_STORE_SUBSCR);

    this->builder_.SetInsertPoint(success);
    this->state_->DecRef(value);
    this->state_->DecRef(obj);
    this->state_->DecRef(key);
}

void
OpcodeContainer::STORE_SUBSCR_safe()
{
    // Performing obj[key] = val
    Value *key = this->fbuilder_->Pop();
    Value *obj = this->fbuilder_->Pop();
    Value *value = this->fbuilder_->Pop();
    Function *setitem =
        this->state_->GetGlobalFunction<INT_OBJ_OBJ_OBJ>("PyObject_SetItem");
    Value *result = this->state_->CreateCall(setitem, obj, key, value,
                                             "STORE_SUBSCR_result");
    this->state_->DecRef(value);
    this->state_->DecRef(obj);
    this->state_->DecRef(key);
    this->fbuilder_->PropagateExceptionOnNonZero(result);
}

#undef INT_OBJ_OBJ_OBJ

void
OpcodeContainer::STORE_SUBSCR()
{
    OpcodeBinops::IncStatsTotal();

    const PyTypeObject *lhs_type = this->fbuilder_->GetTypeFeedback(0);
    const PyTypeObject *rhs_type = this->fbuilder_->GetTypeFeedback(1);

    if (lhs_type == &PyList_Type && rhs_type == &PyInt_Type) {
        OpcodeBinops::IncStatsOptimized();
        this->STORE_SUBSCR_list_int();
        return;
    }
    else {
        OpcodeBinops::IncStatsOmitted();
        this->STORE_SUBSCR_safe();
        return;
    }
}

void
OpcodeContainer::DELETE_SUBSCR()
{
    Value *key = this->fbuilder_->Pop();
    Value *obj = this->fbuilder_->Pop();
    Function *delitem = this->state_->GetGlobalFunction<
          int(PyObject *, PyObject *)>("PyObject_DelItem");
    Value *result = this->state_->CreateCall(delitem, obj, key,
                                             "DELETE_SUBSCR_result");
    this->state_->DecRef(obj);
    this->state_->DecRef(key);
    this->fbuilder_->PropagateExceptionOnNonZero(result);
}

void
OpcodeContainer::LIST_APPEND()
{
    Value *item = this->fbuilder_->Pop();
    Value *listobj = this->fbuilder_->Pop();
    Function *list_append = this->state_->GetGlobalFunction<
        int(PyObject *, PyObject *)>("PyList_Append");
    Value *result = this->state_->CreateCall(list_append, listobj, item,
                                             "LIST_APPEND_result");
    this->state_->DecRef(listobj);
    this->state_->DecRef(item);
    this->fbuilder_->PropagateExceptionOnNonZero(result);
}

void
OpcodeContainer::STORE_MAP()
{
    Value *key = this->fbuilder_->Pop();
    Value *value = this->fbuilder_->Pop();
    Value *dict = this->fbuilder_->Pop();
    this->fbuilder_->Push(dict);
    Value *dict_type = this->builder_.CreateLoad(
        ObjectTy::ob_type(this->builder_, dict));
    Value *is_exact_dict = this->builder_.CreateICmpEQ(
        dict_type, this->state_->GetGlobalVariableFor((PyObject*)&PyDict_Type));
    this->state_->Assert(is_exact_dict,
                         "dict argument to STORE_MAP is not exactly a PyDict");
    Function *setitem = this->state_->GetGlobalFunction<
        int(PyObject *, PyObject *, PyObject *)>("PyDict_SetItem");
    Value *result = this->state_->CreateCall(setitem, dict, key, value,
                                             "STORE_MAP_result");
    this->state_->DecRef(value);
    this->state_->DecRef(key);
    this->fbuilder_->PropagateExceptionOnNonZero(result);
}

#define FUNC_TYPE PyObject *(PyObject *, PyObject *, PyObject *)

void
OpcodeContainer::IMPORT_NAME()
{
    IMPORT_NAME_INC_STATS(total);

    if (this->IMPORT_NAME_fast())
        return;

    Value *mod_name = this->fbuilder_->Pop();
    Value *names = this->fbuilder_->Pop();
    Value *level = this->fbuilder_->Pop();

    Value *module = this->state_->CreateCall(
        this->state_->GetGlobalFunction<FUNC_TYPE>("_PyEval_ImportName"),
        level, names, mod_name);
    this->state_->DecRef(level);
    this->state_->DecRef(names);
    this->state_->DecRef(mod_name);
    this->fbuilder_->PropagateExceptionOnNull(module);
    this->fbuilder_->Push(module);
}

#undef FUNC_TYPE

bool
OpcodeContainer::IMPORT_NAME_fast()
{
    PyCodeObject *code = fbuilder_->code_object();

    // If we're not already monitoring the builtins dict, monitor it.  Normally
    // we pick it up from the eval loop, but if it isn't here, then we make a
    // guess.  If we are wrong, we will bail.
    if (code->co_watching == NULL ||
        code->co_watching[WATCHING_BUILTINS] == NULL) {
        PyObject *builtins = PyThreadState_GET()->interp->builtins;
        _PyCode_WatchDict(code, WATCHING_BUILTINS, builtins);
    }

    const PyRuntimeFeedback *feedback = this->fbuilder_->GetFeedback();
    if (feedback == NULL || feedback->ObjectsOverflowed()) {
        return false;
    }

    llvm::SmallVector<PyObject *, 3> objects;
    feedback->GetSeenObjectsInto(objects);
    if (objects.size() != 1 || !PyModule_Check(objects[0])) {
        return false;
    }
    PyObject *module = objects[0];

    // We need to invalidate this function if someone changes sys.modules.
    if (code->co_watching[WATCHING_SYS_MODULES] == NULL) {
        PyObject *sys_modules = PyImport_GetModuleDict();
        if (sys_modules == NULL) {
            return false;
        }

        if (_PyCode_WatchDict(code,
                              WATCHING_SYS_MODULES,
                              sys_modules)) {
            PyErr_Clear();
            return false;
        }

        fbuilder_->WatchDict(WATCHING_BUILTINS);
        fbuilder_->WatchDict(WATCHING_SYS_MODULES);
    }

    BasicBlock *keep_going =
        this->state_->CreateBasicBlock("IMPORT_NAME_keep_going");
    BasicBlock *invalid_assumptions =
        this->state_->CreateBasicBlock("IMPORT_NAME_invalid_assumptions");

    this->builder_.CreateCondBr(this->fbuilder_->GetUseJitCond(),
                                keep_going,
                                invalid_assumptions);

    /* Our assumptions about the state of sys.modules no longer hold;
       bail back to the interpreter. */
    this->builder_.SetInsertPoint(invalid_assumptions);
    this->fbuilder_->CreateBailPoint(_PYFRAME_FATAL_GUARD_FAIL);

    this->builder_.SetInsertPoint(keep_going);
    /* TODO(collinwinter): we pop to get rid of the inputs to IMPORT_NAME.
       Find a way to omit this work. */
    this->state_->DecRef(this->fbuilder_->Pop());
    this->state_->DecRef(this->fbuilder_->Pop());
    this->state_->DecRef(this->fbuilder_->Pop());

    Value *mod = this->state_->GetGlobalVariableFor(module);
    this->state_->IncRef(mod);
    this->fbuilder_->Push(mod);

    IMPORT_NAME_INC_STATS(optimized);
    return true;
}

}
