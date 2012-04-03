"""Obtain bytes of random data with varying degrees of quality,
using OS facilities for high-quality entropy if available."""

__all__ = ['randbytes', 'rand16']


import sys, os, time
from whrandom import random
seeded = 0

try:
    import posix
except:
    posix = None

try:
    from sha import sha as hashfunc
except:
    from md5 import md5 as hashfunc






















lasthash = seedhash = ''

def prng_some():
    global lasthash

    try:
        import socket
        hn = socket.gethostname()
    except:
        hn = random()

    try:
        p = os.getpid()
    except:
        p = random()

    r = random()

    s = "%s%s%s%s%s" % (p, time.time(), id(time), id(os), lasthash)
    s = "%s%s%s%s%s" % (s, sys.version, sys.byteorder, hn, seedhash)
    s = "%s%s%s%s%s" % (s, sys.getrefcount(None), id(None), id(r), id(p))
    s = "%s%s%s%s%s" % (s, id(time.time()), id(s), id(hn), r)

    lasthash = s = hashfunc(s).digest()

    return s


# Seed the PRNG
prng_some()
seedhash = prng_some()
prng_some()









def prng(nbytes):
    """
    A PRNG that hopefully is better than just using whrandom.
    Don't trust this for crypto, though!
    """

    b = prng_some()
    while len(b) < nbytes:
        b += prng_some()

    return b[:nbytes]


def fail(nbytes):
    return None


def devrandom(nbytes):
    try:
        f = open('/dev/random', 'r')
        s = f.read(nbytes)
        f.close()
        return s
    except:
        return None


def devurandom(nbytes):
    try:
        f = open('/dev/urandom', 'r')
        s = f.read(nbytes)
        f.close()
        return s
    except:
        return None






funcs = {
    #(prng, wait) : function

    (0, 0) : fail,
    (0, 1) : fail,
    (1, 0) : prng,
    (1, 1) : prng,
}


# Use Unix versions if possible
if sys.platform != 'win32' and posix is not None:
    # let's see if there's a /dev/random...
    try:
        f = open('/dev/random', 'r')
        f.close()
        funcs[0, 1] = devrandom
        funcs[1, 0] = devurandom
        funcs[1, 1] = devrandom
    except:
        pass


# Does windows have an API to get at hardware RNG? If you can get at one
# through python, it should be added here. XXX
















def randbytes(nbytes, prng=1, wait=0):
    """
    Get nbytes number of bytes of randomness if possible.

    If prng is true, pseudo-randomly generated data of unknown quality
    is OK.  If false, only crypto-quality entropy is acceptable.

    If wait is true, caller is willing to wait an unspecified period of time
    in exchange for better quality randomness. If false, return the best
    randomness presently available.

    If the constraints cannot be met, return None.
    """

    return funcs[prng, wait](nbytes)



def rand16(prng=1, wait=0):
    """16 bit unsigned random number"""

    s = randbytes(2, prng, wait)
    return (ord(s[0]) << 8) | ord(s[1])


















