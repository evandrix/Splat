"""Lockfiles for inter-process communication

    These are used for synchronization between processes, unlike
    thread.LockType locks.  The common use is non-blocking lock attempts.
    For convenience and in order to reduce confusion with the (somewhat odd)
    thread lock interface, these locks have a different interface.

    attempt()   try to obtain the lock, return boolean success
    obtain()    wait to obtain the lock, returns None
    release()   release an obtained lock, returns None
    locked()    returns True if any thread IN THIS PROCESS
                has obtained the lock, else False

    In general, you should assume that only the 'LockFile' class will be
    available.  Only use a more-specific lockfile type if you have need
    of compatibility with non-PEAK software that uses that special type
    of lockfile.  (In practice, this means that the only time you'll ever
    use anything other than the generic 'LockFile' class is if you need
    to work with something on a Unix-like platform that uses the equivalent
    of 'FLockFile', as 'SHLockFile' is the default implementation of 'LockFile'
    on Unix-like platforms.)

    Currently, only Unix-ish and Windows platforms supported; if your platform
    isn't supported, not even the 'LockFile' class will be available from this
    module.  For Windows, the 'msvcrt' module must be available (it is in the
    standard Python 2.2.1 binary distribution for Windows).

    This module also exports a 'NullLockFile' class, for use when locking is
    not needed, but an object with a locking interface is nonetheless required.
    'NullLockFile' can also be used as a substitute for a thread lock, if you
    prefer this locking interface over the standard Python one.
"""

__all__ = ['LockFile', 'NullLockFile']

import os, errno, time
from peak.util.threads import allocate_lock
from peak.api import naming, protocols
from interfaces import ILock


class LockFileBase:
    """Common base for lockfiles"""

    protocols.advise(
        instancesProvide=[ILock], classProvides = [naming.IObjectFactory]
    )

    def __init__(self, fn):
        self.fn = os.path.abspath(fn)
        self._lock = allocate_lock()
        self._locked = False

    def attempt(self):
        if self._lock.acquire(False):
            r = False
            try:
                r = self.do_acquire(False)
            finally:
                if not r and self._lock.locked():
                    self._lock.release()
            return r
        else:
            return False

    def obtain(self):
        self._lock.acquire()
        r = False
        try:
            r = self.do_acquire(True)
        finally:
            if not r and self._lock.locked():
                self._lock.release()
        if not r:
            raise RuntimeError, "lock obtain shouldn't fail!"

    def release(self):
        self.do_release()
        self._locked = False
        self._lock.release()


    def locked(self):
        return self._locked

    def getObjectInstance(klass,context,refInfo,name,attrs=None):
        url, = refInfo.addresses
        return klass(url.getFilename())

    getObjectInstance = classmethod(getObjectInstance)

































### Posix-y lockfiles ###

try:
    import posix
    from posix import O_EXCL, O_CREAT, O_RDWR
except ImportError:
    posix=None

try:
    import fcntl
except ImportError:
    fcntl = None

try:
    import msvcrt
except ImportError:
    msvcrt = None


def pid_exists(pid):
    """Is there a process with PID pid?"""
    if pid < 0:
        return False

    exist = False
    try:
        os.kill(pid, 0)
        exist = 1
    except OSError, x:
        if x.errno != errno.ESRCH:
            raise

    return exist








def check_lock(fn):

    """Check the validity of an existing lock file

    Reads the PID out of the lock and check if that process exists"""

    try:
        f = open(fn, 'r')
        pid = int(f.read().strip())
        f.close()
        return pid_exists(pid)
    except:
        raise
        return 1 # be conservative



def make_tempfile(fn, pid):

    tfn = os.path.join(os.path.dirname(fn), 'shlock%d' % pid)

    errcount = 1000
    while 1:
        try:
            fd = posix.open(tfn, O_EXCL | O_CREAT | O_RDWR, 0600)
            posix.write(fd, '%d\n' % pid)
            posix.close(fd)

            return tfn
        except OSError, x:
            if (errcount > 0) and (x.errno == errno.EEXIST):
                os.unlink(tfn)
                errcount = errcount - 1
            else:
                raise






