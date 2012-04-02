/* Note: this file is not compiled if configured with --without-llvm. */
#include "Python.h"

#include "osdefs.h"
#undef MAXPATHLEN  /* Conflicts with definition in LLVM's config.h */
#include "JIT/ConstantMirror.h"
#include "JIT/DeadGlobalElim.h"
#include "JIT/global_llvm_data.h"
#include "JIT/PyAliasAnalysis.h"
#include "JIT/PyTBAliasAnalysis.h"
#include "JIT/SingleFunctionInliner.h"
#include "Util/Stats.h"
#include "_llvmfunctionobject.h"

#include "llvm/Analysis/DebugInfo.h"
#include "llvm/Analysis/Verifier.h"
#include "llvm/Bitcode/ReaderWriter.h"
#include "llvm/CallingConv.h"
#include "llvm/Constants.h"
#include "llvm/DerivedTypes.h"
#include "llvm/ExecutionEngine/JIT.h"
#include "llvm/ExecutionEngine/JITEventListener.h"
#include "llvm/Function.h"
#include "llvm/GlobalVariable.h"
#include "llvm/Module.h"
#include "llvm/Support/CommandLine.h"
#include "llvm/Support/Debug.h"
#include "llvm/Support/ManagedStatic.h"
#include "llvm/Support/MemoryBuffer.h"
#include "llvm/Support/ValueHandle.h"
#include "llvm/System/Path.h"
#include "llvm/Target/TargetData.h"
#include "llvm/Target/TargetSelect.h"
#include "llvm/Transforms/Scalar.h"

using llvm::FunctionPassManager;
using llvm::MDNode;
using llvm::MDString;
using llvm::Module;
using llvm::StringRef;

PyGlobalLlvmData *
PyGlobalLlvmData_New()
{
    return new PyGlobalLlvmData;
}

void
PyGlobalLlvmData_Clear(PyGlobalLlvmData *)
{
    // So far, do nothing.
}

void
PyGlobalLlvmData_Free(PyGlobalLlvmData * global_data)
{
    delete global_data;
}

PyGlobalLlvmData *
PyGlobalLlvmData::Get()
{
    return PyThreadState_GET()->interp->global_llvm_data;
}

#define STRINGIFY(X) STRINGIFY2(X)
#define STRINGIFY2(X) #X
// The basename of the bitcode file holding the standard library.
#ifdef MS_WINDOWS
#ifdef Py_DEBUG
#define LIBPYTHON_BC "python" STRINGIFY(PY_MAJOR_VERSION) \
    STRINGIFY(PY_MINOR_VERSION) "_d.bc"
#else
#define LIBPYTHON_BC "python" STRINGIFY(PY_MAJOR_VERSION) \
    STRINGIFY(PY_MINOR_VERSION) ".bc"
#endif
#else
#define LIBPYTHON_BC "libpython" STRINGIFY(PY_MAJOR_VERSION) "." \
    STRINGIFY(PY_MINOR_VERSION) ".bc"
#endif

// Searches for the bitcode file holding the Python standard library.
// If one is found, returns its contents in a MemoryBuffer.  If not,
// dies with a fatal error.
static llvm::MemoryBuffer *
find_stdlib_bc()
{
    llvm::sys::Path path;
    llvm::SmallVector<StringRef, 8> sys_path;
    const char delim[] = { DELIM, '\0' };
    StringRef(Py_GetPath()).split(sys_path, delim);
    for (ssize_t i = 0, size = sys_path.size(); i < size; ++i) {
        StringRef elem = sys_path[i];
        path = elem;
        path.appendComponent(LIBPYTHON_BC);
        llvm::MemoryBuffer *stdlib_file =
            llvm::MemoryBuffer::getFile(path.str(), NULL);
        if (stdlib_file != NULL) {
            return stdlib_file;
        }
    }
    Py_FatalError("Could not find " LIBPYTHON_BC " on sys.path");
    return NULL;
}

