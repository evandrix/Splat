#include "Python.h"
#include "opcode.h"

#include "JIT/opcodes/block.h"
#include "JIT/llvm_fbuilder.h"

#include "llvm/ADT/STLExtras.h"
#include "llvm/BasicBlock.h"
#include "llvm/Function.h"
#include "llvm/Instructions.h"

using llvm::BasicBlock;
using llvm::ConstantInt;
using llvm::Function;
using llvm::Type;
using llvm::Value;
using llvm::array_endof;

// Use like "this->GET_GLOBAL_VARIABLE(Type, variable)".
#define GET_GLOBAL_VARIABLE(TYPE, VARIABLE) \
    GetGlobalVariable<TYPE>(&VARIABLE, #VARIABLE)

namespace py {

OpcodeBlock::OpcodeBlock(LlvmFunctionBuilder *fbuilder) :
    fbuilder_(fbuilder),
    state_(fbuilder->state()),
    builder_(fbuilder->builder()),
    llvm_data_(fbuilder->llvm_data())
{
}

void
OpcodeBlock::SETUP_LOOP(llvm::BasicBlock *target,
                        int target_opindex,
                        llvm::BasicBlock *fallthrough)
{
    this->CallBlockSetup(::SETUP_LOOP, target, target_opindex);
}

void
OpcodeBlock::POP_BLOCK()
{
    Value *block_info = this->state_->CreateCall(
        this->state_->GetGlobalFunction<PyTryBlock *(PyTryBlock *, char *)>(
            "_PyLlvm_Frame_BlockPop"),
        this->fbuilder_->blockstack_addr(),
        this->fbuilder_->num_blocks_addr());
    Value *pop_to_level = this->builder_.CreateLoad(
        PyTypeBuilder<PyTryBlock>::b_level(this->builder_, block_info));
    Value *pop_to_addr =
        this->builder_.CreateGEP(this->fbuilder_->stack_bottom(), pop_to_level);
    this->fbuilder_->PopAndDecrefTo(pop_to_addr);
}

void
OpcodeBlock::SETUP_EXCEPT(llvm::BasicBlock *target,
                          int target_opindex,
                          llvm::BasicBlock *fallthrough)
{
    this->CallBlockSetup(::SETUP_EXCEPT, target, target_opindex);
    llvm::BasicBlock *block = this->builder_.GetInsertBlock();
    this->builder_.SetInsertPoint(target);
    this->fbuilder_->PushException();
    this->builder_.SetInsertPoint(block);
}

void
OpcodeBlock::SETUP_FINALLY(llvm::BasicBlock *target,
                           int target_opindex,
                           llvm::BasicBlock *fallthrough)
{
    BasicBlock *unwind =
        this->state_->CreateBasicBlock("SETUP_FINALLY_unwind");
    this->CallBlockSetup(::SETUP_FINALLY, unwind, target_opindex);
    llvm::BasicBlock *block = this->builder_.GetInsertBlock();
    this->builder_.SetInsertPoint(unwind);
    this->fbuilder_->PushException();
    this->builder_.CreateBr(target);
    this->builder_.SetInsertPoint(block);
}

void
OpcodeBlock::CallBlockSetup(int block_type, llvm::BasicBlock *handler,
                            int handler_opindex)
{
    Value *stack_level = this->fbuilder_->GetStackLevel();
    Value *unwind_target_index =
        this->fbuilder_->AddUnwindTarget(handler, handler_opindex);
    Function *blocksetup =
        this->state_->GetGlobalFunction<void(PyTryBlock *, char *, int, int, int)>(
            "_PyLlvm_Frame_BlockSetup");
    Value *args[] = {
        this->fbuilder_->blockstack_addr(), this->fbuilder_->num_blocks_addr(),
        ConstantInt::get(PyTypeBuilder<int>::get(this->fbuilder_->context()),
                         block_type),
        unwind_target_index,
        stack_level
    };
    this->state_->CreateCall(blocksetup, args, array_endof(args));
}

void
OpcodeBlock::END_FINALLY()
{
    Value *finally_discriminator = this->fbuilder_->Pop();
    Value *second = this->fbuilder_->Pop();
    Value *third = this->fbuilder_->Pop();
    // END_FINALLY is fairly complicated. It decides what to do based
    // on the top value in the stack.  If that value is an int, it's
    // interpreted as one of the unwind reasons.  If it's an exception
    // type, the next two stack values are the rest of the exception,
    // and it's re-raised.  Otherwise, it's supposed to be None,
    // indicating that the finally was entered through normal control
    // flow.

    BasicBlock *unwind_code =
        this->state_->CreateBasicBlock("unwind_code");
    BasicBlock *test_exception =
        this->state_->CreateBasicBlock("test_exception");
    BasicBlock *reraise_exception =
        this->state_->CreateBasicBlock("reraise_exception");
    BasicBlock *check_none = this->state_->CreateBasicBlock("check_none");
    BasicBlock *not_none = this->state_->CreateBasicBlock("not_none");
    BasicBlock *finally_fallthrough =
        this->state_->CreateBasicBlock("finally_fallthrough");

    this->builder_.CreateCondBr(
        this->state_->IsInstanceOfFlagClass(finally_discriminator,
                                            Py_TPFLAGS_INT_SUBCLASS),
        unwind_code, test_exception);

    this->builder_.SetInsertPoint(unwind_code);
    // The top of the stack was an int, interpreted as an unwind code.
    // If we're resuming a return or continue, the return value or
    // loop target (respectively) is now on top of the stack and needs
    // to be popped off.
    Value *unwind_reason = this->builder_.CreateTrunc(
        this->state_->CreateCall(
            this->state_->GetGlobalFunction<long(PyObject *)>("PyInt_AsLong"),
            finally_discriminator),
        Type::getInt8Ty(this->fbuilder_->context()),
        "unwind_reason");
    this->state_->DecRef(finally_discriminator);
    this->state_->DecRef(third);
    // Save the unwind reason for when we jump to the unwind block.
    this->builder_.CreateStore(unwind_reason,
                               this->fbuilder_->unwind_reason_addr());
    // Check if we need to pop the return value or loop target.
    BasicBlock *store_retval = this->state_->CreateBasicBlock("store_retval");
    BasicBlock *decref_second = this->state_->CreateBasicBlock("decref_second");
    llvm::SwitchInst *should_store_retval =
        this->builder_.CreateSwitch(unwind_reason, decref_second, 2);
    should_store_retval->addCase(
        ConstantInt::get(Type::getInt8Ty(this->fbuilder_->context()),
                         UNWIND_RETURN),
        store_retval);
    should_store_retval->addCase(
        ConstantInt::get(Type::getInt8Ty(this->fbuilder_->context()),
                         UNWIND_CONTINUE),
        store_retval);

    this->builder_.SetInsertPoint(store_retval);
    // We're continuing a return or continue.  Retrieve its argument.
    this->builder_.CreateStore(second, this->fbuilder_->retval_addr());
    this->builder_.CreateBr(this->fbuilder_->unwind_block());

    this->builder_.SetInsertPoint(decref_second);
    this->state_->DecRef(second);
    this->builder_.CreateBr(this->fbuilder_->unwind_block());

    this->builder_.SetInsertPoint(test_exception);
    Value *is_exception_or_string = this->state_->CreateCall(
        this->state_->GetGlobalFunction<int(PyObject *)>(
            "_PyLlvm_WrapIsExceptionOrString"),
        finally_discriminator);
    this->builder_.CreateCondBr(
        this->state_->IsNonZero(is_exception_or_string),
        reraise_exception, check_none);

    this->builder_.SetInsertPoint(reraise_exception);
    Value *err_type = finally_discriminator;
    Value *err_value = second;
    Value *err_traceback = third;
    this->state_->CreateCall(
        this->state_->GetGlobalFunction<
            void(PyObject *, PyObject *, PyObject *)>("PyErr_Restore"),
        err_type, err_value, err_traceback);
    // This is a "re-raise" rather than a new exception, so we don't
    // jump to the propagate_exception_block_.
    this->builder_.CreateStore(this->state_->GetNull<PyObject*>(),
                               this->fbuilder_->retval_addr());
    this->builder_.CreateStore(
        ConstantInt::get(Type::getInt8Ty(this->fbuilder_->context()),
                         UNWIND_EXCEPTION),
        this->fbuilder_->unwind_reason_addr());
    this->builder_.CreateBr(this->fbuilder_->unwind_block());

    this->builder_.SetInsertPoint(check_none);
    // The contents of the try block push None onto the stack just
    // before falling through to the finally block.  If we didn't get
    // an unwind reason or an exception, we expect to fall through,
    // but for sanity we also double-check that the None is present.
    Value *is_none = this->builder_.CreateICmpEQ(
        finally_discriminator,
        this->state_->GetGlobalVariableFor(&_Py_NoneStruct));
    this->state_->DecRef(finally_discriminator);
    this->state_->DecRef(second);
    this->state_->DecRef(third);
    this->builder_.CreateCondBr(is_none, finally_fallthrough, not_none);

    this->builder_.SetInsertPoint(not_none);
    // If we didn't get a None, raise a SystemError.
    Value *system_error = this->builder_.CreateLoad(
        this->state_->GET_GLOBAL_VARIABLE(PyObject *, PyExc_SystemError));
    Value *err_msg = llvm_data_->GetGlobalStringPtr(
        "'finally' pops bad exception");
    this->state_->CreateCall(
        this->state_->GetGlobalFunction<void(PyObject *, const char *)>(
            "PyErr_SetString"),
        system_error, err_msg);
    this->builder_.CreateStore(
        ConstantInt::get(Type::getInt8Ty(this->fbuilder_->context()),
                         UNWIND_EXCEPTION),
        this->fbuilder_->unwind_reason_addr());
    this->builder_.CreateBr(this->fbuilder_->unwind_block());

    // After falling through into a finally block, we also fall
    // through out of the block.  This has the nice side-effect of
    // avoiding jumps and switch instructions in the common case,
    // although returning out of a finally may still be slower than
    // ideal.
    this->builder_.SetInsertPoint(finally_fallthrough);
}

void
OpcodeBlock::WITH_CLEANUP()
{
    /* At the top of the stack are 3 values indicating
       how/why we entered the finally clause:
       - (TOP, SECOND, THIRD) = None, None, None
       - (TOP, SECOND, THIRD) = (UNWIND_{RETURN,CONTINUE}), retval, None
       - (TOP, SECOND, THIRD) = UNWIND_*, None, None
       - (TOP, SECOND, THIRD) = exc_info()
       Below them is EXIT, the context.__exit__ bound method.
       In the last case, we must call
       EXIT(TOP, SECOND, THIRD)
       otherwise we must call
       EXIT(None, None, None)

       In all cases, we remove EXIT from the stack, leaving
       the rest in the same order.

       In addition, if the stack represents an exception,
       *and* the function call returns a 'true' value, we
       "zap" this information, to prevent END_FINALLY from
       re-raising the exception. (But non-local gotos
       should still be resumed.)
    */

    Value *exc_type = this->state_->CreateAllocaInEntryBlock(
        PyTypeBuilder<PyObject*>::get(this->fbuilder_->context()),
        NULL, "WITH_CLEANUP_exc_type");
    Value *exc_value = this->state_->CreateAllocaInEntryBlock(
        PyTypeBuilder<PyObject*>::get(this->fbuilder_->context()),
        NULL, "WITH_CLEANUP_exc_value");
    Value *exc_traceback = this->state_->CreateAllocaInEntryBlock(
        PyTypeBuilder<PyObject*>::get(this->fbuilder_->context()),
        NULL, "WITH_CLEANUP_exc_traceback");
    Value *exit_func = this->state_->CreateAllocaInEntryBlock(
        PyTypeBuilder<PyObject*>::get(this->fbuilder_->context()),
        NULL, "WITH_CLEANUP_exit_func");

    BasicBlock *handle_int =
        this->state_->CreateBasicBlock("WITH_CLEANUP_handle_int");
    BasicBlock *main_block =
        this->state_->CreateBasicBlock("WITH_CLEANUP_main_block");

    Value *none = this->state_->GetGlobalVariableFor(&_Py_NoneStruct);

    this->builder_.CreateStore(this->fbuilder_->Pop(), exc_type);
    this->builder_.CreateStore(this->fbuilder_->Pop(), exc_value);
    this->builder_.CreateStore(this->fbuilder_->Pop(), exc_traceback);
    this->builder_.CreateStore(this->fbuilder_->Pop(), exit_func);
    this->fbuilder_->Push(this->builder_.CreateLoad(exc_traceback));
    this->fbuilder_->Push(this->builder_.CreateLoad(exc_value));
    this->fbuilder_->Push(this->builder_.CreateLoad(exc_type));

    Value *is_int = this->state_->CreateCall(
        this->state_->
            GetGlobalFunction<int(PyObject *)>("_PyLlvm_WrapIntCheck"),
        this->builder_.CreateLoad(exc_type),
        "WITH_CLEANUP_pyint_check");
    this->builder_.CreateCondBr(this->state_->IsNonZero(is_int),
                                handle_int, main_block);

    this->builder_.SetInsertPoint(handle_int);
    this->builder_.CreateStore(none, exc_type);
    this->builder_.CreateStore(none, exc_value);
    this->builder_.CreateStore(none, exc_traceback);

    this->fbuilder_->FallThroughTo(main_block);
    // Build a vector because there is no CreateCall5().
    // This is easier than building the tuple ourselves, but doing so would
    // probably be faster.
    std::vector<Value*> args;
    args.push_back(this->builder_.CreateLoad(exit_func));
    args.push_back(this->builder_.CreateLoad(exc_type));
    args.push_back(this->builder_.CreateLoad(exc_value));
    args.push_back(this->builder_.CreateLoad(exc_traceback));
    args.push_back(this->state_->GetNull<PyObject*>());
    Value *ret = this->state_->CreateCall(
        this->state_->GetGlobalFunction<PyObject *(PyObject *, ...)>(
            "PyObject_CallFunctionObjArgs"),
        args.begin(), args.end());
    this->state_->DecRef(this->builder_.CreateLoad(exit_func));
    this->fbuilder_->PropagateExceptionOnNull(ret);

    BasicBlock *check_silence =
        this->state_->CreateBasicBlock("WITH_CLEANUP_check_silence");
    BasicBlock *no_silence =
        this->state_->CreateBasicBlock("WITH_CLEANUP_no_silence");
    BasicBlock *cleanup =
        this->state_->CreateBasicBlock("WITH_CLEANUP_cleanup");
    BasicBlock *next =
        this->state_->CreateBasicBlock("WITH_CLEANUP_next");

    // Don't bother checking whether to silence the exception if there's
    // no exception to silence.
    this->builder_.CreateCondBr(
        this->builder_.CreateICmpEQ(
            this->builder_.CreateLoad(exc_type), none),
        no_silence, check_silence);

    this->builder_.SetInsertPoint(no_silence);
    this->state_->DecRef(ret);
    this->builder_.CreateBr(next);

    this->builder_.SetInsertPoint(check_silence);
    this->builder_.CreateCondBr(this->fbuilder_->IsPythonTrue(ret),
                                cleanup, next);

    this->builder_.SetInsertPoint(cleanup);
    // There was an exception and a true return. Swallow the exception.
    this->fbuilder_->Pop();
    this->fbuilder_->Pop();
    this->fbuilder_->Pop();
    this->state_->IncRef(none);
    this->fbuilder_->Push(none);
    this->state_->IncRef(none);
    this->fbuilder_->Push(none);
    this->state_->IncRef(none);
    this->fbuilder_->Push(none);
    this->state_->DecRef(this->builder_.CreateLoad(exc_type));
    this->state_->DecRef(this->builder_.CreateLoad(exc_value));
    this->state_->DecRef(this->builder_.CreateLoad(exc_traceback));
    this->builder_.CreateBr(next);

    this->builder_.SetInsertPoint(next);
}

}
