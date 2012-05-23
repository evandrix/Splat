#include "Python.h"

#include "JIT/ConstantMirror.h"
#include "JIT/global_llvm_data.h"
#include "JIT/llvm_fbuilder.h"
#include "JIT/opcodes/call.h"

#include "llvm/BasicBlock.h"
#include "llvm/Function.h"
#include "llvm/Instructions.h"
#include "llvm/Support/ManagedStatic.h"
#include "llvm/Support/raw_ostream.h"

using llvm::BasicBlock;
using llvm::Constant;
using llvm::ConstantInt;
using llvm::Function;
using llvm::Type;
using llvm::Value;
using llvm::errs;

#ifdef Py_WITH_INSTRUMENTATION
class CallFunctionStats {
public:
    CallFunctionStats()
        : total(0), direct_calls(0), inlined(0),
          no_opt_kwargs(0), no_opt_params(0),
          no_opt_no_data(0), no_opt_polymorphic(0) {
    }

    ~CallFunctionStats() {
        errs() << "\nCALL_FUNCTION optimization:\n";
        errs() << "Total opcodes: " << this->total << "\n";
        errs() << "Direct C calls: " << this->direct_calls << "\n";
        errs() << "Inlined: " << this->inlined << "\n";
        errs() << "No opt: callsite kwargs: " << this->no_opt_kwargs << "\n";
        errs() << "No opt: function params: " << this->no_opt_params << "\n";
        errs() << "No opt: not C function: " << this->no_opt_not_cfunc << "\n";
        errs() << "No opt: no data: " << this->no_opt_no_data << "\n";
        errs() << "No opt: polymorphic: " << this->no_opt_polymorphic << "\n";
    }

    // How many CALL_FUNCTION opcodes were compiled.
    unsigned total;
    // How many CALL_FUNCTION opcodes were optimized to direct calls to C
    // functions.
    unsigned direct_calls;
    // How many calls were inlined into the caller.
    unsigned inlined;
    // We only optimize call sites without keyword, *args or **kwargs arguments.
    unsigned no_opt_kwargs;
    // We only optimize METH_ARG_RANGE functions so far.
    unsigned no_opt_params;
    // We only optimize callsites where we've collected data. Note that since
    // we record only PyCFunctions, any call to a Python function will show up
    // as having no data.
    unsigned no_opt_no_data;
    // We only optimize monomorphic callsites so far.
    unsigned no_opt_polymorphic;
    // We only optimize direct calls to C functions.
    unsigned no_opt_not_cfunc;
};

static llvm::ManagedStatic<CallFunctionStats> call_function_stats;

#define CF_INC_STATS(field) call_function_stats->field++
#else
#define CF_INC_STATS(field)
#endif  /* Py_WITH_INSTRUMENTATION */