PyGlobalLlvmData::PyGlobalLlvmData()
    : optimized_ops(),
      optimizations_(3, (FunctionPassManager*)NULL),
      num_globals_after_last_gc_(0)
{
    std::string error;
    llvm::MemoryBuffer *stdlib_file = find_stdlib_bc();
    this->module_ =
            llvm::getLazyBitcodeModule(stdlib_file, this->context(), &error);
    if (this->module_ == NULL) {
      Py_FatalError(error.c_str());
    }

    this->debug_info_.reset(new llvm::DIFactory(*this->module_));

    llvm::InitializeNativeTarget();
    engine_ = llvm::ExecutionEngine::create(
        this->module_,
        // Don't force the interpreter (use JIT if possible).
        false,
        &error,
        // JIT slowly, to produce better machine code.  TODO: We'll
        // almost certainly want to make this configurable per
        // function.
        llvm::CodeGenOpt::Default,
        // Allocate GlobalVariables separately from code.
        false);
    if (engine_ == NULL) {
        Py_FatalError(error.c_str());
    }

    engine_->RegisterJITEventListener(llvm::createOProfileJITEventListener());

    // When we ask to JIT a function, we should also JIT other
    // functions that function depends on.  This lets us JIT in a
    // background thread to avoid blocking the main thread during
    // codegen, and (once the GIL is gone) JITting lazily is
    // thread-unsafe anyway.
    engine_->DisableLazyCompilation();

    this->constant_mirror_.reset(new PyConstantMirror(this));

    this->InstallInitialModule();

    this->InitializeTBAA();

    this->InitializeOptimizations();
    this->gc_.add(PyCreateDeadGlobalElimPass(&this->bitcode_gvs_));
}

template<typename Iterator>
static void insert_gvs(
    llvm::DenseSet<llvm::AssertingVH<const llvm::GlobalValue> > &set,
    Iterator first, Iterator last) {
    for (; first != last; ++first) {
        set.insert(&*first);
    }
}

void
PyGlobalLlvmData::InstallInitialModule()
{
    insert_gvs(bitcode_gvs_, this->module_->begin(), this->module_->end());
    insert_gvs(bitcode_gvs_, this->module_->global_begin(),
               this->module_->global_end());
    insert_gvs(bitcode_gvs_, this->module_->alias_begin(),
               this->module_->alias_end());

    for (llvm::Module::iterator it = this->module_->begin();
         it != this->module_->end(); ++it) {
        if (it->getName().find("_PyLlvm_Fast") == 0) {
            it->setCallingConv(llvm::CallingConv::Fast);
        }
    }

    // Fill the ExecutionEngine with the addresses of known global variables.
    for (Module::global_iterator it = this->module_->global_begin();
         it != this->module_->global_end(); ++it) {
        this->engine_->getOrEmitGlobalVariable(it);
    }
}

void
PyGlobalLlvmData::InitializeOptimizations()
{
    optimizations_[0] = new FunctionPassManager(this->module_);

    FunctionPassManager *quick =
        new FunctionPassManager(this->module_);
    optimizations_[1] = quick;
    quick->add(new llvm::TargetData(*engine_->getTargetData()));
    quick->add(llvm::createPromoteMemoryToRegisterPass());
    quick->add(llvm::createInstructionCombiningPass());
    quick->add(llvm::createCFGSimplificationPass());
    quick->add(llvm::createVerifierPass());

    // This is the default optimization used by the JIT.
    FunctionPassManager *O2 =
        new FunctionPassManager(this->module_);
    optimizations_[2] = O2;
    O2->add(new llvm::TargetData(*engine_->getTargetData()));
    O2->add(llvm::createCFGSimplificationPass());
    O2->add(PyCreateSingleFunctionInliningPass());
    O2->add(CreatePyTypeMarkingPass(*this));
    O2->add(llvm::createJumpThreadingPass());
    O2->add(llvm::createPromoteMemoryToRegisterPass());
    O2->add(llvm::createInstructionCombiningPass());
    O2->add(llvm::createCFGSimplificationPass());
    O2->add(llvm::createScalarReplAggregatesPass());
    this->AddPythonAliasAnalyses(O2);
    O2->add(llvm::createLICMPass());
    O2->add(llvm::createJumpThreadingPass());
    this->AddPythonAliasAnalyses(O2);
    O2->add(llvm::createGVNPass());
    O2->add(llvm::createSCCPPass());
    // TypeGuardRemovale only works when most of the stack traffic is removed.
    // LLVM does this for us, but relatively late in the optimization stack.
    // This can be moved to an earlier position after switching to a register-
    // machine-based IR generation.
    O2->add(CreatePyTypeGuardRemovalPass(*this));
    O2->add(llvm::createAggressiveDCEPass());
    O2->add(llvm::createCFGSimplificationPass());
    O2->add(llvm::createVerifierPass());
}

