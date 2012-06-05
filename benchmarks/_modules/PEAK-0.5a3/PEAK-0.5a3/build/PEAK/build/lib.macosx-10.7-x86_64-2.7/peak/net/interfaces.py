"""Interfaces, constants, property names, etc. for peak.net"""

from protocols import Interface, Attribute, declareImplementation
from peak.util.imports import whenImported

__all__ = [
    'IClientSocketAddr', 'IClientSocket',
    'IListenSocketAddr', 'IListeningSocket'
]


class IClientSocket(Interface):
    """XXX See python socket module for methods of a socket"""


class IListeningSocket(Interface):
    """XXX See python socket module for methods of a socket
    Note that this socket has been listen()'d"""


whenImported(
    # If sockets are used, declare that they implement the socket interfaces
    'socket',
    lambda socket:
        declareImplementation(
            socket.socket,
            instancesProvide=[IClientSocket,IListeningSocket]
        )
)












class IClientSocketAddr(Interface):
    """An address that can specify a client socket connection"""

    def connect_addrs(self):
        """return a list of tuples, a'la socket.getaddrinfo(), that
        the caller may attempt to create sockets with and connect on"""


class IListenSocketAddr(Interface):
    """An address that can specify sockets to listen on"""

    def listen_addrs(self):
        """return a list of tuples, a'la socket.getaddrinfo(), that
        the caller may attempt to create listening sockets on"""



























