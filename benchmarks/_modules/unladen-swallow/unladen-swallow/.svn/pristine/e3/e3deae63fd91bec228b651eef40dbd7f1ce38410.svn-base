// -*- C++ -*-
#ifndef OPCODE_CONTAINER_H_
#define OPCODE_CONTAINER_H_

#ifndef __cplusplus
#error This header expects to be included only in C++ source
#endif

#include "llvm/Support/IRBuilder.h"
#include "llvm/Support/TargetFolder.h"

namespace py {

class LlvmFunctionBuilder;
class LlvmFunctionState;

// This class contains most opcodes related to containers.
// BINARY_SUBSCR can be found in OpcodeBinops.
class OpcodeContainer
{
public:
    OpcodeContainer(LlvmFunctionBuilder *fbuilder);

    void BUILD_TUPLE(int size);
    void BUILD_LIST(int size);
    void BUILD_MAP(int size);

    void UNPACK_SEQUENCE(int size);

    void STORE_SUBSCR();
    void DELETE_SUBSCR();
    void STORE_MAP();
    void LIST_APPEND();

    // IMPORT_NAME is a bit of a stretch, but container is the closest group.
    // It imports something from a container/module.
    void IMPORT_NAME();

private:
    typedef llvm::IRBuilder<true, llvm::TargetFolder> BuilderT;

    // Helper method for building a new sequence from items on the stack.
    // 'size' is the number of items to build, 'createname' the Python/C API
    // function to call to create the sequence, and 'getitemslot' is called
    // to get each item's address (GetListItemSlot or GetTupleItemSlot.)
    void BuildSequenceLiteral(
        int size, const char *createname,
        llvm::Value *(LlvmFunctionState::*getitemslot)(llvm::Value *, int));

    // _safe is guaranteed to work; _list_int is specialized for indexing a list
    // with an int.
    void STORE_SUBSCR_safe();
    void STORE_SUBSCR_list_int();

    // A fast version that avoids the import machinery if sys.modules and other
    // modules haven't changed. Returns false if the attempt to optimize failed;
    // the safe version in IMPORT_NAME() will be used.
    bool IMPORT_NAME_fast();

    LlvmFunctionBuilder *fbuilder_;
    LlvmFunctionState *state_;
    BuilderT &builder_;
};

}

#endif /* OPCODE_CONTAINER_H_ */
