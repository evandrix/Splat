"""Setup script prologue - set up functions and constants"""

from distutils.core import Extension
from os.path import join, walk, normpath
from os import sep
import fnmatch

try:
    import Pyrex.Distutils
    EXT = '.pyx'

except ImportError:
    EXT = '.c'


def findDataFiles(dir, skipDepth, *globs):

    def visit(out, dirname, names):
	n = []
        for pat in globs:
            n.extend(fnmatch.filter(names,pat))
        if n:
            instdir = sep.join(dirname.split(sep)[skipDepth:])
            out.append( (instdir, [join(dirname,f) for f in n]) )

    out = []
    walk(normpath(dir),visit,out)
    return out














