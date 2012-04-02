#include "Python.h"

#include "JIT/opcodes/binops.h"
#include "JIT/llvm_fbuilder.h"
#include "Util/Instrumentation.h"

#include "llvm/BasicBlock.h"
#include "llvm/Function.h"
#include "llvm/Instructions.h"
#include "llvm/Support/ManagedStatic.h"

using llvm::BasicBlock;
using llvm::Function;
using llvm::Value;
using llvm::errs;

#ifdef Py_WITH_INSTRUMENTATION
// These are used as template parameter and are required to have external
// linkage. As const char[] default to static in C++, we have to force it.
extern const char binop_full[], binop_short[];
const char binop_full[] = "Binary operators";
const char binop_short[] = "binops";

static llvm::ManagedStatic<
    OpStats<binop_full, binop_short> > binary_operator_stats;

#define BINOP_INC_STATS(field) binary_operator_stats->field++

void
py::OpcodeBinops::IncStatsOptimized()
{
    BINOP_INC_STATS(optimized);
}

void
py::OpcodeBinops::IncStatsOmitted()
{
    BINOP_INC_STATS(omitted);
}

void
py::OpcodeBinops::IncStatsTotal()
{
    BINOP_INC_STATS(total);
}

#else
#define BINOP_INC_STATS(field)
#endif /* Py_WITH_INSTRUMENTATION */

