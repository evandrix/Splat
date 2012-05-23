// -*- C++ -*-
#ifndef PYTHON_LLVM_FBUILDER_H
#define PYTHON_LLVM_FBUILDER_H

#ifndef __cplusplus
#error This header expects to be included only in C++ source
#endif

#include "JIT/llvm_state.h"

#include "JIT/PyTypeBuilder.h"
#include "JIT/RuntimeFeedback.h"
#include "Util/EventTimer.h"
#include "llvm/ADT/SmallPtrSet.h"
#include "llvm/ADT/SparseBitVector.h"
#include "llvm/ADT/Twine.h"
#include "llvm/Analysis/DebugInfo.h"
#include "llvm/Constants.h"
#include "llvm/ExecutionEngine/ExecutionEngine.h"
#include "llvm/GlobalVariable.h"
#include "llvm/Type.h"
#include "llvm/Support/IRBuilder.h"
#include "llvm/Support/TargetFolder.h"

#include <bitset>
#include <string>

struct PyCodeObject;
struct PyGlobalLlvmData;

namespace py {

/// Helps the compiler build LLVM functions corresponding to Python
/// functions.  This class maintains all Value*s which depend on a
/// single frame/code object. It also contains all functions that
/// depend on these Values.
class LlvmFunctionBuilder {
    LlvmFunctionBuilder(const LlvmFunctionBuilder &);  // Not implemented.
    void operator=(const LlvmFunctionBuilder &);  // Not implemented.

public:
    LlvmFunctionBuilder(LlvmFunctionState *state, PyCodeObject *code);

    llvm::Function *function() { return function_; }
    typedef llvm::IRBuilder<true, llvm::TargetFolder> BuilderT;
    BuilderT& builder() { return builder_; }
    LlvmFunctionState *state() const { return this->state_; }
    PyCodeObject *code_object() const { return this->code_object_; }
    PyGlobalLlvmData *llvm_data() const { return this->llvm_data_; }
    llvm::LLVMContext& context() { return this->context_; } 
    bool &uses_delete_fast() { return this->uses_delete_fast_; }
    std::vector<bool> &loads_optimized() { return this->loads_optimized_; }

    llvm::BasicBlock *unreachable_block() const
    { 
        return this->unreachable_block_;
    }
    llvm::BasicBlock *unwind_block() const { return this->unwind_block_; }
    llvm::BasicBlock *do_return_block() const { return this->do_return_block_; }

    llvm::Value *unwind_reason_addr() const
    {
        return this->unwind_reason_addr_;
    }
    llvm::Value *retval_addr() const
    {
        return this->retval_addr_;
    }
    llvm::Value *num_blocks_addr() const
    {
        return this->num_blocks_addr_;
    }
    llvm::Value *blockstack_addr() const
    {
        return this->blockstack_addr_;
    }
    llvm::Value *stack_pointer_addr() const
    {
        return this->stack_pointer_addr_;
    }
    llvm::Value *f_lasti_addr() const { return this->f_lasti_addr_; }

    llvm::Value *stack_bottom() const { return this->stack_bottom_; }
    int stack_top() const { return this->stack_top_; }
    
    llvm::Value *freevars() const { return this->freevars_; }
    llvm::Value *frame() const { return this->frame_; }
    llvm::Value *globals() const { return this->globals_; }
    llvm::Value *builtins() const { return this->builtins_; }
    llvm::Value *fastlocals() const { return this->fastlocals_; }
    
    bool is_generator() const { return this->is_generator_; }

    llvm::Value *GetLocal(int i) const { return this->locals_[i]; }

    void UpdateStackInfo();
    bool Error() { return this->error_; }

    /// Sets the current instruction index.  This is only put into the
    /// frame object when tracing.
    void SetLasti(int current_instruction_index);
    int GetLasti() const { return this->f_lasti_; }

    /// Sets the current line number being executed.  This is used to
    /// make tracebacks correct and to get tracing to fire in the
    /// right places.
    void SetLineNumber(int line);

    /// Inserts a call to llvm.dbg.stoppoint.
    void SetDebugStopPoint(int line_number);

