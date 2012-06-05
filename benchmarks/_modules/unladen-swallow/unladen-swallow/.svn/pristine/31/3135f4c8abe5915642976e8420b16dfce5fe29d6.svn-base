// -*- C++ -*-
#ifndef OPCODE_ATTRIBUTES_H_
#define OPCODE_ATTRIBUTES_H_

#ifndef __cplusplus
#error This header expects to be included only in C++ source
#endif

#include "llvm/Support/IRBuilder.h"
#include "llvm/Support/TargetFolder.h"

namespace llvm {
    class BasicBlock;
    class Value;
}

class PyGlobalLlvmData;

namespace py {

class LlvmFunctionBuilder;
class LlvmFunctionState;


// Specifies which kind of attribute access we are performing, either load
// or store.  Eventually we may support delete, but they are rare enough
// that it is unlikely to be worth it.
enum AttrAccessKind {
    ATTR_ACCESS_LOAD,
    ATTR_ACCESS_STORE
};

// This class encapsulates the common data and code for doing optimized
// attribute access.  This object helps perform checks, generate guard
// code, and register invalidation listeners when generating an optimized
// LOAD_ATTR or STORE_ATTR opcode.
class AttributeAccessor {
public:
    // Construct an attribute accessor object.  "name" is a reference to
    // the attribute to access borrowed from co_names, and access_kind
    // determines whether we are generating a LOAD_ATTR or STORE_ATTR
    // opcode.
    AttributeAccessor(LlvmFunctionBuilder *fbuilder, PyObject *name,
                      AttrAccessKind kind)
        : fbuilder_(fbuilder),
          access_kind_(kind),
          guard_type_(0),
          name_(name),
          dictoffset_(0),
          descr_(0),
          guard_descr_type_(0),
          is_data_descr_(false),
          descr_get_(0),
          descr_set_(0),
          guard_type_v_(0),
          name_v_(0),
          dictoffset_v_(0),
          descr_v_(0),
          is_data_descr_v_(0),
          bail_block_(0) { }

    // This helper method returns false if a LOAD_ATTR or STORE_ATTR opcode
    // cannot be optimized.  If the opcode can be optimized, it fills in
    // all of the fields of this object by reading the feedback from the
    // code object.
    bool CanOptimizeAttrAccess();

    // This helper method emits the common type guards for an optimized
    // LOAD_ATTR or STORE_ATTR.
    void GuardAttributeAccess(llvm::Value *obj_v, llvm::BasicBlock *do_access);

    LlvmFunctionBuilder *fbuilder_;
    AttrAccessKind access_kind_;

    // This is the type we have chosen to guard on from the feedback.  All
    // of the other attributes hold references borrowed from this type
    // reference.  The validity of this type reference is ensured by
    // listening for type modification and destruction.
    PyTypeObject *guard_type_;

    PyObject *name_;
    long dictoffset_;

    // This is the descriptor cached from the type object.  It may be NULL
    // if the type has no attribute with the name we're looking up.
    PyObject *descr_;
    // This is the type of the descriptor, if it exists, at compile time.
    // We guard that the type of the descriptor is the same at run time as
    // it is at compile time.
    PyTypeObject *guard_descr_type_;
    // These fields mirror the descriptor accessor fields if they are
    // available.
    bool is_data_descr_;
    descrgetfunc descr_get_;
    descrsetfunc descr_set_;

    // llvm::Value versions of the above data created with EmbedPointer or
    // ConstantInt::get.
    llvm::Value *guard_type_v_;
    llvm::Value *name_v_;
    llvm::Value *dictoffset_v_;
    llvm::Value *descr_v_;
    llvm::Value *is_data_descr_v_;

    llvm::BasicBlock *bail_block_;

private:
    typedef llvm::IRBuilder<true, llvm::TargetFolder> BuilderT;

    // Cache all of the data required to do attribute access.  This fills
    // in all of the non-llvm::Value fields of this object.
    void CacheTypeLookup();

    // Make LLVM Value versions of all the data we're caching in the IR.
    // Note that we borrow references to the descriptor from the type
    // object.  If the type object is modified to drop its references, this
    // code will be invalidated.  Furthermore, if the type object itself is
    // freed, this code will be invalidated, which will safely drop our
    // references.
    void MakeLlvmValues();
};


// This class includes all code related to access attributes.
class OpcodeAttributes
{
public:
    OpcodeAttributes(LlvmFunctionBuilder *fbuilder);

    void LOAD_ATTR(int index);
    void LOAD_METHOD(int index);
    void STORE_ATTR(int index);
    void DELETE_ATTR(int index);

private:
    // LOAD/STORE_ATTR_safe always works, while LOAD/STORE_ATTR_fast is
    // optimized to skip the descriptor/method lookup on the type if the object
    // type matches.  It will return false if it fails.
    void LOAD_ATTR_safe(int names_index);
    bool LOAD_ATTR_fast(int names_index);
    void STORE_ATTR_safe(int names_index);
    bool STORE_ATTR_fast(int names_index);
    bool LOAD_METHOD_known(int names_index);
    bool LOAD_METHOD_unknown(int names_index);

    typedef llvm::IRBuilder<true, llvm::TargetFolder> BuilderT;

    LlvmFunctionBuilder *const fbuilder_;
    LlvmFunctionState *state_;
    BuilderT &builder_;
    PyGlobalLlvmData *const llvm_data_;
};

}

#endif /* OPCODE_ATTRIBUTES_H_ */
