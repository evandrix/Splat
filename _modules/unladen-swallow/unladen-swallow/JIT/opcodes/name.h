// -*- C++ -*-
#ifndef OPCODE_NAME_H_
#define OPCODE_NAME_H_

#ifndef __cplusplus
#error This header expects to be included only in C++ source
#endif

namespace py {

class LlvmFunctionBuilder;
class LlvmFunctionState;

// This class contains all opcodes used to access variables by name.
class OpcodeName
{
public:
    OpcodeName(LlvmFunctionBuilder *fbuilder);

    void LOAD_NAME(int index);
    void STORE_NAME(int index);
    void DELETE_NAME(int index);

private:
    LlvmFunctionBuilder *fbuilder_;
    LlvmFunctionState *state_;
};

}

#endif /* OPCODE_NAME_H_ */