    /// This function fills the block that handles a backedge.  Each
    /// backedge needs to check if it needs to handle signals or
    /// switch threads.  If the backedge doesn't land at the start of
    /// a line, it also needs to update the line number and check
    /// whether line tracing has been turned on.  This function leaves
    /// the insert point in a block with a terminator already added,
    /// so the caller should re-set the insert point.
    void FillBackedgeLanding(llvm::BasicBlock *backedge_landing,
                             llvm::BasicBlock *target,
                             bool to_start_of_line,
                             int line_number);

    /// Sets the insert point to next_block, inserting an
    /// unconditional branch to there if the current block doesn't yet
    /// have a terminator instruction.
    void FallThroughTo(llvm::BasicBlock *next_block);

    /// Register callbacks that might invalidate native code based on the
    /// optimizations performed in the generated code.
    int FinishFunction();

    /// These two push or pop a value onto or off of the stack. The
    /// behavior is undefined if the Value's type isn't PyObject* or a
    /// subclass.  These do no refcount operations, which means that
    /// Push() consumes a reference and gives ownership of it to the
    /// new value on the stack, and Pop() returns a pointer that owns
    /// a reference (which it got from the stack).
    /// Push/Pop are legacy methods to provide compatibility to existing
    /// opcode implementations. They should not be used any more.
    /// You must call Push only once per argument and Pop only once
    /// per result.
    void Push(llvm::Value *value);
    llvm::Value *Pop();

    /// Set the number of arguments the next opcode uses.
    /// This serves as a baseline for reading/writing to the stack.
    /// It also resets the stack pointer to it's base value.
    void SetOpcodeArguments(int amount);
    
    /// Sets the number of arguments the next opcode uses.
    /// Use this when the opcode needs to implement guards.
    /// GetOpcodeArg can be used as usual. Call BeginOpcodeImpl
    /// if the guard was successfully passed.
    void SetOpcodeArgsWithGuard(int amount);
    /// Changes the stack pointer after a successfully passed guard.
    void BeginOpcodeImpl();
    /// Retrieve an opcode argument. Must be called after SetOpcodeArguments.
    /// Can be called unlimited.
    /// Increasing the argument reads in the direction of stack growth.
    llvm::Value *GetOpcodeArg(int i);
    /// Sets the result of an opcode. Must be called after SetOpcodeArguments.
    /// Must only be called once per result per IR-codepath.
    void SetOpcodeResult(int i, llvm::Value *value);

    /// Normally it is not needed to specify the number of result values an
    /// opcode produces, as the stack top will be set to the correct value
    /// at the beginning of each opcode
    /// If you want to use SetOpcodeArguments/SetOpocodeArgsWithGuard twice
    /// in one opcode (e.g. to split the opcode in to sub-implementations)
    /// call FinishOpcodeImpl with the number of results from the previous
    /// opcode.
    void FinishOpcodeImpl(int amount);

    /// Takes a target stack pointer and pops values off the stack
    /// until it gets there, decref'ing as it goes.
    void PopAndDecrefTo(llvm::Value *target_stack_pointer);

    /// The PyFrameObject holds several values, like the block stack
    /// and stack pointer, that we store in allocas inside this
    /// function.  When we suspend or resume a generator, or bail out
    /// to the interpreter, we need to transfer those values between
    /// the frame and the allocas.
    void CopyToFrameObject();
    void CopyFromFrameObject();

    /// We copy the function's locals into an LLVM alloca so that LLVM can
    /// better reason about them.
    void CopyLocalsFromFrameObject();

    /// Returns the difference between the current stack pointer and
    /// the base of the stack.
    llvm::Value *GetStackLevel();

    /// Get the runtime feedback for the current opcode (as set by SetLasti()).
    /// Opcodes with multiple feedback units should use the arg_index version
    /// to access individual units.
    const PyRuntimeFeedback *GetFeedback() const {
        return GetFeedback(0);
    }
    const PyRuntimeFeedback *GetFeedback(unsigned arg_index) const;
    const PyTypeObject *GetTypeFeedback(unsigned arg_index) const;

    // Look up a name in the function's names list, returning the
    // PyStringObject for the name_index.
    llvm::Value *LookupName(int name_index);

    /// Inserts a call that will print opcode_name and abort the
    /// program when it's reached.
    void DieForUndefinedOpcode(const char *opcode_name);

