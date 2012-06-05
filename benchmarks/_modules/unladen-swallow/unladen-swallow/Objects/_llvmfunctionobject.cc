// Definition of _llvmfunction, the llvm::Function wrapper.

#include "Python.h"
#include "_llvmfunctionobject.h"

#include "frameobject.h"
#include "structmember.h"
#include "JIT/global_llvm_data.h"
#include "Util/Stats.h"

#include "llvm/BasicBlock.h"
#include "llvm/Constants.h"
#include "llvm/Function.h"
#include "llvm/Instructions.h"
#include "llvm/Module.h"
#include "llvm/ADT/SmallPtrSet.h"
#include "llvm/CodeGen/MachineCodeInfo.h"
#include "llvm/ExecutionEngine/ExecutionEngine.h"
#include "llvm/Support/Casting.h"
#include "llvm/Support/ManagedStatic.h"
#include "llvm/Support/ValueHandle.h"
#include "llvm/Support/raw_ostream.h"

#include <sstream>
#include <string>
#include <vector>

using llvm::BasicBlock;
using llvm::Function;
using llvm::Type;
using llvm::Value;

struct _LlvmFunction {
    // This should be an AssertingVH, but that runs into problems on
    // shutdown, where the Module is destroyed without destroying all
    // code objects first.
    Function *lf_function;
};

#ifdef Py_WITH_INSTRUMENTATION
// Collect statistics about the number of lines of LLVM IR we're writing,
// and the amount of native code that translates to. Even if we're not changing
// the amount of generated native code, reducing the number of LLVM IR lines
// helps compilation time.
class NativeSizeStats : public DataVectorStats<size_t> {
public:
    NativeSizeStats() : DataVectorStats<size_t>("Native code size in bytes") {}
};

class LlvmIrSizeStats : public DataVectorStats<size_t> {
public:
    LlvmIrSizeStats() : DataVectorStats<size_t>("LLVM IR size in lines") {}
};

// Count the number of non-blank lines of LLVM IR for the given function.
static size_t
count_ir_lines(llvm::Function *const function)
{
    size_t result = 1;  // Function's 'define' line.
    for (llvm::Function::iterator bb = function->begin(),
         bb_end = function->end(); bb != bb_end; ++bb) {
        ++result;  // 'bb_name:' line.
        for (llvm::BasicBlock::iterator inst = bb->begin(),
             inst_end = bb->end(); inst != inst_end; ++inst) {
            ++result;
        }
    }
    return result;
}

static llvm::ManagedStatic<NativeSizeStats> native_size_stats;
static llvm::ManagedStatic<LlvmIrSizeStats> llvm_ir_size_stats;
#endif  // Py_WITH_INSTRUMENTATION

_LlvmFunction *
_LlvmFunction_New(void *llvm_function)
{
    llvm::Function *typed_function = (llvm::Function*)llvm_function;
    _LlvmFunction *wrapper = new _LlvmFunction();
    wrapper->lf_function = typed_function;
    return wrapper;
}

void
_LlvmFunction_Dealloc(_LlvmFunction *functionobj)
{
    llvm::Function *function = functionobj->lf_function;
    // Clear the AssertingVH to avoid crashing when we delete the function.
    functionobj->lf_function = NULL;
    // Allow global optimizations to destroy the function.
    function->setLinkage(llvm::GlobalValue::InternalLinkage);
    if (function->use_empty()) {
        // Delete the function if it's already unused.
        function->eraseFromParent();
    }
    delete functionobj;
}

