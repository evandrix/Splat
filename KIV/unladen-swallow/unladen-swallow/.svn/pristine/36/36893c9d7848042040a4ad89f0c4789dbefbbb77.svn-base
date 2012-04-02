/* This file defines several functions that we want to be able to
   inline into the LLVM IR we generate.  We compile it with clang and
   llc to produce a C++ function that inserts these definitions into a
   module.

   PyGlobalLlvmData::InstallInitialModule() will apply LLVM's fastcc calling
   convention to all functions defined in this module that start with
   _PyLlvm_Fast.
*/

#include "Python.h"
#include "frameobject.h"
#include "longintrepr.h"
#include "opcode.h"

#include "Util/EventTimer.h"

int __attribute__((always_inline))
_PyLlvm_WrapIntCheck(PyObject *obj)
{
    return PyInt_Check(obj);
}

void __attribute__((always_inline))
_PyLlvm_WrapIncref(PyObject *obj)
{
    Py_INCREF(obj);
}

void __attribute__((always_inline))
_PyLlvm_WrapDecref(PyObject *obj)
{
    Py_DECREF(obj);
}

void __attribute__((always_inline))
_PyLlvm_WrapXDecref(PyObject *obj)
{
    Py_XDECREF(obj);
}

int __attribute__((always_inline))
_PyLlvm_WrapIsExceptionOrString(PyObject *obj)
{
    return PyExceptionClass_Check(obj) || PyString_Check(obj);
}

int __attribute__((always_inline))
_PyLlvm_WrapCFunctionCheck(PyObject *obj)
{
    return PyCFunction_Check(obj);
}


/* TODO(collinwinter): move this special-casing into a common function that
   we can share with eval.cc. */
int
_PyLlvm_FastUnpackIterable(PyObject *iter, int argcount,
                           PyObject **stack_pointer) {
    /* TODO(collinwinter): we could reduce the amount of generated code by
       using &PyTuple_GET_ITEM(iter, 0) and &PyList_GET_ITEM(iter, 0) to find
       the beginning of the items lists, and then having a single loop to copy
       that into the stack. */
    if (PyTuple_Check(iter) && PyTuple_GET_SIZE(iter) == argcount) {
        int i;
        for (i = 0; i < argcount; i++) {
            PyObject *item = PyTuple_GET_ITEM(iter, i);
            Py_INCREF(item);
            *--stack_pointer = item;
        }
        return 0;
    }
    else if (PyList_Check(iter) && PyList_GET_SIZE(iter) == argcount) {
        int i;
        for (i = 0; i < argcount; i++) {
            PyObject *item = PyList_GET_ITEM(iter, i);
            Py_INCREF(item);
            *--stack_pointer = item;
        }
        return 0;
    }
    else {
        return _PyEval_UnpackIterable(iter, argcount, stack_pointer);
    }
}

/* This type collects the set of three values that constitute an
   exception.  So far, it's only used for
   _PyLlvm_WrapEnterExceptOrFinally().  If we use it for more, we
   should move it to pyerrors.h. */
struct PyExcInfo {
    PyObject *exc;
    PyObject *val;
    PyObject *tb;
};

/* Copied from the SETUP_FINALLY && WHY_EXCEPTION block in
   fast_block_end in PyEval_EvalFrame(). */
void
_PyLlvm_FastEnterExceptOrFinally(struct PyExcInfo *exc_info, int block_type)
{
    PyThreadState *tstate = PyThreadState_GET();
    PyErr_Fetch(&exc_info->exc, &exc_info->val, &exc_info->tb);
    if (exc_info->val == NULL) {
        exc_info->val = Py_None;
        Py_INCREF(exc_info->val);
    }
    /* Make the raw exception data
       available to the handler,
       so a program can emulate the
       Python main loop.  Don't do
       this for 'finally'. */
    if (block_type == SETUP_EXCEPT) {
        PyErr_NormalizeException(
            &exc_info->exc, &exc_info->val, &exc_info->tb);
        _PyEval_SetExcInfo(tstate,
                           exc_info->exc, exc_info->val, exc_info->tb);
        PY_LOG_TSC_EVENT(EXCEPT_CATCH_LLVM);
    }
    if (exc_info->tb == NULL) {
        Py_INCREF(Py_None);
        exc_info->tb = Py_None;
    }
    /* Within the except or finally block,
       PyErr_Occurred() should be false.
       END_FINALLY will restore the
       exception if necessary. */
    PyErr_Clear();
}

