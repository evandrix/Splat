import sys
import os
import re
import compileall

def main(GLOBALS):
    valid = False
    if len(sys.argv) >= 2:
        package = sys.argv[1]
        if os.path.isfile(os.path.abspath(package)):
            pkg_name, ext = os.path.splitext(package)
            if ext.endswith('.py'):
                compileall.compile_file(os.path.abspath(package), force=True, quiet=True)
                package += 'c'  # .py -> .pyc
            if ext.endswith('.py') or ext.endswith('.pyc'):
                GLOBALS['pkg_path'] = package
                GLOBALS['pkg_type'] = 'bytecode'
                GLOBALS['pkg_name'] = pkg_name
                GLOBALS['module_name'] = os.path.basename(package).split('.')[-2]
                valid = True
        elif os.path.isdir(os.path.abspath(package)):
            # sanitise - strip trailing '/'
            if package.endswith('/'):   package = package[:-1]
            GLOBALS['pkg_path'] = package
            GLOBALS['pkg_type'] = 'directory'
            GLOBALS['pkg_name'] = package.split('/')[-1]
            valid = True
    return valid

