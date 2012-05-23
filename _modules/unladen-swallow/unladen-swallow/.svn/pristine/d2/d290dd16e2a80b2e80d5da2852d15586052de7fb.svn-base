// -*- C++ -*-
#ifndef OPCODE_STACK_H_
#define OPCODE_STACK_H_

#ifndef __cplusplus
#error This header expects to be included only in C++ source
#endif

namespace py {

class LlvmFunctionBuilder;
class LlvmFunctionState;

// This class contains all stack modifing opcodes.
class OpcodeStack
{
public:
    OpcodeStack(LlvmFunctionBuilder *fbuilder);

    void POP_TOP();
    void DUP_TOP();
    void DUP_TOP_TWO();
    void DUP_TOP_THREE();
    void ROT_TWO();
    void ROT_THREE();
    void ROT_FOUR();

private:
    LlvmFunctionBuilder *fbuilder_;
    LlvmFunctionState *state_;
};

}

#endif /* OPCODE_STACK_H_ */
