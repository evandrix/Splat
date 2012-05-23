#include "Python.h"

#include "JIT/opcodes/control.h"
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
class CondBranchStats {
public:
    CondBranchStats()
        : total(0), optimized(0), not_enough_data(0), unpredictable(0) {
    }


    ~CondBranchStats() {
        errs() << "\nConditional branch optimization:\n";
        errs() << "Total cond branches: " << this->total << "\n";
        errs() << "Optimized branches: " << this->optimized << "\n";
        errs() << "Insufficient data: " << this->not_enough_data << "\n";
        errs() << "Unpredictable branches: " << this->unpredictable << "\n";
    }

    // Total number of conditional branch opcodes compiled.
    unsigned total;
    // Number of predictable conditional branches we were able to optimize.
    unsigned optimized;
    // Number of single-direction branches we don't feel comfortable predicting.
    unsigned not_enough_data;
    // Number of unpredictable conditional branches (both directions
    // taken frequently; unable to be optimized).
    unsigned unpredictable;
};

static llvm::ManagedStatic<CondBranchStats> cond_branch_stats;

#define COND_BRANCH_INC_STATS(field) cond_branch_stats->field++
#else
#define COND_BRANCH_INC_STATS(field)
#endif  /* Py_WITH_INSTRUMENTATION */

