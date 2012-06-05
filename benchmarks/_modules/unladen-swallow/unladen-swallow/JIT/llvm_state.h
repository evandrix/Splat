// -*- C++ -*-
#ifndef PYTHON_LLVM_STATE_H
#define PYTHON_LLVM_STATE_H

#ifndef __cplusplus
#error This header expects to be included only in C++ source
#endif

#include "Util/EventTimer.h"

#include "JIT/PyTypeBuilder.h"
#include "llvm/ADT/Twine.h"
#include "llvm/Analysis/DebugInfo.h"
#include "llvm/Constants.h"
#include "llvm/ExecutionEngine/ExecutionEngine.h"
#include "llvm/GlobalVariable.h"
#include "llvm/Support/IRBuilder.h"
#include "llvm/Support/TargetFolder.h"
#include "llvm/Type.h"

struct PyCodeObject;
struct PyGlobalLlvmData;

namespace py {

llvm::CallInst *
TransferAttributes(llvm::CallInst *callsite, const llvm::Value* callee);

// LlvmFunctionState contains objects which must only be created once
// for every LLVM function. A compiled python function may contain
// code from more than one code object.
class LlvmFunctionState {
    LlvmFunctionState(const LlvmFunctionState &);
    void operator=(const LlvmFunctionState &);
public:
    LlvmFunctionState(PyGlobalLlvmData *global_data, PyCodeObject *code);

    llvm::Function *function() { return function_; }
    typedef llvm::IRBuilder<true, llvm::TargetFolder> BuilderT;
    BuilderT& builder() { return builder_; }
    llvm::LLVMContext& context() { return this->context_; }
    llvm::Module *module() const { return this->module_; }
    PyGlobalLlvmData *llvm_data() const { return this->llvm_data_; }

    // Copies the elements from array[0] to array[N-1] to target, bytewise.
    void MemCpy(llvm::Value *target, llvm::Value *array, llvm::Value *N);

    template<typename T>
    llvm::Constant *GetSigned(int64_t val) {
        return llvm::ConstantInt::getSigned(
             PyTypeBuilder<T>::get(this->context_), val);
    }

    /// Get the LLVM NULL Value for the given type.
    template<typename T>
    llvm::Value *GetNull()
    {
        return llvm::Constant::getNullValue(
            PyTypeBuilder<T>::get(this->context_));
    }

    /// Convenience wrapper for creating named basic blocks using the current
    /// context and function.
    llvm::BasicBlock *CreateBasicBlock(const llvm::Twine &name);

    /// These two functions increment or decrement the reference count
    /// of a PyObject*. The behavior is undefined if the Value's type
    /// isn't PyObject* or a subclass.
    void IncRef(llvm::Value *value);
    void DecRef(llvm::Value *value);
    void XDecRef(llvm::Value *value);

    // These are just like the CreateCall* calls on IRBuilder, except they also
    // apply callee's calling convention and attributes to the call site.
    llvm::CallInst *CreateCall(llvm::Value *callee,
                               const char *name = "");
    llvm::CallInst *CreateCall(llvm::Value *callee,
                               llvm::Value *arg1,
                               const char *name = "");
    llvm::CallInst *CreateCall(llvm::Value *callee,
                               llvm::Value *arg1,
                               llvm::Value *arg2,
                               const char *name = "");
    llvm::CallInst *CreateCall(llvm::Value *callee,
                               llvm::Value *arg1,
                               llvm::Value *arg2,
                               llvm::Value *arg3,
                               const char *name = "");
    llvm::CallInst *CreateCall(llvm::Value *callee,
                               llvm::Value *arg1,
                               llvm::Value *arg2,
                               llvm::Value *arg3,
                               llvm::Value *arg4,
                               const char *name = "");
    template<typename InputIterator>
    llvm::CallInst *CreateCall(llvm::Value *callee,
                               InputIterator begin,
                               InputIterator end,
                               const char *name = "")
    {
        llvm::CallInst *call =
            this->builder().CreateCall(callee, begin, end, name);
        return TransferAttributes(call, callee);
    }

    // Returns the global variable with type T, address 'var_address',
    // and name 'name'.  If the ExecutionEngine already knows of a
    // variable with the given address, we name and return it.
    // Otherwise the variable will be looked up in Python's C runtime.
    template<typename VariableType>
    llvm::Constant *GetGlobalVariable(
        void *var_address, const std::string &name);

