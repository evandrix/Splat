/*

  Fast CGI App Extension Module


     Copyright 

       Copyright 1996 Digital Creations, L.C., 910 Princess Anne
       Street, Suite 300, Fredericksburg, Virginia 22401 U.S.A. All
       rights reserved.  Copyright in this software is owned by DCLC,
       unless otherwise indicated. Permission to use, copy and
       distribute this software is hereby granted, provided that the
       above copyright notice appear in all copies and that both that
       copyright notice and this permission notice appear. Note that
       any product, process or technology described in this software
       may be the subject of other Intellectual Property rights
       reserved by Digital Creations, L.C. and are not licensed
       hereunder.

     Trademarks 

       Digital Creations & DCLC, are trademarks of Digital Creations, L.C..
       All other trademarks are owned by their respective companies. 

     No Warranty 

       The software is provided "as is" without warranty of any kind,
       either express or implied, including, but not limited to, the
       implied warranties of merchantability, fitness for a particular
       purpose, or non-infringement. This software could include
       technical inaccuracies or typographical errors. Changes are
       periodically made to the software; these changes will be
       incorporated in new editions of the software. DCLC may make
       improvements and/or changes in this software at any time
       without notice.

     Limitation Of Liability 

       In no event will DCLC be liable for direct, indirect, special,
       incidental, economic, cover, or consequential damages arising
       out of the use of or inability to use this software even if
       advised of the possibility of such damages. Some states do not
       allow the exclusion or limitation of implied warranties or
       limitation of liability for incidental or consequential
       damages, so the above limitation or exclusion may not apply to
       you.

    If you have questions regarding this software,
    contact:
   
      Jim Fulton, jim@digicool.com
      Digital Creations L.C.  
   
      (540) 371-6909

  Revision 1.4  1997/01/16 13:51:48  jim
  Added support for threaded Python.  The fcgiapp module is still single
  threaded, but now it won't block other Python threads.

  Added additional error checking.

  Included code to support uncooked multi-threaded fcgiapp library.

  Revision 1.3  1996/08/29 22:01:22  jfulton
  Bug fixes and added Finish module function.

  Revision 1.2  1996/08/12 16:08:33  jfulton
  Now return errno as accept exception value.

  Revision 1.1  1996/06/28 16:13:22  jfulton
  Initial version.


*/
static char fcgiapp_module_documentation[] = 
"Fast CGI Module\n"
"\n"
"This module provides an interface to the Fast CGI applications\n"
"library, fcgiapp.  \n"
"\n"
"Fast CGI programs are long running programs that accept multiple \n"
"request.  Programs take the form:\n"
"\n"
"  <pre>\n"
"  import fcgiapp\n"
"  while 1:\n"
"    input, output, error, environ = fcgiapp.Accept()\n"
"    # Read CGI imput from input, write output to output and error, and\n"
"    # get standard CGI environment variables from environ \n"
"  </pre>\n"
"\n"
"\n"
"\n"
"Note that you must also have the "
"<a href=\"http://www.fastcgi.com/applibs/\">\n"
"Fast-CGI developers Kit</a> to compile this module.\n"
"\n"
"$Id: fcgiappmodule.c,v 1.1 2003/05/01 17:43:55 pje Exp $\n"
;

#include <errno.h>
#include <string.h>

#ifdef WITH_THREAD
#include "Python.h"
#else
#define WITH_THREAD 1
#include "Python.h"
#undef WITH_THREAD
#endif

#ifdef THREADED_FCGI
static PyObject *TooManyRequestsError;
#define _REENTRANT
#endif

#include "fcgiapp.h"

#define ASSIGN(V,E) {PyObject *__e; __e=(E); Py_XDECREF(V); (V)=__e;}
#define UNLESS(E) if(!(E))
#define UNLESS_ASSIGN(V,E) ASSIGN(V,E) UNLESS(V)

static PyObject *ErrorObject,
  *UnsupportedVersion, *ProtocolError, *ParamsError, *CallSeqError;


static PyObject *
ErrorFor(int code)
{
  switch(code)
    {
    case FCGX_UNSUPPORTED_VERSION:
      return UnsupportedVersion;
    case FCGX_PROTOCOL_ERROR:
      return ProtocolError;
    case FCGX_PARAMS_ERROR:
      return ParamsError;
    case FCGX_CALL_SEQ_ERROR:
      return CallSeqError;
    default:
      return ErrorObject;
    }
}

/* ----------------------------------------------------- */


/* Declarations for objects of type fcgiEnviron */

typedef struct {
	PyObject_HEAD
	FCGX_ParamArray parms;
} fcgieobject;

staticforward PyTypeObject Fcgietype;



/* ---------------------------------------------------------------- */

/* Declarations for objects of type fcgiStream */

typedef struct {
  PyObject_HEAD
  FCGX_Stream *stream;
  long position;
  long content_length;
} fcgisobject;

staticforward PyTypeObject Fcgistype;

/* ---------------------------------------------------------------- */