namespace py {

OpcodeControl::OpcodeControl(LlvmFunctionBuilder *fbuilder) :
    fbuilder_(fbuilder),
    state_(fbuilder->state()),
    builder_(fbuilder->builder())
{
}

void
OpcodeControl::DoRaise(Value *exc_type, Value *exc_inst, Value *exc_tb)
{
    // Accept code after a raise statement, even though it's never executed.
    // Otherwise, CPython's willingness to insert code after block
    // terminators causes problems.
    BasicBlock *dead_code = this->state_->CreateBasicBlock("dead_code");

    // All raises set 'why' to UNWIND_EXCEPTION and the return value to NULL.
    // This is redundant with the propagate_exception_block_, but mem2reg will
    // remove the redundancy.
    this->builder_.CreateStore(
        ConstantInt::get(Type::getInt8Ty(this->fbuilder_->context()),
                         UNWIND_EXCEPTION),
        this->fbuilder_->unwind_reason_addr());
    this->builder_.CreateStore(this->state_->GetNull<PyObject*>(),
                               this->fbuilder_->retval_addr());

#ifdef WITH_TSC
    this->state_->LogTscEvent(EXCEPT_RAISE_LLVM);
#endif
    Function *do_raise = this->state_->GetGlobalFunction<
        int(PyObject*, PyObject *, PyObject *)>("_PyEval_DoRaise");
    // _PyEval_DoRaise eats references.
    Value *is_reraise = this->state_->CreateCall(
        do_raise, exc_type, exc_inst, exc_tb, "raise_is_reraise");
    // If this is a "re-raise", we jump straight to the unwind block.
    // If it's a new raise, we call PyTraceBack_Here from the
    // propagate_exception_block_.
    this->builder_.CreateCondBr(
        this->builder_.CreateICmpEQ(
            is_reraise,
            ConstantInt::get(is_reraise->getType(), UNWIND_RERAISE)),
        this->fbuilder_->unwind_block(), this->fbuilder_->GetExceptionBlock());

    this->builder_.SetInsertPoint(dead_code);
}

void
OpcodeControl::RAISE_VARARGS_ZERO()
{
    Value *exc_tb = this->state_->GetNull<PyObject*>();
    Value *exc_inst = this->state_->GetNull<PyObject*>();
    Value *exc_type = this->state_->GetNull<PyObject*>();
    this->DoRaise(exc_type, exc_inst, exc_tb);
}

void
OpcodeControl::RAISE_VARARGS_ONE()
{
    Value *exc_tb = this->state_->GetNull<PyObject*>();
    Value *exc_inst = this->state_->GetNull<PyObject*>();
    Value *exc_type = this->fbuilder_->Pop();
    this->DoRaise(exc_type, exc_inst, exc_tb);
}

void
OpcodeControl::RAISE_VARARGS_TWO()
{
    Value *exc_tb = this->state_->GetNull<PyObject*>();
    Value *exc_inst = this->fbuilder_->Pop();
    Value *exc_type = this->fbuilder_->Pop();
    this->DoRaise(exc_type, exc_inst, exc_tb);
}

void
OpcodeControl::RAISE_VARARGS_THREE()
{
    Value *exc_tb = this->fbuilder_->Pop();
    Value *exc_inst = this->fbuilder_->Pop();
    Value *exc_type = this->fbuilder_->Pop();
    this->DoRaise(exc_type, exc_inst, exc_tb);
}

void
OpcodeControl::RETURN_VALUE()
{
    // Accept code after a return statement, even though it's never executed.
    // Otherwise, CPython's willingness to insert code after block
    // terminators causes problems.
    BasicBlock *dead_code = this->state_->CreateBasicBlock("dead_code");

    Value *retval = this->fbuilder_->Pop();
    this->fbuilder_->Return(retval);

    this->builder_.SetInsertPoint(dead_code);
}

void
OpcodeControl::YIELD_VALUE()
{
    assert(this->fbuilder_->is_generator() && "yield in non-generator!");
    BasicBlock *yield_resume =
        this->state_->CreateBasicBlock("yield_resume");
    // Save the current opcode index into f_lasti when we yield so
    // that, if tracing gets turned on while we're outside this
    // function we can jump back to the interpreter at the right
    // place.
    ConstantInt *yield_number =
        ConstantInt::getSigned(
            PyTypeBuilder<int>::get(this->fbuilder_->context()),
            this->fbuilder_->GetLasti());
    this->fbuilder_->AddYieldResumeBB(yield_number, yield_resume);

    Value *retval = this->fbuilder_->Pop();

    // Save everything to the frame object so it'll be there when we
    // resume from the yield.
    this->fbuilder_->CopyToFrameObject();

    // Save the right block to jump back to when we resume this generator.
    this->builder_.CreateStore(yield_number, this->fbuilder_->f_lasti_addr());

    // Yields return from the current function without unwinding the
    // stack.  They do trace the return and call _PyEval_ResetExcInfo
    // like everything else, so we jump to the common return block
    // instead of returning directly.
    this->builder_.CreateStore(retval, this->fbuilder_->retval_addr());
    this->builder_.CreateStore(
        ConstantInt::get(Type::getInt8Ty(this->fbuilder_->context()),
                         UNWIND_YIELD),
        this->fbuilder_->unwind_reason_addr());
    this->builder_.CreateBr(this->fbuilder_->do_return_block());

    // Continue inserting code inside the resume block.
    this->builder_.SetInsertPoint(yield_resume);
    // Set frame->f_lasti back to negative so that exceptions are
    // generated with llvm-provided line numbers.
    this->builder_.CreateStore(
        ConstantInt::getSigned(
            PyTypeBuilder<int>::get(this->fbuilder_->context()), -2),
        this->fbuilder_->f_lasti_addr());
}

void
OpcodeControl::JUMP_ABSOLUTE(llvm::BasicBlock *target,
                             llvm::BasicBlock *fallthrough)
{
    this->builder_.CreateBr(target);
}

enum BranchInput {
    BranchInputFalse = -1,
    BranchInputUnpredictable = 0,
    BranchInputTrue = 1,
};

// If the branch was predictable, return the branch direction: return
// BranchInputTrue if the branch was always True, return BranchInputFalse
// if the branch was always False. If the branch was unpredictable or if we have
// no data, return 0.
static BranchInput
predict_branch_input(const PyRuntimeFeedback *feedback)
{
    if (feedback == NULL) {
        COND_BRANCH_INC_STATS(not_enough_data);
        return BranchInputUnpredictable;
    }

    uintptr_t was_true = feedback->GetCounter(PY_FDO_JUMP_TRUE);
    uintptr_t was_false = feedback->GetCounter(PY_FDO_JUMP_FALSE);

    // We want to be relatively sure of our prediction. 200 was chosen by
    // running the benchmarks and increasing this threshold until we stopped
    // making massively-bad predictions. Example: increasing the threshold from
    // 100 to 200 reduced bad predictions in 2to3 from 3900+ to 2. We currently
    // optimize only perfectly-predictable branches as a baseline; later work
    // should explore the tradeoffs between bail penalties and improved codegen
    // gained from omiting rarely-taken branches.
    if (was_true + was_false <= 200) {
        COND_BRANCH_INC_STATS(not_enough_data);
        return BranchInputUnpredictable;
    }

    BranchInput result = (BranchInput)(bool(was_true) - bool(was_false));
    if (result == BranchInputUnpredictable) {
        COND_BRANCH_INC_STATS(unpredictable);
    }
    return result;
}

void
OpcodeControl::GetPyCondBranchBailBlock(unsigned true_idx,
                                        BasicBlock **true_block,
                                        unsigned false_idx,
                                        BasicBlock **false_block,
                                        unsigned *bail_idx,
                                        BasicBlock **bail_block)
{
    COND_BRANCH_INC_STATS(total);
    BranchInput branch_dir =
        predict_branch_input(this->fbuilder_->GetFeedback());

    if (branch_dir == BranchInputFalse) {
        *bail_idx = false_idx;
        *false_block = *bail_block = this->state_->CreateBasicBlock("FALSE_bail");
    }
    else if (branch_dir == BranchInputTrue) {
        *bail_idx = true_idx;
        *true_block = *bail_block = this->state_->CreateBasicBlock("TRUE_bail");
    }
    else {
        *bail_idx = 0;
        *bail_block = NULL;
    }
}

void
OpcodeControl::FillPyCondBranchBailBlock(BasicBlock *bail_to,
                                         unsigned bail_idx)
{
    COND_BRANCH_INC_STATS(optimized);
    BasicBlock *current = this->builder_.GetInsertBlock();

    this->builder_.SetInsertPoint(bail_to);
    this->fbuilder_->CreateGuardBailPoint(bail_idx, _PYGUARD_BRANCH);

    this->builder_.SetInsertPoint(current);
}

void
OpcodeControl::POP_JUMP_IF_FALSE(unsigned target_idx,
                                 unsigned fallthrough_idx,
                                 BasicBlock *target,
                                 BasicBlock *fallthrough)
{
    unsigned bail_idx = 0;
    BasicBlock *bail_to = NULL;
    this->GetPyCondBranchBailBlock(/*on true: */ target_idx, &target,
                                   /*on false: */ fallthrough_idx, &fallthrough,
                                   &bail_idx, &bail_to);

    Value *test_value = this->fbuilder_->Pop();
    Value *is_true = this->fbuilder_->IsPythonTrue(test_value);
    this->builder_.CreateCondBr(is_true, fallthrough, target);

    if (bail_to)
        this->FillPyCondBranchBailBlock(bail_to, bail_idx);
}

void
OpcodeControl::POP_JUMP_IF_TRUE(unsigned target_idx,
                                unsigned fallthrough_idx,
                                BasicBlock *target,
                                BasicBlock *fallthrough)
{
    unsigned bail_idx = 0;
    BasicBlock *bail_to = NULL;
    this->GetPyCondBranchBailBlock(/*on true: */ fallthrough_idx, &fallthrough,
                                   /*on false: */ target_idx, &target,
                                   &bail_idx, &bail_to);

    Value *test_value = this->fbuilder_->Pop();
    Value *is_true = this->fbuilder_->IsPythonTrue(test_value);
    this->builder_.CreateCondBr(is_true, target, fallthrough);

    if (bail_to)
        this->FillPyCondBranchBailBlock(bail_to, bail_idx);
}

void
OpcodeControl::JUMP_IF_FALSE_OR_POP(unsigned target_idx,
                                    unsigned fallthrough_idx,
                                    BasicBlock *target,
                                    BasicBlock *fallthrough)
{
    unsigned bail_idx = 0;
    BasicBlock *bail_to = NULL;
    this->GetPyCondBranchBailBlock(/*on true: */ target_idx, &target,
                                   /*on false: */ fallthrough_idx, &fallthrough,
                                   &bail_idx, &bail_to);

    BasicBlock *true_path =
        this->state_->CreateBasicBlock("JUMP_IF_FALSE_OR_POP_pop");
    Value *test_value = this->fbuilder_->Pop();
    this->fbuilder_->Push(test_value);
    // IsPythonTrue() will steal the reference to test_value, so make sure
    // the stack owns one too.
    this->state_->IncRef(test_value);
    Value *is_true = this->fbuilder_->IsPythonTrue(test_value);
    this->builder_.CreateCondBr(is_true, true_path, target);
    this->builder_.SetInsertPoint(true_path);
    test_value = this->fbuilder_->Pop();
    this->state_->DecRef(test_value);
    this->builder_.CreateBr(fallthrough);

    if (bail_to)
        this->FillPyCondBranchBailBlock(bail_to, bail_idx);
}

void
OpcodeControl::JUMP_IF_TRUE_OR_POP(unsigned target_idx,
                                   unsigned fallthrough_idx,
                                   BasicBlock *target,
                                   BasicBlock *fallthrough)
{
    unsigned bail_idx = 0;
    BasicBlock *bail_to = NULL;
    this->GetPyCondBranchBailBlock(/*on true: */ fallthrough_idx, &fallthrough,
                                   /*on false: */ target_idx, &target,
                                   &bail_idx, &bail_to);

    BasicBlock *false_path =
        this->state_->CreateBasicBlock("JUMP_IF_TRUE_OR_POP_pop");
    Value *test_value = this->fbuilder_->Pop();
    this->fbuilder_->Push(test_value);
    // IsPythonTrue() will steal the reference to test_value, so make sure
    // the stack owns one too.
    this->state_->IncRef(test_value);
    Value *is_true = this->fbuilder_->IsPythonTrue(test_value);
    this->builder_.CreateCondBr(is_true, target, false_path);
    this->builder_.SetInsertPoint(false_path);
    test_value = this->fbuilder_->Pop();
    this->state_->DecRef(test_value);
    this->builder_.CreateBr(fallthrough);

    if (bail_to)
        this->FillPyCondBranchBailBlock(bail_to, bail_idx);
}

}
