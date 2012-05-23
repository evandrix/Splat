"""Run web-based app locally"""

from __future__ import generators
import sys, webbrowser
from cStringIO import StringIO
from peak.api import *
from peak.net.interfaces import IListeningSocket
import socket

from peak.util.WSGIServer import WSGIServer, WSGIRequestHandler

class Handler(WSGIRequestHandler):

    def log_message(self,format,*args):
        self.server.log.info(format,*args)

    def dump_to_stderr(self,text):
        if text:
            self.server.stderr.write(text)






















class WSGIServer(commands.EventDriven, WSGIServer):

    cgiCommand = binding.Require(
        "IRerunnableCGI to invoke on each hit", adaptTo = running.IRerunnableCGI
    )

    fileno  = binding.Delegate('socket')
    runInBrowser        = False   
    RequestHandlerClass = Handler

    socketURL = binding.Obtain(
        PropertyName('peak.tools.server.url'), default='tcp://localhost:0'
    )

    socket = binding.Obtain(
        naming.Indirect('socketURL'), adaptTo=IListeningSocket
    )

    socket_address = binding.Make(lambda self: self.socket.getsockname())

    server_name = binding.Make(
        lambda self: socket.getfqdn(self.socket_address[0])
    )

    server_port = binding.Make(
        lambda self: self.socket_address[1]
    )

    _getEnv = binding.Make(lambda self: self.setup_environ(), uponAssembly=True)

    def startBrowser(self,new=False,autoraise=True):
        import webbrowser
        if self.server_port<>80:
            port=':%d' % self.server_port
        else:
            port=''
        webbrowser.open("http://%s%s/" % (self.server_name,port),new,autoraise)

    def get_service(self):
        return self.cgiCommand

    eventLoop = binding.Obtain(events.IEventLoop)

    def serve_requests(self):

        yield self.eventLoop.sleep(); events.resume()

        if self.runInBrowser:
            self.startBrowser(True)

        while True:
            yield self.eventLoop.readable(self); events.resume()
            self.handle_request()

    serve_requests = binding.Make(
        events.taskFactory(serve_requests),uponAssembly=True
    )

    log = binding.Obtain('logger:tools.local_server')


class WSGILauncher(WSGIServer):

    runInBrowser = True


class Serve(commands.CGIInterpreter):

    usage = """
Usage: peak serve NAME_OR_URL arguments...

Run NAME_OR_URL as a CGI application in a local webserver on the port specified
by the 'peak.tools.server.url' property.  The object found at the specified
name or URL will be adapted to 'running.IRerunnableCGI' interface, and then
run in a local web server.
"""

    cgiWrapper = WSGIServer




class Launch(commands.CGIInterpreter):

    usage = """
Usage: peak launch NAME_OR_URL arguments...

Run NAME_OR_URL as a CGI application in a local webserver on the port specified
by the 'peak.tools.server.url' property.  The object found at the specified
name or URL will be adapted to 'running.IRerunnableCGI' interface, and then
run in a local web server.

This command is similar to the 'peak serve' command, except that it also
attempts to open the application in a web browser window.
"""

    cgiWrapper = WSGILauncher


class DemoService(binding.Component):

    protocols.advise(
        instancesProvide=[running.IRerunnableCGI]
    )

    def runCGI(self,stdin,stdout,stderr,environ):
        print >>stdout, "Content-type: text/plain"
        print >>stdout
        print >>stdout, "Hello world!"
        print >>stdout
        h = environ.items(); h.sort()
        for k,v in h:
            print >>stdout, k,'=',`v`


if __name__ == '__main__':
    WSGIServer(config.makeRoot(), cgiCommand=DemoService()).run()