static char fcgie_keys__doc__[] = 
"keys() -- Return the Fast CGI environment variable names"
;

static PyObject *
fcgie_keys(self, args)
	fcgieobject *self;
	PyObject *args;
{
  PyObject *r=0, *s=0;

  if (!PyArg_ParseTuple(args, ""))
    return NULL;
  
  if(self->parms)
    {
      char **parm, *e, *c;

      UNLESS(r=PyList_New(0)) return NULL;
      
      for(parm=self->parms; *parm; parm++)
	{
	  c=*parm;
	  if(e=strstr(c,"="))
	    {
	      UNLESS_ASSIGN(s,PyString_FromStringAndSize(c,e-c)) goto err;
	      UNLESS(-1 != PyList_Append(r,s)) goto err;
	    }
	}
      Py_XDECREF(s);
      return r;
    }
  
  PyErr_SetString(ErrorObject,"No current request environment");

err:
  Py_XDECREF(r);
  Py_XDECREF(s);
  return NULL;
  
}


static char fcgie_has_key__doc__[] = 
"has_key(name) -- Test whether the Fast CGI environment includes a"
" variable name"
;

static PyObject *
fcgie_has_key(self, args)
	fcgieobject *self;
	PyObject *args;
{
  char *k;
  int lk;

  if (!PyArg_ParseTuple(args, "s", &k))
    return NULL;
  
  lk=strlen(k);

  if(self->parms)
    {
      char **parm, *e, *c;
      
      for(parm=self->parms; *parm; parm++)
	{
	  c=*parm;
	  if((e=strstr(c,"=")) && lk == e-c && strncmp(c,k,e-c)==0)
		return PyInt_FromLong(1);
	}
      return PyInt_FromLong(0);
    }
  
  PyErr_SetString(ErrorObject,"No current request environment");
  return NULL;
  
}

static char fcgie_values__doc__[] = 
"values() -- Return the Fast CGI environment variable values"
;

static PyObject *
fcgie_values(self, args)
	fcgieobject *self;
	PyObject *args;
{
  PyObject *r=0, *s=0;

  if (!PyArg_ParseTuple(args, ""))
    return NULL;
  
  if(self->parms)
    {
      char **parm, *e, *c;

      UNLESS(r=PyList_New(0)) return NULL;
      
      for(parm=self->parms; *parm; parm++)
	{
	  c=*parm;
	  if(e=strstr(c,"="))
	    {
	      UNLESS_ASSIGN(s,PyString_FromString(e+1)) goto err;
	      UNLESS(-1 != PyList_Append(r,s)) goto err;
	    }
	}
      Py_XDECREF(s);
      return r;
    }
  
  PyErr_SetString(ErrorObject,"No current request environment");

err:
  Py_XDECREF(r);
  Py_XDECREF(s);
  return NULL;
  
}


static char fcgie_items__doc__[] = 
"items() -- Return the Fast CGI environment variable name/value pairs"
;

static PyObject *
fcgie_items(self, args)
	fcgieobject *self;
	PyObject *args;
{
  PyObject *r=0, *k=0, *v=0, *t=0;

  if (!PyArg_ParseTuple(args, ""))
    return NULL;
  
  if(self->parms)
    {
      char **parm, *e, *c;

      UNLESS(r=PyList_New(0)) return NULL;
      
      for(parm=self->parms; *parm; parm++)
	{
	  c=*parm;
	  if(e=strstr(c,"="))
	    {
	      UNLESS_ASSIGN(k,PyString_FromStringAndSize(c,e-c)) goto err;
	      UNLESS_ASSIGN(v,PyString_FromString(e+1)) goto err;
	      UNLESS_ASSIGN(t,Py_BuildValue("(OO)",k,v)) goto err;
	      UNLESS(-1 != PyList_Append(r,t)) goto err;
	    }
	}
      Py_XDECREF(k);
      Py_XDECREF(v);
      Py_XDECREF(t);
      return r;
    }
  
  PyErr_SetString(ErrorObject,"No current request environment");

err:
  Py_XDECREF(r);
  Py_XDECREF(k);
  Py_XDECREF(v);
  Py_XDECREF(t);
  return NULL;
}


static struct PyMethodDef fcgie_methods[] = {
  {"keys",	(PyCFunction)fcgie_keys,	1,	fcgie_keys__doc__},
  {"has_key",	(PyCFunction)fcgie_has_key,	1,	fcgie_has_key__doc__},
  {"values",	(PyCFunction)fcgie_values,	1,	fcgie_values__doc__},
  {"items",	(PyCFunction)fcgie_items,	1,	fcgie_items__doc__},
 
	{NULL,		NULL}		/* sentinel */
};

/* ---------- */

static void
fcgie_dealloc(self)
	fcgieobject *self;
{
  PyMem_DEL(self);
}

