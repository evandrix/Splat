"""BaseHTTPServer that implements the Python WSGI protocol

This is both an example of how WSGI can be implemented, and a basis for running
simple web applications on a local machine.  It has not been reviewed for
security issues, however, and we strongly recommend that you use a "real"
web server for production use, even on a local system."""

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import urllib, sys
from cStringIO import StringIO
__version__ = "0.1"
__all__ = ['WSGIServer','WSGIRequestHandler','DemoService']


class WSGIServer(HTTPServer):

    """BaseHTTPServer that implements the Python WSGI protocol"""

    service = None

    def server_bind(self):
        """Override server_bind to store the server name."""
        HTTPServer.server_bind(self)
        self.setup_environ()

    def setup_environ(self):
        # Set up base environment
        env = self.base_environ = {}
        env['SERVER_NAME'] = self.server_name
        env['GATEWAY_INTERFACE'] = 'CGI/1.1'
        env['SERVER_PORT'] = str(self.server_port)
        env['REMOTE_HOST']=''
        env['CONTENT_LENGTH']=''

    def get_service(self):
        return self.service

    def set_service(self,service):
        self.service = service


class WSGIRequestHandler(BaseHTTPRequestHandler):

    server_version = "WSGIServer/" + __version__

    def get_environ(self):

        env = self.server.base_environ.copy()

        env['SERVER_SOFTWARE'] = self.version_string()
        env['SERVER_PROTOCOL'] = self.protocol_version
        env['REQUEST_METHOD'] = self.command

        if '?' in self.path:
            path,query = self.path.split('?',1)
        else:
            path,query = self.path,''

        env['PATH_INFO'] = urllib.unquote(path)
        env['QUERY_STRING'] = query

        # XXX env['PATH_TRANSLATED'] = self.translate_path(uqrest)

        env['SCRIPT_NAME'] = '/'
        host = self.address_string()
        if host != self.client_address[0]:
            env['REMOTE_HOST'] = host
        env['REMOTE_ADDR'] = self.client_address[0]

        # XXX AUTH_TYPE
        # XXX REMOTE_USER
        # XXX REMOTE_IDENT

        if self.headers.typeheader is None:
            env['CONTENT_TYPE'] = self.headers.type
        else:
            env['CONTENT_TYPE'] = self.headers.typeheader

        length = self.headers.getheader('content-length')
        if length:
            env['CONTENT_LENGTH'] = length

        for h in self.headers.headers:
            k,v = h.split(':',1)
            k=k.replace('-','_').upper()
            v=v.strip()
            if k in env:
                continue                    # skip content length, type,etc.
            if 'HTTP_'+k in env:
                env['HTTP_'+k] += ','+v     # comma-separate multiple headers
            else:
                env['HTTP_'+k] = v

        env.setdefault('HTTP_USER_AGENT','')
        env.setdefault('HTTP_COOKIE','')

        return env


























    def handle(self):
        """Handle a single HTTP request"""

        self.raw_requestline = self.rfile.readline()
        if not self.parse_request(): # An error code has been sent, just exit
            return

        stdout = StringIO()
        stderr = StringIO()
        env = self.get_environ()
        host = env['HTTP_HOST']
        self.server.get_service().runCGI(self.rfile,stdout,stderr,env)
        self.dump_to_stderr(stderr.getvalue())

        # Parse headers output by the script
        stdout.reset()
        headers = self.MessageClass(stdout, 0)

        if headers.has_key('location'):
            default_status = '302 Moved'
            location = headers['location']
            if location.startswith('/'):
                headers['location'] = host+location+'\r\n'
        else:
            default_status = '200 OK'

        status = headers.setdefault('status',default_status).strip()
        code,reason = status.split(' ',1)
        self.send_response(int(code), reason)
        del headers['status']

        self.wfile.writelines(headers.headers)
        self.wfile.write('\r\n')
        self.wfile.write(stdout.read())

    def dump_to_stderr(self,text):
        if text:
            sys.stderr.write(text)



class DemoService:

    def runCGI(self,stdin,stdout,stderr,environ):
        print >>stdout, "Content-type: text/plain"
        print >>stdout
        print >>stdout, "Hello world!"
        print >>stdout
        h = environ.items(); h.sort()
        for k,v in h:
            print >>stdout, k,'=',`v`


if __name__ == '__main__':
    server_address = ('', 8000)
    httpd = WSGIServer(server_address, WSGIRequestHandler)
    httpd.set_service(DemoService())
    sa = httpd.socket.getsockname()
    print "Serving HTTP on", sa[0], "port", sa[1], "..."
    import webbrowser
    webbrowser.open('http://localhost:8000/xyz?abc')
    httpd.handle_request()  # serve one request, then exit




















