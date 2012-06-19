import re
import os
import sys
import imp
import compileall
import byteplay
import time
import struct
import marshal
from cStringIO import StringIO

def get_base_import_dir(GLOBALS, pkg_type):
    if pkg_type == 'directory':
        assert GLOBALS['pkg_path'].split('/')[-1] == GLOBALS['pkg_name']
        PYTHONPATH = os.path.join(os.path.dirname(GLOBALS['pkg_path']))
        sys.path.append(PYTHONPATH)
        return PYTHONPATH
    elif pkg_type == 'bytecode':
        f = open(GLOBALS['pkg_path'], "rb")
        magic, moddate = f.read(4), f.read(4)
        assert magic == imp.get_magic()
        modtime = time.asctime(time.localtime(struct.unpack('=L', moddate)[0]))
        code = marshal.load(f)
        pyc_info = {}
        pyc_info['bytecode'] = byteplay.Code.from_code(code)
        bytecode_list = [(a,b) for a,b in pyc_info['bytecode'].code \
            if a != byteplay.SetLineno]
        if [1 for a,b in bytecode_list if isinstance(b, basestring) \
            and b == 'raw_input']:
            print >> sys.stderr, \
                '[IGNORE] raw_input() found in module %s...'%(GLOBALS['pkg_path'])
            return None
        pyc_info['module_imports'] \
            = [import_name for a,import_name in bytecode_list \
                if a == byteplay.IMPORT_NAME]

        module, PYTHONPATH = None, None
        sys.stdout = StringIO()
        tries, MAX_TRIES, module = 0, 3, None
        while tries < MAX_TRIES:
            try:
                module = imp.load_compiled(GLOBALS['module_name'], GLOBALS['pkg_path'])
            except ImportError as e:
                re_msg = '^No module named (.*)$'
                re_vars = re.split(re_msg, e.message)[1:-1]
                rel_pkg_path = ''.join(re_vars).split('.')
                start = len(GLOBALS['pkg_path'].split('/'))
                for i, p in enumerate(GLOBALS['pkg_path'].split('/')[::-1]):
                    if p == rel_pkg_path[0]:
                        start -= i + 1
                        break
                PYTHONPATH = '/'.join(GLOBALS['pkg_path'].split('/')[:start])
                sys.path.append(PYTHONPATH)
            else:
                break
            tries += 1
        sys.stdout = sys.__stdout__
        if module:
            return PYTHONPATH
        else:
            print >> sys.stderr, \
                '[IGNORE] failed to load module %s@%s...' % \
                    (GLOBALS['module_name'], GLOBALS['pkg_path'])
            return None

def main(GLOBALS):
    valid = False
    if len(sys.argv) >= 2:
        package = sys.argv[1]
        path = os.path.abspath(package)
        if os.path.isfile(path):
            dirname, filename = os.path.split(path)
            pkg_name, ext     = os.path.splitext(filename)
#            if ext.endswith('.py'):
#                compileall.compile_file(path, force=True, quiet=True)
#                package += 'c'  # .py -> .pyc
#                path    += 'c'
#            if ext.endswith('.py') or ext.endswith('.pyc'):
            if ext.endswith('.pyc'):
                GLOBALS['pkg_path'] = path
                GLOBALS['pkg_type'] = 'bytecode'
                GLOBALS['pkg_name'] = pkg_name
                GLOBALS['module_name'] = os.path.basename(package).split('.')[-2]
                GLOBALS['base_import_dir'] = get_base_import_dir(GLOBALS, 'bytecode')
                valid = True
        elif os.path.isdir(path):
            # sanitise - strip trailing '/'
            if package.endswith('/'):   package = package[:-1]
            GLOBALS['pkg_path'] = path
            GLOBALS['pkg_type'] = 'directory'
            GLOBALS['pkg_name'] = package.split('/')[-1]
            GLOBALS['base_import_dir'] = get_base_import_dir(GLOBALS, 'directory')
            valid = True
    return valid