    // Returns the global function with type T and name 'name'. The
    // function will be looked up in Python's C runtime.
    template<typename FunctionType>
    llvm::Function *GetGlobalFunction(const std::string &name)
    {
        return llvm::cast<llvm::Function>(
            this->module()->getOrInsertFunction(name,
                PyTypeBuilder<FunctionType>::get(this->context_)));
    }

    // Returns a global variable that represents 'obj'.  These get
    // cached in the ExecutionEngine's global mapping table, and they
    // incref the object so its address doesn't get re-used while the
    // GlobalVariable is still alive.  See JIT/ConstantMirror.h for
    // more details.  Use this in preference to GetGlobalVariable()
    // for PyObjects that may be immutable.
    llvm::Constant *GetGlobalVariableFor(PyObject *obj);

    // Returns an i1, true if value represents a NULL pointer.
    llvm::Value *IsNull(llvm::Value *value);
    // Returns an i1, true if value is a negative integer.
    llvm::Value *IsNegative(llvm::Value *value);
    // Returns an i1, true if value is a non-zero integer.
    llvm::Value *IsNonZero(llvm::Value *value);
    // Returns an i1, true if value is a positive (>0) integer.
    llvm::Value *IsPositive(llvm::Value *value);
    // Returns an i1, true if value is an instance of the class
    // represented by the flag argument.  flag should be something
    // like Py_TPFLAGS_INT_SUBCLASS.
    llvm::Value *IsInstanceOfFlagClass(llvm::Value *value, int flag);

    /// Implements something like the C assert statement.  If
    /// should_be_true (an i1) is false, prints failure_message (with
    /// puts) and aborts.  Compiles to nothing in optimized mode.
    void Assert(llvm::Value *should_be_true,
                const std::string &failure_message);

    /// Prints failure_message (with puts) and aborts.
    void Abort(const std::string &failure_message);

    // Get the address of the idx'th item in a list or tuple object.
    llvm::Value *GetListItemSlot(llvm::Value *lst, int idx);
    llvm::Value *GetTupleItemSlot(llvm::Value *tup, int idx);

#ifdef WITH_TSC
    // Emit code to record a given event with the TSC EventTimer.h system.
    void LogTscEvent(_PyTscEventId event_id);
#endif

    // Create an alloca in the entry block, so that LLVM can optimize
    // it more easily, and return the resulting address. The signature
    // matches IRBuilder.CreateAlloca()'s.
    llvm::Value *CreateAllocaInEntryBlock(
        const llvm::Type *alloca_type,
        llvm::Value *array_size,
        const char *name);

    /// Embed a pointer of some type directly into the LLVM IR.
    template <typename T>
    llvm::Value *EmbedPointer(void *ptr)
    {
        // We assume that the caller has ensured that ptr will stay live for the
        // life of this native code object.
        return this->builder_.CreateIntToPtr(
            llvm::ConstantInt::get(llvm::Type::getInt64Ty(this->context_),
                             reinterpret_cast<intptr_t>(ptr)),
            PyTypeBuilder<T>::get(this->context_));
    }

private:
    PyGlobalLlvmData *const llvm_data_;
    llvm::LLVMContext &context_;
    llvm::Module *const module_;

    llvm::Function *const function_;
    BuilderT builder_;
};

template<typename VariableType> llvm::Constant *
LlvmFunctionState::GetGlobalVariable(void *var_address, const std::string &name)
{
    const llvm::Type *expected_type =
        PyTypeBuilder<VariableType>::get(this->context_);
    if (llvm::GlobalVariable *global = this->module_->getNamedGlobal(name)) {
        assert (expected_type == global->getType()->getElementType());
        return global;
    }
    if (llvm::GlobalValue *global = const_cast<llvm::GlobalValue*>(
            this->llvm_data_->getExecutionEngine()->
            getGlobalValueAtAddress(var_address))) {
        assert (expected_type == global->getType()->getElementType());
        if (!global->hasName())
            global->setName(name);
        return global;
    }
    return new llvm::GlobalVariable(*this->module_, expected_type,
                                    /*isConstant=*/false,
                                    llvm::GlobalValue::ExternalLinkage,
                                    NULL, name);
}

}  // namespace py

#endif  // PYTHON_LLVM_STATE_H
