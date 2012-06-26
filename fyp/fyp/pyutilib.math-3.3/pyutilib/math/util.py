#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

__all__ = ['approx_equal', 'as_number', 'isint', 'argmax', 'argmin', 'mean', 'median', 'factorial', 'perm']

try:
    from itertools import izip
except:
    # 3.x compatibility
    izip = zip
    xrange = range
    basestring = unicode = str
import math
import sys


def approx_equal(A, B, abstol, reltol):
    if abstol is None:
        abstol = 1e-8
    if reltol is None:
        reltol = 1e-8
    if math.fabs(A-B) <= abstol:
        return True
    if math.fabs(B) > math.fabs(A):
        relError = math.fabs((A-B) // B)
    else:
        relError = math.fabs((A-B) // A)
    if relError <= reltol:
        return True
    return False


def as_number(value):
    if type(value) in [int, float, long]:
        return value
    if isinstance(value,basestring):
        try:
            tmp = int(value)
            return tmp
        except ValueError:
            pass
        try:
            tmp = long(value)
            return tmp
        except ValueError:
            pass
        try:
            tmp = float(value)
            return tmp
        except ValueError:
            pass
    return value


def isint(arg):
    """
    Returns true if the argument is an integer
    """
    if type(arg) is int:
        return True
    if type(arg) is float:
        tmp = int(arg)
        return (tmp == arg)
    if isinstance(arg,basestring):
        try:
            num=float(arg)
            tmp = int(num)
            return (tmp == num)
        except ValueError:
            return False
    return False


def argmax(array):
    """ Return the index to the maximum element of an array """
    return max(izip(array, xrange(len(array))))[1]

def argmin(array):
    """ Return the index to the maximum element of an array """
    return min(izip(array, xrange(len(array))))[1]

def mean(mylist):
    """
    Returns the mean value of a list
    """
    total = 1.0*sum(mylist)
    length = len(mylist)
    if length == 0.0:
        raise ArithmeticError("Attempting to compute the mean of a zero-length list")
    return (total/length)


if sys.version_info < (3,0):
    from pyutilib.math.median2 import median
else:
    from pyutilib.math.median3 import median


def factorial(z):
    """
    Computes z!
    """
    if z<0:
        raise ArithmeticError("Cannot compute the factorial of a negative number")
    if z==0:
        return 1
    else:
        return z*factorial(z-1)


def perm(x,y):
    """
    Computes 'x choose y'
    """
    w = 1
    for i in range(y+1,x+1):
        w = w * i
    return w/factorial(x-y)