static int
fcgie_print(self, fp, flags)
	fcgieobject *self;
	FILE *fp;
	int flags;
{
  if(self->parms)
    {
      char **parm, *e, *c;
      
      fprintf(fp,"{\n");
      for(parm=self->parms; *parm; parm++)
	{
	  c=*parm;
	  if(e=strstr(c,"="))
	    {
	      *e=0;
	      fprintf(fp,"\t%s: %s,\n",c,e+1);
	      *e='=';
	    }
	}
      fprintf(fp,"}");
      return 0;
    }
  
  PyErr_SetString(ErrorObject,"No current request environment");
  return -1;
}

static PyObject *
fcgie_getattr(self, name)
	fcgieobject *self;
	char *name;
{
	/* XXXX Add your own getattr code here */
	return Py_FindMethod(fcgie_methods, (PyObject *)self, name);
}

static PyObject *
fcgie_repr(self)
	fcgieobject *self;
{
  PyObject *r=0, *k=0, *v=0, *t=0;
  static PyObject *format=0;
  
  if(self->parms)
    {
      char **parm, *e, *c;

      UNLESS(format=PyString_FromString("'%s': '%s', ")) return NULL;
      UNLESS(r=PyString_FromString("{")) return NULL;
      
      for(parm=self->parms; *parm; parm++)
	{
	  c=*parm;
	  if(e=strstr(c,"="))
	    {
	      UNLESS_ASSIGN(k,PyString_FromStringAndSize(c,e-c)) goto err;
	      UNLESS_ASSIGN(v,PyString_FromString(e+1)) goto err;
	      UNLESS_ASSIGN(t,Py_BuildValue("(OO)",k,v)) goto err;
	      UNLESS_ASSIGN(t,PyString_Format(format,t)) goto err;
	      UNLESS_ASSIGN(r,PySequence_Concat(r,t)) goto err;
	    }
	}
      UNLESS_ASSIGN(t,PyString_FromString("}")) goto err;
      UNLESS_ASSIGN(r,PySequence_Concat(r,t)) goto err;
      Py_XDECREF(k);
      Py_XDECREF(v);
      Py_XDECREF(t);
      return r;
    }
  
  PyErr_SetString(ErrorObject,"No current request environment");

err:
  Py_XDECREF(r);
  Py_XDECREF(k);
  Py_XDECREF(v);
  Py_XDECREF(t);
  return NULL;
}

/* Code to access fcgiEnviron objects as mappings */

static int
fcgie_length(self)
	fcgieobject *self;
{
  if(self->parms)
    {
      char **parm;
      int l=0;
      
      for(parm=self->parms; *parm; parm++)
	if(strstr(*parm,"=")) l++;

      return l;
    }
  
  PyErr_SetString(ErrorObject,"No current request environment");
  return -1;
}

static PyObject *
fcgie_subscript(self, okey)
	fcgieobject *self;
	PyObject *okey;
{
  char *key;
  
  UNLESS(PyArg_Parse(okey, "s",&key)) return NULL;

  if(self->parms)
    {
      char *v;

      if(v=FCGX_GetParam(key,self->parms))
	return PyString_FromString(v);
      PyErr_SetString(PyExc_KeyError,key);
    }
  else PyErr_SetString(ErrorObject,"No current request environment");
      
  return NULL;
}

static PyMappingMethods fcgie_as_mapping = {
	(inquiry)fcgie_length,		/*mp_length*/
	(binaryfunc)fcgie_subscript,		/*mp_subscript*/
	(objobjargproc)NULL,	/*mp_ass_subscript*/
};

/* -------------------------------------------------------- */

static char Fcgietype__doc__[] = 
"Fast CGI Environment"
"\n"
"Models environment variables for fast CGI processes.\n"
;

static PyTypeObject Fcgietype = {
	PyObject_HEAD_INIT(NULL)	/* PJE 03/05/01 Cygwin fix */
	0,				/*ob_size*/
	"fcgiEnviron",			/*tp_name*/
	sizeof(fcgieobject),		/*tp_basicsize*/
	0,				/*tp_itemsize*/
	/* methods */
	(destructor)fcgie_dealloc,	/*tp_dealloc*/
	(printfunc)fcgie_print,		/*tp_print*/
	(getattrfunc)fcgie_getattr,	/*tp_getattr*/
	(setattrfunc)0,	/*tp_setattr*/
	(cmpfunc)0,		/*tp_compare*/
	(reprfunc)fcgie_repr,		/*tp_repr*/
	0,			/*tp_as_number*/
	0,		/*tp_as_sequence*/
	&fcgie_as_mapping,		/*tp_as_mapping*/
	(hashfunc)0,		/*tp_hash*/
	(ternaryfunc)0,		/*tp_call*/
	(reprfunc)0,		/*tp_str*/

	/* Space for future expansion */
	0L,0L,0L,0L,
	Fcgietype__doc__ /* Documentation string */
};

/* End of code for fcgiEnviron objects */
/* -------------------------------------------------------- */


static char fcgis_read__doc__[] = 
"read(bytes) -- Read bytes from a Fast CGI Stream.\n"
"\n"
"If bytes is ommitted, then the rest of the stream will be read.\n"
"The data read is returned as a string.\n"
;

