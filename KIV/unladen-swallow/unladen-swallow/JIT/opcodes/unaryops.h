// -*- C++ -*-
#ifndef OPCODE_UNARY_H_
#define OPCODE_UNARY_H_

#ifndef __cplusplus
#error This header expects to be included only in C++ source
#endif

namespace py {

class LlvmFunctionBuilder;
class LlvmFunctionState;

// This class contains all unary operators.
class OpcodeUnaryops
{
public:
    OpcodeUnaryops(LlvmFunctionBuilder *fbuilder);

    void UNARY_CONVERT();
    void UNARY_INVERT();
    void UNARY_POSITIVE();
    void UNARY_NEGATIVE();
    void UNARY_NOT();

private:
    // GenericUnaryOp's is "PyObject *(*)(PyObject *)"
    void GenericUnaryOp(const char *apifunc);

    LlvmFunctionBuilder *fbuilder_;
    LlvmFunctionState *state_;
};

}

#endif /* OPCODE_UNARY_H_ */
