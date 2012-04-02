#include "Python.h"

#include "JIT/opcodes/attributes.h"
#include "JIT/llvm_fbuilder.h"

#include "JIT/ConstantMirror.h"
#include "JIT/global_llvm_data.h"
#include "JIT/PyTypeBuilder.h"

#include "llvm/ADT/STLExtras.h"
#include "llvm/BasicBlock.h"
#include "llvm/Function.h"
#include "llvm/Instructions.h"
#include "llvm/Value.h"
#include "llvm/Support/ManagedStatic.h"
#include "llvm/Support/raw_ostream.h"

using llvm::BasicBlock;
using llvm::ConstantInt;
using llvm::Function;
using llvm::Value;
using llvm::array_endof;
using llvm::errs;

#ifdef Py_WITH_INSTRUMENTATION

class AccessAttrStats {
public:
    AccessAttrStats()
        : loads(0), stores(0), optimized_loads(0), optimized_stores(0),
          no_opt_no_data(0), no_opt_no_mcache(0), no_opt_overrode_access(0),
          no_opt_polymorphic(0), no_opt_nonstring_name(0) {
    }

    ~AccessAttrStats() {
        errs() << "\nLOAD/STORE_ATTR optimization:\n";
        errs() << "Total opcodes: " << (this->loads + this->stores) << "\n";
        errs() << "Optimized opcodes: "
               << (this->optimized_loads + this->optimized_stores) << "\n";
        errs() << "LOAD_ATTR opcodes: " << this->loads << "\n";
        errs() << "Optimized LOAD_ATTR opcodes: "
               << this->optimized_loads << "\n";
        errs() << "STORE_ATTR opcodes: " << this->stores << "\n";
        errs() << "Optimized STORE_ATTR opcodes: "
               << this->optimized_stores << "\n";
        errs() << "No opt: no data: " << this->no_opt_no_data << "\n";
        errs() << "No opt: no mcache support: "
               << this->no_opt_no_mcache << "\n";
        errs() << "No opt: overrode getattr: "
               << this->no_opt_overrode_access << "\n";
        errs() << "No opt: polymorphic: " << this->no_opt_polymorphic << "\n";
        errs() << "No opt: non-string name: "
               << this->no_opt_nonstring_name << "\n";
    }

    // Total number of LOAD_ATTR opcodes compiled.
    unsigned loads;
    // Total number of STORE_ATTR opcodes compiled.
    unsigned stores;
    // Number of loads we optimized.
    unsigned optimized_loads;
    // Number of stores we optimized.
    unsigned optimized_stores;
    // Number of opcodes we were unable to optimize due to missing data.
    unsigned no_opt_no_data;
    // Number of opcodes we were unable to optimize because the type didn't
    // support the method cache.
    unsigned no_opt_no_mcache;
    // Number of opcodes we were unable to optimize because the type overrode
    // tp_getattro.
    unsigned no_opt_overrode_access;
    // Number of opcodes we were unable to optimize due to polymorphism.
    unsigned no_opt_polymorphic;
    // Number of opcodes we were unable to optimize because the attribute name
    // was not a string.
    unsigned no_opt_nonstring_name;
};

static llvm::ManagedStatic<AccessAttrStats> access_attr_stats;

class MethodStats {
public:
    ~MethodStats() {
        errs() << "\nLOAD/CALL_METHOD optimization:\n";
        errs() << "Total load opcodes: " << this->total << "\n";
        errs() << "Optimized opcodes: "
               << (this->known + this->unknown) << "\n";
        errs() << "Predictable methods: " << this->known << "\n";
        errs() << "Unpredictable methods: " << this->unknown << "\n";
    }

    // Total number of LOAD_METHOD opcodes compiled.
    unsigned total;
    // Number of monomorphic method call sites.
    unsigned known;
    // Number of polymorphic method call sites that were still optimized.
    unsigned unknown;
};

static llvm::ManagedStatic<MethodStats> method_stats;

#define ACCESS_ATTR_INC_STATS(field) access_attr_stats->field++
#define METHOD_INC_STATS(field) method_stats->field++
#else
#define ACCESS_ATTR_INC_STATS(field)
#define METHOD_INC_STATS(field)
#endif /* Py_WITH_INSTRUMENTATION */