    /// How many parameters does the currently-compiling function have?
    int GetParamCount() const;

    // Emits code to decrement _Py_Ticker and handle signals and
    // thread-switching when it expires.  Falls through to next_block (or a
    // new block if it's NULL) and leaves the insertion point there.
    void CheckPyTicker(llvm::BasicBlock *next_block = NULL);

    /// Marks the end of the function and inserts a return instruction.
    llvm::ReturnInst *CreateRet(llvm::Value *retval);

    // Returns an i1, true if value is a PyObject considered true.
    // Steals the reference to value.
    llvm::Value *IsPythonTrue(llvm::Value *value);

    /// During stack unwinding it may be necessary to jump back into
    /// the function to handle a finally or except block.  Since LLVM
    /// doesn't allow us to directly store labels as data, we instead
    /// add the index->label mapping to a switch instruction and
    /// return the i32 for the index.
    llvm::ConstantInt *AddUnwindTarget(llvm::BasicBlock *target,
                                       int target_opindex);

    // Inserts a jump to the return block, returning retval.  You
    // should _never_ call CreateRet directly from one of the opcode
    // handlers, since doing so would fail to unwind the stack.
    void Return(llvm::Value *retval);

    // Propagates an exception by jumping to the unwind block with an
    // appropriate unwind reason set.
    void PropagateException();

    // Set up a block preceding the bail-to-interpreter block.
    void CreateBailPoint(unsigned bail_idx, char reason);
    void CreateBailPoint(char reason) {
        CreateBailPoint(this->f_lasti_, reason);
    }

    // Set up a block preceding the bail-to-interpreter block.
    void CreateGuardBailPoint(unsigned bail_idx, char reason);
    void CreateGuardBailPoint(char reason) {
        CreateGuardBailPoint(this->f_lasti_, reason);
    }

    // Only for use in the constructor: Fills in the block that
    // handles bailing out of JITted code back to the interpreter
    // loop.  Code jumping to this block must first:
    //  1) Set frame->f_lasti to the current opcode index.
    //  2) Set frame->f_bailed_from_llvm to a reason.
    void FillBailToInterpreterBlock();
    // Only for use in the constructor: Fills in the block that starts
    // propagating an exception.  Jump to this block when you want to
    // add a traceback entry for the current line.  Don't jump to this
    // block (and just set retval_addr_ and unwind_reason_addr_
    // directly) when you're re-raising an exception and you want to
    // use its traceback.
    void FillPropagateExceptionBlock();
    // Only for use in the constructor: Fills in the unwind block.
    void FillUnwindBlock();
    // Only for use in the constructor: Fills in the block that
    // actually handles returning from the function.
    void FillDoReturnBlock();

    // If 'value' represents NULL, propagates the exception.
    // Otherwise, falls through.
    void PropagateExceptionOnNull(llvm::Value *value);
    // If 'value' represents a negative integer, propagates the exception.
    // Otherwise, falls through.
    void PropagateExceptionOnNegative(llvm::Value *value);
    // If 'value' represents a non-zero integer, propagates the exception.
    // Otherwise, falls through.
    void PropagateExceptionOnNonZero(llvm::Value *value);

    /// Emits code to conditionally bail out to the interpreter loop
    /// if a line tracing function is installed.  If the line tracing
    /// function is not installed, execution will continue at
    /// fallthrough_block.  direction should be _PYFRAME_LINE_TRACE or
    /// _PYFRAME_BACKEDGE_TRACE.
    void MaybeCallLineTrace(llvm::BasicBlock *fallthrough_block,
                            char direction);

    /// Emits code to conditionally bail out to the interpreter loop if a
    /// profiling function is installed. If a profiling function is not
    /// installed, execution will continue at fallthrough_block.
    void BailIfProfiling(llvm::BasicBlock *fallthrough_block);

    /// Return the BasicBlock we should jump to in order to bail to the
    /// interpreter.
    llvm::BasicBlock *GetBailBlock() const;

    /// Return the BasicBlock we should jump to in order to handle a Python
    /// exception.
    llvm::BasicBlock *GetExceptionBlock() const;
    void PushException();

    // Add a Type to the watch list.
    void WatchType(PyTypeObject *type);

    void WatchDict(int reason);