// Deletes most of the contents of function but keeps all references
// to global variables so they don't get destroyed by globaldce.
static void
clear_body(llvm::Function *function)
{
    // Gather all the pieces of *function that could be or use globals.
    llvm::SmallPtrSet<Value*, 8> globals;
    // For all basic blocks...
    for (Function::iterator BB = function->begin(), E = function->end();
         BB != E; ++BB)
        // For all instructions...
        for (BasicBlock::iterator I = BB->begin(), E = BB->end(); I != E; ++I)
            // For all operands...
            for (llvm::User::op_iterator U = I->op_begin(), E = I->op_end();
                 U != E; ++U) {
                // We could recursively iterate through the Constants
                // too to find their component GlobalValues, but since
                // Constants are immortal anyway that doesn't seem
                // worth it.  GlobalValues are Constants, so this
                // picks them up too.
                if (llvm::isa<llvm::Constant>(*U))
                    globals.insert(*U);
            }
    const std::vector<Value*> globals_vect(globals.begin(), globals.end());

    // Clear out the function now that we know what it uses.
    function->deleteBody();

    BasicBlock *entry =
        BasicBlock::Create(function->getContext(), "", function);

    // Build a single "call void undef(all_constants)" instruction to
    // keep a use of all the constants.
    std::vector<const Type*> types;
    types.reserve(globals_vect.size());
    for (std::vector<Value*>::const_iterator C = globals_vect.begin(),
             E = globals_vect.end(); C != E; ++C)
        types.push_back((*C)->getType());
    const llvm::FunctionType *user_t = llvm::FunctionType::get(
        Type::getVoidTy(function->getContext()), types, false);
    llvm::CallInst::Create(
        llvm::UndefValue::get(llvm::PointerType::getUnqual(user_t)),
        globals_vect.begin(), globals_vect.end(), "", entry);
}

PyEvalFrameFunction
_LlvmFunction_Jit(_LlvmFunction *function_obj)
{
    llvm::Function *function = (llvm::Function *)function_obj->lf_function;
    PyGlobalLlvmData *global_llvm_data =
        PyThreadState_GET()->interp->global_llvm_data;
    llvm::ExecutionEngine *engine = global_llvm_data->getExecutionEngine();

    PyEvalFrameFunction native_func;
#ifdef Py_WITH_INSTRUMENTATION
    llvm::MachineCodeInfo code_info;
    engine->runJITOnFunction(function, &code_info);
    native_size_stats->RecordDataPoint(code_info.size());

    size_t llvm_ir_lines = count_ir_lines(function);
    llvm_ir_size_stats->RecordDataPoint(llvm_ir_lines);
    // TODO(jyasskin): code_info.address() doesn't work for some reason.
    void *func = engine->getPointerToGlobalIfAvailable(function);
    assert(func && "function not installed in the globals");
    native_func = (PyEvalFrameFunction)func;
#else
    native_func = (PyEvalFrameFunction)engine->getPointerToFunction(function);
#endif
    // Clear the function body to reduce memory usage. This means we'll
    // need to re-compile the bytecode to IR and reoptimize it again, if we
    // need it again.
    clear_body(function);
    return native_func;
}

int
_LlvmFunction_Optimize(PyGlobalLlvmData *global_data,
                       _LlvmFunction *llvm_function,
                       int level)
{
    return global_data->Optimize(*llvm_function->lf_function, level);
}

// Python-level wrapper.
struct PyLlvmFunctionObject {
public:
    PyObject_HEAD
    PyCodeObject *code_object;  // Hold a reference to the PyCodeObject.
};

PyObject *
_PyLlvmFunction_FromCodeObject(PyObject *co)
{
    PyLlvmFunctionObject *result =
        PyObject_NEW(PyLlvmFunctionObject, &PyLlvmFunction_Type);
    if (result == NULL) {
        return NULL;
    }
    Py_INCREF(co);
    result->code_object = (PyCodeObject *)co;

    return (PyObject *)result;
}

static llvm::Function *
_PyLlvmFunction_GetFunction(PyLlvmFunctionObject *llvm_function)
{
    PyCodeObject *code = llvm_function->code_object;
    return (llvm::Function *)code->co_llvm_function->lf_function;
}

PyDoc_STRVAR(llvmfunction_doc,
"_llvmfunction()\n\
\n\
A wrapper around an llvm::Function object. Can only be created from\n\
existing _llvmmodule objects.");

static void
llvmfunction_dealloc(PyLlvmFunctionObject *functionobj)
{
    Py_DECREF(functionobj->code_object);
}

