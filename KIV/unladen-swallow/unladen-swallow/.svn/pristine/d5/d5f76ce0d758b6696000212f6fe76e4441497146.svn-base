#include "JIT/llvm_state.h"

#include "JIT/ConstantMirror.h"

#include "llvm/ADT/Twine.h"
#include "llvm/BasicBlock.h"
#include "llvm/Constant.h"
#include "llvm/Constants.h"
#include "llvm/Instructions.h"
#include "llvm/Intrinsics.h"
#include "llvm/Module.h"
#include "llvm/Type.h"

#include <string>

namespace Intrinsic = llvm::Intrinsic;
using llvm::BasicBlock;
using llvm::Constant;
using llvm::ConstantInt;
using llvm::Function;
using llvm::FunctionType;
using llvm::Module;
using llvm::Type;
using llvm::Value;

namespace py {

static std::string
pystring_to_std_string(PyObject *str)
{
    assert(PyString_Check(str));
    return std::string(PyString_AS_STRING(str), PyString_GET_SIZE(str));
}

static const FunctionType *
get_function_type(Module *module)
{
    std::string function_type_name("__function_type");
    const FunctionType *result =
        llvm::cast_or_null<FunctionType>(
            module->getTypeByName(function_type_name));
    if (result != NULL)
        return result;

    result = PyTypeBuilder<PyObject*(PyFrameObject*)>::get(
        module->getContext());
    module->addTypeName(function_type_name, result);
    return result;
}

LlvmFunctionState::LlvmFunctionState(
    PyGlobalLlvmData *llvm_data, PyCodeObject *code_object)
    : llvm_data_(llvm_data),
      context_(this->llvm_data_->context()),
      module_(this->llvm_data_->module()),
      function_(Function::Create(
                    get_function_type(this->module_),
                    llvm::GlobalValue::ExternalLinkage,
                    // Prefix names with #u# to avoid collisions
                    // with runtime functions.
                    "#u#" + pystring_to_std_string(code_object->co_name),
                    this->module_)),
      builder_(this->context_,
               llvm::TargetFolder(
                   llvm_data_->getExecutionEngine()->getTargetData()))
{
}

void
LlvmFunctionState::MemCpy(llvm::Value *target,
                          llvm::Value *array, llvm::Value *N)
{
    const Type *len_type[] = { Type::getInt64Ty(this->context_) };
    Value *memcpy = Intrinsic::getDeclaration(
        this->module_, Intrinsic::memcpy, len_type, 1);
    assert(target->getType() == array->getType() &&
           "memcpy's source and destination should have the same type.");
    // Calculate the length as int64_t(&array_type(NULL)[N]).
    Value *length = this->builder_.CreatePtrToInt(
        this->builder_.CreateGEP(Constant::getNullValue(array->getType()), N),
        Type::getInt64Ty(this->context_));
    const Type *char_star_type = PyTypeBuilder<char*>::get(this->context_);
    this->CreateCall(
        memcpy,
        this->builder_.CreateBitCast(target, char_star_type),
        this->builder_.CreateBitCast(array, char_star_type),
        length,
        // Unknown alignment.
        ConstantInt::get(Type::getInt32Ty(this->context_), 0));
}

llvm::BasicBlock *
LlvmFunctionState::CreateBasicBlock(const llvm::Twine &name)
{
    return BasicBlock::Create(this->context_, name, this->function_);
}

void
LlvmFunctionState::IncRef(Value *value)
{
    Function *incref = this->GetGlobalFunction<void(PyObject*)>(
        "_PyLlvm_WrapIncref");
    this->CreateCall(incref, value);
}

void
LlvmFunctionState::DecRef(Value *value)
{
    Function *decref = this->GetGlobalFunction<void(PyObject*)>(
        "_PyLlvm_WrapDecref");
    this->CreateCall(decref, value);
}

void
LlvmFunctionState::XDecRef(Value *value)
{
    Function *xdecref = this->GetGlobalFunction<void(PyObject*)>(
        "_PyLlvm_WrapXDecref");
    this->CreateCall(xdecref, value);
}

// For llvm::Functions, copy callee's calling convention and attributes to
// callsite; for non-Functions, leave the default calling convention and
// attributes in place (ie, do nothing). We require this for function pointers.
llvm::CallInst *
TransferAttributes(llvm::CallInst *callsite, const llvm::Value* callee)
{
    if (const llvm::GlobalAlias *alias =
            llvm::dyn_cast<llvm::GlobalAlias>(callee))
        callee = alias->getAliasedGlobal();

    if (const llvm::Function *func = llvm::dyn_cast<llvm::Function>(callee)) {
        callsite->setCallingConv(func->getCallingConv());
        callsite->setAttributes(func->getAttributes());
    }
    return callsite;
}

llvm::CallInst *
LlvmFunctionState::CreateCall(llvm::Value *callee, const char *name)
{
    llvm::CallInst *call = this->builder_.CreateCall(callee, name);
    return TransferAttributes(call, callee);
}

llvm::CallInst *
LlvmFunctionState::CreateCall(llvm::Value *callee, llvm::Value *arg1,
                              const char *name)
{
    llvm::CallInst *call = this->builder_.CreateCall(callee, arg1, name);
    return TransferAttributes(call, callee);
}

llvm::CallInst *
LlvmFunctionState::CreateCall(llvm::Value *callee, llvm::Value *arg1,
                              llvm::Value *arg2, const char *name)
{
    llvm::CallInst *call = this->builder_.CreateCall2(callee, arg1, arg2, name);
    return TransferAttributes(call, callee);
}

llvm::CallInst *
LlvmFunctionState::CreateCall(llvm::Value *callee, llvm::Value *arg1,
                              llvm::Value *arg2, llvm::Value *arg3,
                              const char *name)
{
    llvm::CallInst *call = this->builder_.CreateCall3(callee, arg1, arg2, arg3,
                                                      name);
    return TransferAttributes(call, callee);
}

llvm::CallInst *
LlvmFunctionState::CreateCall(llvm::Value *callee, llvm::Value *arg1,
                              llvm::Value *arg2, llvm::Value *arg3,
                              llvm::Value *arg4, const char *name)
{
    llvm::CallInst *call = this->builder_.CreateCall4(callee, arg1, arg2, arg3,
                                                      arg4, name);
    return TransferAttributes(call, callee);
}

llvm::Constant *
LlvmFunctionState::GetGlobalVariableFor(PyObject *obj)
{
    return this->llvm_data_->constant_mirror().GetGlobalVariableFor(obj);
}

Value *
LlvmFunctionState::IsNull(Value *value)
{
    return this->builder_.CreateICmpEQ(
        value, Constant::getNullValue(value->getType()));
}

Value *
LlvmFunctionState::IsNonZero(Value *value)
{
    return this->builder_.CreateICmpNE(
        value, Constant::getNullValue(value->getType()));
}

Value *
LlvmFunctionState::IsNegative(Value *value)
{
    return this->builder_.CreateICmpSLT(
        value, ConstantInt::getSigned(value->getType(), 0));
}

Value *
LlvmFunctionState::IsPositive(Value *value)
{
    return this->builder_.CreateICmpSGT(
        value, ConstantInt::getSigned(value->getType(), 0));
}

Value *
LlvmFunctionState::IsInstanceOfFlagClass(llvm::Value *value, int flag)
{
    Value *type = this->builder_.CreateBitCast(
        this->builder_.CreateLoad(
            ObjectTy::ob_type(this->builder_, value),
            "type"),
        PyTypeBuilder<PyTypeObject *>::get(this->context_));
    Value *type_flags = this->builder_.CreateLoad(
        TypeTy::tp_flags(this->builder_, type),
        "type_flags");
    Value *is_instance = this->builder_.CreateAnd(
        type_flags,
        ConstantInt::get(type_flags->getType(), flag));
    return this->IsNonZero(is_instance);
}

void
LlvmFunctionState::Assert(llvm::Value *should_be_true,
                          const std::string &failure_message)
{
#ifndef NDEBUG
    BasicBlock *assert_passed =
            this->CreateBasicBlock(failure_message + "_assert_passed");
    BasicBlock *assert_failed =
            this->CreateBasicBlock(failure_message + "_assert_failed");
    this->builder_.CreateCondBr(should_be_true, assert_passed, assert_failed);

    this->builder_.SetInsertPoint(assert_failed);
    this->Abort(failure_message);
    this->builder_.CreateUnreachable();

    this->builder_.SetInsertPoint(assert_passed);
#endif
}

void
LlvmFunctionState::Abort(const std::string &failure_message)
{
    this->CreateCall(
        this->GetGlobalFunction<int(const char*)>("puts"),
        this->llvm_data_->GetGlobalStringPtr(failure_message));
    this->CreateCall(this->GetGlobalFunction<void()>("abort"));
}

Value *
LlvmFunctionState::GetListItemSlot(Value *lst, int idx)
{
    Value *listobj = this->builder_.CreateBitCast(
        lst, PyTypeBuilder<PyListObject *>::get(this->context_));
    // Load the target of the ob_item PyObject** into list_items.
    Value *list_items = this->builder_.CreateLoad(
        ListTy::ob_item(this->builder_, listobj));
    // GEP the list_items PyObject* up to the desired item
    const Type *int_type = Type::getInt32Ty(this->context_);
    return this->builder_.CreateGEP(list_items,
                                    ConstantInt::get(int_type, idx),
                                    "list_item_slot");
}

Value *
LlvmFunctionState::GetTupleItemSlot(Value *tup, int idx)
{
    Value *tupobj = this->builder_.CreateBitCast(
        tup, PyTypeBuilder<PyTupleObject*>::get(this->context_));
    // Make CreateGEP perform &tup_item_indices[0].ob_item[idx].
    Value *tuple_items = TupleTy::ob_item(this->builder_, tupobj);
    return this->builder_.CreateStructGEP(tuple_items, idx,
                                          "tuple_item_slot");
}

#ifdef WITH_TSC
void
LlvmFunctionState::LogTscEvent(_PyTscEventId event_id)
{
    Function *timer_function = this->GetGlobalFunction<void (int)>(
            "_PyLog_TscEvent");
    // Int8Ty doesn't seem to work here, so we use Int32Ty instead.
    Value *enum_ir = ConstantInt::get(Type::getInt32Ty(this->context_),
                                      event_id);
    this->CreateCall(timer_function, enum_ir);
}
#endif

Value *
LlvmFunctionState::CreateAllocaInEntryBlock(
    const Type *alloca_type, Value *array_size, const char *name="")
{
    // In order for LLVM to optimize alloca's, we should emit alloca
    // instructions in the function entry block. We can get at the
    // block with this->function_->begin(), but it will already have a
    // 'br' instruction at the end. Instantiating the AllocaInst class
    // directly, we pass it the begin() iterator of the entry block,
    // causing it to insert itself right before the first instruction
    // in the block.
    return new llvm::AllocaInst(alloca_type, array_size, name,
                                this->function_->begin()->begin());
}

}