static PyObject *
fcgis_read(self, args)
	fcgisobject *self;
	PyObject *args;
{
  long n=-1;
  PyObject *r=0, *s=0;
  char buf[512];
  int rr=sizeof(buf)-1, nr;

  UNLESS(PyArg_ParseTuple(args, "|l", &n)) return NULL;

  if(! self->stream)
    {
      PyErr_SetString(ErrorObject,"Attempt to access stream for finished request");
      return NULL;
    }

  while(n && self->position < self->content_length)
    {
      if(n >= 0 && rr > n) rr=n;
      if(rr + self->position > self->content_length)
	rr=self->content_length-self->position;
      Py_BEGIN_ALLOW_THREADS
      nr=FCGX_GetStr(buf,rr,self->stream);
      Py_END_ALLOW_THREADS
      if(nr > 0)
	{
	  self->position += nr;
	  if(r)
	    {
	      UNLESS_ASSIGN(s,PyString_FromStringAndSize(buf,nr)) goto err;
	      UNLESS_ASSIGN(r,PySequence_Concat(r,s)) goto err;
	    }
	  else
	    {
	      UNLESS(r=PyString_FromStringAndSize(buf,nr)) goto err;
	    }
	}
      if(nr < rr)
	break;
      if(n > 0)
	n -= nr;
    }

  Py_XDECREF(s);

  if(r)
    return r;
  else
    return PyString_FromString("");

err:
  Py_XDECREF(r);
  return NULL;
}


static char fcgis_readline__doc__[] = 
"readline() -- Read a line of data from a Fast CGI Stream"
;

static int
binary_fcgi_readline(FCGX_Stream *stream, int lbuf, char *buf)
{
  int i, c;
  char *b;

  Py_BEGIN_ALLOW_THREADS
  for(i=0, b=buf; i < lbuf; i++, b++)
    {
      c=FCGX_GetChar(stream);
      if(c==EOF) break;
      *b=c;
      if(c=='\n') {
	i++;
	break;
      }
    }
  Py_END_ALLOW_THREADS
  
  return i;
}


static PyObject *
fcgis_readline(self, args)
	fcgisobject *self;
	PyObject *args;
{
  PyObject *r=0, *s=0;
  char buf[128], *c;
  int rr=sizeof(buf), nr;
  long max;

  UNLESS(! args || PyArg_ParseTuple(args, "")) return NULL;

  if(! self->stream)
    {
      PyErr_SetString(ErrorObject,"Attempt to access stream for finished request");
      return NULL;
    }
  
  max=self->content_length-self->position;
  if(rr > max)rr=max;
  while(nr=binary_fcgi_readline(self->stream, rr, buf))
    {
      self->position += nr;
      if(r)
	{
	  UNLESS_ASSIGN(s,PyString_FromStringAndSize(buf,nr)) goto err;
	  UNLESS_ASSIGN(r,PySequence_Concat(r,s)) goto err;
	}
      else
	{
	  UNLESS(r=PyString_FromStringAndSize(buf,nr)) goto err;
	}
      if(buf[nr-1]=='\n') break;
      max=self->content_length-self->position;
      if(rr > max)rr=max;
    }

  Py_XDECREF(s);

  if(r)
    return r;
  else
    return PyString_FromString("");

err:
  Py_XDECREF(s);
  Py_XDECREF(r);
  return NULL;
}


static char fcgis_readlines__doc__[] = 
"readlines() -- Read remaining lines from a Fast CGI Stream"
;

static PyObject *
fcgis_readlines(self, args)
	fcgisobject *self;
	PyObject *args;
{
  PyObject *r=0, *s=0;
  long l;

  UNLESS(PyArg_ParseTuple(args, "")) return NULL;

  UNLESS(r=PyList_New(0)) return NULL;

  while(1)
    {
      UNLESS_ASSIGN(s,fcgis_readline(self,NULL)) goto err;
      UNLESS(-1 != (l=PyObject_Length(s))) goto err;
      if(l)
	{
	  UNLESS(PyList_Append(r,s)) goto err;
	}
      else
	break;
    }
  Py_XDECREF(s);
  return r;

err:
  Py_XDECREF(s);
  Py_XDECREF(r);
  return NULL;
}


static char fcgis_write__doc__[] = 
"write(s) -- Write a string, s, to a Fast CGI Stream"
;

static PyObject *
fcgis_write(self, args)
	fcgisobject *self;
	PyObject *args;
{
  char *s;
  int n;
  PyObject *arg;

  UNLESS(PyArg_ParseTuple(args, "O", &arg)) return NULL;

  if(! self->stream)
    {
      PyErr_SetString(ErrorObject,"Attempt to access stream for finished request");
      return NULL;
    }

  if(PyString_Check(arg))
    s=PyString_AS_STRING((PyStringObject*)arg);
  else
    {
      PyErr_SetString(PyExc_TypeError, "string argument expected for write");
      return NULL;
    }

  UNLESS(-1 != (n=PyString_Size(arg))) return NULL;
  self->position += n;
  Py_BEGIN_ALLOW_THREADS
  if(FCGX_PutStr(s,n,self->stream) == -1)
    {
      Py_BLOCK_THREADS
      PyErr_SetString(PyExc_IOError, "write error");
      return NULL;
    }      
  Py_END_ALLOW_THREADS

  Py_INCREF(Py_None);
  return Py_None;
}