namespace py {

OpcodeCall::OpcodeCall(LlvmFunctionBuilder *fbuilder) :
    fbuilder_(fbuilder),
    state_(fbuilder->state()),
    builder_(fbuilder->builder()),
    llvm_data_(fbuilder->llvm_data())
{
}

bool
OpcodeCall::CALL_FUNCTION_fast(int oparg)
{
    // Check for keyword arguments; we only optimize callsites with positional
    // arguments.
    if ((oparg >> 8) & 0xff) {
        CF_INC_STATS(no_opt_kwargs);
        return false;
    }

    // Only optimize monomorphic callsites.
    const PyRuntimeFeedback *feedback = this->fbuilder_->GetFeedback();
    if (!feedback) {
        CF_INC_STATS(no_opt_no_data);
        return false;
    }
    if (feedback->FuncsOverflowed()) {
        CF_INC_STATS(no_opt_polymorphic);
        return false;
    }

    llvm::SmallVector<PyTypeMethodPair, 3> fdo_data;
    feedback->GetSeenFuncsInto(fdo_data);
    if (fdo_data.size() != 1) {
#ifdef Py_WITH_INSTRUMENTATION
        if (fdo_data.size() == 0)
            CF_INC_STATS(no_opt_no_data);
        else
            CF_INC_STATS(no_opt_polymorphic);
#endif
        return false;
    }

    PyMethodDef *func_record = fdo_data[0].second;
    PyTypeObject *type_record = (PyTypeObject *)fdo_data[0].first;
    // We embed a pointer to type_record but we don't incref it because it can
    // only be PyCFunction_Type or PyMethodDescr_Type, which are statically
    // allocated anyway.
    if (type_record != &PyCFunction_Type &&
        type_record != &PyMethodDescr_Type) {
        CF_INC_STATS(no_opt_not_cfunc);
        return false;
    }
    bool func_is_cfunc = (type_record == &PyCFunction_Type);

    // Only optimize calls to C functions with a known number of parameters,
    // where the number of arguments we have is in that range.
    int flags = func_record->ml_flags;
    int min_arity = func_record->ml_min_arity;
    int max_arity = func_record->ml_max_arity;
    int num_args = oparg & 0xff;
    if (!(flags & METH_ARG_RANGE &&
          min_arity <= num_args && num_args <= max_arity)) {
        CF_INC_STATS(no_opt_params);
        return false;
    }
    assert(num_args <= PY_MAX_ARITY);

    PyCFunction cfunc_ptr = func_record->ml_meth;

    // Expose the C function pointer to LLVM. This is what will actually get
    // called.
    Constant *llvm_func =
        llvm_data_->constant_mirror().GetGlobalForCFunction(
            cfunc_ptr,
            max_arity,
            func_record->ml_name);

    BasicBlock *not_profiling =
        this->state_->CreateBasicBlock("CALL_FUNCTION_not_profiling");
    BasicBlock *check_is_same_func =
        this->state_->CreateBasicBlock("CALL_FUNCTION_check_is_same_func");
    BasicBlock *invalid_assumptions =
        this->state_->CreateBasicBlock("CALL_FUNCTION_invalid_assumptions");
    BasicBlock *all_assumptions_valid =
        this->state_->CreateBasicBlock("CALL_FUNCTION_all_assumptions_valid");

    this->fbuilder_->BailIfProfiling(not_profiling);

    // Handle bailing back to the interpreter if the assumptions below don't
    // hold.
    this->builder_.SetInsertPoint(invalid_assumptions);
    this->fbuilder_->CreateGuardBailPoint(_PYGUARD_CFUNC);

    this->builder_.SetInsertPoint(not_profiling);
#ifdef WITH_TSC
    this->state_->LogTscEvent(CALL_START_LLVM);
#endif
    // Retrieve the function to call from the Python stack.
    Value *stack_pointer =
        this->builder_.CreateLoad(this->fbuilder_->stack_pointer_addr());
    llvm_data_->tbaa_stack.MarkInstruction(stack_pointer);

    Value *actual_func = this->builder_.CreateLoad(
        this->builder_.CreateGEP(
            stack_pointer,
            ConstantInt::getSigned(
                Type::getInt64Ty(this->fbuilder_->context()),
                -num_args - 1)));

    // Make sure it's the right type; if not, bail.
    Value *actual_type = this->builder_.CreateLoad(
            ObjectTy::ob_type(this->builder_, actual_func));
    Value *right_type = this->state_->EmbedPointer<PyTypeObject*>(type_record);
    Value *is_right_type = this->builder_.CreateICmpEQ(
            actual_type, right_type, "is_right_type");
    this->builder_.CreateCondBr(is_right_type, check_is_same_func,
                                invalid_assumptions);

    // Make sure we got the same underlying function pointer; if not, bail.
    this->builder_.SetInsertPoint(check_is_same_func);
    Value *actual_as_righttype, *actual_method_def;
    if (func_is_cfunc) {
        const Type *pycfunction_ty =
            PyTypeBuilder<PyCFunctionObject *>::get(this->fbuilder_->context());
        actual_as_righttype = this->builder_.CreateBitCast(
            actual_func, pycfunction_ty);
        actual_method_def = this->builder_.CreateLoad(
            CFunctionTy::m_ml(this->builder_, actual_as_righttype),
            "CALL_FUNCTION_actual_method_def");
    } else {
        actual_as_righttype = this->builder_.CreateBitCast(
            actual_func,
            PyTypeBuilder<PyMethodDescrObject *>::get(
                this->fbuilder_->context()));
        actual_method_def = this->builder_.CreateLoad(
            MethodDescrTy::d_method(this->builder_, actual_as_righttype),
            "CALL_FUNCTION_actual_method_def");
    }

    Value *actual_func_ptr = this->builder_.CreateLoad(
        MethodDefTy::ml_meth(this->builder_, actual_method_def),
        "CALL_FUNCTION_actual_func_ptr");
    Value *is_same = this->builder_.CreateICmpEQ(
        // TODO(jyasskin): change this to "llvm_func" when
        // http://llvm.org/PR5126 is fixed.
        this->state_->EmbedPointer<PyCFunction>((void*)cfunc_ptr),
        actual_func_ptr);
    this->builder_.CreateCondBr(is_same,
        all_assumptions_valid, invalid_assumptions);

    // Once we get to this point, we know we can make some kind of fast call,
    // either, a) a specialized inline version, or b) a direct call to a C
    // function, bypassing the CPython function call machinery. We check them
    // in that order.
    this->builder_.SetInsertPoint(all_assumptions_valid);

    // Check if we are calling a built-in function that can be specialized.
    if (cfunc_ptr == _PyBuiltin_Len) {
        // Feedback index 0 is the function itself, index 1 is the first
        // argument.
        const PyTypeObject *arg1_type = this->fbuilder_->GetTypeFeedback(1);
        const char *function_name = NULL;
        if (arg1_type == &PyString_Type)
            function_name = "_PyLlvm_BuiltinLen_String";
        else if (arg1_type == &PyUnicode_Type)
            function_name = "_PyLlvm_BuiltinLen_Unicode";
        else if (arg1_type == &PyList_Type)
            function_name = "_PyLlvm_BuiltinLen_List";
        else if (arg1_type == &PyTuple_Type)
            function_name = "_PyLlvm_BuiltinLen_Tuple";
        else if (arg1_type == &PyDict_Type)
            function_name = "_PyLlvm_BuiltinLen_Dict";

        if (function_name != NULL) {
            this->CALL_FUNCTION_fast_len(actual_func, stack_pointer,
                                         invalid_assumptions,
                                         function_name);
            CF_INC_STATS(inlined);
            return true;
        }
    }

    // If we get here, we know we have a C function pointer
    // that takes some number of arguments: first the invocant, then some
    // PyObject *s. If the underlying function is nullary, we use NULL for the
    // second argument. Because "the invocant" differs between built-in
    // functions like len() and C-level methods like list.append(), we pull the
    // invocant (called m_self) from the PyCFunction object we popped
    // off the stack. Once the function returns, we patch up the stack pointer.
    llvm::SmallVector<Value*, PY_MAX_ARITY + 1> args;  // +1 for self.
    // If the function is a PyCFunction, pass its self member.
    if (func_is_cfunc) {
        Value *self = this->builder_.CreateLoad(
            CFunctionTy::m_self(this->builder_, actual_as_righttype),
            "CALL_FUNCTION_actual_self");
        args.push_back(self);
    }

    // Pass the arguments that are on the stack.
    for (int i = num_args; i >= 1; --i) {
        args.push_back(
            this->builder_.CreateLoad(
                this->builder_.CreateGEP(
                    stack_pointer,
                    ConstantInt::getSigned(
                        Type::getInt64Ty(this->fbuilder_->context()), -i))));
    }

    // Pad optional arguments with NULLs.
    for (int i = args.size(); i < max_arity + 1; ++i) {
        args.push_back(this->state_->GetNull<PyObject *>());
    }

    // Pass a single NULL after self for METH_NOARGS functions.
    if (args.size() == 1 && max_arity == 0) {
        args.push_back(this->state_->GetNull<PyObject *>());
    }

#ifdef WITH_TSC
    this->state_->LogTscEvent(CALL_ENTER_C);
#endif
    Value *result =
        this->state_->CreateCall(llvm_func, args.begin(), args.end());

    // Decref and the function and all of its arguments.
    this->state_->DecRef(actual_func);
    // If func is a cfunc, decrefing args[0] will cause self to be
    // double-decrefed, so avoid that.
    for (unsigned i = (func_is_cfunc ? 1 : 0); i < args.size(); ++i) {
        // If LLVM knows that args[i] is NULL, it will delete this code.
        this->state_->XDecRef(args[i]);
    }

    this->fbuilder_->SetOpcodeArguments(num_args + 1);
    this->fbuilder_->PropagateExceptionOnNull(result);
    this->fbuilder_->SetOpcodeResult(0, result);

    // Check signals and maybe switch threads after each function call.
    this->fbuilder_->CheckPyTicker();

    CF_INC_STATS(direct_calls);
    return true;
}

void
OpcodeCall::CALL_FUNCTION_fast_len(Value *actual_func,
                                   Value *stack_pointer,
                                   BasicBlock *invalid_assumptions,
                                   const char *function_name)
{
    BasicBlock *success = this->state_->CreateBasicBlock("BUILTIN_LEN_success");
    this->fbuilder_->SetOpcodeArguments(2);

    Value *obj = this->fbuilder_->GetOpcodeArg(1);
    Function *builtin_len =
        this->state_->GetGlobalFunction<PyObject *(PyObject *)>(function_name);

    Value *result = this->state_->CreateCall(builtin_len, obj,
                                             "BUILTIN_LEN_result");
    this->builder_.CreateCondBr(this->state_->IsNonZero(result),
                                success, invalid_assumptions);
    
    this->builder_.SetInsertPoint(success);
    this->state_->DecRef(actual_func);
    this->state_->DecRef(obj);

    this->fbuilder_->SetOpcodeResult(0, result);

    // Check signals and maybe switch threads after each function call.
    this->fbuilder_->CheckPyTicker();
}

void
OpcodeCall::CALL_FUNCTION_safe(int oparg)
{
#ifdef WITH_TSC
    this->state_->LogTscEvent(CALL_START_LLVM);
#endif
    Value *stack_pointer =
        this->builder_.CreateLoad(this->fbuilder_->stack_pointer_addr());
    llvm_data_->tbaa_stack.MarkInstruction(stack_pointer);

    int num_args = oparg & 0xff;
    int num_kwargs = (oparg>>8) & 0xff;
    Function *call_function = this->state_->GetGlobalFunction<
        PyObject *(PyObject **, int, int)>("_PyEval_CallFunction");
    Value *result = this->state_->CreateCall(
        call_function,
        stack_pointer,
        ConstantInt::get(PyTypeBuilder<int>::get(this->fbuilder_->context()),
                         num_args),
        ConstantInt::get(PyTypeBuilder<int>::get(this->fbuilder_->context()),
                         num_kwargs),
        "CALL_FUNCTION_result");

    this->fbuilder_->SetOpcodeArguments(num_args + 2*num_kwargs + 1);
    this->fbuilder_->PropagateExceptionOnNull(result);
    this->fbuilder_->SetOpcodeResult(0, result);

    // Check signals and maybe switch threads after each function call.
    this->fbuilder_->CheckPyTicker();
}

void
OpcodeCall::CALL_FUNCTION(int oparg)
{
    CF_INC_STATS(total);
    if (!this->CALL_FUNCTION_fast(oparg)) {
        this->CALL_FUNCTION_safe(oparg);
    }
}

void
OpcodeCall::CALL_METHOD(int oparg)
{
    // We only want to generate code to handle one case, but we need to be
    // robust in the face of malformed code objects, which might cause there to
    // be mismatched LOAD_METHOD/CALL_METHOD opcodes.  Therefore the value we
    // get from the loads_optimized_ stack is only a guess, but it should be
    // accurate for all code objects with matching loads and calls.
    bool load_optimized = false;
    std::vector<bool> &loads_optimized = this->fbuilder_->loads_optimized();
    if (!loads_optimized.empty()) {
        load_optimized = loads_optimized.back();
        loads_optimized.pop_back();
    }

    BasicBlock *call_block = state_->CreateBasicBlock("CALL_METHOD_call");
    BasicBlock *bail_block = state_->CreateBasicBlock("CALL_METHOD_bail");

    int num_args = (oparg & 0xff);
    int num_kwargs = (oparg>>8) & 0xff;
    // +1 for the actual function object, +1 for self.
    int num_stack_slots = num_args + 2 * num_kwargs + 1 + 1;

    // Look down the stack for the cell that is either padding or a method.
    Value *stack_pointer =
        this->builder_.CreateLoad(this->fbuilder_->stack_pointer_addr());
    Value *stack_idx =
        ConstantInt::getSigned(Type::getInt32Ty(this->fbuilder_->context()),
                               -num_stack_slots);
    Value *padding_ptr = this->builder_.CreateGEP(stack_pointer,
                                                       stack_idx);
    Value *method_or_padding = this->builder_.CreateLoad(padding_ptr);

    // Depending on how we optimized the load, we either expect it to be NULL
    // or we expect it to be non-NULL.  We bail if it's not what we expect.
    Value *bail_cond = state_->IsNull(method_or_padding);
    if (!load_optimized) {
        bail_cond = this->builder_.CreateNot(bail_cond);
    }
    this->builder_.CreateCondBr(bail_cond, bail_block, call_block);

    // Restore the stack in the bail bb.
    this->builder_.SetInsertPoint(bail_block);
    this->fbuilder_->CreateGuardBailPoint(_PYGUARD_CALL_METHOD);

    this->builder_.SetInsertPoint(call_block);
    if (load_optimized) {
        // Increment the argument count in oparg and do a regular CALL_FUNCTION.
        assert((num_args + 1) <= 0xff &&
               "TODO(rnk): Deal with oparg overflow.");
        oparg = (oparg & ~0xff) | ((num_args + 1) & 0xff);
    }

    this->CALL_FUNCTION(oparg);

    if (!load_optimized) {
        // Use a sub-opcode to remove the padding.
        this->fbuilder_->FinishOpcodeImpl(1);

        // Pop off the padding cell.
        this->fbuilder_->SetOpcodeArguments(2);
        Value *result = this->fbuilder_->GetOpcodeArg(1);
        Value *padding = this->fbuilder_->GetOpcodeArg(0);
        this->state_->Assert(this->state_->IsNull(padding),
                             "Padding was non-NULL!");
        this->fbuilder_->SetOpcodeResult(0, result);
    }
}

// Keep this in sync with eval.cc
#define CALL_FLAG_VAR 1
#define CALL_FLAG_KW 2

void
OpcodeCall::CallVarKwFunction(int oparg, int call_flag)
{
#ifdef WITH_TSC
    this->state_->LogTscEvent(CALL_START_LLVM);
#endif
    Value *stack_pointer =
        this->builder_.CreateLoad(this->fbuilder_->stack_pointer_addr());
    llvm_data_->tbaa_stack.MarkInstruction(stack_pointer);

    int num_args = oparg & 0xff;
    int num_kwargs = (oparg>>8) & 0xff;
    Function *call_function = this->state_->GetGlobalFunction<
        PyObject *(PyObject **, int, int, int)>("_PyEval_CallFunctionVarKw");
    Value *result = this->state_->CreateCall(
        call_function,
        stack_pointer,
        ConstantInt::get(PyTypeBuilder<int>::get(this->fbuilder_->context()),
                         num_args),
        ConstantInt::get(PyTypeBuilder<int>::get(this->fbuilder_->context()),
                         num_kwargs),
        ConstantInt::get(PyTypeBuilder<int>::get(this->fbuilder_->context()),
                         call_flag),
        "CALL_FUNCTION_VAR_KW_result");
    int stack_items = num_args + 2 * num_kwargs + 1;
    if (call_flag & CALL_FLAG_VAR) {
        ++stack_items;
    }
    if (call_flag & CALL_FLAG_KW) {
        ++stack_items;
    }
    this->fbuilder_->SetOpcodeArguments(stack_items);
    this->fbuilder_->PropagateExceptionOnNull(result);
    this->fbuilder_->SetOpcodeResult(0, result);

    // Check signals and maybe switch threads after each function call.
    this->fbuilder_->CheckPyTicker();
}

void
OpcodeCall::CALL_FUNCTION_VAR(int oparg)
{
#ifdef WITH_TSC
    this->state_->LogTscEvent(CALL_START_LLVM);
#endif
    this->CallVarKwFunction(oparg, CALL_FLAG_VAR);
}

void
OpcodeCall::CALL_FUNCTION_KW(int oparg)
{
#ifdef WITH_TSC
    this->state_->LogTscEvent(CALL_START_LLVM);
#endif
    this->CallVarKwFunction(oparg, CALL_FLAG_KW);
}

void
OpcodeCall::CALL_FUNCTION_VAR_KW(int oparg)
{
#ifdef WITH_TSC
    this->state_->LogTscEvent(CALL_START_LLVM);
#endif
    this->CallVarKwFunction(oparg, CALL_FLAG_KW | CALL_FLAG_VAR);
}

#undef CALL_FLAG_VAR
#undef CALL_FLAG_KW

}