static _LlvmFunction *
recompile(PyLlvmFunctionObject *functionobj)
{
    // We clear out all llvm::Functions after emitting machine code for
    // them. Compile the code object back to IR, then throw that IR away. We
    // assume that people aren't printing out code objects in tight loops.
    PyCodeObject *code = functionobj->code_object;
    _LlvmFunction *cur_function = code->co_llvm_function;
    int cur_opt_level = code->co_optimization;
    // Null these out to trick _PyCode_ToOptimizedLlvmIr() into recompiling
    // this function, then restore the original values when we're done.
    // TODO(collinwinter): this approach is suboptimal.
    code->co_llvm_function = NULL;
    code->co_optimization = 0;

    int ret = _PyCode_ToOptimizedLlvmIr(code, cur_opt_level);
    _LlvmFunction *new_function = code->co_llvm_function;
    code->co_llvm_function = cur_function;
    code->co_optimization = cur_opt_level;
    // The only way we could have rejected compilation is if the code
    // object changed. I don't know how this could happen, but Python has
    // surprised me before.
    if (ret == 1) {  // Compilation rejected.
      PyErr_BadInternalCall();
      return NULL;
    }
    else if (ret == -1)  // Error during compilation.
      return NULL;

    return new_function;
}

static PyObject *
llvmfunction_str(PyLlvmFunctionObject *function_obj)
{
    std::string result;
    llvm::raw_string_ostream wrapper(result);

    _LlvmFunction *new_function = recompile(function_obj);
    if (new_function == NULL) {
        return NULL;
    }
    llvm::Function *func = (llvm::Function *)new_function->lf_function;
    func->print(wrapper);
    _LlvmFunction_Dealloc(new_function);

    wrapper.flush();
    return PyString_FromStringAndSize(result.data(), result.size());
}

static PyObject *
func_view_cfg(PyLlvmFunctionObject *function_obj)
{
    _LlvmFunction *new_function = recompile(function_obj);
    if (new_function == NULL) {
        return NULL;
    }
    llvm::Function *func = (llvm::Function *)new_function->lf_function;
    func->viewCFG();
    _LlvmFunction_Dealloc(new_function);
    Py_RETURN_NONE;
}

static PyObject *
func_get_module(PyLlvmFunctionObject *op)
{
    llvm::Module *module = _PyLlvmFunction_GetFunction(op)->getParent();
    if (module == NULL) {
        PyErr_BadInternalCall();
        return NULL;
    }

    std::string result;
    llvm::raw_string_ostream wrapper(result);
    module->print(wrapper, NULL /* No extra annotations in the output */);
    wrapper.flush();

    return PyString_FromStringAndSize(result.data(),
                                      result.size());
}

static PyMethodDef llvmfunction_methods[] = {
    {"view_cfg",  (PyCFunction)func_view_cfg, METH_NOARGS,
     "View the CFG for this function."},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

static PyGetSetDef llvmfunction_getsetlist[] = {
    {"module", (getter)func_get_module, NULL},
    {NULL, NULL, NULL},
};

// PyType_Ready is called on this in global_llvm_data.cc:_PyLlvm_Init().
PyTypeObject PyLlvmFunction_Type = {
	PyVarObject_HEAD_INIT(&PyType_Type, 0)
	"_llvmfunction",
	sizeof(PyLlvmFunctionObject),
	0,
	(destructor)llvmfunction_dealloc,   /* tp_dealloc */
	0,				/* tp_print */
	0, 				/* tp_getattr */
	0,				/* tp_setattr */
	0,				/* tp_compare */
	0,				/* tp_repr */
	0,				/* tp_as_number */
	0,				/* tp_as_sequence */
	0,				/* tp_as_mapping */
	0,				/* tp_hash */
	0,				/* tp_call */
	(reprfunc)llvmfunction_str,	/* tp_str */
	PyObject_GenericGetAttr,	/* tp_getattro */
	0,				/* tp_setattro */
	0,				/* tp_as_buffer */
	Py_TPFLAGS_DEFAULT,		/* tp_flags */
	llvmfunction_doc,		/* tp_doc */
	0,				/* tp_traverse */
	0,				/* tp_clear */
	0,				/* tp_richcompare */
	0,				/* tp_weaklistoffset */
	0,				/* tp_iter */
	0,				/* tp_iternext */
	llvmfunction_methods,		/* tp_methods */
	0,				/* tp_members */
	llvmfunction_getsetlist,	/* tp_getset */
	0,				/* tp_base */
	0,				/* tp_dict */
	0,				/* tp_descr_get */
	0,				/* tp_descr_set */
	0,				/* tp_dictoffset */
	0,				/* tp_init */
	0,				/* tp_alloc */
	0,				/* tp_new */
};