static char fcgis_StartFilterData__doc__[] = 
"StartFilterData() -- Start filter stream???"
"\n"
"The stream is an input stream for a FCGI_FILTER request.\n"
"The stream is positioned at EOF on FCGI_STDIN.\n"
"Repositions stream to the start of FCGI_DATA.\n"
"If the preconditions are not met (e.g. FCGI_STDIN has not\n"
"been read to EOF) sets the stream error code to\n"
"FCGX_CALL_SEQ_ERROR.\n"
;

static PyObject *
fcgis_StartFilterData(self, args)
	fcgisobject *self;
	PyObject *args;
{
  int code;

  if (!PyArg_ParseTuple(args, ""))
    return NULL;

  if(! self->stream)
    {
      PyErr_SetString(ErrorObject,"Attempt to access stream for finished request");
      return NULL;
    }

  Py_BEGIN_ALLOW_THREADS
  if(code=FCGX_StartFilterData(self->stream))
    {
      Py_BLOCK_THREADS
      PyErr_SetObject(ErrorFor(code), (PyObject*)self);
      return NULL;
    }
  Py_END_ALLOW_THREADS

    Py_INCREF(Py_None);
    return Py_None;
}


static char fcgis_SetExitStatus__doc__[] = 
"SetExitStatus(code) -- Sets the exit status for stream's request."
"\n"
"The exit status is the status code the request would have exited with,\n"
"had the request been run as a CGI program.  You can call SetExitStatus\n"
"several times during a request; the last call before the request ends\n"
"determines the value.\n"
;

static PyObject *
fcgis_SetExitStatus(self, args)
	fcgisobject *self;
	PyObject *args;
{
  int status;

  if (!PyArg_ParseTuple(args, "i", &status))
    return NULL;

  if(! self->stream)
    {
      PyErr_SetString(ErrorObject,"Attempt to access stream for finished request");
      return NULL;
    }

  FCGX_SetExitStatus(status, self->stream);
  
  Py_INCREF(Py_None);
  return Py_None;
}


static char fcgis_flush__doc__[] = 
"flush() -- Flushes a Fast CGI output stream"
;

static PyObject *
fcgis_flush(self, args)
	fcgisobject *self;
	PyObject *args;
{
  UNLESS(PyArg_ParseTuple(args, "")) return NULL;

  if(! self->stream)
    {
      PyErr_SetString(ErrorObject,"Attempt to access stream for finished request");
      return NULL;
    }

  Py_BEGIN_ALLOW_THREADS
  if(FCGX_FFlush(self->stream) == -1)
    {
      Py_BLOCK_THREADS
      PyErr_SetObject(ErrorObject, (PyObject*)self);
      return NULL;
    }
  Py_END_ALLOW_THREADS
  
  Py_INCREF(Py_None);
  return Py_None;
}


static char fcgis_close__doc__[] = 
"close() -- Close a Fast CGI stream"
;

static PyObject *
fcgis_close(self, args)
	fcgisobject *self;
	PyObject *args;
{
  UNLESS(PyArg_ParseTuple(args, "")) return NULL;

  if(! self->stream)
    {
      PyErr_SetString(ErrorObject,"Attempt to access stream for finished request");
      return NULL;
    }

  Py_BEGIN_ALLOW_THREADS
  if(FCGX_FClose(self->stream) == -1)
    {
      Py_BLOCK_THREADS
      PyErr_SetObject(ErrorObject, (PyObject*)self);
      return NULL;
    }
  Py_END_ALLOW_THREADS

  Py_INCREF(Py_None);
  return Py_None;
}


static char fcgis_GetError__doc__[] = 
"GetError() -- Return the stream error code."
"\n"
"0 means no error, > 0 is an errno(2) error, < 0 is an FastCGI error.\n"
;

static PyObject *
fcgis_GetError(self, args)
	fcgisobject *self;
	PyObject *args;
{
  int code;
  PyObject *r;

  UNLESS(PyArg_ParseTuple(args, "")) return NULL;

  if(! self->stream)
    {
      PyErr_SetString(ErrorObject,"Attempt to access stream for finished request");
      return NULL;
    }

  if(code=FCGX_GetError(self->stream))
    {
      if(code < 0)
	{
	  r=ErrorFor(code);
	  Py_INCREF(r);
	}
      else
	{
	  char *e;

	  e=strerror(code);
	  if(! e) e="unknown";
	  r=PyString_FromString(e);
	}
      return r;
    }

  Py_INCREF(Py_None);
  return Py_None;
}


static char fcgis_ClearError__doc__[] = 
"ClearError() -- Clear the stream error code and end-of-file indication."
;

