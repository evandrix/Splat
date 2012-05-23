#include "JIT/PyTBAliasAnalysis.h"

#include "JIT/ConstantMirror.h"
#include "JIT/PyTypeBuilder.h"

#include "llvm/Analysis/AliasAnalysis.h"
#include "llvm/ADT/SmallPtrSet.h"
#include "llvm/ADT/DenseMap.h"
#include "llvm/ADT/StringMap.h"

#include <utility>

namespace {

using llvm::AliasAnalysis;
using llvm::BasicBlock;
using llvm::BranchInst;
using llvm::CallInst;
using llvm::Function;
using llvm::FunctionPass;
using llvm::ICmpInst;
using llvm::Instruction;
using llvm::LLVMContext;
using llvm::MDNode;
using llvm::Module;
using llvm::Pass;
using llvm::PassInfo;
using llvm::Value;
using llvm::dyn_cast;
using llvm::isa;

// This function unwinds casts and GEPs until it finds an instruction with
// a TBAA Metadata node. Returns NULL if no metadata is found. Automatically
// tags pointers to PyObject.
static MDNode *getFirstMDNode(const PyGlobalLlvmData *const llvm_data,
                              const unsigned kind, const Value *V)
{
    unsigned MaxLookup = 10;
    bool is_pyobject = false;
    const llvm::Type *pyobject_type =
        PyTypeBuilder<PyObject*>::get(V->getContext());

    do {
        if (const Instruction *instr = dyn_cast<Instruction>(V))
            if (MDNode *n = instr->getMetadata(kind))
                return n;

        // TODO: This makes the assumption that there is only one struct
        // with the structure of a PyObject. If this changes, this may mark
        // Values wrongly.
        if (V->getType() == pyobject_type)
            is_pyobject = true;

        // It's save to remove any GEPs. Even if the type of the value changes,
        // it is still within some outer structure about which we can make
        // aliasing assumptions.
        if (const llvm::GEPOperator *GEP = dyn_cast<llvm::GEPOperator>(V)) {
            V = GEP->getPointerOperand();
        } else if (llvm::Operator::getOpcode(V) == llvm::Instruction::BitCast) {
            V = llvm::cast<llvm::Operator>(V)->getOperand(0);
        } else if (const llvm::GlobalAlias *GA =
                   dyn_cast<llvm::GlobalAlias>(V)) {
            if (GA->mayBeOverridden()) {
                break;
            }
            V = GA->getAliasee();
        } else {
            break;
        }
    } while (--MaxLookup);

    if (is_pyobject) {
        return llvm_data->tbaa_PyObject.type();
    }
    return NULL;
}



class PyTBAliasAnalysis : public FunctionPass, public AliasAnalysis {
public:
    static char ID;
    PyTBAliasAnalysis(PyGlobalLlvmData &global_data)
        : FunctionPass(&ID), context_(&global_data.context()),
          llvm_data_(&global_data),
          kind_(global_data.GetTBAAKind())
    {}

    PyTBAliasAnalysis()
        : FunctionPass(&ID), context_(NULL), llvm_data_(NULL),
          kind_(0)
    {}

    virtual void getAnalysisUsage(llvm::AnalysisUsage &usage) const {
        AliasAnalysis::getAnalysisUsage(usage);
        usage.setPreservesAll();
    }

    virtual bool runOnFunction(Function&);

    virtual AliasResult alias(const Value *V1, unsigned V1Size,
                              const Value *V2, unsigned V2Size);

    virtual void *getAdjustedAnalysisPointer(const PassInfo *PI) {
        if (PI->isPassID(&AliasAnalysis::ID))
            return (AliasAnalysis*)this;
        return this;
    }

private:
    bool typesMayAlias(MDNode *T1, MDNode *T2) const;

