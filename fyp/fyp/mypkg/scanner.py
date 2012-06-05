import os
import sys
import imp
import inspect
from collections import defaultdict
from constants import *

def load_single_pyc(GLOBALS, original, basedir, module_name, path):
    module = imp.load_compiled(module_name, path)
    for name, predicate in inspect_types.iteritems():
        submodule_key = basedir[len(original)+1:]+'/'+module_name
        GLOBALS['modules'][submodule_key][name] \
            = inspect.getmembers(module,
            lambda m: inspect.getmodule(m) == module and apply(predicate,[m]))

def list_files(GLOBALS, original, basedir):
    file_list = []
    subdir_list = []
    for item in os.listdir(basedir):
        if os.path.isfile(os.path.join(basedir, item)):
            module_name, ext = os.path.splitext(item)
            if not module_name.startswith('_') and ext.endswith('.pyc'):
                file_list.append(item)
                path = basedir + '/' + item
                load_single_pyc(GLOBALS, original, basedir, module_name, path)
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
        load_single_pyc(GLOBALS, pkg_path, pkg_path, pkg_name, pkg_path)
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
