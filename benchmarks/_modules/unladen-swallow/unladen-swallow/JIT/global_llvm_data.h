// -*- C++ -*-
//
// Defines PyGlobalLlvmData, the per-interpreter state that LLVM needs
// to JIT-compile and optimize code.
#ifndef PYTHON_GLOBAL_LLVM_DATA_H
#define PYTHON_GLOBAL_LLVM_DATA_H

#ifndef __cplusplus
#error This header expects to be included only in C++ source
#endif

#ifdef WITH_LLVM
#include "JIT/global_llvm_data_fwd.h"

#include "llvm/LLVMContext.h"
#include "llvm/Metadata.h"
#include "llvm/PassManager.h"
#include "llvm/ADT/DenseSet.h"
#include "llvm/ADT/OwningPtr.h"
#include "llvm/ADT/SmallSet.h"
#include "llvm/ADT/StringMap.h"
#include "llvm/ADT/ValueMap.h"
#include "llvm/Support/ValueHandle.h"
#include "llvm/Instruction.h"

#include <string>

namespace llvm {
class DIFactory;
class ExecutionEngine;
class GlobalValue;
class GlobalVariable;
class MDNode;
class Module;
class Value;
}

class PyConstantMirror;

class PyTBAAType {
    unsigned pytbaa_kind_;
    llvm::TrackingVH<llvm::MDNode> type_metadata_;

public:
    PyTBAAType(llvm::LLVMContext &context, llvm::StringRef name) {
        pytbaa_kind_ = context.getMDKindID("PyTBAA");
        llvm::Value *tbaa_type_string = llvm::MDString::get(context, name);
        type_metadata_ = llvm::MDNode::get(context, &tbaa_type_string, 1);
    }

    PyTBAAType() : pytbaa_kind_(), type_metadata_() {}

    void MarkInstruction(llvm::Value *value) const {
        if (llvm::Instruction *instruction = 
            llvm::dyn_cast<llvm::Instruction>(value)) {
            instruction->setMetadata(pytbaa_kind_, type_metadata_);
        }
    }

    const llvm::TrackingVH<llvm::MDNode> &type() const {
        return type_metadata_;
    }
};

// A struct to associate functions and types with optimized functions
// for inlining. This supports inlining of binary operator implementations
// that have been compiled with Clang.
struct InlineOperatorEntry {
    // This holds a representation of the operator name. Usually the 
    // function name of the operator we want to inline.
    const char *op;
    const PyTypeObject *lhs_type;
    const PyTypeObject *rhs_type;
};

// Indicate that we don't care about the specialization argument's type.
static const PyTypeObject *const Wildcard = NULL;

namespace llvm {

template<>
struct DenseMapInfo<InlineOperatorEntry> {
    typedef DenseMapInfo<const PyTypeObject *> PyTypeObjectInfo;
    typedef DenseMapInfo<const char *> ConstCharStarInfo;

    static inline InlineOperatorEntry getEmptyKey() {
        InlineOperatorEntry e;
        e.op = ConstCharStarInfo::getEmptyKey();
        e.rhs_type = e.lhs_type = PyTypeObjectInfo::getEmptyKey();
        return e;
    }

    static inline InlineOperatorEntry getTombstoneKey() {
        InlineOperatorEntry e;
        e.op = ConstCharStarInfo::getTombstoneKey();
        e.rhs_type = e.lhs_type = PyTypeObjectInfo::getEmptyKey();
        return e;
    }

    static unsigned getHashValue(const InlineOperatorEntry& Val) {
        // Some avalanching inspired by 
        // http://burtleburtle.net/bob/hash/doobs.html.
        uint64_t key =
            (uint64_t)PyTypeObjectInfo::getHashValue(Val.lhs_type) << 32
          | (uint64_t)PyTypeObjectInfo::getHashValue(Val.rhs_type);
        key += ~(key << 32);
        key ^= (key >> 22);
        key += ~(key << 13);
        key ^= (key >> 8);
        key += (key << 3);
        key ^= (key >> 15);
        key += ~(key << 27);
        key ^= (key >> 31);

        if (Val.op != NULL) {
            // From http://burtleburtle.net/bob/hash/doobs.html
            // Bernstein's hash
            uint64_t hash = 0xdeadbeef;
            const char *ptr = Val.op;
            while (*ptr != 0) {
                hash = (hash * 65) + *ptr++;
            }
            key = key | hash;
        }
        key += ~(key << 32);
        key ^= (key >> 22);
        key += ~(key << 13);
        key ^= (key >> 8);
        key += (key << 3);
        key ^= (key >> 15);
        key += ~(key << 27);
        key ^= (key >> 31);

        return (unsigned)key;
    }

    static bool isPod() { return true; }

