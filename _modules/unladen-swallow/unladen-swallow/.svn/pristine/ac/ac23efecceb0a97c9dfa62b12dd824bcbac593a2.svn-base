#include "JIT/llvm_fbuilder.h"

#include "Python.h"
#include "code.h"
#include "opcode.h"
#include "frameobject.h"

#include "JIT/ConstantMirror.h"
#include "JIT/PyBytecodeIterator.h"
#include "JIT/PyTypeBuilder.h"
#include "JIT/global_llvm_data.h"
#include "Util/EventTimer.h"

#include "llvm/ADT/DenseMap.h"
#include "llvm/ADT/STLExtras.h"
#include "llvm/ADT/Twine.h"
#include "llvm/BasicBlock.h"
#include "llvm/Constant.h"
#include "llvm/Constants.h"
#include "llvm/DerivedTypes.h"
#include "llvm/ExecutionEngine/ExecutionEngine.h"
#include "llvm/Function.h"
#include "llvm/GlobalAlias.h"
#include "llvm/Instructions.h"
#include "llvm/Intrinsics.h"
#include "llvm/Module.h"
#include "llvm/Support/ManagedStatic.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/Type.h"

#include <vector>

#ifndef DW_LANG_Python
// Python has an official ID number in the draft Dwarf4 spec.
#define DW_LANG_Python 0x0014
#endif

struct PyExcInfo;

namespace Intrinsic = llvm::Intrinsic;
using llvm::BasicBlock;
using llvm::CallInst;
using llvm::Constant;
using llvm::ConstantExpr;
using llvm::ConstantInt;
using llvm::Function;
using llvm::FunctionType;
using llvm::GlobalVariable;
using llvm::Module;
using llvm::Type;
using llvm::Value;
using llvm::array_endof;
using llvm::errs;

