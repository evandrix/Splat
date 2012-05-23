from unittest import TestCase, makeSuite, TestSuite
import peak.util.mockets as mockets
import errno


class SystemTests(TestCase):

    def setUp(self):
        self.ss = mockets.SocketSystem()

    def testMakeSocket(self):
        ss = self.ss
        sock = ss.socket(ss.AF_INET, ss.SOCK_STREAM)




























class SocketTests(TestCase):

    addr = ('localhost',80)

    def setUp(self):
        self.ss = mockets.SocketSystem()
        self.sock = self.makeSock()

    def makeSock(self):
        return self.ss.socket(self.ss.AF_INET, self.ss.SOCK_STREAM)

    def testFileno(self):
        ss = self.ss
        self.failUnless(isinstance(self.sock.fileno(),int))
        sock2 = ss.socket(ss.AF_INET, ss.SOCK_STREAM)
        self.failUnless(isinstance(sock2.fileno(),int))
        self.assertNotEqual(self.sock.fileno(), sock2.fileno())

    def testBindAndName(self):
        sock = self.sock
        sock.bind(self.addr)
        self.assertEqual(sock.getsockname(), self.addr)
        self.assertRaises(self.ss.error, sock.bind, self.addr)

    def testNoNameBeforeBind(self):
        # This is actually win32 behavior; on Unix an unbound AF_INET socket
        # has an address of '("0.0.0.0",0)'.  But this is lowest denominator.
        self.assertRaises(self.ss.error, self.sock.getsockname)

    def testNoPeerBeforeConnect(self):
        self.assertRaises(self.ss.error, self.sock.getpeername)

    def testSetBlocking(self):
        self.sock.setblocking(0)
        self.sock.setblocking(1)

    def testConnectFailures(self):
        self.assertRaises(self.ss.error, self.sock.connect, self.addr)
        self.assertEqual(self.sock.connect_ex(self.addr), errno.ECONNREFUSED)


    def testListen(self):
        # On unix, a socket is always bound, even if to 0.0.0.0, but on windows
        # listening on an unbound socket fails
        self.assertRaises(self.ss.error, self.sock.listen, 5)
        self.sock.bind(self.addr)
        self.sock.listen(5)


    def testAcceptFailures(self):
        # No accept before listen, regardless of platform
        self.assertRaises(self.ss.error, self.sock.accept)
        self.sock.bind(self.addr)
        self.assertRaises(self.ss.error, self.sock.accept)
        self.sock.listen(1)
        self.sock.setblocking(0)
        self.assertRaises(self.ss.error, self.sock.accept)
        self.sock.setblocking(1)
        self.assertRaises(mockets.WouldBlock, self.sock.accept)

    def makeListener(self):
        listener = self.makeSock()
        listener.bind(self.addr)
        listener.listen(5)
        return listener

    def connect(self):
        self.sock.setblocking(0)
        result = self.sock.connect_ex(self.addr)
        self.failUnless(result in [0,errno.EWOULDBLOCK,errno.EINPROGRESS])

    def testConnectSuccess(self):
        listener = self.makeListener()
        self.connect()
        conn, peer = listener.accept()
        self.assertEqual(peer, self.sock.getsockname())
        self.assertEqual(conn.getsockname(), self.sock.getpeername())
        self.assertEqual(conn.getpeername(), self.sock.getsockname())




    def testRWConditions(self):
        listener = self.makeListener()
        self.failIf(listener.readable() or listener.writable())
        self.connect()
        self.failIf(self.sock.readable() or self.sock.writable())
        self.failUnless(listener.readable())
        conn, peer = listener.accept()
        self.failUnless(conn.writable() and not conn.readable())
        self.failUnless(self.sock.writable() and not self.sock.readable())
        msg = 'Welcome!\n'
        sent = conn.send(msg)
        self.assertEqual(sent,len(msg))
        self.failUnless(self.sock.writable() and self.sock.readable())
        recvd = self.sock.recv(sent)
        self.assertEqual(recvd,msg)
        self.failUnless(self.sock.writable() and not self.sock.readable())


    def testSendReceive(self):
        listener = self.makeListener()
        client = self.sock
        client.setblocking(0)
        self.assertRaises(self.ss.error,client.send,'test')
        self.connect()
        server, addr = listener.accept()
        client.send('test')
        self.assertEqual(server.recv(2),'te')
        self.assertEqual(server.recv(2),'st')
        self.assertRaises(mockets.WouldBlock, server.recv, 2)
        sent = server.send('test1')
        self.assertEqual(sent,5)
        sent = server.send('test2')
        self.assertEqual(sent,0)
        self.assertRaises(mockets.WouldBlock, server.sendall, 'test2')
        self.assertEqual(client.recv(5),'test1')
        self.assertRaises(self.ss.error, client.recv,5)     # nonblocking client
        sent = server.send('test3')
        self.assertEqual(sent,5)
        self.assertEqual(client.recv(5),'test3')


    def makeClientServer(self):
        listener = self.makeListener()
        client = self.sock
        client.setblocking(0)
        result = client.connect_ex(self.addr)
        server, addr = listener.accept()
        return client,server

    def testClose(self):
        c,s = self.makeClientServer()
        c.close()
        self.assertRaises(self.ss.error, s.send, 'x')
        self.assertEqual(s.recv(1), '')
        s.close()
        self.assertRaises(self.ss.error, s.send, 'x')
        self.assertRaises(self.ss.error, s.recv, 1)

    def testSelect(self):
        c,s = self.makeClientServer()
        r = [c.fileno(),s]; w = [c,s.fileno()]; e = [c,s]

        self.assertEqual(self.ss.select(r,w,e,0), ([],w,[]))
        c.send('test')
        self.assertEqual(self.ss.select(r,w,e,0), ([s],[s.fileno()],[]))
        s.recv(4)
        self.assertEqual(self.ss.select(r,w,e,0), ([],[c,s.fileno()],[]))
        s.send('test')
        self.assertEqual(self.ss.select(r,w,e,0), ([c.fileno()],[c],[]))
        c.recv(4)
        self.assertEqual(self.ss.select(r,w,e,0), ([],w,[]))

        c.close()
        self.assertEqual(self.ss.select([s],[s],[s],0), ([s],[],[]))
        self.assertRaises(self.ss.error, self.ss.select, [c],[],[])
        self.assertRaises(self.ss.error, self.ss.select, [],[c],[])
        self.assertRaises(self.ss.error, self.ss.select, [],[],[c])





    def testSelectTimeouts(self):
        self.assertRaises(mockets.WouldBlock, self.ss.select, [],[],[])
        self.assertEqual(self.ss.select([],[],[],1), ([],[],[]))
        self.assertEqual(self.ss.select([],[],[],0), ([],[],[]))

    def testConnectFailAfterClosedListener(self):
        listener = self.makeListener()
        listener.close()
        self.sock.setblocking(0)
        self.assertEqual(self.sock.connect_ex(self.addr), errno.ECONNREFUSED)

    def testAcceptAfterClosedClient(self):
        listener = self.makeListener()
        self.connect()
        self.sock.close()
        server,addr = listener.accept()
        self.assertEqual(server.recv(1),'')
        























TestClasses = (
    SystemTests, SocketTests,
)

def test_suite():
    return TestSuite([makeSuite(t,'test') for t in TestClasses])



