static PyObject *
fcgis_ClearError(self, args)
	fcgisobject *self;
	PyObject *args;
{

  UNLESS(PyArg_ParseTuple(args, "")) return NULL;

  if(! self->stream)
    {
      PyErr_SetString(ErrorObject,"Attempt to access stream for finished request");
      return NULL;
    }

  FCGX_ClearError(self->stream);
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *
fcgis_tell(self, args)
	fcgisobject *self;
	PyObject *args;
{
  UNLESS(PyArg_ParseTuple(args, "")) return NULL;
  return PyInt_FromLong(self->position);
}


static struct PyMethodDef fcgis_methods[] = {
  {"read",	(PyCFunction)fcgis_read,	1,	fcgis_read__doc__},
  {"readline",	(PyCFunction)fcgis_readline,	1,	fcgis_readline__doc__},
  {"readlines",	(PyCFunction)fcgis_readlines,	1,	fcgis_readlines__doc__},
  {"write",	(PyCFunction)fcgis_write,	1,	fcgis_write__doc__},
  {"tell",	(PyCFunction)fcgis_tell, 	1,
   "Return stream position"},
  {"StartFilterData",	(PyCFunction)fcgis_StartFilterData,1,
   fcgis_StartFilterData__doc__},
  {"SetExitStatus",	(PyCFunction)fcgis_SetExitStatus,1,
   fcgis_SetExitStatus__doc__},
  {"flush",	(PyCFunction)fcgis_flush,	1,	fcgis_flush__doc__},
  {"close",	(PyCFunction)fcgis_close,	1,	fcgis_close__doc__},
  {"GetError",	(PyCFunction)fcgis_GetError,	1,	fcgis_GetError__doc__},
  {"ClearError",(PyCFunction)fcgis_ClearError,	1,fcgis_ClearError__doc__},
 
  {NULL,		NULL}		/* sentinel */
};

/* ---------- */

static void
fcgis_dealloc(self)
	fcgisobject *self;
{
  PyMem_DEL(self);
}

static PyObject *
fcgis_getattr(self, name)
     fcgisobject *self;
     char *name;
{
  return Py_FindMethod(fcgis_methods, (PyObject *)self, name);
}

static char Fcgistype__doc__[] = 
"Fast CGI Stream\n"
"\n"
"Fast CGI streams are modeled after file objects and are used to\n"
"handle fast CGI input and output data.\n"
;

static PyTypeObject Fcgistype = {
  PyObject_HEAD_INIT(NULL)	/* PJE 03/05/01 Cygwin fix */
  0,				/*ob_size*/
  "fcgiStream",			/*tp_name*/
  sizeof(fcgisobject),		/*tp_basicsize*/
  0,				/*tp_itemsize*/
  /* methods */
  (destructor)fcgis_dealloc,	/*tp_dealloc*/
  (printfunc)0,		/*tp_print*/
  (getattrfunc)fcgis_getattr,	/*tp_getattr*/
  (setattrfunc)0,	/*tp_setattr*/
  (cmpfunc)0,		/*tp_compare*/
  (reprfunc)0,		/*tp_repr*/
  0,			/*tp_as_number*/
  0,		/*tp_as_sequence*/
  0,		/*tp_as_mapping*/
  (hashfunc)0,		/*tp_hash*/
  (ternaryfunc)0,		/*tp_call*/
  (reprfunc)0,		/*tp_str*/
  
  /* Space for future expansion */
  0L,0L,0L,0L,
  Fcgistype__doc__ /* Documentation string */
};

/* End of code for fcgiStream objects */
/* -------------------------------------------------------- */


static char fcgi_isCGI__doc__[] =
"isCGI() -- Is this a CGI Program"
;

static PyObject *
fcgi_isCGI(self, args)
	PyObject *self;	/* Not used */
	PyObject *args;
{
  UNLESS(PyArg_ParseTuple(args, "")) return NULL;
  return PyInt_FromLong(FCGX_IsCGI());
}

static char fcgi_Finish__doc__[] =
"Finish() -- Finishes the current request from the HTTP server.";

static PyObject *
fcgi_Finish(self, args)
	PyObject *self;	/* Not used */
	PyObject *args;
{
  Py_BEGIN_ALLOW_THREADS
  FCGX_Finish();
  Py_END_ALLOW_THREADS
  Py_INCREF(Py_None);
  return Py_None;
}

static char fcgi_Accept__doc__[] =
"Accept() -- Accept a Fast CGI Connection\n"
"\n"
"The function returns the input, output, and error streams\n"
"associated with the connection as well as the environment\n"
"dictionary.\n"
"\n"
"input, output, err, environ = Accept()\n"
;

static PyObject *
fcgi_Accept(self, args)
	PyObject *self;	/* Not used */
	PyObject *args;
{
  static fcgieobject *fcgi_environ=0;
  static fcgisobject *fcgi_stdin=0, *fcgi_stdout=0, *fcgi_stderr=0;
  char *content_length;

  UNLESS(PyArg_ParseTuple(args, "")) return NULL;

  if(! fcgi_environ)
    {
      fcgi_stdin  =(fcgisobject *)PyObject_NEW(fcgisobject, &Fcgistype);
      fcgi_stdout =(fcgisobject *)PyObject_NEW(fcgisobject, &Fcgistype);
      fcgi_stderr =(fcgisobject *)PyObject_NEW(fcgisobject, &Fcgistype);
      fcgi_environ=(fcgieobject *)PyObject_NEW(fcgieobject, &Fcgietype);
    }

  Py_BEGIN_ALLOW_THREADS
  if(-1 == FCGX_Accept(&(fcgi_stdin->stream),
		       &(fcgi_stdout->stream),
		       &(fcgi_stderr->stream),
		       &(fcgi_environ->parms)
		       )
     )
    {
      PyObject *v;

      Py_BLOCK_THREADS
      v=PyInt_FromLong(errno);
      PyErr_SetObject(ErrorObject, v);
      Py_DECREF(v);
      return NULL;
    }
  Py_END_ALLOW_THREADS

  fcgi_stdin->position=0;
  fcgi_stdout->position=0;
  fcgi_stderr->position=0;
  fcgi_stdin->content_length=0;
  fcgi_stdout->content_length=0;
  fcgi_stderr->content_length=0;
  if(content_length=FCGX_GetParam("CONTENT_LENGTH",fcgi_environ->parms))
    fcgi_stdin->content_length=atol(content_length);

  return Py_BuildValue("(OOOO)",
		       fcgi_stdin, fcgi_stdout, fcgi_stderr, fcgi_environ);
}

#ifdef THREADED_FCGI

/* Declarations for objects of type Request */

typedef struct {
  PyObject_HEAD
  FCGX_Request *request;
  fcgisobject *in, *out, *err;
  fcgieobject *env;
} Requestobject;

staticforward PyTypeObject Requesttype;

/* ---------------------------------------------------------------- */

static char Request_Finish__doc__[] = 
"Finish() -- Finish the FastCGI request"
;

static PyObject *
Request_Finish(self, args)
	Requestobject *self;
	PyObject *args;
{
  UNLESS(!args || PyArg_ParseTuple(args, "")) return NULL;

  if(self->request)
    {
      Py_BEGIN_ALLOW_THREADS 
      FCGX_RequestFinish(self->request);
      Py_END_ALLOW_THREADS
      self->in->stream=NULL;
      self->out->stream=NULL;
      self->err->stream=NULL;
      self->env->parms=NULL;
    }
  Py_INCREF(Py_None);
  return Py_None;
}


static struct PyMethodDef Request_methods[] = {
  {"Finish",	(PyCFunction)Request_Finish,	1,	Request_Finish__doc__}, 
  {NULL,		NULL}		/* sentinel */
};

/* ---------- */

static Requestobject *
newRequestobject()
{
  Requestobject *self;
  FCGX_Request *request;
  int errcd;

  UNLESS(self = PyObject_NEW(Requestobject, &Requesttype)) return NULL;

  self->request=NULL;
  self->in=self->out=self->err=NULL;
  self->env=NULL;

  UNLESS(self->in  =(fcgisobject *)PyObject_NEW(fcgisobject, &Fcgistype)) goto err;
  UNLESS(self->out =(fcgisobject *)PyObject_NEW(fcgisobject, &Fcgistype)) goto err;
  UNLESS(self->err =(fcgisobject *)PyObject_NEW(fcgisobject, &Fcgistype)) goto err;
  UNLESS(self->env=(fcgieobject *)PyObject_NEW(fcgieobject, &Fcgietype)) goto err;	

  Py_BEGIN_ALLOW_THREADS 
  request=FCGX_RequestAccept(&errcd)
  Py_END_ALLOW_THREADS

  UNLESS(request)
    {
      if(errcd==FCGX_MAX_REQUESTS_EXCEEDED)
	PyErr_SetString(TooManyRequestsError,"Too many requests");
      else
	PyErr_SetObject(ErrorObject,PyInt_FromLong(errcd));
      goto err;
    }

  self->request=request;
  self->in->stream=request->in; self->in->position=self->in->content_length=0;
  self->out->stream=request->out; self->out->position=self->out->content_length=0;
  self->err->stream=request->err; self->err->position=self->err->content_length=0;
  self->env->parms=request->envp;

  return self;
err:
  Py_DECREF(self);
  return NULL;
}


static void
Request_dealloc(self)
	Requestobject *self;
{
  Request_Finish(self,NULL);
  Py_XDECREF(self->in);
  Py_XDECREF(self->out);
  Py_XDECREF(self->err);
  Py_XDECREF(self->env);
  PyMem_DEL(self);
}

static PyObject *
Request_getattr(self, name)
	Requestobject *self;
	char *name;
{
  if(*name=='i' && strcmp(name,"input" )==0)
    {
      Py_INCREF(self->in );
      return (PyObject*)self->in ;
    }
  if(*name=='o' && strcmp(name,"output")==0)
    {
      Py_INCREF(self->out);
      return (PyObject*)self->out;
    }
  if(*name=='e' && strcmp(name,"error")==0)
    {
      Py_INCREF(self->err);
      return (PyObject*)self->err;
    }
  if(*name=='e' && strcmp(name,"environment")==0)
    {
      Py_INCREF(self->env);
      return (PyObject*)self->env;
    }
  return Py_FindMethod(Request_methods, (PyObject *)self, name);
}

static char Requesttype__doc__[] = 
"A Fast CGI Request\n"
"\n"
"This object has attributes for accessing a request's environment,\n"
"standard in, and standard out.\n"
;

static PyTypeObject Requesttype = {
	PyObject_HEAD_INIT(NULL)	/* PJE 03/05/01 Cygwin fix */
	0,				/*ob_size*/
	"Request",			/*tp_name*/
	sizeof(Requestobject),		/*tp_basicsize*/
	0,				/*tp_itemsize*/
	/* methods */
	(destructor)Request_dealloc,	/*tp_dealloc*/
	(printfunc)0,		/*tp_print*/
	(getattrfunc)Request_getattr,	/*tp_getattr*/
	(setattrfunc)0,	/*tp_setattr*/
	(cmpfunc)0,		/*tp_compare*/
	(reprfunc)0,		/*tp_repr*/
	0,			/*tp_as_number*/
	0,		/*tp_as_sequence*/
	0,		/*tp_as_mapping*/
	(hashfunc)0,		/*tp_hash*/
	(ternaryfunc)0,		/*tp_call*/
	(reprfunc)0,		/*tp_str*/

	/* Space for future expansion */
	0L,0L,0L,0L,
	Requesttype__doc__ /* Documentation string */
};

/* End of code for Request objects */
/* -------------------------------------------------------- */


static char tfcgi_AcceptRequest__doc__[] =
"AcceptRequest() -- Accept a new FastCGI request in a threaded environment\n"
"\n"
"Returns a Request object that has attributes for standard input,\n"
"output, and error, and has an attribute for the environment.\n"
"\n"
"When done processing the request, make sure to call the Request\n"
"object's Finish method.\n"
;

static PyObject *
tfcgi_AcceptRequest(self, args)
	PyObject *self;	/* Not used */
	PyObject *args;
{
  if (!PyArg_ParseTuple(args, ""))
    return NULL;

  return (PyObject*)newRequestobject();
}

/* List of methods defined in the module */

static struct PyMethodDef tfcgi_methods[] = {
  {"AcceptRequest",(PyCFunction)tfcgi_AcceptRequest,	1,	tfcgi_AcceptRequest__doc__},
  
  {NULL,		NULL}		/* sentinel */
};


#endif


/* List of methods defined in the module */

static struct PyMethodDef fcgi_methods[] = {
  {"isCGI",	(PyCFunction)fcgi_isCGI,	1,	fcgi_isCGI__doc__},
  {"Finish",	(PyCFunction)fcgi_Finish,	1,	fcgi_Finish__doc__},
  {"Accept",	(PyCFunction)fcgi_Accept,	1,	fcgi_Accept__doc__},
#ifdef THREADED_FCGI
  {"AcceptRequest",(PyCFunction)tfcgi_AcceptRequest,	1,	tfcgi_AcceptRequest__doc__},
#endif
  {NULL,		NULL}		/* sentinel */
};


/* Initialization function for the module (*must* be called initfcgiapp) */

void
initfcgiapp()
{
  PyObject *m, *d;

#ifdef THREADED_FCGI
  Requesttype.ob_type = &PyType_Type;	/* PJE 03/05/01 Cygwin fix */
#endif
  Fcgietype.ob_type = &PyType_Type;	/* PJE 03/05/01 Cygwin fix */
  Fcgistype.ob_type = &PyType_Type;	/* PJE 03/05/01 Cygwin fix */  

  /* Create the module and add the functions */
  m = Py_InitModule4("fcgiapp", fcgi_methods,
		     fcgiapp_module_documentation,
		     (PyObject*)NULL,PYTHON_API_VERSION);

  /* Add some symbolic constants to the module */
  d = PyModule_GetDict(m);
  ErrorObject = PyString_FromString("fcgiapp.error");
  PyDict_SetItemString(d, "error", ErrorObject);

#define ADDERR(N) N = PyString_FromString("fcgiapp." #N); \
	          PyDict_SetItemString(d, #N, N);

  ADDERR(UnsupportedVersion);
  ADDERR(ProtocolError);
  ADDERR(ParamsError);
  ADDERR(CallSeqError);

#ifdef THREADED_FCGI
  ADDERR(TooManyRequestsError);
  {
    char *maxRequestsString;
    int maxRequests;

    if(!((maxRequestsString=getenv("FCGI_MAX_REQUESTS")) &&
	 (maxRequests=atol(maxRequestsString)) > 0))
      maxRequests=10;
      
    FCGX_ModuleInit(maxRequests);
  }
#endif
	
  /* Check for errors */
  if (PyErr_Occurred())
    Py_FatalError("can't initialize module fcgiapp");
}