int __attribute__((always_inline))
_PyLlvm_DecAndCheckPyTicker(PyThreadState *tstate)
{
    if (--_Py_Ticker < 0) {
        return _PyEval_HandlePyTickerExpired(tstate);
    }
    return 0;
}

PyThreadState * __attribute__((always_inline))
_PyLlvm_WrapPyThreadState_GET()
{
    return PyThreadState_GET();
}

/* Keep these in sync with the definitions of PyFrame_Block{Setup,Pop}
   in frameobject.c. */
void __attribute__((always_inline))
_PyLlvm_Frame_BlockSetup(PyTryBlock *blocks, char *num_blocks,
                         int type, int handler, int level)
{
    PyTryBlock *b;
    if (*num_blocks >= CO_MAXBLOCKS)
        Py_FatalError("XXX block stack overflow");
    b = &blocks[*num_blocks];
    b->b_type = type;
    b->b_level = level;
    b->b_handler = handler;
    ++*num_blocks;
}

PyTryBlock * __attribute__((always_inline))
_PyLlvm_Frame_BlockPop(PyTryBlock *blocks, char *num_blocks)
{
    PyTryBlock *b;
    if (*num_blocks <= 0)
        Py_FatalError("XXX block stack underflow");
    --*num_blocks;
    b = &blocks[*num_blocks];
    return b;
}

/* Keep this in sync with _PyObject_GetDictPtr.  We need it inlined in order
 * for constant propagation to work.
 */
static inline PyObject **
get_dict_ptr(PyObject *obj, PyTypeObject *tp, long dictoffset)
{
    if (dictoffset == 0)
        return NULL;
    if (dictoffset < 0) {
        Py_ssize_t tsize;
        size_t size;

        tsize = ((PyVarObject *)obj)->ob_size;
        if (tsize < 0)
            tsize = -tsize;
        size = _PyObject_VAR_SIZE(tp, tsize);

        dictoffset += (long)size;
        /* TODO(rnk): Put these back once we get NDEBUG properly
         * defined during clang compilation for release builds.
         *assert(dictoffset > 0);
         *assert(dictoffset % SIZEOF_VOID_P == 0);
         */
    }
    return (PyObject **) ((char *)obj + dictoffset);
}

/* Try to get an attribute from the attribute dictionary of obj, or return NULL
 * on failure.
 */
static inline PyObject *
get_attr_from_dict(PyObject *obj, PyTypeObject *tp, long dictoffset,
                   PyObject *name)
{
    PyObject **dictptr = get_dict_ptr(obj, tp, dictoffset);
    PyObject *dict = dictptr == NULL ? NULL : *dictptr;
    PyObject *attr = NULL;

    /* If the object has a dict, and the attribute is in it, return it.  */
    if (dict != NULL) {
        /* TODO(rnk): @reviewer: Are these refcounts necessary?  */
        Py_INCREF(dict);
        attr = PyDict_GetItem(dict, name);
        Py_DECREF(dict);
    }

    return attr;
}

/* Keep this in sync with PyObject_GenericGetAttr.  The reason we take so many
 * extra arguments is to allow LLVM optimizers to notice that all of these
 * things are constant.  By passing them as parameters and always inlining this
 * function, we ensure that they will benefit from constant propagation.
 */