    const LLVMContext *const context_;
    const PyGlobalLlvmData *const llvm_data_;
    const unsigned kind_;
};


// The address of this variable identifies the pass.  See
// http://llvm.org/docs/WritingAnLLVMPass.html#basiccode.
char PyTBAliasAnalysis::ID = 0;

// Register this pass.
static llvm::RegisterPass<PyTBAliasAnalysis>
U("python-tbaa", "Python-specific Type Based Alias Analysis", false, true);

// Declare that we implement the AliasAnalysis interface.
static llvm::RegisterAnalysisGroup<AliasAnalysis> V(U);


bool
PyTBAliasAnalysis::runOnFunction(Function &f)
{
    AliasAnalysis::InitializeAliasAnalysis(this);
    return false;
}


AliasAnalysis::AliasResult
PyTBAliasAnalysis::alias(const Value *V1, unsigned V1Size,
                         const Value *V2, unsigned V2Size)
{
    MDNode *T1 = getFirstMDNode(this->llvm_data_, this->kind_,
                                const_cast<Value*>(V1));
    MDNode *T2 = getFirstMDNode(this->llvm_data_, this->kind_,
                                const_cast<Value*>(V2));

    if (T1 == NULL || T2 == NULL) {
        return AliasAnalysis::alias(V1, V1Size, V2, V2Size);
    }

    if (!this->typesMayAlias(T1, T2)) {
        return NoAlias;
    }
    return AliasAnalysis::alias(V1, V1Size, V2, V2Size);
}

bool
PyTBAliasAnalysis::typesMayAlias(MDNode *T1, MDNode *T2) const
{
    if (T1 == T2)
        return true;

    if (llvm_data_->IsTBAASubtype(T1, T2))
        return true;

    if (llvm_data_->IsTBAASubtype(T2, T1))
        return true;

    return false;
}

} // End of anonymous namespace

Pass *
CreatePyTBAliasAnalysis(PyGlobalLlvmData &global_data)
{
    return new PyTBAliasAnalysis(global_data);
}


namespace {

class PyTypeMarkingPass : public FunctionPass {
public:
    static char ID;
    PyTypeMarkingPass(PyGlobalLlvmData &global_data);

    PyTypeMarkingPass()
        : FunctionPass(&ID), context_(NULL), llvm_data_(NULL), kind_(0)
    {}

    virtual void getAnalysisUsage(llvm::AnalysisUsage &usage) const {
        usage.setPreservesAll();
    }

    virtual bool runOnFunction(Function&);

private:
    void addMark(const char *name, const PyTBAAType &type);
    bool markFunction(CallInst *callInst);

    const LLVMContext *const context_;
    const PyGlobalLlvmData *const llvm_data_;
    const unsigned kind_;

    llvm::ValueMap<Function *, const PyTBAAType *> func_map_;
};


// The address of this variable identifies the pass.  See
// http://llvm.org/docs/WritingAnLLVMPass.html#basiccode.
char PyTypeMarkingPass::ID = 0;

// Register this pass.
static llvm::RegisterPass<PyTypeMarkingPass>
W("python-typemarking", "Python-specific Type Marking pass", false, true);


PyTypeMarkingPass::PyTypeMarkingPass(PyGlobalLlvmData &global_data)
    : FunctionPass(&ID), context_(&global_data.context()),
      llvm_data_(&global_data),
      kind_(global_data.GetTBAAKind())
{
}

bool
PyTypeMarkingPass::runOnFunction(Function &F)
{
    if (this->func_map_.empty()) {
        // This functions should get loaded with the BC file.
        addMark("PyInt_FromLong", llvm_data_->tbaa_PyIntObject);
        addMark("PyInt_FromSsize_t", llvm_data_->tbaa_PyIntObject);
        // PyBoolObject is a subtype of PyIntObject
        addMark("PyBool_FromLong", llvm_data_->tbaa_PyIntObject);
        addMark("PyFloat_FromDouble", llvm_data_->tbaa_PyFloatObject);
        addMark("PyString_Format", llvm_data_->tbaa_PyStringObject);

        // getFunction needs the real function name. Expand macros.
#ifndef Py_UNICODE_WIDE
        addMark("PyUnicodeUCS2_Format", llvm_data_->tbaa_PyUnicodeObject);
#else
        addMark("PyUnicodeUCS4_Format", llvm_data_->tbaa_PyUnicodeObject);
#endif

    }

    bool changed = false;

    for (Function::iterator b = F.begin(), be = F.end(); b != be; ++b) {
        for (BasicBlock::iterator i = b->begin(), ie = b->end(); i != ie; ++i) {
            if (CallInst* callInst = dyn_cast<CallInst>(&*i)) {
                changed |= this->markFunction(callInst);
            }
        }
    }

    return changed;
}

void
PyTypeMarkingPass::addMark(const char *name, const PyTBAAType &type)
{
    const Module *module = this->llvm_data_->module();
    Function *func = module->getFunction(name);

    // There should already be GVs for functions in the runtime library.
    assert(func != NULL);

    this->func_map_[func] = &type;
}

bool
PyTypeMarkingPass::markFunction(CallInst *callInst)
{
    Function *called = callInst->getCalledFunction();
    if (called == NULL)
        return false;

    if (callInst->getMetadata(this->kind_) != NULL)
        return false;

    const PyTBAAType *type = this->func_map_.lookup(called);
    if (type == NULL)
        return false;

    type->MarkInstruction(callInst);
    return true;
}

} // End of anonymous namespace

