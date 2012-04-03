#include "Python.h"
#include "object.h"

PyObject *
GET_DICTIONARY(PyObject *ob) {

        PyObject **dictptr = _PyObject_GetDictPtr(ob);
        PyObject *dict = NULL;

        if (dictptr == NULL) {

            if (PyInstance_Check(ob))
		dict = ((PyInstanceObject *)ob)->in_dict;

            if (dict == NULL) {
                PyErr_SetString(PyExc_AttributeError,
                                "This object has no __dict__");
                return NULL;
            }

        } else {
            dict = *dictptr;
            if (dict == NULL)
                *dictptr = dict = PyDict_New();
        }

        Py_XINCREF(dict);
        return dict;
}