// Use like "this->GET_GLOBAL_VARIABLE(Type, variable)".
#define GET_GLOBAL_VARIABLE(TYPE, VARIABLE) \
    state()->GetGlobalVariable<TYPE>(&VARIABLE, #VARIABLE)

extern "C" {
    extern int _Py_OpcodeStackEffect(int opcode, int oparg);
}

namespace py {

// find_stack_top fills stack info with the absolute stack levels
// for each opcode. This takes jumps into account.

static int
find_stack_top(PyBytecodeIterator iter,
               int stack_level,
               std::vector<int>& stack_info)
{
    // Stop recursion if stack_info for this block is already set.
    // Sanity check if both codepaths return the same stack level.
    if (stack_info[iter.CurIndex()] >= 0) {
        assert(stack_level == stack_info[iter.CurIndex()]);
        return 0;
    }

    for (; !iter.Done() && !iter.Error(); iter.Advance()) {
        stack_info[iter.CurIndex()] = stack_level;
        stack_level += _Py_OpcodeStackEffect(iter.Opcode(), iter.Oparg());
        switch (iter.Opcode()) {
        case RETURN_VALUE:
            return 0;
        case JUMP_IF_FALSE_OR_POP:
        case JUMP_IF_TRUE_OR_POP:
            find_stack_top(PyBytecodeIterator(iter, iter.Oparg()),
                           stack_level,
                           stack_info);
            stack_level -= 1;
            break;
        case POP_JUMP_IF_FALSE:
        case POP_JUMP_IF_TRUE:
            // Jump abs, cond
            find_stack_top(PyBytecodeIterator(iter, iter.Oparg()),
                           stack_level,
                           stack_info);
            break;

        case JUMP_ABSOLUTE:
        case CONTINUE_LOOP:
            // Jump abs, always
            find_stack_top(PyBytecodeIterator(iter, iter.Oparg()),
                           stack_level,
                           stack_info);
            return 0;
            break;

        case FOR_ITER:
            find_stack_top(PyBytecodeIterator(iter,
                                              iter.NextIndex() + iter.Oparg()),
                           stack_level - 2,
                           stack_info);
            break;

        case SETUP_LOOP:
            find_stack_top(PyBytecodeIterator(iter,
                                              iter.NextIndex() + iter.Oparg()),
                           stack_level,
                           stack_info);
            break;
        case SETUP_EXCEPT:
        case SETUP_FINALLY:
            find_stack_top(PyBytecodeIterator(iter,
                                              iter.NextIndex() + iter.Oparg()),
                           stack_level,
                           stack_info);
            stack_level -= 3;
            break;

        case JUMP_FORWARD:
            // Jump rel, always
            find_stack_top(PyBytecodeIterator(iter,
                                              iter.NextIndex() + iter.Oparg()),
                           stack_level,
                           stack_info);
            return 0;
            break;

        }
    }
    return 0;
}

static llvm::StringRef
pystring_to_stringref(const PyObject* str)
{
    assert(PyString_CheckExact(str));
    return llvm::StringRef(PyString_AS_STRING(str), PyString_GET_SIZE(str));
}

LlvmFunctionBuilder::LlvmFunctionBuilder(
    LlvmFunctionState *state, PyCodeObject *code_object)
    : state_(state),
      llvm_data_(state->llvm_data()),
      code_object_(code_object),
      context_(this->llvm_data_->context()),
      module_(this->llvm_data_->module()),
      function_(this->state_->function()),
      builder_(this->state_->builder()),
      debug_info_(this->llvm_data_->DebugInfo()),
      debug_compile_unit_(this->debug_info_.CreateCompileUnit(
                              DW_LANG_Python,
                              PyString_AS_STRING(code_object->co_filename),
                              "",  // Directory
                              "Unladen Swallow " PY_VERSION,
                              false, // Not main.
                              false, // Not optimized
                              "")),
      debug_subprogram_(this->debug_info_.CreateSubprogram(
                            debug_compile_unit_,
                            PyString_AS_STRING(code_object->co_name),
                            PyString_AS_STRING(code_object->co_name),
                            PyString_AS_STRING(code_object->co_name),
                            debug_compile_unit_,
                            code_object->co_firstlineno,
                            llvm::DIType(),
                            false,   // Not local to unit.
                            true)),  // Is definition.
      stack_info_(0),
      error_(false),
      is_generator_(code_object->co_flags & CO_GENERATOR),
      uses_delete_fast_(false)
{
    Function::arg_iterator args = this->function_->arg_begin();
    this->frame_ = args++;
    assert(args == this->function_->arg_end() &&
           "Unexpected number of arguments");
    this->frame_->setName("frame");

    BasicBlock *entry = this->state()->CreateBasicBlock("entry");
    this->unreachable_block_ =
        this->state()->CreateBasicBlock("unreachable");
    this->bail_to_interpreter_block_ =
        this->state()->CreateBasicBlock("bail_to_interpreter");
    this->propagate_exception_block_ =
        this->state()->CreateBasicBlock("propagate_exception");
    this->unwind_block_ = this->state()->CreateBasicBlock("unwind_block");
    this->do_return_block_ = this->state()->CreateBasicBlock("do_return");

    this->builder_.SetInsertPoint(entry);
    // CreateAllocaInEntryBlock will insert alloca's here, before
    // any other instructions in the 'entry' block.

    this->stack_pointer_addr_ = this->builder_.CreateAlloca(
        PyTypeBuilder<PyObject**>::get(this->context_),
        NULL, "stack_pointer_addr");
    this->tmp_stack_pointer_addr_ = this->builder_.CreateAlloca(
        PyTypeBuilder<PyObject**>::get(this->context_),
        NULL, "tmp_stack_pointer_addr");
    this->retval_addr_ = this->builder_.CreateAlloca(
        PyTypeBuilder<PyObject*>::get(this->context_),
        NULL, "retval_addr");
    this->unwind_reason_addr_ = this->builder_.CreateAlloca(
        Type::getInt8Ty(this->context_), NULL, "unwind_reason_addr");
    this->unwind_target_index_addr_ = this->builder_.CreateAlloca(
        Type::getInt32Ty(this->context_), NULL, "unwind_target_index_addr");
    this->blockstack_addr_ = this->builder_.CreateAlloca(
        PyTypeBuilder<PyTryBlock>::get(this->context_),
        ConstantInt::get(Type::getInt32Ty(this->context_), CO_MAXBLOCKS),
        "blockstack_addr");
    this->num_blocks_addr_ = this->builder_.CreateAlloca(
        PyTypeBuilder<char>::get(this->context_), NULL, "num_blocks_addr");
    for (int i = 0; i < code_object->co_nlocals; ++i) {
        PyObject *local_name = PyTuple_GetItem(code_object->co_varnames, i);
        if (local_name == NULL) {
            this->error_ = true;
            return;
        }
        this->locals_.push_back(
            this->builder_.CreateAlloca(
                PyTypeBuilder<PyObject*>::get(this->context_),
                NULL,
                "local_" + pystring_to_stringref(local_name)));
    }

    this->tstate_ = this->state()->CreateCall(
            this->state()->GetGlobalFunction<PyThreadState*()>(
            "_PyLlvm_WrapPyThreadState_GET"));
    this->stack_bottom_ = this->builder_.CreateLoad(
        FrameTy::f_valuestack(this->builder_, this->frame_),
        "stack_bottom");
    this->llvm_data_->tbaa_stack.MarkInstruction(this->stack_bottom_);
    if (this->is_generator_) {
        // When we're re-entering a generator, we have to copy the stack
        // pointer, block stack and locals from the frame.
        this->CopyFromFrameObject();
    } else {
        // If this isn't a generator, the stack pointer always starts at
        // the bottom of the stack.
        this->builder_.CreateStore(this->stack_bottom_,
                                   this->stack_pointer_addr_);
        /* f_stacktop remains NULL unless yield suspends the frame. */
        this->builder_.CreateStore(
            this->state()->GetNull<PyObject **>(),
            FrameTy::f_stacktop(this->builder_, this->frame_));

        this->builder_.CreateStore(
            ConstantInt::get(PyTypeBuilder<char>::get(this->context_), 0),
            this->num_blocks_addr_);

        // If this isn't a generator, we only need to copy the locals.
        this->CopyLocalsFromFrameObject();
    }

    Value *use_tracing = this->builder_.CreateLoad(
        ThreadStateTy::use_tracing(this->builder_, this->tstate_),
        "use_tracing");
    BasicBlock *trace_enter_function =
        this->state()->CreateBasicBlock("trace_enter_function");
    BasicBlock *continue_entry =
        this->state()->CreateBasicBlock("continue_entry");
    this->builder_.CreateCondBr(this->state()->IsNonZero(use_tracing),
                                trace_enter_function, continue_entry);

    this->builder_.SetInsertPoint(trace_enter_function);
    // Don't touch f_lasti since we just entered the function..
    this->builder_.CreateStore(
        ConstantInt::get(PyTypeBuilder<char>::get(this->context_),
                         _PYFRAME_TRACE_ON_ENTRY),
        FrameTy::f_bailed_from_llvm(this->builder_, this->frame_));
    this->builder_.CreateBr(this->GetBailBlock());

    this->builder_.SetInsertPoint(continue_entry);
    Value *frame_code = this->builder_.CreateLoad(
        FrameTy::f_code(this->builder_, this->frame_),
        "frame->f_code");
    this->use_jit_addr_ = CodeTy::co_use_jit(this->builder_, frame_code);
#ifndef NDEBUG
    // Assert that the code object we pull out of the frame is the
    // same as the one passed into this object.
    Value *passed_in_code_object =
        ConstantInt::get(Type::getInt64Ty(this->context_),
                         reinterpret_cast<uintptr_t>(this->code_object_));
    this->state()->Assert(this->builder_.CreateICmpEQ(
        this->builder_.CreatePtrToInt(frame_code,
                                      Type::getInt64Ty(this->context_)),
                     passed_in_code_object),
                 "Called with unexpected code object.");
#endif  // NDEBUG
    this->varnames_ = this->state()->GetGlobalVariableFor(
        this->code_object_->co_varnames);

    Value *names_tuple = this->builder_.CreateBitCast(
        this->state()->GetGlobalVariableFor(this->code_object_->co_names),
        PyTypeBuilder<PyTupleObject*>::get(this->context_),
        "names");
    // Get the address of the names_tuple's first item as well.
    this->names_ = this->state()->GetTupleItemSlot(names_tuple, 0);

    // The next GEP-magic assigns &frame_[0].f_localsplus[0] to
    // this->fastlocals_.
    Value *localsplus = FrameTy::f_localsplus(this->builder_, this->frame_);
    this->llvm_data_->tbaa_locals.MarkInstruction(localsplus);
    this->fastlocals_ = this->builder_.CreateStructGEP(
        localsplus, 0, "fastlocals");
    Value *nlocals = ConstantInt::get(PyTypeBuilder<int>::get(this->context_),
                                      this->code_object_->co_nlocals);
    this->freevars_ =
        this->builder_.CreateGEP(this->fastlocals_, nlocals, "freevars");
    this->globals_ =
        this->builder_.CreateBitCast(
            this->builder_.CreateLoad(
                FrameTy::f_globals(this->builder_, this->frame_)),
            PyTypeBuilder<PyObject *>::get(this->context_));
    this->builtins_ =
        this->builder_.CreateBitCast(
            this->builder_.CreateLoad(
                FrameTy::f_builtins(this->builder_,this->frame_)),
            PyTypeBuilder<PyObject *>::get(this->context_));
    this->f_lineno_addr_ = FrameTy::f_lineno(this->builder_, this->frame_);
    this->f_lasti_addr_ = FrameTy::f_lasti(this->builder_, this->frame_);

    BasicBlock *start = this->state()->CreateBasicBlock("body_start");
    if (this->is_generator_) {
      // Support generator.throw().  If frame->f_throwflag is set, the
      // caller has set an exception, and we're supposed to propagate
      // it.
      BasicBlock *propagate_generator_throw =
          this->state()->CreateBasicBlock("propagate_generator_throw");
      BasicBlock *continue_generator_or_start_func =
          this->state()->CreateBasicBlock("continue_generator_or_start_func");

      Value *throwflag = this->builder_.CreateLoad(
          FrameTy::f_throwflag(this->builder_, this->frame_),
          "f_throwflag");
      this->builder_.CreateCondBr(
          this->state()->IsNonZero(throwflag),
          propagate_generator_throw, continue_generator_or_start_func);

      this->builder_.SetInsertPoint(propagate_generator_throw);
      PropagateException();

      this->builder_.SetInsertPoint(continue_generator_or_start_func);
      Value *resume_block = this->builder_.CreateLoad(
          this->f_lasti_addr_, "resume_block");
      // Each use of a YIELD_VALUE opcode will add a new case to this
      // switch.  eval.cc just assigns the new IP, allowing wild jumps,
      // but LLVM won't let us do that so we default to jumping to the
      // unreachable block.
      this->yield_resume_switch_ =
          this->builder_.CreateSwitch(resume_block, this->unreachable_block_);

      this->yield_resume_switch_->addCase(
          ConstantInt::getSigned(PyTypeBuilder<int>::get(this->context_), -1),
          start);
    } else {
      // This function is not a generator, so we just jump to the start.
      this->builder_.CreateBr(start);
    }

    this->builder_.SetInsertPoint(this->unreachable_block_);
#ifndef NDEBUG
    // In debug mode, die when we get to unreachable code.  In
    // optimized mode, let the LLVM optimizers get rid of it.
    this->state()->Abort("Jumped to unreachable code.");
#endif  // NDEBUG
    this->builder_.CreateUnreachable();

    FillBailToInterpreterBlock();
    FillPropagateExceptionBlock();
    FillUnwindBlock();
    FillDoReturnBlock();

    this->builder_.SetInsertPoint(start);
#ifdef WITH_TSC
    this->state()->LogTscEvent(CALL_ENTER_LLVM);
#endif
}

void
LlvmFunctionBuilder::UpdateStackInfo()
{
    this->stack_info_
        .resize(PyString_GET_SIZE(this->code_object_->co_code), -1);
    PyBytecodeIterator iter(this->code_object_->co_code);
    find_stack_top(iter, 0, this->stack_info_);
}

void
LlvmFunctionBuilder::FillPropagateExceptionBlock()
{
    this->builder_.SetInsertPoint(this->propagate_exception_block_);
    this->builder_.CreateStore(this->state()->GetNull<PyObject*>(),
                               this->retval_addr_);
    this->builder_.CreateStore(ConstantInt::get(Type::getInt8Ty(this->context_),
                                                UNWIND_EXCEPTION),
                               this->unwind_reason_addr_);
    this->state()->CreateCall(
        this->state()->GetGlobalFunction<int(PyFrameObject*)>(
            "PyTraceBack_Here"),
        this->frame_);
    BasicBlock *call_exc_trace =
        this->state()->CreateBasicBlock("call_exc_trace");
    Value *tracefunc = this->builder_.CreateLoad(
        ThreadStateTy::c_tracefunc(this->builder_, this->tstate_));
    this->builder_.CreateCondBr(this->state()->IsNull(tracefunc),
                                this->unwind_block_, call_exc_trace);

    this->builder_.SetInsertPoint(call_exc_trace);
    this->state()->CreateCall(
             this->state()->GetGlobalFunction<
                 void(PyThreadState *, PyFrameObject *)>(
            "_PyEval_CallExcTrace"),
        this->tstate_, this->frame_);
    this->builder_.CreateBr(this->unwind_block_);
}

void
LlvmFunctionBuilder::FillUnwindBlock()
{
    // Handles, roughly, the eval.cc JUMPTO macro.
    BasicBlock *goto_unwind_target_block =
        this->state()->CreateBasicBlock("goto_unwind_target");
    this->builder_.SetInsertPoint(goto_unwind_target_block);
    Value *unwind_target_index =
        this->builder_.CreateLoad(this->unwind_target_index_addr_,
                                  "unwind_target_index");
    // Each call to AddUnwindTarget() will add a new case to this
    // switch.  eval.cc just assigns the new IP, allowing wild jumps,
    // but LLVM won't let us do that so we default to jumping to the
    // unreachable block.
    this->unwind_target_switch_ = this->builder_.CreateSwitch(
        unwind_target_index, this->unreachable_block_);

    // Code that needs to unwind the stack will jump here.
    // (e.g. returns, exceptions, breaks, and continues).
    this->builder_.SetInsertPoint(this->unwind_block_);
    Value *unwind_reason =
        this->builder_.CreateLoad(this->unwind_reason_addr_, "unwind_reason");

    BasicBlock *pop_remaining_objects =
        this->state()->CreateBasicBlock("pop_remaining_objects");
    {  // Implements the fast_block_end loop toward the end of
       // PyEval_EvalFrame().  This pops blocks off the block-stack
       // and values off the value-stack until it finds a block that
       // wants to handle the current unwind reason.
        BasicBlock *unwind_loop_header =
            this->state()->CreateBasicBlock("unwind_loop_header");
        BasicBlock *unwind_loop_body =
            this->state()->CreateBasicBlock("unwind_loop_body");

        this->FallThroughTo(unwind_loop_header);
        // Continue looping if we still have blocks left on the blockstack.
        Value *blocks_left = this->builder_.CreateLoad(this->num_blocks_addr_);
        this->builder_.CreateCondBr(this->state()->IsPositive(blocks_left),
                                    unwind_loop_body, pop_remaining_objects);

        this->builder_.SetInsertPoint(unwind_loop_body);
        Value *popped_block = this->state()->CreateCall(
            this->state()->GetGlobalFunction<
                PyTryBlock *(PyTryBlock *, char *)>(
                "_PyLlvm_Frame_BlockPop"),
            this->blockstack_addr_,
            this->num_blocks_addr_);
        Value *block_type = this->builder_.CreateLoad(
            PyTypeBuilder<PyTryBlock>::b_type(this->builder_, popped_block),
            "block_type");
        Value *block_handler = this->builder_.CreateLoad(
            PyTypeBuilder<PyTryBlock>::b_handler(this->builder_,
                                                     popped_block),
            "block_handler");
        Value *block_level = this->builder_.CreateLoad(
            PyTypeBuilder<PyTryBlock>::b_level(this->builder_,
                                                   popped_block),
            "block_level");

        // Handle SETUP_LOOP with UNWIND_CONTINUE.
        BasicBlock *not_continue =
            this->state()->CreateBasicBlock("not_continue");
        BasicBlock *unwind_continue =
            this->state()->CreateBasicBlock("unwind_continue");
        Value *is_setup_loop = this->builder_.CreateICmpEQ(
            block_type,
            ConstantInt::get(block_type->getType(), ::SETUP_LOOP),
            "is_setup_loop");
        Value *is_continue = this->builder_.CreateICmpEQ(
            unwind_reason,
            ConstantInt::get(Type::getInt8Ty(this->context_), UNWIND_CONTINUE),
            "is_continue");
        this->builder_.CreateCondBr(
            this->builder_.CreateAnd(is_setup_loop, is_continue),
            unwind_continue, not_continue);

        this->builder_.SetInsertPoint(unwind_continue);
        // Put the loop block back on the stack, clear the unwind reason,
        // then jump to the proper FOR_ITER.
        Value *args[] = {
            this->blockstack_addr_,
            this->num_blocks_addr_,
            block_type,
            block_handler,
            block_level
        };
        this->state()->CreateCall(
            this->state()->GetGlobalFunction<
                void(PyTryBlock *, char *, int, int, int)>(
                "_PyLlvm_Frame_BlockSetup"),
            args, array_endof(args));
        this->builder_.CreateStore(
            ConstantInt::get(Type::getInt8Ty(this->context_), UNWIND_NOUNWIND),
            this->unwind_reason_addr_);
        // Convert the return value to the unwind target. This is in keeping
        // with eval.cc. There's probably some LLVM magic that will allow
        // us to skip the boxing/unboxing, but this will work for now.
        Value *boxed_retval = this->builder_.CreateLoad(this->retval_addr_);
        Value *unbox_retval = this->builder_.CreateTrunc(
            this->state()->CreateCall(
                this->state()->GetGlobalFunction<
                    long(PyObject *)>("PyInt_AsLong"),
                boxed_retval),
            Type::getInt32Ty(this->context_),
            "unboxed_retval");
        this->state()->DecRef(boxed_retval);
        this->builder_.CreateStore(unbox_retval,
                                   this->unwind_target_index_addr_);
        this->builder_.CreateBr(goto_unwind_target_block);

        this->builder_.SetInsertPoint(not_continue);
        // Pop values back to where this block started.
        this->PopAndDecrefTo(
            this->builder_.CreateGEP(this->stack_bottom_, block_level));

        BasicBlock *handle_loop =
            this->state()->CreateBasicBlock("handle_loop");
        BasicBlock *handle_except =
            this->state()->CreateBasicBlock("handle_except");
        BasicBlock *handle_finally =
            this->state()->CreateBasicBlock("handle_finally");
        BasicBlock *push_exception =
            this->state()->CreateBasicBlock("push_exception");
        BasicBlock *goto_block_handler =
            this->state()->CreateBasicBlock("goto_block_handler");

        llvm::SwitchInst *block_type_switch = this->builder_.CreateSwitch(
            block_type, this->unreachable_block_, 3);
        const llvm::IntegerType *block_type_type =
            llvm::cast<llvm::IntegerType>(block_type->getType());
        block_type_switch->addCase(
            ConstantInt::get(block_type_type, ::SETUP_LOOP),
            handle_loop);
        block_type_switch->addCase(
            ConstantInt::get(block_type_type, ::SETUP_EXCEPT),
            handle_except);
        block_type_switch->addCase(
            ConstantInt::get(block_type_type, ::SETUP_FINALLY),
            handle_finally);

        this->builder_.SetInsertPoint(handle_loop);
        Value *unwinding_break = this->builder_.CreateICmpEQ(
            unwind_reason, ConstantInt::get(Type::getInt8Ty(this->context_),
                                            UNWIND_BREAK),
            "currently_unwinding_break");
        this->builder_.CreateCondBr(unwinding_break,
                                    goto_block_handler, unwind_loop_header);

        this->builder_.SetInsertPoint(handle_except);
        // We only consider visiting except blocks when an exception
        // is being unwound.
        Value *unwinding_exception = this->builder_.CreateICmpEQ(
            unwind_reason, ConstantInt::get(Type::getInt8Ty(this->context_),
                                            UNWIND_EXCEPTION),
            "currently_unwinding_exception");
        this->builder_.CreateCondBr(unwinding_exception,
                                    push_exception, unwind_loop_header);

        this->builder_.SetInsertPoint(push_exception);
        // We need an alloca here so _PyLlvm_FastEnterExceptOrFinally
        // can return into it.  This alloca _won't_ be optimized by
        // mem2reg because its address is taken.
        Value *exc_info = this->state()->CreateAllocaInEntryBlock(
            PyTypeBuilder<PyExcInfo>::get(this->context_), NULL, "exc_info");
        this->state()->CreateCall(
            this->state()->GetGlobalFunction<void(PyExcInfo*, int)>(
                "_PyLlvm_FastEnterExceptOrFinally"),
            exc_info,
            block_type);

        // We don't know for sure what the absolute stack position will be
        // after handling an exception. We store the exception in allocas,
        // the opcode implementation must take care to copy it on the stack.
        this->exception_tb_ = this->state_->CreateAllocaInEntryBlock(
            PyTypeBuilder<PyObject*>::get(this->context_),
            NULL,
            "exception_tb");
        this->exception_val_ = this->state_->CreateAllocaInEntryBlock(
            PyTypeBuilder<PyObject*>::get(this->context_),
            NULL,
            "exception_val");
        this->exception_exc_ = this->state_->CreateAllocaInEntryBlock(
            PyTypeBuilder<PyObject*>::get(this->context_),
            NULL,
            "exception_exc");

        this->builder_.CreateStore(
            this->builder_.CreateLoad(
                this->builder_.CreateStructGEP(
                    exc_info, PyTypeBuilder<PyExcInfo>::FIELD_TB)),
            this->exception_tb_);
        this->builder_.CreateStore(
            this->builder_.CreateLoad(
                this->builder_.CreateStructGEP(
                    exc_info, PyTypeBuilder<PyExcInfo>::FIELD_VAL)),
            this->exception_val_);
        this->builder_.CreateStore(
            this->builder_.CreateLoad(
                this->builder_.CreateStructGEP(
                    exc_info, PyTypeBuilder<PyExcInfo>::FIELD_EXC)),
            this->exception_exc_);
        this->builder_.CreateBr(goto_block_handler);

        this->builder_.SetInsertPoint(handle_finally);
        // Jump to the finally block, with the stack prepared for
        // END_FINALLY to continue unwinding.

        BasicBlock *push_pseudo_exception =
            this->state()->CreateBasicBlock("push_pseudo_exception");
        BasicBlock *push_retval =
            this->state()->CreateBasicBlock("push_retval");
        BasicBlock *push_no_retval =
            this->state()->CreateBasicBlock("push_no_retval");
        BasicBlock *handle_finally_end =
            this->state()->CreateBasicBlock("handle_finally_end");
        // When unwinding for an exception, we have to save the
        // exception onto the stack.
        Value *unwinding_exception2 = this->builder_.CreateICmpEQ(
            unwind_reason, ConstantInt::get(Type::getInt8Ty(this->context_),
                                            UNWIND_EXCEPTION),
            "currently_unwinding_exception");
        this->builder_.CreateCondBr(unwinding_exception2,
                                    push_exception, push_pseudo_exception);

        this->builder_.SetInsertPoint(push_pseudo_exception);
        Value *none = this->state()->GetGlobalVariableFor(&_Py_NoneStruct);
        this->state()->IncRef(none);
        this->builder_.CreateStore(none, this->exception_tb_);

        llvm::SwitchInst *should_push_retval = this->builder_.CreateSwitch(
            unwind_reason, push_no_retval, 2);
        // When unwinding for a return or continue, we have to save
        // the return value or continue target onto the stack.
        should_push_retval->addCase(
            ConstantInt::get(Type::getInt8Ty(this->context_), UNWIND_RETURN),
            push_retval);
        should_push_retval->addCase(
            ConstantInt::get(Type::getInt8Ty(this->context_), UNWIND_CONTINUE),
            push_retval);

        this->builder_.SetInsertPoint(push_retval);
        this->builder_.CreateStore(
            this->builder_.CreateLoad(this->retval_addr_, "retval"),
            this->exception_val_);
        this->builder_.CreateBr(handle_finally_end);

        this->builder_.SetInsertPoint(push_no_retval);
        this->state()->IncRef(none);
        this->builder_.CreateStore(none, this->exception_val_);

        this->FallThroughTo(handle_finally_end);
        // END_FINALLY expects to find the unwind reason on the top of
        // the stack.  There's probably a way to do this that doesn't
        // involve allocating an int for every unwind through a
        // finally block, but imitating CPython is simpler.
        Value *unwind_reason_as_pyint = this->state()->CreateCall(
            this->state()->GetGlobalFunction<PyObject *(long)>(
                "PyInt_FromLong"),
            this->builder_.CreateZExt(unwind_reason,
                                      PyTypeBuilder<long>::get(this->context_)),
            "unwind_reason_as_pyint");
        this->builder_.CreateStore(
            unwind_reason_as_pyint,
            this->exception_exc_);

        this->FallThroughTo(goto_block_handler);
        // Clear the unwind reason while running through the block's
        // handler.  mem2reg should never actually decide to use this
        // value, but having it here should make such forgotten stores
        // more obvious.
        this->builder_.CreateStore(
            ConstantInt::get(Type::getInt8Ty(this->context_), UNWIND_NOUNWIND),
            this->unwind_reason_addr_);
        // The block's handler field holds the index of the block
        // defining this finally or except, or the tail of the loop we
        // just broke out of.  Jump to it through the unwind switch
        // statement defined above.
        this->builder_.CreateStore(block_handler,
                                   this->unwind_target_index_addr_);
        this->builder_.CreateBr(goto_unwind_target_block);
    }  // End unwind loop.

    // If we fall off the end of the unwind loop, there are no blocks
    // left and it's time to pop the rest of the value stack and
    // return.
    this->builder_.SetInsertPoint(pop_remaining_objects);
    this->PopAndDecrefTo(this->stack_bottom_);

    // Unless we're returning (or yielding which comes into the
    // do_return_block_ through another path), the retval should be
    // NULL.
    BasicBlock *reset_retval =
        this->state()->CreateBasicBlock("reset_retval");
    Value *unwinding_for_return =
        this->builder_.CreateICmpEQ(
            unwind_reason, ConstantInt::get(Type::getInt8Ty(this->context_),
                                            UNWIND_RETURN));
    this->builder_.CreateCondBr(unwinding_for_return,
                                this->do_return_block_, reset_retval);

    this->builder_.SetInsertPoint(reset_retval);
    this->builder_.CreateStore(this->state()->GetNull<PyObject*>(),
                               this->retval_addr_);
    this->builder_.CreateBr(this->do_return_block_);
}

void
LlvmFunctionBuilder::FillDoReturnBlock()
{
    this->builder_.SetInsertPoint(this->do_return_block_);
    BasicBlock *check_frame_exception =
        this->state()->CreateBasicBlock("check_frame_exception");
    BasicBlock *trace_leave_function =
        this->state()->CreateBasicBlock("trace_leave_function");
    BasicBlock *tracer_raised =
        this->state()->CreateBasicBlock("tracer_raised");

    // Trace exiting from this function, if tracing is turned on.
    Value *use_tracing = this->builder_.CreateLoad(
        ThreadStateTy::use_tracing(this->builder_, this->tstate_));
    this->builder_.CreateCondBr(this->state()->IsNonZero(use_tracing),
                                trace_leave_function, check_frame_exception);

    this->builder_.SetInsertPoint(trace_leave_function);
    Value *unwind_reason =
        this->builder_.CreateLoad(this->unwind_reason_addr_);
    Value *is_return = this->builder_.CreateICmpEQ(
        unwind_reason, ConstantInt::get(Type::getInt8Ty(this->context_),
                                        UNWIND_RETURN),
        "is_return");
    Value *is_yield = this->builder_.CreateICmpEQ(
        unwind_reason, ConstantInt::get(Type::getInt8Ty(this->context_),
                                        UNWIND_YIELD),
        "is_yield");
    Value *is_exception = this->builder_.CreateICmpEQ(
        unwind_reason, ConstantInt::get(Type::getInt8Ty(this->context_),
                                        UNWIND_EXCEPTION),
        "is_exception");
    Value *is_yield_or_return = this->builder_.CreateOr(is_return, is_yield);
    Value *traced_retval = this->builder_.CreateLoad(this->retval_addr_);
    Value *trace_args[] = {
        this->tstate_,
        this->frame_,
        traced_retval,
        this->builder_.CreateIntCast(
            is_yield_or_return, PyTypeBuilder<char>::get(this->context_),
            false /* unsigned */),
        this->builder_.CreateIntCast(
            is_exception, PyTypeBuilder<char>::get(this->context_),
            false /* unsigned */)
    };
    Value *trace_result = this->state()->CreateCall(
        this->state()->GetGlobalFunction<int(PyThreadState *, struct _frame *,
                                             PyObject *, char, char)>(
                                        "_PyEval_TraceLeaveFunction"),
        trace_args, array_endof(trace_args));
    this->builder_.CreateCondBr(this->state()->IsNonZero(trace_result),
                                tracer_raised, check_frame_exception);

    this->builder_.SetInsertPoint(tracer_raised);
    this->state()->XDecRef(traced_retval);
    this->builder_.CreateStore(this->state()->GetNull<PyObject*>(),
                               this->retval_addr_);
    this->builder_.CreateBr(check_frame_exception);

    this->builder_.SetInsertPoint(check_frame_exception);
    // If this frame raised and caught an exception, it saved it into
    // sys.exc_info(). The calling frame may also be in the process of
    // handling an exception, in which case we don't want to clobber
    // its sys.exc_info().  See eval.cc's _PyEval_ResetExcInfo for
    // details.
    BasicBlock *have_frame_exception =
        this->state()->CreateBasicBlock("have_frame_exception");
    BasicBlock *no_frame_exception =
        this->state()->CreateBasicBlock("no_frame_exception");
    BasicBlock *finish_return =
        this->state()->CreateBasicBlock("finish_return");
    Value *tstate_frame = this->builder_.CreateLoad(
        ThreadStateTy::frame(this->builder_, this->tstate_),
        "tstate->frame");
    Value *f_exc_type = this->builder_.CreateLoad(
        FrameTy::f_exc_type(this->builder_, tstate_frame),
        "tstate->frame->f_exc_type");
    this->builder_.CreateCondBr(this->state()->IsNull(f_exc_type),
                                no_frame_exception, have_frame_exception);

    this->builder_.SetInsertPoint(have_frame_exception);
    // The frame did have an exception, so un-clobber the caller's exception.
    this->state()->CreateCall(
        this->state()->GetGlobalFunction<void(PyThreadState*)>(
            "_PyEval_ResetExcInfo"),
        this->tstate_);
    this->builder_.CreateBr(finish_return);

    this->builder_.SetInsertPoint(no_frame_exception);
    // The frame did not have an exception.  In debug mode, check for
    // consistency.
#ifndef NDEBUG
    Value *f_exc_value = this->builder_.CreateLoad(
        FrameTy::f_exc_value(this->builder_, tstate_frame),
        "tstate->frame->f_exc_value");
    Value *f_exc_traceback = this->builder_.CreateLoad(
        FrameTy::f_exc_traceback(this->builder_, tstate_frame),
        "tstate->frame->f_exc_traceback");
    this->state()->Assert(this->state()->IsNull(f_exc_value),
        "Frame's exc_type was null but exc_value wasn't");
    this->state()->Assert(this->state()->IsNull(f_exc_traceback),
        "Frame's exc_type was null but exc_traceback wasn't");
#endif
    this->builder_.CreateBr(finish_return);

    this->builder_.SetInsertPoint(finish_return);
    // Grab the return value and return it.
    Value *retval = this->builder_.CreateLoad(this->retval_addr_, "retval");
    this->CreateRet(retval);
}

// Before jumping to this block, make sure frame->f_lasti points to
// the opcode index at which to resume.
void
LlvmFunctionBuilder::FillBailToInterpreterBlock()
{
    this->builder_.SetInsertPoint(this->bail_to_interpreter_block_);
    // Don't just immediately jump back to the JITted code.
    this->builder_.CreateStore(
        ConstantInt::get(PyTypeBuilder<int>::get(this->context_), 0),
        FrameTy::f_use_jit(this->builder_, this->frame_));
    // Fill the frame object with any information that was in allocas here.
    this->CopyToFrameObject();

    // Tail-call back to the interpreter.  As of 2009-06-12 this isn't
    // codegen'ed as a tail call
    // (http://llvm.org/docs/CodeGenerator.html#tailcallopt), but that
    // should improve eventually.
    CallInst *bail = this->state()->CreateCall(
        this->state()->GetGlobalFunction<PyObject*(PyFrameObject*)>(
            "PyEval_EvalFrame"),
        this->frame_);
    bail->setTailCall(true);
    this->CreateRet(bail);
}

llvm::BasicBlock *
LlvmFunctionBuilder::GetBailBlock() const
{
    // TODO(collinwinter): bail block chaining needs to change this.
    return this->bail_to_interpreter_block_;
}

llvm::BasicBlock *
LlvmFunctionBuilder::GetExceptionBlock() const
{
    // TODO(collinwinter): exception block chaining needs to change this.
    return this->propagate_exception_block_;
}

void
LlvmFunctionBuilder::PushException()
{
    this->SetOpcodeResult(0,
         this->builder_.CreateLoad(this->exception_tb_));
    this->SetOpcodeResult(1,
         this->builder_.CreateLoad(this->exception_val_));
    this->SetOpcodeResult(2,
         this->builder_.CreateLoad(this->exception_exc_));
}

void
LlvmFunctionBuilder::PopAndDecrefTo(Value *target_stack_pointer)
{
    BasicBlock *pop_loop = this->state()->CreateBasicBlock("pop_loop");
    BasicBlock *pop_block = this->state()->CreateBasicBlock("pop_stack");
    BasicBlock *pop_done = this->state()->CreateBasicBlock("pop_done");

    this->FallThroughTo(pop_loop);
    Value *stack_pointer = this->builder_.CreateLoad(this->stack_pointer_addr_);
    this->llvm_data_->tbaa_stack.MarkInstruction(stack_pointer);

    Value *finished_popping = this->builder_.CreateICmpULE(
        stack_pointer, target_stack_pointer);
    this->builder_.CreateCondBr(finished_popping, pop_done, pop_block);

    this->builder_.SetInsertPoint(pop_block);
    this->state()->XDecRef(this->PopRel());
    this->builder_.CreateBr(pop_loop);

    this->builder_.SetInsertPoint(pop_done);
}

void
LlvmFunctionBuilder::CopyToFrameObject()
{
    // Save the current stack pointer into the frame.
    // Note that locals are mirrored to the frame as they're modified.
    Value *stack_pointer = this->builder_.CreateLoad(this->stack_pointer_addr_);
    Value *f_stacktop = FrameTy::f_stacktop(this->builder_, this->frame_);
    this->builder_.CreateStore(stack_pointer, f_stacktop);
    Value *num_blocks = this->builder_.CreateLoad(this->num_blocks_addr_);
    this->builder_.CreateStore(num_blocks,
                               FrameTy::f_iblock(this->builder_, this->frame_));
    this->state()->MemCpy(
        this->builder_.CreateStructGEP(
            FrameTy::f_blockstack(this->builder_, this->frame_), 0),
        this->blockstack_addr_, num_blocks);
}

void
LlvmFunctionBuilder::CopyFromFrameObject()
{
    Value *f_stacktop = FrameTy::f_stacktop(this->builder_, this->frame_);
    Value *stack_pointer =
        this->builder_.CreateLoad(f_stacktop,
                                  "stack_pointer_from_frame");
    this->builder_.CreateStore(stack_pointer, this->stack_pointer_addr_);
    /* f_stacktop remains NULL unless yield suspends the frame. */
    this->builder_.CreateStore(this->state()->GetNull<PyObject**>(),
                               f_stacktop);

    Value *num_blocks = this->builder_.CreateLoad(
        FrameTy::f_iblock(this->builder_, this->frame_));
    this->builder_.CreateStore(num_blocks, this->num_blocks_addr_);
    this->state()->MemCpy(this->blockstack_addr_,
        this->builder_.CreateStructGEP(
            FrameTy::f_blockstack(this->builder_, this->frame_), 0),
        num_blocks);

    this->CopyLocalsFromFrameObject();
}

int
LlvmFunctionBuilder::GetParamCount() const
{
    int co_flags = this->code_object_->co_flags;
    return this->code_object_->co_argcount +
        bool(co_flags & CO_VARARGS) + bool(co_flags & CO_VARKEYWORDS);
}


// Rules for copying locals from the frame:
// - If this is a generator, copy everything from the frame.
// - If this is a regular function, only copy the function's parameters; these
//   can never be NULL. Set all other locals to NULL explicitly. This gives
//   LLVM's optimizers more information.
//
// TODO(collinwinter): when LLVM's metadata supports it, mark all parameters
// as "not-NULL" so that constant propagation can have more information to work
// with.
void
LlvmFunctionBuilder::CopyLocalsFromFrameObject()
{
    const Type *int_type = Type::getInt32Ty(this->context_);
    Value *locals =
        this->builder_.CreateStructGEP(
                 FrameTy::f_localsplus(this->builder_, this->frame_), 0);
    this->llvm_data_->tbaa_locals.MarkInstruction(locals);

    Value *null = this->state()->GetNull<PyObject*>();

    // Figure out how many total parameters we have.
    int param_count = this->GetParamCount();

    for (int i = 0; i < this->code_object_->co_nlocals; ++i) {
        PyObject *pyname =
            PyTuple_GET_ITEM(this->code_object_->co_varnames, i);

        if (this->is_generator_ || i < param_count) {
            Value *local_slot = this->builder_.CreateLoad(
                this->builder_.CreateGEP(
                    locals, ConstantInt::get(int_type, i)),
                "local_" + std::string(PyString_AsString(pyname)));

            this->builder_.CreateStore(local_slot, this->locals_[i]);
        }
        else {
            this->builder_.CreateStore(null, this->locals_[i]);
        }
    }
}

void
LlvmFunctionBuilder::SetLasti(int current_instruction_index)
{
    this->f_lasti_ = current_instruction_index;
    this->stack_top_ = this->stack_info_[current_instruction_index];
}

void
LlvmFunctionBuilder::SetLineNumber(int line)
{
    BasicBlock *this_line = this->state()->CreateBasicBlock("line_start");

    this->builder_.CreateStore(
        this->state()->GetSigned<int>(line),
        this->f_lineno_addr_);
    this->SetDebugStopPoint(line);

    this->MaybeCallLineTrace(this_line, _PYFRAME_LINE_TRACE);

    this->builder_.SetInsertPoint(this_line);
}

void
LlvmFunctionBuilder::FillBackedgeLanding(BasicBlock *backedge_landing,
                                         BasicBlock *target,
                                         bool to_start_of_line,
                                         int line_number)
{
    BasicBlock *continue_backedge = NULL;
    if (to_start_of_line) {
        continue_backedge = target;
    }
    else {
        continue_backedge = this->state()->CreateBasicBlock(
                backedge_landing->getName() + ".cont");
    }

    this->builder_.SetInsertPoint(backedge_landing);
    this->CheckPyTicker(continue_backedge);

    if (!to_start_of_line) {
        continue_backedge->moveAfter(backedge_landing);
        this->builder_.SetInsertPoint(continue_backedge);
        // Record the new line number.  This is after _Py_Ticker, so
        // exceptions from signals will appear to come from the source of
        // the backedge.
        this->builder_.CreateStore(
            ConstantInt::getSigned(PyTypeBuilder<int>::get(this->context_),
                                   line_number),
            this->f_lineno_addr_);
        this->SetDebugStopPoint(line_number);

        // If tracing has been turned on, jump back to the interpreter.
        this->MaybeCallLineTrace(target, _PYFRAME_BACKEDGE_TRACE);
    }
}

void
LlvmFunctionBuilder::MaybeCallLineTrace(BasicBlock *fallthrough_block,
                                        char direction)
{
    BasicBlock *call_trace = this->state()->CreateBasicBlock("call_trace");

    Value *tracing_possible = this->builder_.CreateLoad(
        this->GET_GLOBAL_VARIABLE(int, _Py_TracingPossible));
    this->builder_.CreateCondBr(this->state()->IsNonZero(tracing_possible),
                                call_trace, fallthrough_block);

    this->builder_.SetInsertPoint(call_trace);
    this->CreateBailPoint(direction);
}

void
LlvmFunctionBuilder::BailIfProfiling(llvm::BasicBlock *fallthrough_block)
{
    BasicBlock *profiling = this->state()->CreateBasicBlock("profiling");

    Value *profiling_possible = this->builder_.CreateLoad(
        this->GET_GLOBAL_VARIABLE(int, _Py_ProfilingPossible));
    this->builder_.CreateCondBr(this->state()->IsNonZero(profiling_possible),
                                profiling, fallthrough_block);

    this->builder_.SetInsertPoint(profiling);
    this->CreateBailPoint(_PYFRAME_CALL_PROFILE);
}

void
LlvmFunctionBuilder::FallThroughTo(BasicBlock *next_block)
{
    if (this->builder_.GetInsertBlock()->getTerminator() == NULL) {
        // If the block doesn't already end with a branch or
        // return, branch to the next block.
        this->builder_.CreateBr(next_block);
    }
    this->builder_.SetInsertPoint(next_block);
}

ConstantInt *
LlvmFunctionBuilder::AddUnwindTarget(llvm::BasicBlock *target,
                                     int target_opindex)
{
    // The size of the switch instruction will give us a small unique
    // number for each target block.
    ConstantInt *target_index =
            ConstantInt::get(Type::getInt32Ty(this->context_), target_opindex);
    if (!this->existing_unwind_targets_.test(target_opindex)) {
        this->unwind_target_switch_->addCase(target_index, target);
        this->existing_unwind_targets_.set(target_opindex);
    }
    return target_index;
}

void
LlvmFunctionBuilder::Return(Value *retval)
{
    this->builder_.CreateStore(retval, this->retval_addr_);
    this->builder_.CreateStore(ConstantInt::get(Type::getInt8Ty(this->context_),
                                                UNWIND_RETURN),
                               this->unwind_reason_addr_);
    this->builder_.CreateBr(this->unwind_block_);
}

void
LlvmFunctionBuilder::PropagateException()
{
    this->builder_.CreateBr(this->GetExceptionBlock());
}

void
LlvmFunctionBuilder::SetDebugStopPoint(int line_number)
{
    this->builder_.SetCurrentDebugLocation(
        this->debug_info_.CreateLocation(line_number, 0,
                                         this->debug_subprogram_,
                                         llvm::DILocation(NULL)).getNode());
}

const PyTypeObject *
LlvmFunctionBuilder::GetTypeFeedback(unsigned arg_index) const
{
    const PyRuntimeFeedback *feedback = this->GetFeedback(arg_index);
    if (feedback == NULL || feedback->ObjectsOverflowed())
        return NULL;

    llvm::SmallVector<PyObject*, 3> types;
    feedback->GetSeenObjectsInto(types);
    if (types.size() != 1)
        return NULL;

    if (!PyType_CheckExact(types[0]))
        return NULL;

    return (PyTypeObject*)types[0];
}

const PyRuntimeFeedback *
LlvmFunctionBuilder::GetFeedback(unsigned arg_index) const
{
    const PyFeedbackMap *map = this->code_object_->co_runtime_feedback;
    if (map == NULL)
        return NULL;
    return map->GetFeedbackEntry(this->f_lasti_, arg_index);
}

void
LlvmFunctionBuilder::CreateBailPoint(unsigned bail_idx, char reason)
{
    this->builder_.CreateStore(
        // -1 so that next_instr gets set right in EvalFrame.
        this->state()->GetSigned<int>(bail_idx - 1),
        this->f_lasti_addr_);
    this->builder_.CreateStore(
        ConstantInt::get(PyTypeBuilder<char>::get(this->context_), reason),
        FrameTy::f_bailed_from_llvm(this->builder_, this->frame_));
    this->builder_.CreateBr(this->GetBailBlock());
}

void
LlvmFunctionBuilder::CreateGuardBailPoint(unsigned bail_idx, char reason)
{
#ifdef Py_WITH_INSTRUMENTATION
    this->builder_.CreateStore(
        ConstantInt::get(PyTypeBuilder<char>::get(this->context_), reason),
        FrameTy::f_guard_type(this->builder_, this->frame_));
#endif
    this->CreateBailPoint(bail_idx, _PYFRAME_GUARD_FAIL);
}

void
LlvmFunctionBuilder::Push(Value *value)
{
    Value *stack_pointer = this->builder_.CreateLoad(this->stack_pointer_addr_);
    this->llvm_data_->tbaa_stack.MarkInstruction(stack_pointer);
    Value *new_stack_pointer = this->builder_.CreateGEP(
        stack_pointer, ConstantInt::get(Type::getInt32Ty(this->context_), 1));
    this->llvm_data_->tbaa_stack.MarkInstruction(stack_pointer);
    this->builder_.CreateStore(new_stack_pointer, this->stack_pointer_addr_);
    
    Value *from_bottom = this->builder_.CreateGEP(
        this->stack_bottom_,
        ConstantInt::get(Type::getInt32Ty(this->context_), this->stack_top_));
    this->builder_.CreateStore(value, from_bottom);
    this->llvm_data_->tbaa_stack.MarkInstruction(from_bottom);
    ++this->stack_top_;
}

Value *
LlvmFunctionBuilder::Pop()
{
    Value *stack_pointer = this->builder_.CreateLoad(this->stack_pointer_addr_);
    this->llvm_data_->tbaa_stack.MarkInstruction(stack_pointer);
    Value *new_stack_pointer = this->builder_.CreateGEP(
        stack_pointer, ConstantInt::getSigned(Type::getInt32Ty(this->context_),
                                              -1));
    this->llvm_data_->tbaa_stack.MarkInstruction(new_stack_pointer);
    this->builder_.CreateStore(new_stack_pointer, this->stack_pointer_addr_);

    --this->stack_top_;
    Value *from_bottom = this->builder_.CreateGEP(
        this->stack_bottom_,
        ConstantInt::get(Type::getInt32Ty(this->context_), this->stack_top_));

    Value *former_top = this->builder_.CreateLoad(from_bottom);
    return former_top;
}

Value *
LlvmFunctionBuilder::PopRel()
{
    Value *stack_pointer = this->builder_.CreateLoad(this->stack_pointer_addr_);
    this->llvm_data_->tbaa_stack.MarkInstruction(stack_pointer);

    Value *new_stack_pointer = this->builder_.CreateGEP(
        stack_pointer, ConstantInt::getSigned(Type::getInt32Ty(this->context_),
                                              -1));
    this->llvm_data_->tbaa_stack.MarkInstruction(new_stack_pointer);

    Value *former_top = this->builder_.CreateLoad(new_stack_pointer);
    this->builder_.CreateStore(new_stack_pointer, this->stack_pointer_addr_);
    return former_top;
}

Value *
LlvmFunctionBuilder::GetStackLevel()
{
    Value *stack_pointer = this->builder_.CreateLoad(this->stack_pointer_addr_);
    Value *level64 =
        this->builder_.CreatePtrDiff(stack_pointer, this->stack_bottom_);
    // The stack level is stored as an int, not an int64.
    return this->builder_.CreateTrunc(level64,
                                      PyTypeBuilder<int>::get(this->context_),
                                      "stack_level");
}

void
LlvmFunctionBuilder::SetOpcodeArguments(int amount)
{
    if (amount > 0) {
        this->stack_top_ -= amount;

        Value *stack_pointer =
            this->builder_.CreateLoad(this->stack_pointer_addr_);
        this->llvm_data_->tbaa_stack.MarkInstruction(stack_pointer);

        Value *new_stack_pointer = this->builder_.CreateGEP(
            stack_pointer,
            ConstantInt::getSigned(Type::getInt32Ty(this->context_),
                                   -amount));
        this->llvm_data_->tbaa_stack.MarkInstruction(new_stack_pointer);
        this->builder_.CreateStore(new_stack_pointer,
                                   this->stack_pointer_addr_);
    }
}

void
LlvmFunctionBuilder::SetOpcodeArgsWithGuard(int amount)
{
    this->stack_top_ -= amount;
}

void
LlvmFunctionBuilder::BeginOpcodeImpl()
{
    Value *from_bottom = this->builder_.CreateGEP(
        this->stack_bottom_,
        ConstantInt::get(Type::getInt32Ty(this->context_),
                         this->stack_top_));
    this->llvm_data_->tbaa_stack.MarkInstruction(from_bottom);
    this->builder_.CreateStore(from_bottom,
                               this->stack_pointer_addr_);
}

Value *
LlvmFunctionBuilder::GetOpcodeArg(int i)
{
    Value *from_bottom = this->builder_.CreateGEP(
        this->stack_bottom_,
        ConstantInt::get(Type::getInt32Ty(this->context_),
                         this->stack_top_ + i));
    this->llvm_data_->tbaa_stack.MarkInstruction(from_bottom);
    return this->builder_.CreateLoad(from_bottom);
}

void
LlvmFunctionBuilder::SetOpcodeResult(int i, llvm::Value *value)
{
    Value *stack_pointer = this->builder_.CreateLoad(this->stack_pointer_addr_);
    this->llvm_data_->tbaa_stack.MarkInstruction(stack_pointer);

    Value *new_stack_pointer = this->builder_.CreateGEP(
        stack_pointer, ConstantInt::getSigned(Type::getInt32Ty(this->context_),
                                              1));
    this->llvm_data_->tbaa_stack.MarkInstruction(new_stack_pointer);
    this->builder_.CreateStore(new_stack_pointer, this->stack_pointer_addr_);

    Value *from_bottom = this->builder_.CreateGEP(
        this->stack_bottom_,
        ConstantInt::get(Type::getInt32Ty(this->context_),
                         this->stack_top_ + i));
    this->builder_.CreateStore(value, from_bottom);
    this->llvm_data_->tbaa_stack.MarkInstruction(from_bottom);
}

void
LlvmFunctionBuilder::FinishOpcodeImpl(int i)
{
    this->stack_top_ += i;
}

void
LlvmFunctionBuilder::CheckPyTicker(BasicBlock *next_block)
{
    if (next_block == NULL) {
        next_block = this->state()->CreateBasicBlock("ticker_dec_end");
    }
    Value *pyticker_result = this->builder_.CreateCall(
        this->state()->GetGlobalFunction<int(PyThreadState*)>(
            "_PyLlvm_DecAndCheckPyTicker"),
        this->tstate_);
    this->builder_.CreateCondBr(this->state()->IsNegative(pyticker_result),
                                this->GetExceptionBlock(),
                                next_block);
    this->builder_.SetInsertPoint(next_block);
}

void
LlvmFunctionBuilder::DieForUndefinedOpcode(const char *opcode_name)
{
    std::string message("Undefined opcode: ");
    message.append(opcode_name);
    this->state()->Abort(message);
}

llvm::ReturnInst *
LlvmFunctionBuilder::CreateRet(llvm::Value *retval)
{
    return this->builder_.CreateRet(retval);
}

void
LlvmFunctionBuilder::PropagateExceptionOnNull(Value *value)
{
    BasicBlock *propagate =
        this->state()->CreateBasicBlock("PropagateExceptionOnNull_propagate");
    BasicBlock *pass =
        this->state()->CreateBasicBlock("PropagateExceptionOnNull_pass");
    this->builder_.CreateCondBr(this->state()->IsNull(value), propagate, pass);

    this->builder_.SetInsertPoint(propagate);
    this->PropagateException();

    this->builder_.SetInsertPoint(pass);
}

void
LlvmFunctionBuilder::PropagateExceptionOnNegative(Value *value)
{
    BasicBlock *propagate =
        this->state()->CreateBasicBlock(
            "PropagateExceptionOnNegative_propagate");
    BasicBlock *pass =
        this->state()->CreateBasicBlock("PropagateExceptionOnNegative_pass");
    this->builder_.CreateCondBr(this->state()->IsNegative(value),
                                propagate, pass);

    this->builder_.SetInsertPoint(propagate);
    this->PropagateException();

    this->builder_.SetInsertPoint(pass);
}

void
LlvmFunctionBuilder::PropagateExceptionOnNonZero(Value *value)
{
    BasicBlock *propagate =
        this->state()->CreateBasicBlock(
            "PropagateExceptionOnNonZero_propagate");
    BasicBlock *pass =
        this->state()->CreateBasicBlock("PropagateExceptionOnNonZero_pass");
    this->builder_.CreateCondBr(this->state()->IsNonZero(value),
                                propagate, pass);

    this->builder_.SetInsertPoint(propagate);
    this->PropagateException();

    this->builder_.SetInsertPoint(pass);
}

Value *
LlvmFunctionBuilder::LookupName(int name_index)
{
    Value *name = this->builder_.CreateLoad(
        this->builder_.CreateGEP(
            this->names_, ConstantInt::get(Type::getInt32Ty(this->context_),
                                           name_index),
            "constant_name"));
    return name;
}

llvm::Value *
LlvmFunctionBuilder::IsPythonTrue(Value *value)
{
    BasicBlock *not_py_true =
        this->state()->CreateBasicBlock("IsPythonTrue_is_not_PyTrue");
    BasicBlock *not_py_false =
        this->state()->CreateBasicBlock("IsPythonTrue_is_not_PyFalse");
    BasicBlock *decref_value =
        this->state()->CreateBasicBlock("IsPythonTrue_decref_value");
    BasicBlock *done =
        this->state()->CreateBasicBlock("IsPythonTrue_done");

    Value *result_addr = this->state()->CreateAllocaInEntryBlock(
        Type::getInt1Ty(this->context_), NULL, "IsPythonTrue_result");
    Value *py_false =
        this->state()->GetGlobalVariableFor((PyObject*)&_Py_ZeroStruct);
    Value *py_true =
        this->state()->GetGlobalVariableFor((PyObject*)&_Py_TrueStruct);

    Value *is_PyTrue = this->builder_.CreateICmpEQ(
        py_true, value, "IsPythonTrue_is_PyTrue");
    this->builder_.CreateStore(is_PyTrue, result_addr);
    this->builder_.CreateCondBr(is_PyTrue, decref_value, not_py_true);

    this->builder_.SetInsertPoint(not_py_true);
    Value *is_not_PyFalse = this->builder_.CreateICmpNE(
        py_false, value, "IsPythonTrue_is_PyFalse");
    this->builder_.CreateStore(is_not_PyFalse, result_addr);
    this->builder_.CreateCondBr(is_not_PyFalse, not_py_false, decref_value);

    this->builder_.SetInsertPoint(not_py_false);
    Function *pyobject_istrue =
        this->state()->GetGlobalFunction<int(PyObject *)>("PyObject_IsTrue");
    Value *istrue_result = this->state()->CreateCall(
        pyobject_istrue, value, "PyObject_IsTrue_result");
    this->state()->DecRef(value);
    this->PropagateExceptionOnNegative(istrue_result);
    this->builder_.CreateStore(
        this->state()->IsPositive(istrue_result),
        result_addr);
    this->builder_.CreateBr(done);

    this->builder_.SetInsertPoint(decref_value);
    this->state()->DecRef(value);
    this->builder_.CreateBr(done);

    this->builder_.SetInsertPoint(done);
    return this->builder_.CreateLoad(result_addr);
}

void
LlvmFunctionBuilder::WatchType(PyTypeObject *type)
{
    this->types_used_.insert(type);
}

void
LlvmFunctionBuilder::WatchDict(int reason)
{
    this->uses_watched_dicts_.set(reason);
}


Value *
LlvmFunctionBuilder::GetUseJitCond()
{
    Value *use_jit = this->builder_.CreateLoad(this->use_jit_addr_,
                                               "co_use_jit");
    return this->state()->IsNonZero(use_jit);
}

void
LlvmFunctionBuilder::AddYieldResumeBB(llvm::ConstantInt *number,
                                      llvm::BasicBlock *block)
{
    this->yield_resume_switch_->addCase(number, block);
}

int
LlvmFunctionBuilder::FinishFunction()
{
    // If the code object doesn't need to watch any dicts, it shouldn't be
    // invalidated when those dicts change.
    PyCodeObject *code = this->code_object_;
    if (code->co_watching) {
        for (unsigned i = 0; i < NUM_WATCHING_REASONS; ++i) {
            if (!this->uses_watched_dicts_.test(i)) {
                _PyCode_IgnoreDict(code, (ReasonWatched)i);
            }
        }
    }

    // We need to register to become invalidated from any types we've touched.
    for (llvm::SmallPtrSet<PyTypeObject*, 5>::const_iterator
         i = this->types_used_.begin(), e = this->types_used_.end();
         i != e; ++i) {
        // TODO(rnk): When we support recompilation, we will need to remove
        // ourselves from the code listeners list, or we may be invalidated due
        // to changes on unrelated types.  This requires remembering a list of
        // associated types in the code object.
        if (_PyType_AddCodeListener(*i, (PyObject*)code) < 0) {
            return -1;
        }
    }

    return 0;
}

}  // namespace py