Pass *
CreatePyTypeMarkingPass(PyGlobalLlvmData &global_data)
{
    return new PyTypeMarkingPass(global_data);
}



namespace {

class PyTypeGuardRemovalPass : public FunctionPass {
public:
    static char ID;
    PyTypeGuardRemovalPass(PyGlobalLlvmData &global_data);

    PyTypeGuardRemovalPass()
        : FunctionPass(&ID), context_(NULL), llvm_data_(NULL), kind_(0)
    {}

    virtual bool runOnFunction(Function&);

private:
    void addGuardType(PyObject *obj, const PyTBAAType &type);
    bool checkICmp(ICmpInst *icmpIns);

    LLVMContext *const context_;
    const PyGlobalLlvmData *const llvm_data_;
    const unsigned kind_;

    typedef llvm::ValueMap<const Value *,
                           llvm::TrackingVH<MDNode> > GuardTypes;

    // Type checks in LlvmIR compare the type field of a PyObject with a
    // instance of PyTypeObject. This maps the Python type to a TBAA MDNode.
    GuardTypes type_map_;

};

// The address of this variable identifies the pass.  See
// http://llvm.org/docs/WritingAnLLVMPass.html#basiccode.
char PyTypeGuardRemovalPass::ID = 0;

// Register this pass.
static llvm::RegisterPass<PyTypeGuardRemovalPass>
X("python-typeguard", "Python-specific Type Guard Removal Pass", false, true);

PyTypeGuardRemovalPass::PyTypeGuardRemovalPass(PyGlobalLlvmData &global_data)
    : FunctionPass(&ID), context_(&global_data.context()),
      llvm_data_(&global_data),
      kind_(global_data.GetTBAAKind())
{
}

void
PyTypeGuardRemovalPass::addGuardType(PyObject *obj, const PyTBAAType &type)
{
    const llvm::Value *value =
        this->llvm_data_->constant_mirror().GetGlobalVariableFor(obj);
    type_map_[value] = type.type();
}

bool
PyTypeGuardRemovalPass::runOnFunction(Function &F)
{

    if (type_map_.empty()) {
        // Lazy initialisation. GetGlobalVariable does not work during init.
        // Connects type objects with Metadata. Do this for every
        // *_CheckExact you want to remove.
        this->addGuardType((PyObject *)&PyInt_Type,
                           llvm_data_->tbaa_PyIntObject);
        this->addGuardType((PyObject *)&PyFloat_Type,
                           llvm_data_->tbaa_PyFloatObject);
    }

    bool changed = false;

    for (Function::iterator b = F.begin(), be = F.end(); b != be; ++b) {
        for (BasicBlock::iterator i = b->begin(), ie = b->end(); i != ie; ++i) {
            if (ICmpInst *icmpInst = dyn_cast<ICmpInst>(&*i)) {
                changed |= this->checkICmp(icmpInst);
            }
        }
    }

    return changed;
}

bool
PyTypeGuardRemovalPass::checkICmp(ICmpInst *icmpInst)
{
    const llvm::Type *type_object =
        PyTypeBuilder<PyTypeObject*>::get(*this->context_);

    if (icmpInst->getPredicate() != ICmpInst::ICMP_EQ) {
        return false;
    }

    Value *op1 = icmpInst->getOperand(0);
    if (op1->getType() != type_object) {
        return false;
    }

    Value *load = op1->getUnderlyingObject();
    llvm::LoadInst *loadInst = dyn_cast<llvm::LoadInst>(load);
    if (loadInst == NULL) {
        return false;
    }

    Value *src = loadInst->getOperand(0);

    MDNode *type_hint = getFirstMDNode(this->llvm_data_, this->kind_, src);

    if (type_hint == NULL)
        return false;

    GuardTypes::iterator it = type_map_.find(icmpInst->getOperand(1));
    if (it == type_map_.end())
        return false;

    MDNode *req_type = it->second;

    /* This only removes type checks which would result in true */
    if (type_hint != req_type)
        return false;

    bool changed = false;
    for (Value::use_iterator i = icmpInst->use_begin(), e = icmpInst->use_end();
            i != e; ++i) {
        if (BranchInst *branch = dyn_cast<BranchInst>(*i)) {
            if (branch->isConditional()) {
                changed = true;
                BasicBlock *true_block = branch->getSuccessor(0);
                branch->setUnconditionalDest(true_block);
            }
        }
    }
    return changed;
}

} // End of anonymous namespace

Pass *
CreatePyTypeGuardRemovalPass(PyGlobalLlvmData &global_data)
{
    return new PyTypeGuardRemovalPass(global_data);
}