PyObject * __attribute__((always_inline))
_PyLlvm_Object_GenericGetAttr(PyObject *obj, PyTypeObject *tp,
                              PyObject *name, long dictoffset, PyObject *descr,
                              descrgetfunc descr_get, char is_data_descr)
{
    PyObject *dict_attr;

    /* If it's a data descriptor, that has the most precedence, so we just call
     * the getter.  */
    if (is_data_descr) {
        return descr_get(descr, obj, (PyObject *)tp);
    }

    dict_attr = get_attr_from_dict(obj, tp, dictoffset, name);
    if (dict_attr != NULL) {
        Py_INCREF(dict_attr);
        return dict_attr;
    }

    /* Otherwise, try calling the descriptor getter.  */
    if (descr_get != NULL) {
        return descr_get(descr, obj, (PyObject *)tp);
    }

    /* If the descriptor has no getter, it's probably a vanilla PyObject
     * hanging off the class, in which case we just return it.  */
    if (descr != NULL) {
        Py_INCREF(descr);
        return descr;
    }

    PyErr_Format(PyExc_AttributeError,
                 "'%.50s' object has no attribute '%.400s'",
                 tp->tp_name, PyString_AS_STRING(name));
    return NULL;
}

/* A stripped down version of PyObject_GenericGetAttr that only gets methods or
 * returns NULL if the object it would return is not a method.  Rather than try
 * to handle those possible alternative cases, we focus on drastically reducing
 * the final generated code size.  */
PyObject *
_PyLlvm_Object_GetUnknownMethod(PyObject *obj, PyObject *name)
{
    PyObject *descr;
    PyObject *dict_attr;
    PyTypeObject *tp = Py_TYPE(obj);

    /* We only support string names.  */
    /* TODO(rnk): Uncomment when NDEBUG works.
     *assert(PyString_Check(name));
     */

    /* Bail if the type isn't ready.  We could call PyType_Ready, but that
     * would add unecessary code.  */
    if (tp->tp_dict == NULL) {
        return NULL;
    }

    /* Bail for objects that have overridden tp_getattro.  */
    if (tp->tp_getattro != &PyObject_GenericGetAttr) {
        return NULL;
    }

    descr = _PyType_Lookup(tp, name);

    /* Bail in any of the following cases:
     * - There is no descriptor on the type.
     * - The descriptor type does not have Py_TPFLAGS_HAVE_CLASS.
     * - The descriptor is a data descriptor.
     */
    if (descr == NULL ||
        !PyType_HasFeature(descr->ob_type, Py_TPFLAGS_HAVE_CLASS) ||
        PyDescr_IsData(descr)) {
        return NULL;
    }

    /* Bail if there is a dict attribute shadowing the method.  */
    dict_attr = get_attr_from_dict(obj, tp, tp->tp_dictoffset, name);
    if (dict_attr != NULL) {
        return NULL;
    }

    /* Bail if this isn't a method that we should be binding to obj.  */
    if (!_PyObject_ShouldBindMethod((PyObject*)tp, descr)) {
        return NULL;
    }

    /* Otherwise, we've found ourselves a real method!  */
    Py_INCREF(descr);
    return descr;
}

PyObject * __attribute__((always_inline))
_PyLlvm_Object_GetKnownMethod(PyObject *obj, PyTypeObject *tp,
                              PyObject *name, long dictoffset,
                              PyObject *method)
{
    PyObject *dict_attr;

    /* Bail if there is a dict attribute shadowing the method.  */
    dict_attr = get_attr_from_dict(obj, tp, dictoffset, name);
    if (dict_attr != NULL) {
        printf("shadowed dict attr!\n");
        return NULL;
    }

    /* Otherwise, return the method descriptor unmodified.  */
    /* TODO(rnk): Uncomment when NDEBUG works.
     *assert(_PyObject_ShouldBindMethod(tp, method));
     */
    Py_INCREF(method);
    return method;
}

