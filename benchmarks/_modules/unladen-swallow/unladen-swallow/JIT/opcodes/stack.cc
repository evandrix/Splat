#include "Python.h"

#include "JIT/opcodes/stack.h"
#include "JIT/llvm_fbuilder.h"

#include "llvm/BasicBlock.h"
#include "llvm/Function.h"
#include "llvm/Instructions.h"

using llvm::BasicBlock;
using llvm::ConstantInt;
using llvm::Function;
using llvm::Type;
using llvm::Value;

namespace py {

OpcodeStack::OpcodeStack(LlvmFunctionBuilder *fbuilder) :
    fbuilder_(fbuilder), state_(fbuilder->state())
{
}

void
OpcodeStack::POP_TOP()
{
    this->state_->DecRef(this->fbuilder_->Pop());
}

void
OpcodeStack::DUP_TOP()
{
    Value *first = this->fbuilder_->Pop();
    this->state_->IncRef(first);
    this->fbuilder_->Push(first);
    this->fbuilder_->Push(first);
}

void
OpcodeStack::DUP_TOP_TWO()
{
    Value *first = this->fbuilder_->Pop();
    Value *second = this->fbuilder_->Pop();
    this->state_->IncRef(first);
    this->state_->IncRef(second);
    this->fbuilder_->Push(second);
    this->fbuilder_->Push(first);
    this->fbuilder_->Push(second);
    this->fbuilder_->Push(first);
}

void
OpcodeStack::DUP_TOP_THREE()
{
    Value *first = this->fbuilder_->Pop();
    Value *second = this->fbuilder_->Pop();
    Value *third = this->fbuilder_->Pop();
    this->state_->IncRef(first);
    this->state_->IncRef(second);
    this->state_->IncRef(third);
    this->fbuilder_->Push(third);
    this->fbuilder_->Push(second);
    this->fbuilder_->Push(first);
    this->fbuilder_->Push(third);
    this->fbuilder_->Push(second);
    this->fbuilder_->Push(first);
}

void
OpcodeStack::ROT_TWO()
{
    Value *first = this->fbuilder_->Pop();
    Value *second = this->fbuilder_->Pop();
    this->fbuilder_->Push(first);
    this->fbuilder_->Push(second);
}

void
OpcodeStack::ROT_THREE()
{
    Value *first = this->fbuilder_->Pop();
    Value *second = this->fbuilder_->Pop();
    Value *third = this->fbuilder_->Pop();
    this->fbuilder_->Push(first);
    this->fbuilder_->Push(third);
    this->fbuilder_->Push(second);
}

void
OpcodeStack::ROT_FOUR()
{
    Value *first = this->fbuilder_->Pop();
    Value *second = this->fbuilder_->Pop();
    Value *third = this->fbuilder_->Pop();
    Value *fourth = this->fbuilder_->Pop();
    this->fbuilder_->Push(first);
    this->fbuilder_->Push(fourth);
    this->fbuilder_->Push(third);
    this->fbuilder_->Push(second);
}

}
