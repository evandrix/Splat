"""Threading-related utilities

    This module provides a degree of platform independence for thread support.
    At the moment, it only really provides conditional 'allocate_lock()' and
    'get_ident()' functions, but other API's may be added in the future.

    By default, this module will use thread support if it is available.  You
    can override this, however, by using the 'disableThreading()',
    'allowThreading()', or 'requireThreading()' API function, preferably at the
    start of your program before any other modules have a chance to use any
    of this module's APIs.
"""

__all__ = [
    'allocate_lock', 'get_ident', 'DummyLock', 'RLock', 'ResourceManager',
    'allowThreading', 'disableThreading', 'requireThreading',
    'HAVE_THREADS', 'globalRM',
]

try:
    import thread
except ImportError:
    HAVE_THREADS = False
else:
    HAVE_THREADS = True


# default is to 'allowThreading'

USE_THREADS = HAVE_THREADS


if HAVE_THREADS:
    from thread import get_ident
else:
    def get_ident(): return 1





def allowThreading():

    """Enable the use of real thread locks, if possible"""

    global USE_THREADS
    USE_THREADS = HAVE_THREADS


def disableThreading():

    """Don't use threads, even if we have them.

    Note that this must be called *before* any locks have been allocated, as it
    only affects subsequent allocations."""

    global USE_THREADS
    USE_THREADS = False


def requireThreading():

    """Raise RuntimeError if threads aren't available; otherwise enable them"""

    if not HAVE_THREADS:
        raise RuntimeError, "Threads required but not available"

    self.allowThreading()


def allocate_lock():

    """Returns either a real or dummy thread lock, depending on availability"""

    if USE_THREADS:
        return thread.allocate_lock()

    else:
        return DummyLock()



class DummyLock(object):

    """Dummy lock type used when threads are inactive or unavailable"""

    __slots__ = ['_lockCount']

    def __init__(self):
        self._lockCount = 0


    def acquire(self, *waitflag):

        lc = self._lockCount = self._lockCount + 1

        if lc==1:
            if waitflag:
                # an argument was supplied, return success
                return 1
            else:
                # no argument, just return None
                return None

        else:
            self._lockCount -= 1

            if waitflag and not waitflag[0]:
                # no-wait; unlock/return failure
                return 0

            raise RunTimeError(
                "Attempt to double-lock a lock in a single-threaded program"
            )


    def release(self):
        self._lockCount -= 1

    def locked(self):
        return self._lockCount and True or False


class RLock(object):

    """Re-entrant lock; can be locked multiple times by same thread"""

    __slots__ = 'lock','owner','count'

    def __init__(self):
        self.lock  = allocate_lock()
        self.owner = 0
        self.count = 0

    def attempt(self):
        """Nonblocking, nestable attempt to acquire; returns success flag"""
        return self._doAcquire(False)

    def obtain(self):
        """Blocking, nestable wait to acquire; success unless error"""
        return self._doAcquire(True)

    def release(self):
        """Release one level of lock nesting; must be 'locked()' when called"""

        me = get_ident()

        if self.owner <> me:
            raise RuntimeError, "release() of un-acquire()d lock"

        count = self.count = self.count - 1

        if count==0:
            self.owner = 0
            self.lock.release()

    def locked(self):
        """Is this lock owned by the current thread?"""
        return self.owner==get_ident() and self.count>0





    def _doAcquire(self, blocking):

        me = get_ident()

        if self.owner == me:
            self.count += 1
            return True

        if blocking:
            self.lock.acquire(); rc = True
        else:
            rc = self.lock.acquire(blocking)

        if rc:
            self.owner = me
            self.count = 1

        return rc























class ResourceManager(object):

    """Hold/manage thread locks for arbitrary resource keys"""

    __slots__ = 'locks', 'lock'

    def __init__(self):
        self.locks = {}
        self.lock  = allocate_lock()

    def attempt(self, key):
        """Nonblocking, nestable attempt to acquire; returns success flag"""
        return self[key].attempt()

    def obtain(self, key):
        """Blocking, nestable wait to acquire; success unless error"""
        return self[key].obtain()

    def release(self, key):
        """Release one level of locking; key must be 'locked()' when called"""
        return self[key].release()

    def locked(self, key):
        """Is this key owned by the current thread?"""
        return self[key].locked()

    def __getitem__(self, key):
        self.lock.acquire()
        try:
            try:
                return self.locks[key]
            except KeyError:
                rlock = self.locks[key] = RLock()
                return rlock
        finally:
            self.lock.release()


globalRM = ResourceManager()