namespace py {

OpcodeBinops::OpcodeBinops(LlvmFunctionBuilder *fbuilder) :
    fbuilder_(fbuilder), state_(fbuilder->state())
{
}

// Common code for almost all binary operations
void
OpcodeBinops::GenericBinOp(const char *apifunc)
{
    Value *rhs = this->fbuilder_->Pop();
    Value *lhs = this->fbuilder_->Pop();
    Function *op = this->state_->GetGlobalFunction<
        PyObject*(PyObject*, PyObject*)>(apifunc);
    Value *result = this->state_->CreateCall(op, lhs, rhs, "binop_result");
    this->state_->DecRef(lhs);
    this->state_->DecRef(rhs);
    this->fbuilder_->PropagateExceptionOnNull(result);
    this->fbuilder_->Push(result);
}

void
OpcodeBinops::OptimizedBinOp(const char *apifunc)
{
    const PyTypeObject *lhs_type = this->fbuilder_->GetTypeFeedback(0);
    const PyTypeObject *rhs_type = this->fbuilder_->GetTypeFeedback(1);
    if (lhs_type == NULL || rhs_type == NULL) {
        BINOP_INC_STATS(unpredictable);
        this->GenericBinOp(apifunc);
        return;
    }

    // We're always specializing the receiver, so don't check the lhs for
    // wildcards.
    const char *name = this->fbuilder_->llvm_data()->optimized_ops.
        Find(apifunc, lhs_type, rhs_type);

    if (name == NULL) {
        name = this->fbuilder_->llvm_data()->optimized_ops.
            Find(apifunc, lhs_type, Wildcard);
        if (name == NULL) {
            BINOP_INC_STATS(omitted);
            this->GenericBinOp(apifunc);
            return;
        }
    }

    this->fbuilder_->SetOpcodeArgsWithGuard(2);

    BINOP_INC_STATS(optimized);
    BasicBlock *success = this->state_->CreateBasicBlock("BINOP_OPT_success");
    BasicBlock *bailpoint = this->state_->CreateBasicBlock("BINOP_OPT_bail");

    Value *lhs = this->fbuilder_->GetOpcodeArg(0);
    Value *rhs = this->fbuilder_->GetOpcodeArg(1);

    // This strategy of bailing may duplicate the work (once in the inlined
    // version, once again in the eval loop). This is generally (in a Halting
    // Problem kind of way) unsafe, but works since we're dealing with a known
    // subset of all possible types where we control the semantics of __add__,
    // etc.
    Function *op =
        this->state_->GetGlobalFunction<PyObject*(PyObject*, PyObject*)>(name);
    Value *result = this->state_->CreateCall(op, lhs, rhs, "binop_result");
    this->fbuilder_->builder().CreateCondBr(this->state_->IsNull(result),
                                            bailpoint, success);

    this->fbuilder_->builder().SetInsertPoint(bailpoint);
    this->fbuilder_->CreateGuardBailPoint(_PYGUARD_BINOP);

    this->fbuilder_->builder().SetInsertPoint(success);
    this->fbuilder_->BeginOpcodeImpl();
    this->state_->DecRef(lhs);
    this->state_->DecRef(rhs);
    this->fbuilder_->SetOpcodeResult(0, result);
}

#define BINOP_METH(OPCODE, APIFUNC)     \
void                                    \
OpcodeBinops::OPCODE()                  \
{                                       \
    BINOP_INC_STATS(total);             \
    BINOP_INC_STATS(omitted);           \
    this->GenericBinOp(#APIFUNC);       \
}

#define BINOP_OPT(OPCODE, APIFUNC)      \
void                                    \
OpcodeBinops::OPCODE()                  \
{                                       \
    BINOP_INC_STATS(total);             \
    this->OptimizedBinOp(#APIFUNC);     \
}

BINOP_OPT(BINARY_ADD, PyNumber_Add)
BINOP_OPT(BINARY_SUBTRACT, PyNumber_Subtract)
BINOP_OPT(BINARY_MULTIPLY, PyNumber_Multiply)
BINOP_OPT(BINARY_DIVIDE, PyNumber_Divide)
BINOP_OPT(BINARY_MODULO, PyNumber_Remainder)
BINOP_OPT(BINARY_SUBSCR, PyObject_GetItem)

BINOP_METH(BINARY_TRUE_DIVIDE, PyNumber_TrueDivide)
BINOP_METH(BINARY_LSHIFT, PyNumber_Lshift)
BINOP_METH(BINARY_RSHIFT, PyNumber_Rshift)
BINOP_METH(BINARY_OR, PyNumber_Or)
BINOP_METH(BINARY_XOR, PyNumber_Xor)
BINOP_METH(BINARY_AND, PyNumber_And)
BINOP_METH(BINARY_FLOOR_DIVIDE, PyNumber_FloorDivide)

BINOP_METH(INPLACE_ADD, PyNumber_InPlaceAdd)
BINOP_METH(INPLACE_SUBTRACT, PyNumber_InPlaceSubtract)
BINOP_METH(INPLACE_MULTIPLY, PyNumber_InPlaceMultiply)
BINOP_METH(INPLACE_TRUE_DIVIDE, PyNumber_InPlaceTrueDivide)
BINOP_METH(INPLACE_DIVIDE, PyNumber_InPlaceDivide)
BINOP_METH(INPLACE_MODULO, PyNumber_InPlaceRemainder)
BINOP_METH(INPLACE_LSHIFT, PyNumber_InPlaceLshift)
BINOP_METH(INPLACE_RSHIFT, PyNumber_InPlaceRshift)
BINOP_METH(INPLACE_OR, PyNumber_InPlaceOr)
BINOP_METH(INPLACE_XOR, PyNumber_InPlaceXor)
BINOP_METH(INPLACE_AND, PyNumber_InPlaceAnd)
BINOP_METH(INPLACE_FLOOR_DIVIDE, PyNumber_InPlaceFloorDivide)

#undef BINOP_METH
#undef BINOP_OPT

// PyNumber_Power() and PyNumber_InPlacePower() take three arguments, the
// third should be Py_None when calling from BINARY_POWER/INPLACE_POWER.
void
OpcodeBinops::GenericPowOp(const char *apifunc)
{
    Value *rhs = this->fbuilder_->Pop();
    Value *lhs = this->fbuilder_->Pop();
    Function *op = this->state_->GetGlobalFunction<
        PyObject*(PyObject*, PyObject*, PyObject *)>(apifunc);
    Value *pynone = this->state_->GetGlobalVariableFor(&_Py_NoneStruct);
    Value *result = this->state_->CreateCall(op, lhs, rhs, pynone,
                                             "powop_result");
    this->state_->DecRef(lhs);
    this->state_->DecRef(rhs);
    this->fbuilder_->PropagateExceptionOnNull(result);
    this->fbuilder_->Push(result);
}

void
OpcodeBinops::BINARY_POWER()
{
    this->GenericPowOp("PyNumber_Power");
}

void
OpcodeBinops::INPLACE_POWER()
{
    this->GenericPowOp("PyNumber_InPlacePower");
}

}