    static bool isEqual(const InlineOperatorEntry& LHS,
                        const InlineOperatorEntry& RHS) {
        if (LHS.lhs_type != RHS.lhs_type ||
            LHS.rhs_type != RHS.rhs_type)
            return false;

        if (LHS.op == RHS.op)
            return true;

        if (LHS.op == NULL || RHS.op == NULL)
            return false;

        return strcmp(LHS.op, RHS.op) == 0;
    }
};

}  // namespace llvm

// Static mapping of binop name -> inlinable LLVM function.
class OptimizedOps {
public:
    // Map default binary operations and type information to optimized versions.
    typedef llvm::DenseMap<InlineOperatorEntry, const char*> InlinableOpMap;

    OptimizedOps() {
#define INLINABLE_OP(OP, LHS, RHS, OPT) { \
        InlineOperatorEntry e; \
        e.op = #OP; \
        e.lhs_type = &LHS; e.rhs_type = &RHS; \
        this->optimized_operations_[e] = #OPT; \
    }
    // Int specializations.
    INLINABLE_OP(PyNumber_Add, PyInt_Type, PyInt_Type,
                 _PyLlvm_BinAdd_Int);
    INLINABLE_OP(PyNumber_Subtract, PyInt_Type, PyInt_Type,
                 _PyLlvm_BinSub_Int);
    INLINABLE_OP(PyNumber_Multiply, PyInt_Type, PyInt_Type,
                 _PyLlvm_BinMult_Int);
    INLINABLE_OP(PyNumber_Divide, PyInt_Type, PyInt_Type,
                 _PyLlvm_BinDiv_Int);
    INLINABLE_OP(PyNumber_Remainder, PyInt_Type, PyInt_Type,
                 _PyLlvm_BinMod_Int);

    // Float specializations
    INLINABLE_OP(PyNumber_Add, PyFloat_Type, PyFloat_Type,
                 _PyLlvm_BinAdd_Float);
    INLINABLE_OP(PyNumber_Subtract, PyFloat_Type, PyFloat_Type,
                 _PyLlvm_BinSub_Float);
    INLINABLE_OP(PyNumber_Multiply, PyFloat_Type, PyFloat_Type,
                 _PyLlvm_BinMult_Float);
    INLINABLE_OP(PyNumber_Divide, PyFloat_Type, PyFloat_Type,
                 _PyLlvm_BinDiv_Float);

    // Int combined with float
    INLINABLE_OP(PyNumber_Multiply, PyFloat_Type, PyInt_Type,
                 _PyLlvm_BinMul_FloatInt);
    INLINABLE_OP(PyNumber_Divide, PyFloat_Type, PyInt_Type,
                 _PyLlvm_BinDiv_FloatInt);

    // List specializations
    INLINABLE_OP(PyObject_GetItem, PyList_Type, PyInt_Type,
                 _PyLlvm_BinSubscr_List);

    // Tuple specializations
    INLINABLE_OP(PyObject_GetItem, PyTuple_Type, PyInt_Type,
                 _PyLlvm_BinSubscr_Tuple);

    // Cmpop Integer specializations
    INLINABLE_OP(PyCmp_LT, PyInt_Type, PyInt_Type, _PyLlvm_BinLt_Int);
    INLINABLE_OP(PyCmp_LE, PyInt_Type, PyInt_Type, _PyLlvm_BinLe_Int);
    INLINABLE_OP(PyCmp_EQ, PyInt_Type, PyInt_Type, _PyLlvm_BinEq_Int);
    INLINABLE_OP(PyCmp_NE, PyInt_Type, PyInt_Type, _PyLlvm_BinNe_Int);
    INLINABLE_OP(PyCmp_GT, PyInt_Type, PyInt_Type, _PyLlvm_BinGt_Int);
    INLINABLE_OP(PyCmp_GE, PyInt_Type, PyInt_Type, _PyLlvm_BinGe_Int);

    // Cmpop Float specialization
    INLINABLE_OP(PyCmp_GT, PyFloat_Type, PyFloat_Type, _PyLlvm_BinGt_Float);

#undef INLINABLE_OP

    // Wildcard as second operand
#define INLINABLE_OP_W(OP, LHS, OPT) { \
        InlineOperatorEntry e; \
        e.op = #OP; \
        e.lhs_type = &LHS; e.rhs_type = Wildcard; \
        this->optimized_operations_[e] = #OPT; \
    }

    // String specializations
    INLINABLE_OP_W(PyNumber_Remainder, PyString_Type,
                 _PyLlvm_BinMod_Str);
    INLINABLE_OP_W(PyNumber_Remainder, PyUnicode_Type,
                 _PyLlvm_BinMod_Unicode);

#undef INLINEABLE_OP_W

    }

    const char *Find(const char *op, const PyTypeObject *lhs_type,
                     const PyTypeObject *rhs_type) const {
        InlineOperatorEntry key;
        key.op = op;
        key.lhs_type = lhs_type;
        key.rhs_type = rhs_type;

        return this->optimized_operations_.lookup(key);
    }