void
PyGlobalLlvmData::AddPythonAliasAnalyses(llvm::FunctionPassManager *mngr)
{
    mngr->add(CreatePyTBAliasAnalysis(*this));
    mngr->add(CreatePyAliasAnalysis(*this));
}

bool
PyGlobalLlvmData::IsTBAASubtype(llvm::MDNode *p, llvm::MDNode *c) const
{
    TBAAInheritanceMap::const_iterator iter = this->tbaa_inheritance_.find(p);

    if (iter == this->tbaa_inheritance_.end())
        return false;

    return iter->second.count(c) > 0;
}

void
PyGlobalLlvmData::AddTBAAInherits(PyTBAAType &p, PyTBAAType &c)
{
    this->tbaa_inheritance_[p.type()].insert(c.type());
}

void
PyGlobalLlvmData::InitializeTBAA()
{
    // We have to generate a MDNode for every type we want the AliasAnalysis
    // to know about. These are wrapped and identified by a PyTBAAType object.
    // Instructions must be marked with a MDNode generated here.
    // Pointers to PyObject* are marked automatically.
    tbaa_stack = PyTBAAType(context(), "#stack");
    tbaa_locals = PyTBAAType(context(), "#locals");
    tbaa_PyObject = PyTBAAType(context(), "PyObject");
    tbaa_PyIntObject = PyTBAAType(context(), "PyIntObject");
    tbaa_PyFloatObject = PyTBAAType(context(), "PyFloatObject");
    tbaa_PyStringObject = PyTBAAType(context(), "PyStringObject");
    tbaa_PyUnicodeObject = PyTBAAType(context(), "PyUnicodeObject");
    tbaa_PyListObject = PyTBAAType(context(), "PyListObject");
    tbaa_PyTupleObject = PyTBAAType(context(), "PyTupleObject");

    // Add one entry for every superclass
    // e.g.: A->B->C => (A,C), (A,B) and (B,C)
    // Does not support multiple inheritance
    // The Alias Analysis needs to know about the inheritance between objects
    // e.g.: A may alias B and C
    AddTBAAInherits(tbaa_PyObject, tbaa_PyIntObject);
    AddTBAAInherits(tbaa_PyObject, tbaa_PyFloatObject);
    AddTBAAInherits(tbaa_PyObject, tbaa_PyStringObject);
    AddTBAAInherits(tbaa_PyObject, tbaa_PyUnicodeObject);
    AddTBAAInherits(tbaa_PyObject, tbaa_PyListObject);
    AddTBAAInherits(tbaa_PyObject, tbaa_PyTupleObject);
}

PyGlobalLlvmData::~PyGlobalLlvmData()
{
    this->bitcode_gvs_.clear();  // Stop asserting values aren't destroyed.
    this->constant_mirror_->python_shutting_down_ = true;
    for (size_t i = 0; i < this->optimizations_.size(); ++i) {
        delete this->optimizations_[i];
    }
    delete this->engine_;
}

int
PyGlobalLlvmData::Optimize(llvm::Function &f, int level)
{
    if (level < 0 || (size_t)level >= this->optimizations_.size())
        return -1;
    FunctionPassManager *opts_pm = this->optimizations_[level];
    assert(opts_pm != NULL && "Optimization was NULL");
    assert(this->module_ == f.getParent() &&
           "We assume that all functions belong to the same module.");
    opts_pm->run(f);
    return 0;
}