class SHLockFile(LockFileBase):
    """HoneyDanBer/NNTP/shlock(1)-style locking

    Two bigs wins to this algorithm:

      o Locks do not survive crashes of either the system or the
        application by any appreciable period of time.

      o No clean up to do if the system or application crashes.

    Loses:

      o In the off chance that another process comes along with
        the same pid, we can get a false positive for lock validity.

      o Not compatible with NFS or any shared filesystem
        (due to disjoint PID spaces)

      o Waiting for lock must be implemented by polling"""

    def do_acquire(self, waitflag):
        if waitflag:
            sleep = 1
            locked = self.do_acquire(False)

            while not locked:
                time.sleep(sleep)
                sleep = min(sleep + 1, 15)
                locked = self.do_acquire(False)

            return locked

        else:
            tfn = make_tempfile(self.fn, os.getpid())
            while 1:
                try:
                    os.link(tfn,self.fn)
                    os.unlink(tfn)
                    self._locked = True
                    return True

                except OSError, x:
                    if x.errno == errno.EEXIST:
                        if check_lock(self.fn):
                            os.unlink(tfn)
                            self._locked = False
                            return False
                        else:
                            # nuke invalid lock file, and try to lock again
                            os.unlink(self.fn)
                    else:
                        os.unlink(tfn)
                        raise


    def do_release(self):
        os.unlink(self.fn)

























class FLockFile(LockFileBase):
    """
    flock(3)-based locks.

    Wins:

      o Locks do not survive crashes of either the system or the
        application.

      o Waiting for a lock is handled by the kernel and doesn't require
        polling

      o Potentially compatible with NFS or other shared filesystem
        _if_ you trust their lockd (or equivalent) implemenation.
        Note that this is a *big* if!

      o No false positives on stale locks

    Loses:

      o Leaves lockfiles around, since unlink would cause a race.
    """

    def do_acquire(self, waitflag=False):
        locked = False

        if waitflag:
            blockflag = 0
        else:
            blockflag = fcntl.LOCK_NB

        self.fd = posix.open(self.fn, O_CREAT | O_RDWR, 0600)
        try:
            fcntl.flock(self.fd, fcntl.LOCK_EX|blockflag)
            # locked it
            try:
                posix.ftruncate(self.fd, 0)
                posix.write(self.fd, `os.getpid()` + '\n')
                locked = True
            except:
                self.do_release()
                raise
        except IOError, x:
            if x.errno == errno.EWOULDBLOCK:
                # failed to lock
                posix.close(self.fd)
                del self.fd
            else:
                raise

        self._locked = locked

        return locked

    def do_release(self):
        posix.ftruncate(self.fd, 0)
        fcntl.flock(self.fd, fcntl.LOCK_UN)
        posix.close(self.fd)
        del self.fd























class WinFLockFile(LockFileBase):

    """Like FLockFile, but for Windows"""

    def do_acquire(self, waitflag=False):

        if waitflag:
            sleep = 1
            locked = self.do_acquire(False)

            while not locked:
                time.sleep(sleep)
                sleep = min(sleep + 1, 15)
                locked = self.do_acquire(False)
            return locked

        locked = False

        self.f = open(self.fn, 'a')
        try:
            msvcrt.locking(self.f.fileno(), msvcrt.LK_NBLCK, 1)
            try:
                self.f.write(`os.getpid()` + '\n')  # informational only
                self.f.seek(0)  # lock is at offset 0, so go back there
                locked = True
            except:
                self.do_release()
                raise

        except IOError, x:
            if x.errno == errno.EACCES:
                self.f.close()
                del self.f
            else:
                raise

        self._locked = locked
        return locked



    def do_release(self):
        msvcrt.locking(self.f.fileno(), msvcrt.LK_UNLCK, 1)
        self.f.close()
        del self.f



class NullLockFile(LockFileBase):

    """Pseudo-LockFile (locks only for threads in this process)"""

    def __init__(self):
        self._lock = allocate_lock()
        self._locked = False

    def do_acquire(self, waitflag=False):
        return True

    def do_release(self):
        pass

    def getObjectInstance(klass,context,refInfo,name,attrs=None):
        return klass()

    getObjectInstance = classmethod(getObjectInstance)
















# Default is shlock(1)-style if available

if posix:
    __all__.extend(['SHLockFile','FLockFile'])
    LockFile = SHLockFile
    del WinFLockFile

else:

    # don't need them and they won't work...
    del make_tempfile, check_lock, pid_exists

    if msvcrt:
        __all__.append('WinFLockFile')
        LockFile = WinFLockFile

    else:
        # Waaaaaaa!, as Jim F. would say...
        __all__.remove('LockFile')






















from peak.naming.factories.openable import FileURL

class lockfileURL(FileURL):

    supportedSchemes = {
        'lockfile': 'peak.running.lockfiles.LockFile',
        'shlockfile': 'peak.running.lockfiles.SHLockFile',
        'flockfile': 'peak.running.lockfiles.FLockFile',
        'winflockfile': 'peak.running.lockfiles.WinFLockFile',
        'nulllockfile': 'peak.running.lockfiles.NullLockFile',
    }

    defaultFactory = property(
        lambda self: self.supportedSchemes[self.scheme]
    )


