/* Keep this in sync with PyObject_GenericSetAttr.  */
int __attribute__((always_inline))
_PyLlvm_Object_GenericSetAttr(PyObject *obj, PyObject *value,
                              PyTypeObject *tp, PyObject *name,
                              long dictoffset, PyObject *descr,
                              descrsetfunc descr_set, char is_data_descr)
{
    int res = -1;
    PyObject **dictptr;
    PyObject *dict;

    /* If it's a data descriptor, that has the most precedence, so we just call
     * the setter.  */
    if (is_data_descr) {
        return descr_set(descr, obj, value);
    }

    dictptr = get_dict_ptr(obj, tp, dictoffset);

    /* If the object has a dict slot, store it in there.  */
    if (dictptr != NULL) {
        PyObject *dict = *dictptr;
        if (dict == NULL && value != NULL) {
            dict = PyDict_New();
            if (dict == NULL)
                return -1;
            *dictptr = dict;
        }
        if (dict != NULL) {
            Py_INCREF(dict);
            if (value == NULL)
                res = PyDict_DelItem(dict, name);
            else
                res = PyDict_SetItem(dict, name, value);
            if (res < 0 && PyErr_ExceptionMatches(PyExc_KeyError))
                PyErr_SetObject(PyExc_AttributeError, name);
            Py_DECREF(dict);
            return res;
        }
    }

    /* Otherwise, try calling the descriptor setter.  */
    if (descr_set != NULL) {
        return descr_set(descr, obj, value);
    }

    if (descr == NULL) {
        PyErr_Format(PyExc_AttributeError,
                     "'%.100s' object has no attribute '%.200s'",
                     tp->tp_name, PyString_AS_STRING(name));
        return -1;
    }

    PyErr_Format(PyExc_AttributeError,
                 "'%.50s' object attribute '%.400s' is read-only",
                 tp->tp_name, PyString_AS_STRING(name));
    return -1;
}

/* Optimized BINARY_OP functions for several datatypes */
PyObject * __attribute__((always_inline))
_PyLlvm_BinAdd_Int(PyObject *v, PyObject *w)
{
    long a, b, i;

    if (!(PyInt_CheckExact(v) && PyInt_CheckExact(w)))
        return NULL;

    a = PyInt_AS_LONG(v);
    b = PyInt_AS_LONG(w);

    i = a + b;

    if ((i^a) < 0 && (i^b) < 0)
        return NULL;

    return PyInt_FromLong(i);
}

PyObject * __attribute__((always_inline))
_PyLlvm_BinSub_Int(PyObject *v, PyObject *w)
{
    long a, b, i;

    if (!(PyInt_CheckExact(v) && PyInt_CheckExact(w)))
        return NULL;

    a = PyInt_AS_LONG(v);
    b = PyInt_AS_LONG(w);

    i = a - b;

    if ((i^a) < 0 && (i^~b) < 0)
        return NULL;

    return PyInt_FromLong(i);
}

PyObject * __attribute__((always_inline))
_PyLlvm_BinMult_Int(PyObject *v, PyObject *w)
{
    long a, b, i;
    double di;

    if (!(PyInt_CheckExact(v) && PyInt_CheckExact(w)))
        return NULL;

    a = PyInt_AS_LONG(v);
    b = PyInt_AS_LONG(w);

    i = a * b;
    di = (double)a * (double)b;

    if ((double)i != di)
        return NULL;

    return PyInt_FromLong(i);
}

#define UNARY_NEG_WOULD_OVERFLOW(x) \
    ((x) < 0 && (unsigned long)(x) == 0-(unsigned long)(x))


PyObject * __attribute__((always_inline))
_PyLlvm_BinDiv_Int(PyObject *v, PyObject *w)
{
    long xdivy, xmody, x, y;

    if (!(PyInt_CheckExact(v) && PyInt_CheckExact(w)))
        return NULL;

    x = PyInt_AS_LONG(v);
    y = PyInt_AS_LONG(w);

    if (y == 0)
        return NULL;

    /* (-sys.maxint-1)/-1 is the only overflow case. */
    if (y == -1 && UNARY_NEG_WOULD_OVERFLOW(x))
        return NULL;

    xdivy = x / y;
    xmody = x - xdivy * y;
    /* If the signs of x and y differ, and the remainder is non-0,
    * C89 doesn't define whether xdivy is now the floor or the
    * ceiling of the infinitely precise quotient.  We want the floor,
    * and we have it iff the remainder's sign matches y's.
    */
    if (xmody && ((y ^ xmody) < 0) /* i.e. and signs differ */) {
        xmody += y;
        --xdivy;
        assert(xmody && ((y ^ xmody) >= 0));
    }

    return PyInt_FromLong(xdivy);
}

