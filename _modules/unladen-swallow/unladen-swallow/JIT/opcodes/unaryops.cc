#include "Python.h"

#include "JIT/opcodes/unaryops.h"
#include "JIT/llvm_fbuilder.h"

#include "llvm/BasicBlock.h"
#include "llvm/Function.h"
#include "llvm/Instructions.h"

using llvm::BasicBlock;
using llvm::Function;
using llvm::Value;

namespace py {

OpcodeUnaryops::OpcodeUnaryops(LlvmFunctionBuilder *fbuilder) :
    fbuilder_(fbuilder), state_(fbuilder->state())
{
}

// Implementation of almost all unary operations
void
OpcodeUnaryops::GenericUnaryOp(const char *apifunc)
{
    Value *value = this->fbuilder_->Pop();
    Function *op =
        this->state_->GetGlobalFunction<PyObject*(PyObject*)>(apifunc);
    Value *result = this->state_->CreateCall(op, value, "unaryop_result");
    this->state_->DecRef(value);
    this->fbuilder_->PropagateExceptionOnNull(result);
    this->fbuilder_->Push(result);
}

#define UNARYOP_METH(NAME, APIFUNC)			\
void							\
OpcodeUnaryops::NAME()				        \
{							\
    this->GenericUnaryOp(#APIFUNC);			\
}

UNARYOP_METH(UNARY_CONVERT, PyObject_Repr)
UNARYOP_METH(UNARY_INVERT, PyNumber_Invert)
UNARYOP_METH(UNARY_POSITIVE, PyNumber_Positive)
UNARYOP_METH(UNARY_NEGATIVE, PyNumber_Negative)

#undef UNARYOP_METH

void
OpcodeUnaryops::UNARY_NOT()
{
    Value *value = this->fbuilder_->Pop();
    Value *retval = this->fbuilder_->builder().CreateSelect(
        this->fbuilder_->IsPythonTrue(value),
        this->state_->GetGlobalVariableFor((PyObject*)&_Py_ZeroStruct),
        this->state_->GetGlobalVariableFor((PyObject*)&_Py_TrueStruct),
        "UNARY_NOT_result");
    this->state_->IncRef(retval);
    this->fbuilder_->Push(retval);
}

}
