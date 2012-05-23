/* _llvm module */

/*
This module provides a way to get at the minimal LLVM wrapper
types. It's not intended to be a full LLVM interface. For that, use
LLVM-py.
*/

#include "Python.h"
#include "_llvmfunctionobject.h"
#include "JIT/global_llvm_data_fwd.h"
#include "JIT/llvm_compile.h"
#include "JIT/RuntimeFeedback_fwd.h"

PyDoc_STRVAR(llvm_module_doc,
"Defines thin wrappers around fundamental LLVM types.");

PyDoc_STRVAR(setdebug_doc,
             "set_debug(bool).  Sets LLVM debug output on or off.");
static PyObject *
llvm_setdebug(PyObject *self, PyObject *on_obj)
{
    int on = PyObject_IsTrue(on_obj);
    if (on == -1)  /* Error. */
        return NULL;

    if (!PyLlvm_SetDebug(on)) {
        PyErr_SetString(PyExc_ValueError, "llvm debugging not available");
        return NULL;
    }
    Py_RETURN_NONE;
}

PyDoc_STRVAR(llvm_compile_doc,
"compile(code, optimization_level) -> llvm_function\n\
\n\
Compile a code object to an llvm_function object at the given\n\
optimization level.");

static PyObject *
llvm_compile(PyObject *self, PyObject *args)
{
    PyObject *obj;
    PyCodeObject *code;
    long opt_level;

    if (!PyArg_ParseTuple(args, "O!l:compile",
                          &PyCode_Type, &obj, &opt_level))
        return NULL;

    if (opt_level < -1 || opt_level > Py_MAX_LLVM_OPT_LEVEL) {
        PyErr_SetString(PyExc_ValueError, "invalid optimization level");
        return NULL;
    }

    code = (PyCodeObject *)obj;
    if (code->co_llvm_function)
        _LlvmFunction_Dealloc(code->co_llvm_function);
    code->co_llvm_function = _PyCode_ToLlvmIr(code);
    if (code->co_llvm_function == NULL)
        return NULL;
    if (code->co_optimization < opt_level &&
        PyGlobalLlvmData_Optimize(PyGlobalLlvmData_GET(),
                                  code->co_llvm_function, opt_level) < 0) {
        PyErr_Format(PyExc_ValueError,
                     "Failed to optimize to level %ld", opt_level);
        _LlvmFunction_Dealloc(code->co_llvm_function);
        return NULL;
    }

    return _PyLlvmFunction_FromCodeObject((PyObject *)code);
}

PyDoc_STRVAR(llvm_clear_feedback_doc,
"clear_feedback(func)\n\
\n\
Clear the runtime feedback collected for the given function.");

static PyObject *
llvm_clear_feedback(PyObject *self, PyObject *obj)
{
    PyCodeObject *code;
    if (PyFunction_Check(obj)) {
        PyFunctionObject *func = (PyFunctionObject *)obj;
        code = (PyCodeObject *)func->func_code;
    }
    else if (PyMethod_Check(obj)) {
        /* Methods contain other callable objects, including, potentially other
           methods. */
        return llvm_clear_feedback(self, ((PyMethodObject *)obj)->im_func);
    }
    else if (PyCode_Check(obj)) {
        code = (PyCodeObject *)obj;
    }
    else if (PyCFunction_Check(obj)) {  /* No feedback; this is a no-op. */
        Py_RETURN_NONE;
    }
    else {
        PyErr_Format(PyExc_TypeError,
                     "cannot clear feedback for %.100s objects",
                     Py_TYPE(obj)->tp_name);
        return NULL;
    }

    if (code->co_runtime_feedback)
        PyFeedbackMap_Clear(code->co_runtime_feedback);
    Py_RETURN_NONE;
}

PyDoc_STRVAR(llvm_set_jit_control_doc,
"set_jit_control(string)\n\
\n\
Set the JIT control mode.  Valid values are 'always', 'never', and 'whenhot'.");

static PyObject *
llvm_set_jit_control(PyObject *self, PyObject *flag_obj)
{
    const char *flag_str;
    if (!PyString_Check(flag_obj)) {
        PyErr_Format(PyExc_TypeError,
                     "expected str, not %.100s object",
                     Py_TYPE(flag_obj)->tp_name);
        return NULL;
    }

    flag_str = PyString_AsString(flag_obj);
    if (flag_str == NULL)
        return NULL;
    if (Py_JitControlStrToEnum(flag_str, &Py_JitControl) < 0) {
        PyErr_Format(PyExc_ValueError,
                     "invalid jit control value: \"%s\"", flag_str);
        return NULL;
    }
    Py_RETURN_NONE;
}

PyDoc_STRVAR(llvm_get_jit_control_doc,
"get_jit_control() -> string\n\
\n\
Returns the current value for the Py_JitControl flag.  This may disagree\n\
with sys.flags.jit_control because the sys.flags structure is immutable and\n\
it is initialized at load time, so it reflects the value passed to the\n\
program on the command line.");

static PyObject *
llvm_get_jit_control(PyObject *self)
{
    const char *flag_str = Py_JitControlEnumToStr(Py_JitControl);
    assert(flag_str != NULL && "Current JIT control value was invalid!");
    return PyString_FromString(flag_str);
}

PyDoc_STRVAR(llvm_get_hotness_threshold_doc,
"get_hotness_threshold() -> long\n\
\n\
Return the threshold for co_hotness before the code is 'hot'.");

static PyObject *
llvm_get_hotness_threshold(PyObject *self)
{
    return PyInt_FromLong(PY_HOTNESS_THRESHOLD);
}

PyDoc_STRVAR(llvm_collect_unused_globals_doc,
"collect_unused_globals()\n\
\n\
Collect any unused LLVM global variables that may be holding references to\n\
Python objects.");

static PyObject *
llvm_collect_unused_globals(PyObject *self)
{
    PyGlobalLlvmData_CollectUnusedGlobals(PyGlobalLlvmData_GET());
    Py_RETURN_NONE;
}

static struct PyMethodDef llvm_methods[] = {
    {"set_debug", (PyCFunction)llvm_setdebug, METH_O, setdebug_doc},
    {"compile", llvm_compile, METH_VARARGS, llvm_compile_doc},
    {"clear_feedback", (PyCFunction)llvm_clear_feedback, METH_O,
     llvm_clear_feedback_doc},
    {"get_jit_control", (PyCFunction)llvm_get_jit_control, METH_NOARGS,
     llvm_get_jit_control_doc},
    {"set_jit_control", (PyCFunction)llvm_set_jit_control, METH_O,
     llvm_set_jit_control_doc},
    {"get_hotness_threshold", (PyCFunction)llvm_get_hotness_threshold,
     METH_NOARGS, llvm_get_hotness_threshold_doc},
    {"collect_unused_globals", (PyCFunction)llvm_collect_unused_globals,
     METH_NOARGS, llvm_collect_unused_globals_doc},
    { NULL, NULL }
};

PyMODINIT_FUNC
init_llvm(void)
{
    PyObject *module;

    /* Create the module and add the functions */
    module = Py_InitModule3("_llvm", llvm_methods, llvm_module_doc);
    if (module == NULL)
        return;

    Py_INCREF(&PyLlvmFunction_Type);
    if (PyModule_AddObject(module, "_function",
                           (PyObject *)&PyLlvmFunction_Type))
        return;
}
