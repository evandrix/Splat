import dis
import marshal
import struct
import re
import os
import sys
import time
import types
import byteplay
import imp
import inspect
import decompiler
from pprint import pprint
from collections import defaultdict
from cStringIO import StringIO
from constants import *

def load_single_pyc(GLOBALS, original, basedir, path):
    dirname, filename = os.path.split(path)
    module_name, ext  = os.path.splitext(filename)
    f = open(path, "rb")
    magic, moddate = f.read(4), f.read(4)
    assert magic == imp.get_magic()
    modtime = time.asctime(time.localtime(struct.unpack('=L', moddate)[0]))
    code = marshal.load(f)

    pyc_info = defaultdict(dict)
    pyc_info['magic_no']          = magic.encode('hex')
    pyc_info['mod_ts']['date']    = moddate.encode('hex')
    pyc_info['mod_ts']['time']    = modtime
    pyc_info['code_object']       = code
    pyc_info['ext_bytecode']      = decompiler.decompile(code)
    pyc_info['code']['argcount']  = code.co_argcount
    pyc_info['code']['nlocals']   = code.co_nlocals
    pyc_info['code']['stacksize'] = code.co_stacksize
    pyc_info['code']['flags']     = code.co_flags
    pyc_info['code']['name']      = code.co_name
    pyc_info['code']['names']     = code.co_names
    pyc_info['code']['varnames']  = code.co_varnames
    pyc_info['code']['freevars']  = code.co_freevars
    pyc_info['code']['cellvars']  = code.co_cellvars
    pyc_info['code']['filename']  = code.co_filename
    pyc_info['code']['firstlineno']  = code.co_firstlineno
    pyc_info['code']['consts']    = code.co_consts
    pyc_info['code']['lnotab']    = code.co_lnotab

    if False:
        import mypkg.instrumentor
        instrumentor = mypkg.instrumentor.Instrumentor(path.replace('_instrumented.pyc','.pyc'))
        exit_code = instrumentor.run()
        if module_name in sys.modules:
            del sys.modules[module_name]
        new_path = os.path.join(dirname, module_name+'_instrumented.pyc')
        module = imp.load_compiled(module_name, new_path)

    module = imp.load_compiled(module_name, path)
    submodule_key = basedir[len(original)+1:]+'/'+module_name
    GLOBALS['pyc_info'][submodule_key] = pyc_info
    for name, predicate in inspect_types.iteritems():
        the_list = inspect.getmembers(module,
            lambda m: inspect.getmodule(m) == module and apply(predicate,[m]))
        if the_list:
            GLOBALS['modules'][submodule_key][name] = the_list
    return True

def list_files(GLOBALS, original, basedir):
    file_list = []
    subdir_list = []
    for item in os.listdir(basedir):
        path = os.path.join(basedir, item)
        dirname, filename = os.path.split(path)
        module_name, ext  = os.path.splitext(filename)
        if os.path.isfile(path):
            if not module_name.startswith('_') \
                and not module_name.startswith('test_') \
                and not module_name.endswith('_instrumented') \
                and ext == '.pyc' \
                and load_single_pyc(GLOBALS, original, basedir, path):
                file_list.append(item)
        else:
            subdir_list.append(os.path.join(basedir, item))
    for subdir in subdir_list:
        list_files(GLOBALS, original, subdir)
    return file_list

def debug(GLOBALS):
    for k,v in GLOBALS.iteritems():
        if k == 'modules':
            if GLOBALS['pkg_type'] == 'directory':
                for k,v in v.iteritems():
                    print k+':'
                    for k,v in v.iteritems():
                        filtered_list = [a for a,b in v if not a.startswith('_')]
                        if filtered_list:
                            print '\t',k+':',filtered_list

def main(GLOBALS):
    pkg_path = os.path.abspath(GLOBALS['pkg_path'])
    pkg_type = GLOBALS['pkg_type']
    pkg_name = GLOBALS['pkg_name']

    if pkg_type == 'bytecode':
        load_single_pyc(GLOBALS, pkg_path, pkg_path, pkg_path)
    elif pkg_type == 'directory':
        list_files(GLOBALS, pkg_path, pkg_path)

    # aggregate class/function pools
    classes, functions = [], []
    for _v in GLOBALS['modules'].values():
        for k,v in _v.iteritems():
            filtered_list = [(a,b) for a,b in v if not a.startswith('_')]
            if filtered_list:
                if k == 'class':
                    classes.extend(filtered_list)
                elif k == 'function':
                    functions.extend(filtered_list)

    all_classes   = { name: c for name,c in classes }
    all_functions = { name: fn for name,fn in functions }

    for class_name, klass in GLOBALS['all_classes'].iteritems():
        class_methods = {}
        for name, method in inspect.getmembers(klass, inspect.ismethod):
            if not name.startswith('_'):
                class_methods[name] = method
        class_type = None
        if type(klass) is types.TypeType:
            class_type = ClassType.NEW
        elif type(klass) is types.ClassType:
            class_type = ClassType.OLD
        all_classes[class_name] = (class_type, klass, class_methods)

    GLOBALS['all_classes']   = all_classes
    GLOBALS['all_functions'] = all_functions