    // Return a i1 which is true when the use_jit field is set in the
    // code object
    llvm::Value *GetUseJitCond();

    void AddYieldResumeBB(llvm::ConstantInt *number, llvm::BasicBlock *block);

private:
    // Stack pointer relative push and pop methods are for internal
    // use only.
    llvm::Value *PopRel();

    LlvmFunctionState *state_;
    PyGlobalLlvmData *const llvm_data_;
    // The code object is used for looking up peripheral information
    // about the function.  It's not used to examine the bytecode
    // string.
    PyCodeObject *const code_object_;
    llvm::LLVMContext &context_;
    llvm::Module *const module_;
    llvm::Function *const function_;
    BuilderT &builder_;
    llvm::DIFactory &debug_info_;
    const llvm::DICompileUnit debug_compile_unit_;
    const llvm::DISubprogram debug_subprogram_;

    // The most recent index we've started emitting an instruction for.
    int f_lasti_;

    // Flags to indicate whether the code object is watching any of the
    // watchable dicts.
    std::bitset<NUM_WATCHING_REASONS> uses_watched_dicts_;

    // The following pointers hold values created in the function's
    // entry block. They're constant after construction.
    llvm::Value *frame_;

    // Address of code_object_->co_use_jit, used for guards.
    llvm::Value *use_jit_addr_;

    llvm::Value *tstate_;
    llvm::Value *stack_bottom_;
    llvm::Value *stack_pointer_addr_;
    // The tmp_stack_pointer is used when we need to have another
    // function update the stack pointer.  Passing the stack pointer
    // directly would prevent mem2reg from working on it, so we copy
    // it to and from the tmp_stack_pointer around the call.
    llvm::Value *tmp_stack_pointer_addr_;
    llvm::Value *varnames_;
    llvm::Value *names_;
    llvm::Value *globals_;
    llvm::Value *builtins_;
    llvm::Value *fastlocals_;
    llvm::Value *freevars_;
    llvm::Value *f_lineno_addr_;
    llvm::Value *f_lasti_addr_;
    // These two fields correspond to the f_blockstack and f_iblock
    // fields in the frame object.  They get explicitly copied back
    // and forth when the frame escapes.
    llvm::Value *blockstack_addr_;
    llvm::Value *num_blocks_addr_;

    // Expose the frame's locals to LLVM. We copy them in on function-entry,
    // copy them out on write. We use a separate alloca for each local
    // because LLVM's scalar replacement of aggregates pass doesn't handle
    // array allocas.
    std::vector<llvm::Value*> locals_;

    llvm::BasicBlock *unreachable_block_;

    // In generators, we use this switch to jump back to the most
    // recently executed yield instruction.
    llvm::SwitchInst *yield_resume_switch_;

    llvm::BasicBlock *bail_to_interpreter_block_;

    llvm::BasicBlock *propagate_exception_block_;
    llvm::BasicBlock *unwind_block_;
    llvm::Value *unwind_target_index_addr_;
    llvm::SparseBitVector<> existing_unwind_targets_;
    llvm::SwitchInst *unwind_target_switch_;
    // Stores one of the UNWIND_XXX constants defined at the top of
    // llvm_fbuilder.cc
    llvm::Value *unwind_reason_addr_;
    llvm::Value *exception_tb_;
    llvm::Value *exception_val_;
    llvm::Value *exception_exc_;
    llvm::BasicBlock *do_return_block_;
    llvm::Value *retval_addr_;

    llvm::SmallPtrSet<PyTypeObject*, 5> types_used_;

    // A stack that corresponds to LOAD_METHOD/CALL_METHOD pairs.  For every
    // load, we push on a boolean for whether or not the load was optimized.
    // The call uses this value to decide whether to expect an extra "self"
    // argument.  The stack is necessary if the user wrote code with nested
    // method calls, like this: f.foo(b.bar()).
    std::vector<bool> loads_optimized_;

    // Stores information about the stack top for every opcode
    std::vector<int> stack_info_;
    int stack_top_;

    // True if something went wrong and we need to stop compilation without
    // aborting the process. If this is true, a Python error has already
    // been set.
    bool error_;

    const bool is_generator_;
    bool uses_delete_fast_;
};

}  // namespace py

#endif  // PYTHON_LLVM_FBUILDER_H