int
PyGlobalLlvmData_Optimize(struct PyGlobalLlvmData *global_data,
                          _LlvmFunction *llvm_function,
                          int level)
{
    return _LlvmFunction_Optimize(global_data, llvm_function, level);
}

#ifdef Py_WITH_INSTRUMENTATION
// Collect statistics about the time it takes to collect unused globals.
class GlobalGCTimes : public DataVectorStats<int64_t> {
public:
    GlobalGCTimes()
        : DataVectorStats<int64_t>("Time for a globaldce run in ns") {}
};

class GlobalGCCollected : public DataVectorStats<int> {
public:
    GlobalGCCollected()
        : DataVectorStats<int>("Number of globals collected by globaldce") {}
};

static llvm::ManagedStatic<GlobalGCTimes> global_gc_times;
static llvm::ManagedStatic<GlobalGCCollected> global_gc_collected;

#endif  // Py_WITH_INSTRUMENTATION

void
PyGlobalLlvmData::MaybeCollectUnusedGlobals()
{
    unsigned num_globals = this->module_->getGlobalList().size() +
        this->module_->getFunctionList().size();
    // Don't incur the cost of collecting globals if there are too few
    // of them, or if doing so now would cost a quadratic amount of
    // time as we allocate more long-lived globals.  The thresholds
    // here are just guesses, not tuned numbers.
    if (num_globals < 20 ||
        num_globals < (this->num_globals_after_last_gc_ +
                       (this->num_globals_after_last_gc_ >> 2)))
        return;
    this->CollectUnusedGlobals();
}

void
PyGlobalLlvmData::CollectUnusedGlobals()
{
#if Py_WITH_INSTRUMENTATION
    unsigned num_globals = this->module_->getGlobalList().size() +
        this->module_->getFunctionList().size();
#endif
    {
#if Py_WITH_INSTRUMENTATION
        Timer timer(*global_gc_times);
#endif
        this->gc_.run(*this->module_);
    }
    this->num_globals_after_last_gc_ = this->module_->getGlobalList().size() +
        this->module_->getFunctionList().size();
#if Py_WITH_INSTRUMENTATION
    global_gc_collected->RecordDataPoint(
        num_globals - num_globals_after_last_gc_);
#endif
}

void
PyGlobalLlvmData_CollectUnusedGlobals(struct PyGlobalLlvmData *global_data)
{
    global_data->CollectUnusedGlobals();
}

llvm::Value *
PyGlobalLlvmData::GetGlobalStringPtr(const std::string &value)
{
    // Use operator[] because we want to insert a new value if one
    // wasn't already present.
    llvm::WeakVH& the_string = this->constant_strings_[value];
    if (the_string == NULL) {
        llvm::Constant *str_const = llvm::ConstantArray::get(this->context(),
                                                             value, true);
        the_string = new llvm::GlobalVariable(
            *this->module_,
            str_const->getType(),
            true,  // Is constant.
            llvm::GlobalValue::InternalLinkage,
            str_const,
            value,  // Name.
            false);  // Not thread-local.
    }

    // the_string is a [(value->size()+1) x i8]*. C functions
    // expecting string constants instead expect an i8* pointing to
    // the first element.  We use GEP instead of bitcasting to make
    // type safety more obvious.
    const llvm::Type *int64_type = llvm::Type::getInt64Ty(this->context());
    llvm::Constant *indices[] = {
        llvm::ConstantInt::get(int64_type, 0),
        llvm::ConstantInt::get(int64_type, 0)
    };
    return llvm::ConstantExpr::getGetElementPtr(
        llvm::cast<llvm::Constant>(the_string), indices, 2);
}

int
_PyLlvm_Init()
{
    if (PyType_Ready(&PyLlvmFunction_Type) < 0)
        return 0;

    llvm::cl::ParseEnvironmentOptions("python", "PYTHONLLVMFLAGS", "", true);

    return 1;
}

void
_PyLlvm_Fini()
{
    llvm::llvm_shutdown();
}

int
PyLlvm_SetDebug(int on)
{
#ifdef NDEBUG
    if (on)
        return 0;
#else
    llvm::DebugFlag = on;
#endif
    return 1;
}