PyObject * __attribute__((always_inline))
_PyLlvm_BinMod_Int(PyObject *v, PyObject *w)
{
    long xdivy, xmody, x, y;

    if (!(PyInt_CheckExact(v) && PyInt_CheckExact(w)))
        return NULL;

    x = PyInt_AS_LONG(v);
    y = PyInt_AS_LONG(w);

    if (y == 0)
        return NULL;

    /* (-sys.maxint-1)/-1 is the only overflow case. */
    if (y == -1 && UNARY_NEG_WOULD_OVERFLOW(x))
        return NULL;

    xdivy = x / y;
    xmody = x - xdivy * y;
    /* If the signs of x and y differ, and the remainder is non-0,
    * C89 doesn't define whether xdivy is now the floor or the
    * ceiling of the infinitely precise quotient.  We want the floor,
    * and we have it iff the remainder's sign matches y's.
    */
    if (xmody && ((y ^ xmody) < 0) /* i.e. and signs differ */) {
        xmody += y;
        --xdivy;
        assert(xmody && ((y ^ xmody) >= 0));
    }

    return PyInt_FromLong(xmody);
}

PyObject * __attribute__((always_inline))
_PyLlvm_BinAdd_Float(PyObject *v, PyObject *w)
{
    double a, b, i;

    if (!(PyFloat_CheckExact(v) && PyFloat_CheckExact(w)))
        return NULL;

    a = PyFloat_AS_DOUBLE(v);
    b = PyFloat_AS_DOUBLE(w);
    PyFPE_START_PROTECT("add", return 0)
    i = a + b;
    PyFPE_END_PROTECT(i)
    return PyFloat_FromDouble(i);

}

PyObject * __attribute__((always_inline))
_PyLlvm_BinSub_Float(PyObject *v, PyObject *w)
{
    double a, b, i;

    if (!(PyFloat_CheckExact(v) && PyFloat_CheckExact(w)))
        return NULL;

    a = PyFloat_AS_DOUBLE(v);
    b = PyFloat_AS_DOUBLE(w);
    PyFPE_START_PROTECT("subtract", return 0)
    i = a - b;
    PyFPE_END_PROTECT(i)
    return PyFloat_FromDouble(i);
}

PyObject * __attribute__((always_inline))
_PyLlvm_BinMult_Float(PyObject *v, PyObject *w)
{
    double a, b, i;

    if (!(PyFloat_CheckExact(v) && PyFloat_CheckExact(w)))
        return NULL;

    a = PyFloat_AS_DOUBLE(v);
    b = PyFloat_AS_DOUBLE(w);
    PyFPE_START_PROTECT("multiply", return 0)
    i = a * b;
    PyFPE_END_PROTECT(i)
    return PyFloat_FromDouble(i);
}

PyObject * __attribute__((always_inline))
_PyLlvm_BinDiv_Float(PyObject *v, PyObject *w)
{
    double a, b, i;

    if (!(PyFloat_CheckExact(v) && PyFloat_CheckExact(w)))
        return NULL;

    a = PyFloat_AS_DOUBLE(v);
    b = PyFloat_AS_DOUBLE(w);

#ifdef Py_NAN
    if (b == 0.0)
        return NULL;
#endif

    PyFPE_START_PROTECT("divide", return 0)
    i = a / b;
    PyFPE_END_PROTECT(i)
    return PyFloat_FromDouble(i);
}

PyObject * __attribute__((always_inline))
_PyLlvm_BinMul_FloatInt(PyObject *v, PyObject *w)
{
    double a, b, i;
    if (!(PyFloat_CheckExact(v) && PyInt_CheckExact(w))) {
        return NULL;
    }


    a = PyFloat_AS_DOUBLE(v);
    b = (double)PyInt_AS_LONG(w);
    PyFPE_START_PROTECT("multiply", return 0)
    i = a * b;
    PyFPE_END_PROTECT(i)
    return PyFloat_FromDouble(i);
}

PyObject * __attribute__((always_inline))
_PyLlvm_BinDiv_FloatInt(PyObject *v, PyObject *w)
{
    double a, b, i;
    if (!(PyFloat_CheckExact(v) && PyInt_CheckExact(w))) {
        return NULL;
    }

    a = PyFloat_AS_DOUBLE(v);
    b = (double)PyInt_AS_LONG(w);

#ifdef Py_NAN
    if (b == 0.0) {
        return NULL;
    }
#endif

    PyFPE_START_PROTECT("divide", return 0)
    i = a / b;
    PyFPE_END_PROTECT(i)
    return PyFloat_FromDouble(i);
}

