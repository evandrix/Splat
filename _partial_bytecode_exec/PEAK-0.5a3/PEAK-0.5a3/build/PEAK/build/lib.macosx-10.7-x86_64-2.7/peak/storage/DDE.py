from peak.api import *

import os, sys, weakref
from time import sleep


class DDEConnectionError(Exception):
    """Problem connecting to a DDE Server"""


class ServerManager(object):

    """This ensures that 'Shutdown()' gets called when the server is GC'd"""

    def __init__(self,name,logger=logs.AbstractLogger(levelName='EMERG')):
        import win32ui, dde
        server = self.server = dde.CreateServer()
        self.name = name
        self.logger = logger
        server.Create(name)

    def __call__(self, serviceName, topicName):
        import dde
        conn = dde.CreateConversation(self.server)

        self.logger.debug("%s: attempting DDE connection to (%s,%s)",
            self.name, serviceName, topicName
        )

        conn.ConnectTo(serviceName, topicName)
        return conn

    def __del__(self):
        if self.server is not None:
            self.logger.debug("%s: shutting down DDE server", self.name)
            self.server.Shutdown()
            self.server = None

    close = __del__


class ddeURL(naming.URL.Base):

    """PEAK Win32 DDE URL

    Example::

        "win32.dde:service::topic;file=c:\\foo;retries=5;sleep=5"

    Syntax is 'service::topic' followed by semicolon-separated
    parameters, which may be 'file' to designate a file to be launched
    if the initial connection attempt is unsuccessful, 'retries' to
    indicate how many retries should occur if the initial attempt is
    unsuccessful, and 'sleep' to set the number of seconds to wait between
    retry attempts.

    These parameters are all available as attributes of the same names,
    including 'service' and 'topic'."""

    supportedSchemes = 'win32.dde',
    defaultFactory = 'peak.storage.DDE.DDEConnection'

    class service(naming.URL.RequiredField):
        pass

    class topic(naming.URL.RequiredField):
        pass

    class file(naming.URL.Field):
        pass

    class retries(naming.URL.IntField):
        defaultValue = 10

    class sleep(naming.URL.IntField):
        defaultValue = 1






    syntax = naming.URL.Sequence(
        service, '::', topic,
        naming.URL.Set(
            naming.URL.Sequence(';file=',file),
            naming.URL.Sequence(';retries=',retries),
            naming.URL.Sequence(';sleep=',sleep),
        ),
    )

































class DDEConnection(storage.ManagedConnection):

    """Managed DDE connection"""

    protocols.advise(
        instancesProvide = [storage.IDDEConnection],
    )

    serviceName = binding.Obtain("address/service")
    topicName   = binding.Obtain("address/topic")
    launchFile  = binding.Obtain("address/file", default=None)

    retries  = binding.Obtain("address/retries", default=10)
    sleepFor = binding.Obtain("address/sleep", default=1)

    logger = binding.Obtain('logger:dde')

    def ddeServer(self):
        return ServerManager(
            str(binding.getComponentPath(self)),
            # weakref to the logger so that the ServerManager isn't part of
            # a cycle with us (if our logger refers to us)
            logger=weakref.proxy(self.logger)
        )

    ddeServer = binding.Make(ddeServer)

    def __call__(self, requestStr):
        """Issue a DDE request (requestStr -> responseStr)"""
        return self.connection.Request(requestStr)

    def execute(self, commandStr):
        """Execute a DDE command"""
        return self.connection.Exec(commandStr)

    def poke(self, commandStr, data=None):
        """DDE Poke of command string and optional data buffer"""
        return self.connection.Poke(commandStr, data)



    def _open(self):

        attemptedLaunch = False

        for i in range(self.retries+1):

            try:
                conn = self.ddeServer(self.serviceName, self.topicName)
            except:
                t,v,tb = sys.exc_info()
                if (t,v) != ('error','ConnectTo failed'):
                    del t,v,tb,conn
                    raise
            else:
                return conn

            if attemptedLaunch:
                sleep(self.sleepFor)
            else:
                if self.launchFile:
                    self.logger.debug("%s: launching %s",self,self.launchFile)
                    os.startfile(self.launchFile)

                attemptedLaunch = True


        else:
            raise DDEConnectionError(
                "ConnectTo failed", self.serviceName, self.topicName
            )

    def _close(self):
        self.ddeServer.close()
        del self.ddeServer  # force shutdown







