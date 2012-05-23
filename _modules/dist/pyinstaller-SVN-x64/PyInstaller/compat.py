#! /usr/bin/env python
#
# Various classes and functions to provide some backwards-compatibility
# with previous versions of Python from 2.3 onward.
#
# Copyright (C) 2011, Martin Zibricky
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA

import os
import sys

try:
    import subprocess
except ImportError:
    # :todo: remove when dropping Python 2.3 compatibility
    # fall back to out version of `subprocess`
    import PyInstaller.lib.__subprocess as subprocess


is_py23 = sys.version_info >= (2, 3)
is_py24 = sys.version_info >= (2, 4)
is_py25 = sys.version_info >= (2, 5)
is_py26 = sys.version_info >= (2, 6)
is_py27 = sys.version_info >= (2, 7)

is_win = sys.platform.startswith('win')
is_cygwin = sys.platform == 'cygwin'
is_darwin = sys.platform == 'darwin'  # Mac OS X

# Unix platforms
is_linux = sys.platform == 'linux2'
is_solar = sys.platform.startswith('sun')  # Solaris
is_aix = sys.platform.startswith('aix')

# Some code parts are similar to several unix platforms
# (e.g. Linux, Solaris, AIX)
# Mac OS X is not considered as unix since there are many
# platform specific details for Mac in PyInstaller.
is_unix = is_linux or is_solar or is_aix


# Obsolete command line options (do not exist anymore)
_OLD_OPTIONS = ['--upx', '-X']


# Options for python interpreter when invoked in a subprocess.
_PYOPTS = __debug__ and '-O' or ''


try:
    # Python 2.5+
    import hashlib
except ImportError:
    class hashlib(object):
        from md5 import new as md5
        from sha import new as sha


# In Python 2.4+ there is a builtin type set(). In Python 2.3
# it is class Set in module sets.
try:
    from __builtin__ import set
except ImportError:
    from sets import Set as set


def architecture():
    """
    Returns the bit depth of the python interpreter's architecture as
    a string ('32bit' or '64bit'). Similar to platform.architecture(),
    but with fixes for universal binaries on MacOS.
    """
    import platform
    if is_darwin:
        # Darwin's platform.architecture() is buggy and always
        # returns "64bit" event for the 32bit version of Python's
        # universal binary. So we roll out our own (that works
        # on Darwin).
        if sys.maxint > 2L ** 32:
            return '64bit'
        else:
            return '32bit'
    else:
        return platform.architecture()[0]


def system():
    import platform
    # On some Windows installation (Python 2.4) platform.system() is
    # broken and incorrectly returns 'Microsoft' instead of 'Windows'.
    # http://mail.python.org/pipermail/patches/2007-June/022947.html
    syst = platform.system()
    if syst == 'Microsoft':
        return 'Windows'
    return syst


# Set and get environment variables does not handle unicode strings correctly
# on Windows.

# Acting on os.environ instead of using getenv()/setenv()/unsetenv(),
# as suggested in <http://docs.python.org/library/os.html#os.environ>:
# "Calling putenv() directly does not change os.environ, so it's
# better to modify os.environ." (Same for unsetenv.)

def getenv(name, default=None):
    """
    Returns unicode string containing value of environment variable 'name'.
    """
    return os.environ.get(name, default)


def setenv(name, value):
    """
    Accepts unicode string and set it as environment variable 'name' containing
    value 'value'.
    """
    os.environ[name] = value


def unsetenv(name):
    """
    Delete the environment variable 'name'.
    """
    # Some platforms (e.g. AIX) do not support `os.unsetenv()` and
    # thus `del os.environ[name]` has no effect onto the real
    # environment. For this case we set the value to the empty string.
    os.environ[name] = ""
    del os.environ[name]


# Exec commands in subprocesses.


def exec_command(*cmdargs):
    """
    Wrap creating subprocesses

    Return stdout of the invoked command.
    Todo: Use module `subprocess` if available, else `os.system()`
    """
    return subprocess.Popen(cmdargs, stdout=subprocess.PIPE).communicate()[0]


def exec_command_rc(*cmdargs, **kwargs):
    """
    Wrap creating subprocesses.

    Return exit code of the invoked command.
    Todo: Use module `subprocess` if available, else `os.system()`
    """
    return subprocess.call(cmdargs, **kwargs)


def __wrap_python(args, kwargs):
    cmdargs = [sys.executable]

    # Mac OS X supports universal binaries (binary for multiple architectures.
    # We need to ensure that subprocess binaries are running for the same
    # architecture as python executable.
    # It is necessary to run binaries with 'arch' command.
    if is_darwin:
        mapping = {'32bit': '-i386', '64bit': '-x86_64'}
        py_prefix = ['arch', mapping[architecture()]]
        cmdargs = py_prefix + cmdargs

    if _PYOPTS:
        cmdargs.append(_PYOPTS)

    cmdargs.extend(args)
    return cmdargs, kwargs


def exec_python(*args, **kwargs):
    """
    Wrap running python script in a subprocess.

    Return stdout of the invoked command.
    """
    cmdargs, kwargs = __wrap_python(args, kwargs)
    return exec_command(*cmdargs, **kwargs)


def exec_python_rc(*args, **kwargs):
    """
    Wrap running python script in a subprocess.

    Return exit code of the invoked command.
    """
    cmdargs, kwargs = __wrap_python(args, kwargs)
    return exec_command_rc(*cmdargs, **kwargs)


# Obsolete command line options.


def __obsolete_option(option, opt, value, parser):
    parser.error('%s option does not exist anymore (obsolete).' % opt)


def __add_obsolete_options(parser):
    """
    Add the obsolete options to a option-parser instance and
    print error message when they are present.
    """
    g = parser.add_option_group('Obsolete options (not used anymore)')
    g.add_option(*_OLD_OPTIONS,
                 **{'action': 'callback',
                    'callback': __obsolete_option,
                    'help': 'This option does not exist anymore.'})