PyObject * __attribute__((always_inline))
_PyLlvm_BinMod_Str(PyObject *format, PyObject *args)
{
    if (!PyString_Check(format))
        return NULL;
    return PyString_Format(format, args);
}

PyObject * __attribute__((always_inline))
_PyLlvm_BinMod_Unicode(PyObject *format, PyObject *args)
{
    if (!PyUnicode_Check(format))
        return NULL;
    return PyUnicode_Format(format, args);
}

/* Work directly on the tuple data structure */
PyObject * __attribute__((always_inline))
_PyLlvm_BinSubscr_Tuple(PyObject *v, PyObject *w)
{
    Py_ssize_t i;
    if (!(PyTuple_CheckExact(v) && PyInt_CheckExact(w)))
        return NULL;

    i = PyInt_AsSsize_t(w);

    if (i < 0) {
        Py_ssize_t l = Py_SIZE(v);
        if (l < 0)
            return NULL;
        i += l;
    }
    if (i < 0 || i >= Py_SIZE(v)) {
        return NULL;
    }
    Py_INCREF(PyTuple_GET_ITEM(v, i));
    return PyTuple_GET_ITEM(v, i);
}

/* Work directly on the list data structure */
PyObject * __attribute__((always_inline))
_PyLlvm_BinSubscr_List(PyObject *v, PyObject *w)
{
    Py_ssize_t i;
    if (!(PyList_CheckExact(v) && PyInt_CheckExact(w)))
        return NULL;

    i = PyInt_AsSsize_t(w);

    if (i < 0) {
        Py_ssize_t l = Py_SIZE(v);
        if (l < 0)
            return NULL;
        i += l;
    }
    if (i < 0 || i >= Py_SIZE(v)) {
        return NULL;
    }
    Py_INCREF(PyList_GET_ITEM(v, i));
    return PyList_GET_ITEM(v, i);
}

int __attribute__((always_inline))
_PyLlvm_StoreSubscr_List(PyObject *o, PyObject *key, PyObject *value)
{
    Py_ssize_t i;
    PyObject *old_value;
    if (!(PyList_CheckExact(o) && PyInt_CheckExact(key)))
        return -1;

    i = PyInt_AsSsize_t(key);

    if (i < 0) {
        Py_ssize_t l = Py_SIZE(o);
        if (l < 0)
            return -1;
        i += l;
    }

    if (i < 0 || i >= Py_SIZE(o)) {
        return -1;
    }

    Py_INCREF(value);
    old_value = ((PyListObject *)o)->ob_item[i];
    ((PyListObject *)o)->ob_item[i] = value;
    Py_DECREF(old_value);
    return 0;
}

PyObject * __attribute__((always_inline))
_PyLlvm_BinLt_Int(PyObject *v, PyObject *w)
{
    if (!(PyInt_CheckExact(v) && PyInt_CheckExact(w))) {
        return NULL;
    }

    return PyBool_FromLong(PyInt_AS_LONG(v) < PyInt_AS_LONG(w));
}

PyObject * __attribute__((always_inline))
_PyLlvm_BinLe_Int(PyObject *v, PyObject *w)
{
    if (!(PyInt_CheckExact(v) && PyInt_CheckExact(w))) {
        return NULL;
    }

    return PyBool_FromLong(PyInt_AS_LONG(v) <= PyInt_AS_LONG(w));
}

PyObject * __attribute__((always_inline))
_PyLlvm_BinEq_Int(PyObject *v, PyObject *w)
{
    if (!(PyInt_CheckExact(v) && PyInt_CheckExact(w))) {
        return NULL;
    }

    return PyBool_FromLong(PyInt_AS_LONG(v) == PyInt_AS_LONG(w));
}

PyObject * __attribute__((always_inline))
_PyLlvm_BinNe_Int(PyObject *v, PyObject *w)
{
    if (!(PyInt_CheckExact(v) && PyInt_CheckExact(w))) {
        return NULL;
    }

    return PyBool_FromLong(PyInt_AS_LONG(v) != PyInt_AS_LONG(w));
}