private:
    InlinableOpMap optimized_operations_;
    typedef InlinableOpMap::const_iterator const_iterator;
};


struct PyGlobalLlvmData {
public:
    // Retrieves the PyGlobalLlvmData out of the interpreter state.
    static PyGlobalLlvmData *Get();

    PyGlobalLlvmData();
    ~PyGlobalLlvmData();

    // Optimize f to a particular level. Currently, levels from 0 to 2
    // are valid.
    //
    // Returns 0 on success or -1 on failure (if level is out of
    // range, for example).
    int Optimize(llvm::Function &f, int level);

    llvm::ExecutionEngine *getExecutionEngine() { return this->engine_; }

    // Use this accessor for the LLVMContext rather than
    // getGlobalContext() directly so that we can more easily add new
    // contexts later.
    llvm::LLVMContext &context() const { return llvm::getGlobalContext(); }

    llvm::Module *module() const { return this->module_; }

    PyConstantMirror &constant_mirror() const 
    { 
        return *this->constant_mirror_; 
    }

    /// Can be used to add debug info to LLVM functions.
    llvm::DIFactory &DebugInfo() { return *this->debug_info_; }

    // Runs globaldce to remove unreferenced global variables.
    // Globals still used in machine code must be referenced from IR or this
    // pass will delete them and crash.
    void CollectUnusedGlobals();

    // Run globaldce if we've allocated a significant number of globals between
    // calls to this function.  This function uses the same strategy as
    // Python's gc to avoid running the collection "too often"; see
    // long_lived_pending and long_lived_total in Modules/gcmodule.c for
    // details.  Running MaybeCollectUnusedGlobals() for the second time in a
    // row with no allocation in between should be a no-op.
    void MaybeCollectUnusedGlobals();

    // Helper functions for building functions in IR.

    // Returns an i8* pointing to a 0-terminated C string holding the
    // characters from value.  If two such strings have the same
    // value, only one global constant will be created in the Module.
    llvm::Value *GetGlobalStringPtr(const std::string &value);

    // Used to store type inheritance for TBAA by mapping types to all
    // possible subtypes.
    typedef llvm::ValueMap<llvm::MDNode *,
                llvm::SmallSet<
                    llvm::TrackingVH<llvm::MDNode>, 4> > TBAAInheritanceMap;

    unsigned GetTBAAKind() {
        return context().getMDKindID("PyTBAA");
    }

    bool IsTBAASubtype(llvm::MDNode *p, llvm::MDNode *c) const;

    PyTBAAType tbaa_stack;
    PyTBAAType tbaa_locals;
    PyTBAAType tbaa_PyObject;
    PyTBAAType tbaa_PyIntObject;
    PyTBAAType tbaa_PyFloatObject;
    PyTBAAType tbaa_PyStringObject;
    PyTBAAType tbaa_PyUnicodeObject;
    PyTBAAType tbaa_PyListObject;
    PyTBAAType tbaa_PyTupleObject;

    OptimizedOps optimized_ops;

private:
    // We use Clang to compile a number of C functions to LLVM IR. Install
    // those functions and set up any special calling conventions or attributes
    // we may want.
    void InstallInitialModule();

    void InitializeOptimizations();

    void InitializeTBAA();

    void AddTBAAInherits(PyTBAAType &p, PyTBAAType &c);

    void AddPythonAliasAnalyses(llvm::FunctionPassManager *mngr);

    // We have a single global module that holds all compiled code.
    // Any cached global object that function definitions use will be
    // stored in here.  These are owned by engine_.
    llvm::Module *module_;
    llvm::OwningPtr<llvm::DIFactory> debug_info_;

    llvm::ExecutionEngine *engine_;  // Not modified after the constructor.

    std::vector<llvm::FunctionPassManager *> optimizations_;
    llvm::PassManager gc_;

    // Cached data in module_.  The WeakVH should only hold GlobalVariables.
    llvm::StringMap<llvm::WeakVH> constant_strings_;

    // All the GlobalValues that are backed by the stdlib bitcode file.  We're
    // not allowed to delete these.
    llvm::DenseSet<llvm::AssertingVH<const llvm::GlobalValue> > bitcode_gvs_;

    llvm::OwningPtr<PyConstantMirror> constant_mirror_;

    unsigned num_globals_after_last_gc_;

    // The MetadataKind we register our type information with
    unsigned tbaa_metadata_kind_;

    // All Metadata for TBAA types
    llvm::StringMap<llvm::MDNode *> tbaa_types_;

    // Metadata for TBAA inheritance
    TBAAInheritanceMap tbaa_inheritance_;
};
#endif  /* WITH_LLVM */

#endif  /* PYTHON_GLOBAL_LLVM_DATA_H */