namespace py {

OpcodeAttributes::OpcodeAttributes(LlvmFunctionBuilder *fbuilder) :
    fbuilder_(fbuilder),
    state_(fbuilder->state()),
    builder_(fbuilder->builder()),
    llvm_data_(fbuilder->llvm_data())
{
}

void
OpcodeAttributes::LOAD_ATTR(int names_index)
{
    ACCESS_ATTR_INC_STATS(loads);
    if (!this->LOAD_ATTR_fast(names_index)) {
        this->LOAD_ATTR_safe(names_index);
    }
}

void
OpcodeAttributes::LOAD_ATTR_safe(int names_index)
{
    Value *attr = this->fbuilder_->LookupName(names_index);
    this->fbuilder_->SetOpcodeArguments(1);
    Value *obj = this->fbuilder_->GetOpcodeArg(0);
    Function *pyobj_getattr = this->state_->GetGlobalFunction<
        PyObject *(PyObject *, PyObject *)>("PyObject_GetAttr");
    Value *result = this->state_->CreateCall(
        pyobj_getattr, obj, attr, "LOAD_ATTR_result");
    this->state_->DecRef(obj);
    this->fbuilder_->PropagateExceptionOnNull(result);
    this->fbuilder_->SetOpcodeResult(0, result);
}

bool
OpcodeAttributes::LOAD_ATTR_fast(int names_index)
{
    PyObject *name =
        PyTuple_GET_ITEM(this->fbuilder_->code_object()->co_names, names_index);
    AttributeAccessor accessor(this->fbuilder_, name, ATTR_ACCESS_LOAD);

    // Check that we can optimize this load.
    if (!accessor.CanOptimizeAttrAccess()) {
        return false;
    }
    ACCESS_ATTR_INC_STATS(optimized_loads);

    this->fbuilder_->SetOpcodeArgsWithGuard(1);

    // Emit the appropriate guards.
    Value *obj_v = this->fbuilder_->GetOpcodeArg(0);
    BasicBlock *do_load = this->state_->CreateBasicBlock("LOAD_ATTR_do_load");
    accessor.GuardAttributeAccess(obj_v, do_load);

    // Call the inline function that deals with the lookup.  LLVM propagates
    // these constant arguments through the body of the function.
    this->builder_.SetInsertPoint(do_load);
    this->fbuilder_->BeginOpcodeImpl();
    PyConstantMirror &mirror = llvm_data_->constant_mirror();
    Value *descr_get_v = mirror.GetGlobalForFunctionPointer<descrgetfunc>(
            (void*)accessor.descr_get_, "");
    Value *getattr_func = this->state_->GetGlobalFunction<
        PyObject *(PyObject *obj, PyTypeObject *type, PyObject *name,
                   long dictoffset, PyObject *descr, descrgetfunc descr_get,
                   char is_data_descr)>("_PyLlvm_Object_GenericGetAttr");
    Value *args[] = {
        obj_v,
        accessor.guard_type_v_,
        accessor.name_v_,
        accessor.dictoffset_v_,
        accessor.descr_v_,
        descr_get_v,
        accessor.is_data_descr_v_
    };
    Value *result = this->state_->CreateCall(getattr_func,
                                             args, array_endof(args));

    // Put the result on the stack and possibly propagate an exception.
    this->state_->DecRef(obj_v);
    this->fbuilder_->PropagateExceptionOnNull(result);
    this->fbuilder_->SetOpcodeResult(0, result);
    return true;
}

void
OpcodeAttributes::STORE_ATTR(int names_index)
{
    ACCESS_ATTR_INC_STATS(stores);
    if (!this->STORE_ATTR_fast(names_index)) {
        this->STORE_ATTR_safe(names_index);
    }
}

void
OpcodeAttributes::STORE_ATTR_safe(int names_index)
{
    Value *attr = this->fbuilder_->LookupName(names_index);
    Value *obj = this->fbuilder_->Pop();
    Value *value = this->fbuilder_->Pop();
    Function *pyobj_setattr = this->state_->GetGlobalFunction<
        int(PyObject *, PyObject *, PyObject *)>("PyObject_SetAttr");
    Value *result = this->state_->CreateCall(
        pyobj_setattr, obj, attr, value, "STORE_ATTR_result");
    this->state_->DecRef(obj);
    this->state_->DecRef(value);
    this->fbuilder_->PropagateExceptionOnNonZero(result);
}

bool
OpcodeAttributes::STORE_ATTR_fast(int names_index)
{
    PyObject *name =
        PyTuple_GET_ITEM(this->fbuilder_->code_object()->co_names, names_index);
    AttributeAccessor accessor(this->fbuilder_, name, ATTR_ACCESS_STORE);

    // Check that we can optimize this store.
    if (!accessor.CanOptimizeAttrAccess()) {
        return false;
    }
    ACCESS_ATTR_INC_STATS(optimized_stores);

    this->fbuilder_->SetOpcodeArgsWithGuard(2);

    // Emit appropriate guards.
    Value *val_v = this->fbuilder_->GetOpcodeArg(0);
    Value *obj_v = this->fbuilder_->GetOpcodeArg(1);
    BasicBlock *do_store =
      this->state_->CreateBasicBlock("STORE_ATTR_do_store");
    accessor.GuardAttributeAccess(obj_v, do_store);

    // Call the inline function that deals with the lookup.  LLVM propagates
    // these constant arguments through the body of the function.
    this->builder_.SetInsertPoint(do_store);
    this->fbuilder_->BeginOpcodeImpl();
    PyConstantMirror &mirror = llvm_data_->constant_mirror();
    Value *descr_set_v = mirror.GetGlobalForFunctionPointer<descrsetfunc>(
        (void*)accessor.descr_set_, "");
    Value *setattr_func = this->state_->GetGlobalFunction<
        int (PyObject *obj, PyObject *val, PyTypeObject *type, PyObject *name,
             long dictoffset, PyObject *descr, descrsetfunc descr_set,
             char is_data_descr)>("_PyLlvm_Object_GenericSetAttr");
    Value *args[] = {
        obj_v,
        val_v,
        accessor.guard_type_v_,
        accessor.name_v_,
        accessor.dictoffset_v_,
        accessor.descr_v_,
        descr_set_v,
        accessor.is_data_descr_v_
    };
    Value *result = this->state_->CreateCall(setattr_func, args,
                                             array_endof(args));

    this->state_->DecRef(obj_v);
    this->state_->DecRef(val_v);
    this->fbuilder_->PropagateExceptionOnNonZero(result);
    return true;
}

void
OpcodeAttributes::LOAD_METHOD(int names_index)
{
    const PyRuntimeFeedback *counters = this->fbuilder_->GetFeedback(1);
    int method_count = 0;
    int nonmethod_count = 0;
    if (counters != NULL) {
        method_count = counters->GetCounter(PY_FDO_LOADMETHOD_METHOD);
        nonmethod_count = counters->GetCounter(PY_FDO_LOADMETHOD_OTHER);
    }

    METHOD_INC_STATS(total);

    bool optimized = false;
    if (method_count > 0 && nonmethod_count == 0) {
        // We have data, and all loads have turned out to be methods.
        optimized = this->LOAD_METHOD_known(names_index);
        // If we can't use type feedback, fall back to a simpler optimization.
        if (!optimized) {
            optimized = this->LOAD_METHOD_unknown(names_index);
        }
    }

    if (!optimized) {
        // No data, conflicting data, or we couldn't do the optimization.  Emit
        // the unoptimized, safe code.
        this->LOAD_ATTR(names_index);
        // Use a sub-opcode to insert the padding.
        this->fbuilder_->FinishOpcodeImpl(1);
        this->fbuilder_->SetOpcodeArguments(1);
        Value *attr = this->fbuilder_->GetOpcodeArg(0);
        this->fbuilder_->SetOpcodeResult(0,
                                         this->state_->GetNull<PyObject*>());
        this->fbuilder_->SetOpcodeResult(1, attr);
    } else {
        // We currently count LOAD_METHODs as attribute loads.  LOAD_ATTR will
        // automatically count the opcode, but we won't call it if we took the
        // optimized path.
        ACCESS_ATTR_INC_STATS(loads);
    }

    this->fbuilder_->loads_optimized().push_back(optimized);
}

bool
OpcodeAttributes::LOAD_METHOD_unknown(int names_index)
{
    PyObject *name =
        PyTuple_GET_ITEM(this->fbuilder_->code_object()->co_names, names_index);

    // This optimization only supports string names.
    if (!PyString_Check(name)) {
        return false;
    }

    METHOD_INC_STATS(unknown);

    this->fbuilder_->SetOpcodeArgsWithGuard(1);
    // Call the inline function that deals with the lookup.  LLVM propagates
    // these constant arguments through the body of the function.
    Value *obj_v = this->fbuilder_->GetOpcodeArg(0);
    Value *name_v = this->state_->EmbedPointer<PyObject*>(name);
    Value *getattr_func = this->state_->GetGlobalFunction<
        PyObject *(PyObject *obj, PyObject *name)>(
                "_PyLlvm_Object_GetUnknownMethod");
    Value *method = this->state_->CreateCall(getattr_func, obj_v, name_v);

    // Bail if method is NULL.
    BasicBlock *bail_block =
        this->state_->CreateBasicBlock("LOAD_METHOD_unknown_bail_block");
    BasicBlock *push_result =
        this->state_->CreateBasicBlock("LOAD_METHOD_unknown_push_result");
    this->builder_.CreateCondBr(this->state_->IsNull(method),
                                           bail_block, push_result);

    // Fill in the bail bb.
    this->builder_.SetInsertPoint(bail_block);
    this->fbuilder_->CreateGuardBailPoint(_PYGUARD_LOAD_METHOD);

    // Put the method and self on the stack.  We bail instead of raising
    // exceptions.
    this->builder_.SetInsertPoint(push_result);
    this->fbuilder_->BeginOpcodeImpl();
    this->fbuilder_->SetOpcodeResult(0, method);
    this->fbuilder_->SetOpcodeResult(1, obj_v);
    return true;
}

bool
OpcodeAttributes::LOAD_METHOD_known(int names_index)
{
    // Do an optimized LOAD_ATTR with the optimized LOAD_METHOD.
    PyObject *name =
        PyTuple_GET_ITEM(this->fbuilder_->code_object()->co_names, names_index);
    AttributeAccessor accessor(this->fbuilder_, name, ATTR_ACCESS_LOAD);

    // Check that we can optimize this load.
    if (!accessor.CanOptimizeAttrAccess()) {
        return false;
    }

    // Check that the descriptor is in fact a method.  The only way this could
    // fail is if between recording feedback and optimizing this code, the type
    // is modified and the method replaced.
    if (!_PyObject_ShouldBindMethod((PyObject*)accessor.guard_type_,
                                    accessor.descr_)) {
        return false;
    }

    METHOD_INC_STATS(known);
    ACCESS_ATTR_INC_STATS(optimized_loads);

    this->fbuilder_->SetOpcodeArgsWithGuard(1);

    // Emit the appropriate guards.
    Value *obj_v = this->fbuilder_->GetOpcodeArg(0);
    BasicBlock *do_load = state_->CreateBasicBlock("LOAD_METHOD_do_load");
    accessor.GuardAttributeAccess(obj_v, do_load);

    // Call the inline function that deals with the lookup.  LLVM propagates
    // these constant arguments through the body of the function.
    this->builder_.SetInsertPoint(do_load);
    Value *getattr_func = state_->GetGlobalFunction<
        PyObject *(PyObject *obj, PyTypeObject *tp, PyObject *name,
                   long dictoffset, PyObject *method)>(
                           "_PyLlvm_Object_GetKnownMethod");
    Value *args[] = {
        obj_v,
        accessor.guard_type_v_,
        accessor.name_v_,
        accessor.dictoffset_v_,
        accessor.descr_v_,
    };
    Value *method_v = state_->CreateCall(getattr_func, args, array_endof(args));

    // Bail if method_v is NULL.
    BasicBlock *push_result =
        state_->CreateBasicBlock("LOAD_METHOD_push_result");
    this->builder_.CreateCondBr(state_->IsNull(method_v),
                                     accessor.bail_block_, push_result);

    // Put the method and self on the stack.  We bail instead of raising
    // exceptions.
    this->builder_.SetInsertPoint(push_result);
    this->fbuilder_->BeginOpcodeImpl();
    this->fbuilder_->SetOpcodeResult(0, method_v);
    this->fbuilder_->SetOpcodeResult(1, obj_v);
    return true;
}

bool
AttributeAccessor::CanOptimizeAttrAccess()
{
    // Only optimize string attribute loads.  This leaves unicode hanging for
    // now, but most objects are still constructed with string objects.  If it
    // becomes a problem, our instrumentation will detect it.
    if (!PyString_Check(this->name_)) {
        ACCESS_ATTR_INC_STATS(no_opt_nonstring_name);
        return false;
    }

    // Only optimize monomorphic load sites with data.
    const PyRuntimeFeedback *feedback = this->fbuilder_->GetFeedback();
    if (feedback == NULL) {
        ACCESS_ATTR_INC_STATS(no_opt_no_data);
        return false;
    }

    if (feedback->ObjectsOverflowed()) {
        ACCESS_ATTR_INC_STATS(no_opt_polymorphic);
        return false;
    }
    llvm::SmallVector<PyObject*, 3> types_seen;
    feedback->GetSeenObjectsInto(types_seen);
    if (types_seen.size() != 1) {
        ACCESS_ATTR_INC_STATS(no_opt_polymorphic);
        return false;
    }

    // During the course of the compilation, we borrow a reference to the type
    // object from the feedback.  When compilation finishes, we listen for type
    // object modifications.  When a type object is freed, it notifies its
    // listeners, and the code object will be invalidated.  All other
    // references are borrowed from the type object, which cannot change
    // without invalidating the code.
    PyObject *type_obj = types_seen[0];
    assert(PyType_Check(type_obj));
    PyTypeObject *type = this->guard_type_ = (PyTypeObject*)type_obj;

    // The type must support the method cache so we can listen for
    // modifications to it.
    if (!PyType_HasFeature(type, Py_TPFLAGS_HAVE_VERSION_TAG)) {
        ACCESS_ATTR_INC_STATS(no_opt_no_mcache);
        return false;
    }

    // Don't optimize attribute lookup for types that override tp_getattro or
    // tp_getattr.
    bool overridden = true;
    if (this->access_kind_ == ATTR_ACCESS_LOAD) {
        overridden = (type->tp_getattro != &PyObject_GenericGetAttr);
    } else if (this->access_kind_ == ATTR_ACCESS_STORE) {
        overridden = (type->tp_setattro != &PyObject_GenericSetAttr);
    } else {
        assert(0 && "invalid enum!");
    }
    if (overridden) {
        ACCESS_ATTR_INC_STATS(no_opt_overrode_access);
        return false;
    }

    // Do the lookups on the type.
    this->CacheTypeLookup();

    // If we find a descriptor with a getter, make sure its type supports the
    // method cache, or we won't be able to receive updates.
    if (this->descr_get_ != NULL &&
        !PyType_HasFeature(this->guard_descr_type_,
                           Py_TPFLAGS_HAVE_VERSION_TAG)) {
        ACCESS_ATTR_INC_STATS(no_opt_no_mcache);
        return false;
    }

    return true;
}

void
AttributeAccessor::CacheTypeLookup()
{
    this->dictoffset_ = this->guard_type_->tp_dictoffset;
    this->descr_ = _PyType_Lookup(this->guard_type_, this->name_);
    if (this->descr_ != NULL) {
        this->guard_descr_type_ = this->descr_->ob_type;
        if (PyType_HasFeature(this->guard_descr_type_, Py_TPFLAGS_HAVE_CLASS)) {
            this->descr_get_ = this->guard_descr_type_->tp_descr_get;
            this->descr_set_ = this->guard_descr_type_->tp_descr_set;
            if (this->descr_get_ != NULL && PyDescr_IsData(this->descr_)) {
                this->is_data_descr_ = true;
            }
        }
    }
}

void
AttributeAccessor::MakeLlvmValues()
{
    LlvmFunctionState *state = this->fbuilder_->state();
    this->guard_type_v_ =
        state->EmbedPointer<PyTypeObject*>(this->guard_type_);
    this->name_v_ = state->EmbedPointer<PyObject*>(this->name_);
    this->dictoffset_v_ =
        ConstantInt::get(PyTypeBuilder<long>::get(this->fbuilder_->context()),
                         this->dictoffset_);
    this->descr_v_ = state->EmbedPointer<PyObject*>(this->descr_);
    this->is_data_descr_v_ =
        ConstantInt::get(PyTypeBuilder<char>::get(this->fbuilder_->context()),
                         this->is_data_descr_);
}

void
AttributeAccessor::GuardAttributeAccess(Value *obj_v, BasicBlock *do_access)
{
    LlvmFunctionBuilder *fbuilder = this->fbuilder_;
    BuilderT &builder = this->fbuilder_->builder();
    LlvmFunctionState *state = this->fbuilder_->state();

    // Now that we know for sure that we are going to optimize this lookup, add
    // the type to the list of types we need to listen for modifications from
    // and make the llvm::Values.
    fbuilder->WatchType(this->guard_type_);
    this->MakeLlvmValues();

    BasicBlock *bail_block = state->CreateBasicBlock("ATTR_bail_block");
    BasicBlock *guard_type = state->CreateBasicBlock("ATTR_check_valid");
    BasicBlock *guard_descr = state->CreateBasicBlock("ATTR_check_descr");
    this->bail_block_ = bail_block;

    // Make sure that the code object is still valid.  This may fail if the
    // code object is invalidated inside of a call to the code object.
    builder.CreateCondBr(fbuilder->GetUseJitCond(), guard_type, bail_block);

    // Compare ob_type against type and bail if it's the wrong type.  Since
    // we've subscribed to the type object for modification updates, the code
    // will be invalidated before the type object is freed.  Therefore we don't
    // need to incref it, or any of its members.
    builder.SetInsertPoint(guard_type);
    Value *type_v = builder.CreateLoad(ObjectTy::ob_type(builder, obj_v));
    Value *is_right_type = builder.CreateICmpEQ(type_v, this->guard_type_v_);
    builder.CreateCondBr(is_right_type, guard_descr, bail_block);

    // If there is a descriptor, we need to guard on the descriptor type.  This
    // means emitting one more guard as well as subscribing to changes in the
    // descriptor type.
    builder.SetInsertPoint(guard_descr);
    if (this->descr_ != NULL) {
        fbuilder->WatchType(this->guard_descr_type_);
        Value *descr_type_v =
            builder.CreateLoad(ObjectTy::ob_type(builder, this->descr_v_));
        Value *guard_descr_type_v =
            state->EmbedPointer<PyTypeObject*>(this->guard_descr_type_);
        Value *is_right_descr_type =
            builder.CreateICmpEQ(descr_type_v, guard_descr_type_v);
        builder.CreateCondBr(is_right_descr_type, do_access, bail_block);
    } else {
        builder.CreateBr(do_access);
    }

    // Fill in the bail bb.
    builder.SetInsertPoint(bail_block);
    fbuilder->CreateGuardBailPoint(_PYGUARD_ATTR);
}

void
OpcodeAttributes::DELETE_ATTR(int index)
{
    Value *attr = this->fbuilder_->LookupName(index);
    Value *obj = this->fbuilder_->Pop();
    Value *value = this->state_->GetNull<PyObject*>();
    Function *pyobj_setattr = this->state_->GetGlobalFunction<
        int(PyObject *, PyObject *, PyObject *)>("PyObject_SetAttr");
    Value *result = this->state_->CreateCall(
        pyobj_setattr, obj, attr, value, "DELETE_ATTR_result");
    this->state_->DecRef(obj);
    this->fbuilder_->PropagateExceptionOnNonZero(result);
}

}
