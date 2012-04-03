"""FastCGI support, using busy-start plugin"""

from peak.api import *
from interfaces import *
from peak.net.interfaces import IListeningSocket
from peak.running.commands import Bootstrap, AbstractInterpreter
from peak.running.process import AbstractProcessTemplate
from busy import BusyProxy, BusyStarter


class FCGITemplateCommand(AbstractInterpreter):

    """Command to process a socket URL + a FastCGI command to run on it"""

    def interpret(self, filename):

        stdin = self.lookupComponent(filename, adaptTo=IListeningSocket)

        return FastCGITemplate(
            stdin=stdin,
            command = self.getSubcommand(Bootstrap,stdin = stdin)
        )



















class FastCGITemplate(AbstractProcessTemplate):
    """Process template for FastCGI subprocess w/busy monitoring"""

    protocols.advise(
        instancesProvide=[running.IRerunnableCGI, ISupervisorPluginProvider]
    )

    proxyClass = BusyProxy
    readPipes  = ('busyStream',)

    socketURL = binding.Require("URL of TCP or Unix socket to listen on")

    command   = binding.Require(
        "IRerunnableCGI command to run in subprocess",
        adaptTo=running.IRerunnableCGI,
        uponAssembly=True   # force creation to occur in parent process
    )

    stdin = binding.Make(
        lambda self: self.lookupComponent(self.socketURL),
        adaptTo = IListeningSocket
    )

    def runCGI(self, *args):
        self.sendToParent('+')      # start being busy
        try:
            self.command.runCGI(*args)
        finally:
            self.sendToParent('-')  # finish being busy

    def _redirect(self):
        if self.stdin.fileno():
            self.os.dup2(self.stdin.fileno(),0)

    def _makeStub(self):
        from peak.running.commands import CGICommand
        return CGICommand(self, cgiCommand=self, stdin=self.stdin)

    def getSupervisorPlugins(self, supervisor):
        return [BusyStarter(supervisor, template=self, stream=self.stdin)]

    def sendToParent(self,s):
        """Write to parent; handle errors by stopping writes and reactor"""
        if self.busyStream is None:
            return
        try:
            self.busyStream.write(s)
        except IOError,v:
            import errno
            if v.errno==errno.EPIPE:    # parent went away, so we should leave
                self.busyStream = None
                self.lookupComponent(running.IBasicReactor).stop()
            else:
                raise




























