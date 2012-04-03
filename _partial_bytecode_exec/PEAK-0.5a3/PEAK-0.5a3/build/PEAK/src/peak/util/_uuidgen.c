#include "Python.h"
#include <sys/types.h>
#include <sys/uuid.h>

static PyObject *uuidgen_uuidgen(PyObject *self, PyObject *args)
{
	char buf[37];
	uuid_t u;
	int res;
        
	if (!PyArg_Parse(args, ":uuidgen")) {
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS

	res = uuidgen(&u, 1);
	sprintf(buf, "%08x-%04x-%04x-%02x%02x-%02x%02x%02x%02x%02x%02x",
		u.time_low, u.time_mid, u.time_hi_and_version,
		u.clock_seq_hi_and_reserved, u.clock_seq_low,
		u.node[0], u.node[1], u.node[2],
		u.node[3], u.node[4], u.node[5]);
			    
        
	Py_END_ALLOW_THREADS
        
	if (res < 0)
		return PyErr_SetFromErrno(PyExc_OSError);
        
	return Py_BuildValue("s", buf);
}

static char uuidgen_uuidgen__doc__[] = "\
uuidgen() -> string\n\
provides access to the uuidgen(2) system call. The result is returned\n\
as a formatted hex string with dashes.";


static PyMethodDef uuidgen_methods[] = {
	{"uuidgen",	uuidgen_uuidgen, METH_OLDARGS, uuidgen_uuidgen__doc__},
	{NULL,		NULL}		/* sentinel */
};

DL_EXPORT(void)
init_uuidgen(void)
{
	Py_InitModule("_uuidgen", uuidgen_methods);
}
