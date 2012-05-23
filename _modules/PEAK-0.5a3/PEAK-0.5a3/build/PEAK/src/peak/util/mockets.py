"""Mock Sockets and related types, used for testing socket code

 Mockets currently only implement 'AF_INET' and 'SOCK_STREAM'.  They also don't
 support the 'getsockopt()', 'setsockopt()', 'recvfrom()', 'sendto()',
 'makefile()', or 'shutdown()' operations of real sockets, or the 'flags'
 argument to 'send()' or 'recv()'.  They don't support out of band data,
 exception conditions, or anything else whose implementation is too platform
 or protocol-dependent.

 Some of these limitations may be lifted later, e.g. 'SOCK_DGRAM',
 'recvfrom()', and 'sendto()', if/when we need to test things that use them.
 We should probably also at least support storing and retrieving options via
 the 'getsockopt()' and 'setsockopt()' methods, so that tests can verify
 whether code is setting options that should be set.

 Note that real sockets' 'shutdown()' and 'makefile()' behavior is *extremely*
 platform-dependent, to the point that we should simply avoid them altogether
 if possible.  In particular, 'shutdown()' on Windows seems to be seriously
 broken, and 'makefile()' on Windows, RISCOS, and BeOS is emulated with a
 crude simulation of a file that doesn't support most real file operations.

 TODO

  * Integrate into 'peak.events.tests' for testing un-Twisted selector

"""

import errno
from weakref import WeakValueDictionary

__all__ = ['WouldBlock', 'SocketSystem']

class WouldBlock(Exception):
    """Socket is in blocking mode, and operation would block"""







class SocketSystem:

    """A collection of socket objects that can connect to each other

    This object is effectively the "universe" of sockets and addresses, and
    provides replacements for 'select.select' and 'socket.socket'.
    """

    from socket import AF_INET, SOCK_STREAM, error     # XXX

    def __init__(self):
        self.listeners = WeakValueDictionary()
        self.selectables = WeakValueDictionary()

    def socket(self, family, type, proto=0):
        """Return a mock socket, ala 'socket.socket'"""
        if family<>self.AF_INET or type<>self.SOCK_STREAM or proto:
            raise NotImplementedError(
                "Unsupported mocket type:", (family,type,proto)
            )
        return MocketType(self)

    def sleep(self,secs):
        """Override in subclasses to implement/trap 'select()' delays"""
        pass


    def fixupAddress(self,addr):
        """Override in subclasses to validate addresses for bind and connect"""
        return addr











    def select(self,iwtd,owtd,ewtd,timeout=-1):

        def get_socket(ob):
            if hasattr(ob,'fileno'):
                fd=ob.fileno()
            else:
                fd=int(ob)
            if fd not in self.selectables:
                raise self.error(errno.EBADF, 'Bad file descriptor')
            return self.selectables[fd]

        r = w = []

        while True:
            r = [i for i in iwtd if get_socket(i).readable()]
            w = [o for o in owtd if get_socket(o).writable()]
            map(get_socket,ewtd)    # ensure error if invalid socket listed

            if r or w or timeout==0:
                break

            if timeout>0:
                self.sleep(timeout)
                timeout=0
            else:
                raise WouldBlock("Blocking select()",iwtd,owtd,timeout)

        return r,w,[]













class MocketType:

    """Emulation of a socket object"""

    addr = None
    blocking = 1
    backlog = None
    queue = None
    other = None
    recvd = ''
    _closed = False

    def __init__(self,system):
        self.system = system
        system.selectables[self.fileno()] = self

    def fileno(self):
        if self._closed:
            return -1
        return id(self)

    def bind(self,addr):
        self._checkOpen()
        if self.addr is not None:
            self._invalid()
        self.addr = self.system.fixupAddress(addr)

    def getsockname(self):
        self._checkOpen()
        if self.addr is None:
            self._invalid()
        return self.addr

    def getpeername(self):
        self._checkOpen()
        if self.other is not None:
            return self.other.getsockname()
        raise self.system.error(errno.ENOTCONN,
            'Transport endpoint is not connected'
        )

    def setblocking(self,blocking):
        self.blocking = blocking

    def connect(self,addr):
        self._checkOpen()
        other = self.system.listeners.get(self.system.fixupAddress(addr))
        if other is None:
            raise self.system.error(errno.ECONNREFUSED,"Connection refused")
        other._enqueue(self)
        self._wouldblock()  # Unix actually does EINPROGRESS here

    def connect_ex(self,addr):
        try:
            self.connect(addr)
        except self.system.error,v:
            return v.args[0]
        return 0

    def listen(self,backlog):
        self._checkOpen()
        if self.addr is None:
            self._invalid()
        self.backlog = backlog
        self.queue = []
        self.system.listeners[self.addr] = self

    def accept(self):
        self._checkOpen()
        if self.backlog is None:
            self._invalid()
        if self.queue:
            other = self.queue.pop(0)
            newsock = self.__class__(self.system)
            newsock.bind(self.addr)
            other._connected(newsock)
            newsock._connected(other)
            return newsock,other.addr
        self._wouldblock()



    def send(self,data,flags=0):
        self._checkConnected()
        if flags:
            raise NotImplementedError("No send flags allowed",self,flags)
        return self.other._recv(data)

    def recv(self,bufsize,flags=0):
        self._checkOpen()
        if flags:
            raise NotImplementedError("No receive flags allowed",self,flags)
        if self.recvd:
            data, self.recvd = self.recvd[:bufsize], self.recvd[bufsize:]
            return data
        if self.other and self.other._closed:
            # Emulate Unix behavior; Windows would raise ECONNRESET here
            return ''
        self._checkConnected()
        self._wouldblock()

    def sendall(self,data,flags=0):
        self._checkOpen()
        if self.writable():
            self.send(data,flags)
        else:
            self._wouldblock()

    def close(self):
        if not self._closed:
            if self.queue is not None:
                del self.system.listeners[self.addr]
            del self.system.selectables[self.fileno()]
            self._closed = True

    def readable(self):
        return self.queue or self.recvd or self.other and self.other._closed

    def writable(self):
        return self.other and not self.other._closed and not self.other.recvd



    def _invalid(self):
        raise self.system.error(errno.EINVAL, "Invalid argument")

    def _checkOpen(self):
        if self._closed:
            raise self.system.error(errno.EBADF, 'Bad file descriptor')

    def _checkConnected(self):
        self._checkOpen()
        if self.other is None:
            # Unix can do EPIPE here for write operations
            raise self.system.error(errno.ENOTCONN,'Socket is not connected')
        elif self.other._closed:
            raise self.system.error(errno.ECONNRESET,'Connection reset by peer')

    def _wouldblock(self):
        if self.blocking:
            raise WouldBlock("Blocking operation invoked", self)
        else:
            raise self.system.error(errno.EWOULDBLOCK,
                'Resource temporarily unavailable'
            )

    def _enqueue(self,incoming):
        if len(self.queue)>=self.backlog:
            incoming._wouldblock()
        self.queue.append(incoming)

    def _connected(self,other):
        self.other = other
        if self.addr is None:
            self.addr = 'localhost',id(self)

    def _recv(self,data):
        if not self.recvd:
            self.recvd = data
            return len(data)
        return 0