PyObject * __attribute__((always_inline))
_PyLlvm_BinGt_Int(PyObject *v, PyObject *w)
{
    if (!(PyInt_CheckExact(v) && PyInt_CheckExact(w))) {
        return NULL;
    }

    return PyBool_FromLong(PyInt_AS_LONG(v) > PyInt_AS_LONG(w));
}

PyObject * __attribute__((always_inline))
_PyLlvm_BinGe_Int(PyObject *v, PyObject *w)
{
    if (!(PyInt_CheckExact(v) && PyInt_CheckExact(w))) {
        return NULL;
    }

    return PyBool_FromLong(PyInt_AS_LONG(v) >= PyInt_AS_LONG(w));
}


PyObject * __attribute__((always_inline))
_PyLlvm_BinGt_Float(PyObject *v, PyObject *w)
{
    if (!(PyFloat_CheckExact(v) && PyFloat_CheckExact(w))) {
        return NULL;
    }

    return PyBool_FromLong(PyFloat_AS_DOUBLE(v) > PyFloat_AS_DOUBLE(w));
}


// TODO(jyasskin): remove these in favor of Clang-based top-down inlining. These
// establish a baseline the more sophisticated system will need to meet or
// exceed.
PyObject * __attribute__((always_inline))
_PyLlvm_BuiltinLen_String(PyObject *o)
{
    if (!PyString_CheckExact(o))
        return NULL;

    Py_ssize_t size = Py_SIZE(o);
    return PyInt_FromSsize_t(size);
}

PyObject * __attribute__((always_inline))
_PyLlvm_BuiltinLen_Unicode(PyObject *o)
{
    if (!PyUnicode_CheckExact(o))
        return NULL;

    Py_ssize_t size = ((PyUnicodeObject *)o)->length;
    return PyInt_FromSsize_t(size);
}

PyObject * __attribute__((always_inline))
_PyLlvm_BuiltinLen_List(PyObject *o)
{
    if (!PyList_CheckExact(o))
        return NULL;

    Py_ssize_t size = Py_SIZE(o);
    return PyInt_FromSsize_t(size);
}

PyObject * __attribute__((always_inline))
_PyLlvm_BuiltinLen_Tuple(PyObject *o)
{
    if (!PyTuple_CheckExact(o))
        return NULL;

    Py_ssize_t size = Py_SIZE(o);
    return PyInt_FromSsize_t(size);
}

PyObject * __attribute__((always_inline))
_PyLlvm_BuiltinLen_Dict(PyObject *o)
{
    if (!PyDict_CheckExact(o))
        return NULL;

    Py_ssize_t size = ((PyDictObject *)o)->ma_used;
    return PyInt_FromSsize_t(size);
}

/* Define a global using PyTupleObject so we can look it up from
   TypeBuilder<PyTupleObject>. */
PyTupleObject *_dummy_TupleObject;
/* Ditto for PyListObject, */
PyListObject *_dummy_ListObject;
/* PyStringObject, */
PyStringObject *_dummy_StringObject;
/* PyUnicodeObject, */
PyUnicodeObject *_dummy_UnicodeObject;
/* PyCFunctionObject, */
PyCFunctionObject *_dummy_CFunctionObject;
/* PyMethodDescrObject, */
PyMethodDescrObject *_dummy_MethodDescrObject;
/* PyIntObject, */
PyIntObject *_dummy_IntObject;
/* PyLongObject, */
PyLongObject *_dummy_LongObject;
/* PyFloatObject, */
PyFloatObject *_dummy_FloatObject;
/* PyComplexObject, */
PyComplexObject *_dummy_ComplexObject;
/* PyFunctionObject, */
PyFunctionObject *_dummy_PyFunctionObject;
/* PyMethodObject, */
PyMethodObject *_dummy_PyMethodObject;
/* and PyVarObject. */
PyVarObject *_dummy_PyVarObject;

/* Expose PyEllipsis to ConstantMirror. */
PyObject* objectEllipsis() { return Py_Ellipsis; }
