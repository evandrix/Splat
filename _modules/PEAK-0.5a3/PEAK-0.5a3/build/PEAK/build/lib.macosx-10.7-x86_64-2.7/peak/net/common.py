from peak.api import *

class StreamProto(binding.Component):

    reactor = binding.Obtain(running.IBasicReactor)
    socket  = binding.Require("Socket to run the protocol on")
    bufsize = binding.Make(lambda: 2048)
    _fileno = binding.Make(lambda self: self.socket.fileno())
    _o_buf  = binding.Make(list)

    _writer_added = False


    def fileno(self):
        return self._fileno


    def doRead(self):
        d = self.socket.recv(self.bufsize)
        if not d:
            self.connectionLost()
        else:
            self.dataReceived(d)


    def connectionLost(self):
        self.socket.close()


    def dataReceived(self, data):
        pass


    def write(self, data):
        ob = self._o_buf
        ob.append(data)
        if ob and not self._writer_added:
            self._writer_added = True
            self.reactor.addWriter(self)


    def doWrite(self):
        ob = self._o_buf
        while ob:
            d = ob.pop(0)
            l = len(d)
            sl = self.socket.send(d)
            if sl < l:
                ob.insert(0, d[sl:])
                return

        if not ob and self._writer_added:
            self.reactor.removeWriter(self)
            self._writer_added = False
