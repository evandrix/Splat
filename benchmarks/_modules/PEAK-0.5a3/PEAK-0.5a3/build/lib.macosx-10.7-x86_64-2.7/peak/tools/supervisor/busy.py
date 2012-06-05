"""Start-on-busy-children plugin for ProcessSupervisor"""

from __future__ import generators
from peak.api import *
from interfaces import *
from peak.running.process import ChildProcess

__all__ = ['BusyProxy', 'BusyStarter']

































class BusyProxy(ChildProcess):

    """Proxy for process that communicates its "busy" status"""

    log        = binding.Obtain('logger:supervisor.busy-monitor')
    busyStream = binding.Require("readable pipe from child")
    fileno     = binding.Delegate('busyStream')
    isBusy     = binding.Make(lambda: events.Condition(False))

    def _monitor(self):

        readable = self.eventLoop.readable(self)
        readableOrDone = events.AnyOf(readable, ~self.isOpen)
        
        while True:

            yield readableOrDone; src,evt = events.resume()

            if src is not readable:
                break

            try:
                # We need a try block because the pipe could close at any time
                byte = self.busyStream.read(1)
            except ValueError:
                # already closed
                return

            if byte=='+':
                self.log.trace("Child process %d is now busy", self.pid)
                self.isBusy.set(True)

            elif byte=='-':
                self.log.trace("Child process %d is now free", self.pid)
                self.isBusy.set(False)

        self.busyStream.close()
        
    _monitor = binding.Make(events.taskFactory(_monitor), uponAssembly = True)


class BusyStarter(binding.Component):

    """Start processes for incoming connections if all children are busy"""

    children = binding.Make(dict)
    template = binding.Obtain(running.IProcessTemplate, suggestParent=False)
    stream   = binding.Obtain('./template/stdin')
    fileno   = binding.Delegate('stream')
    log      = binding.Obtain('logger:supervisor.busy-stats')
    busyCount  = binding.Make(lambda: events.Value(0))
    childCount = binding.Make(lambda: events.Value(0))
    supervisor = binding.Obtain('..')
    eventLoop  = binding.Obtain(events.IEventLoop)

    def monitorUsage(self):

        from time import time
        trace = self.log.trace
        maxChildren = self.supervisor.maxChildren

        busy = self.busyCount()

        while True:
            # wait until all children are started and busy
            while busy<self.childCount() or self.childCount()<maxChildren:
                yield self.busyCount; busy = events.resume()

            start = time()  # then begin timing

            # Time while N or N-1 children are busy
            while busy and busy>=self.childCount()-1 and self.childCount()==maxChildren:
                yield self.busyCount; busy = events.resume()

            duration = time()-start
            trace("All children were busy for: %s seconds", duration)

    monitorUsage = binding.Make(
        events.taskFactory(monitorUsage), uponAssembly = True
    )


    def processStarted(self, proxy):

        self.childCount.set(self.childCount()+1)

        busy   = proxy.isBusy.value
        closed = ~proxy.isOpen
        somethingChanged = events.AnyOf(busy,closed)

        while True:
            yield somethingChanged; src,evt = events.resume()

            if src is closed:
                break
            elif evt:
                self.busyCount.set(self.busyCount()+1)
            else:
                self.busyCount.set(self.busyCount()-1)

        self.childCount.set(self.childCount()-1)

    processStarted = events.taskFactory(processStarted)


    def monitorBusy(self):
        untilReadable = self.eventLoop.readable(self) 

        while True:
            # Wait until we have stream activity
            yield untilReadable; events.resume()

            # Is everybody busy?
            if self.busyCount()==self.childCount():
                self.supervisor.requestStart()

            # Wait until the child or busy count changes before proceeding
            yield events.AnyOf(self.busyCount,self.childCount); events.resume()
            
    monitorBusy = binding.Make(
        events.taskFactory(monitorBusy), uponAssembly = True
    )

