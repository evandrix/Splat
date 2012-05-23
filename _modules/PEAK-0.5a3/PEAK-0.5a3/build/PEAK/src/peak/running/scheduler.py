"""Event-driven Scheduling"""

from __future__ import generators
from peak.api import *
from interfaces import *
from peak.util.EigenData import EigenCell, AlreadyRead
from errno import EINTR

__all__ = [
    'MainLoop', 'UntwistedReactor',
]






























class MainLoop(binding.Component):

    """Top-level application event loop, with timeout management"""

    protocols.advise(
        instancesProvide=[IMainLoop]
    )

    exitCode      = binding.Make(lambda: events.Value(None))
    lastActivity  = binding.Make(lambda: events.Value(None))
    stopOnSignals = binding.Obtain(PropertyName('peak.running.mainLoop.stopOnSignals'))
    eventLoop     = binding.Obtain(events.IEventLoop)
    sleep         = binding.Obtain('import:time.sleep') # XXX testing hook

    def activityOccurred(self):
        self.lastActivity.set(self.eventLoop.now())

    def run(self, stopAfter=0, idleTimeout=0, runAtLeast=0):
        """Loop polling for IO or GUI events and calling scheduled funcs"""

        self.activityOccurred()
        self.exitCode.set(None)

        if self.stopOnSignals:
            handler = self.eventLoop.signals(*self.stopOnSignals)
            handler.addCallback(lambda s,e: self.exitWith(None))

        try:
            if stopAfter:
                self.eventLoop.sleep(stopAfter).addCallback(
                    lambda s,e: self.exitWith(None)
                )

            if idleTimeout:
                self._checkIdle(runAtLeast, idleTimeout)

            return self.eventLoop.runUntil(self.exitCode,True,idle=self.sleep)[0]

        finally:
            self.lastActivity.set(None); handler = None

    def _checkIdle(self, runAtLeast, timeout):

        yield self.eventLoop.sleep(runAtLeast); events.resume()

        untilActivityOrTimeout = events.AnyOf(
            self.lastActivity, self.eventLoop.sleep(timeout)
        )

        src = self.lastActivity

        while src is self.lastActivity:
            yield untilActivityOrTimeout; src,evt = events.resume()

        self.exitWith(None)

    _checkIdle = events.taskFactory(_checkIdle)


    def exitWith(self, exitCode):
        self.exitCode.set((exitCode,), force=True)





















class UntwistedReactor(binding.Component):

    """Primitive partial replacement for 'twisted.internet.reactor'"""

    protocols.advise(
        instancesProvide=[IBasicReactor]
    )

    running = False
    stopped = binding.Make(lambda: events.Condition(True))

    writers = binding.Make(dict)
    readers = binding.Make(dict)
    sleep   = binding.Obtain('import:time.sleep')

    eventLoop = binding.Obtain(events.IEventLoop)

    def addReader(self, reader):
        if reader not in self.readers:
            e = self.readers[reader] = self.eventLoop.readable(reader)
            e.addCallback(lambda s,e: self._fire(self.readers, reader, reader.doRead))

    def addWriter(self, writer):
        if writer not in self.writers:
            self.writers[writer]=self.eventLoop.writable(writer)
            e.addCallback(lambda s,e: self._fire(self.writers, writer, writer.doWrite))

    def removeReader(self, reader):
        if reader in self.readers: del self.readers[reader]

    def removeWriter(self, writer):
        if writer in self.writers: del self.writers[writer]









    def run(self, installSignalHandlers=True):

        if installSignalHandlers:
            handler = self.eventLoop.signals('SIGTERM','SIGBREAK','SIGINT')
            handler.addCallback(lambda s,e: self.stop())

        self.stopped.set(False)
        self.running = True

        try:
            self.eventLoop.runUntil(
                self.stopped, suppressErrors=True, idle=self.sleep
            )
        finally:
            self.running = False
            handler = None  # drop signal handling, if we were using it

            # clear selectables (XXX why???)
            self._delBinding('readers')
            self._delBinding('writers')


    def stop(self):
        self.callLater(0, self.crash)

    def crash(self):
        self.stopped.set(True)

    def callLater(self, delay, callable, *args, **kw):
        self.eventLoop.sleep(delay).addCallback(
            lambda s,e: callable(*args,**kw) or True
        )









    def _fire(self, events, target, method):

        if target in events:
            # Only fire currently-active events
            events[target].addCallback(
                lambda s,e: self._fire(events,target,method)
            )
            method()


    def iterate(self, delay=None):
        """Handle scheduled events for up to 'delay' seconds"""

        if delay is None:
            if not self.running:
                delay = 0
            else:
                delay = self.eventLoop.time_available()
                if delay is None:
                    delay = 0

        # Run the event loop
        self.stopped.set(False)

        self.eventLoop.runUntil(
            events.AnyOf(self.stopped, self.eventLoop.sleep(delay)),
            suppressErrors=True, idle=self.sleep
        )


Reactor = UntwistedReactor  # for easy reference in peak.ini










