import sys
from PyQt4 import QtGui, QtCore, QtNetwork

class Application(QtGui.QApplication):
    def __init__(self, argv, key):
        QtGui.QApplication.__init__(self, argv)
        self._memory = QtCore.QSharedMemory(self)
        self._memory.setKey(key)
        if self._memory.attach():
            self._running = True
        else:
            self._running = False
            if not self._memory.create(1):
                raise RuntimeError(
                    self._memory.errorString().toLocal8Bit().data())
        self._key = key
        self._timeout = 1000
        self._server = QtNetwork.QLocalServer(self)
        if not self.isRunning():
            self._server.newConnection.connect(self.handleMessage)
            self._server.listen(self._key)

    def isRunning(self):
        return self._running

    def handleMessage(self):
        socket = self._server.nextPendingConnection()
        if socket.waitForReadyRead(self._timeout):
            self.emit(QtCore.SIGNAL('messageAvailable'),
                      QtCore.QString.fromUtf8(socket.readAll().data()))
            socket.disconnectFromServer()
        else:
            QtCore.qDebug(socket.errorString().toLatin1())

    def sendMessage(self, message):
        if self.isRunning():
            socket = QtNetwork.QLocalSocket(self)
            socket.connectToServer(self._key, QtCore.QIODevice.WriteOnly)
            if not socket.waitForConnected(self._timeout):
                print >> sys.stderr, socket.errorString().toLocal8Bit().data()
                return False
            socket.write(unicode(message).encode('utf-8'))
            if not socket.waitForBytesWritten(self._timeout):
                print >> sys.stderr, socket.errorString().toLocal8Bit().data()
                return False
            socket.disconnectFromServer()
            return True
        return False
