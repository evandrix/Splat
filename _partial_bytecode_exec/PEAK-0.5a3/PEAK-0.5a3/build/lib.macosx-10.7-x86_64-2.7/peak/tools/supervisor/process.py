"""Pre-forking process supervisor for FastCGI and other server-like apps"""

from __future__ import generators
from peak.api import *
from interfaces import *
from peak.running.commands import EventDriven, Bootstrap
from peak.running.process import signals, signal_names
from shlex import shlex
from cStringIO import StringIO

def tokenize(s):
    return list(iter(shlex(StringIO(s)).get_token,''))

def unquote(s):
    if s.startswith('"') or s.startswith("'"):
        s = s[1:-1]
    return s
























class ProcessSupervisor(EventDriven, config.ServiceArea):

    log           = binding.Obtain('logger:supervisor')

    pidFile       = binding.Require("Filename where process ID is kept")
    minChildren   = 1
    maxChildren   = 4
    startInterval = 15  # seconds between forks
    importModules = ()  # Placeholder for ZConfig pre-import hook; see schema

    cmdText = ""        # String form of subprocess command line

    cmdLine = binding.Make(
        lambda self: [
            unquote(x) for x in tokenize(self.cmdText)
        ]+self.argv[1:]
    )

    template = binding.Make(
        lambda self: self.getSubcommand(
            Bootstrap,
            argv = ['supervise'] + self.cmdLine,
            parentComponent = config.makeRoot(),
        ),
        adaptTo=running.IProcessTemplate,
        offerAs=[running.IProcessTemplate],
        suggestParent=False
    )

    startLockURL = binding.Make(
        lambda self: "flockfile:%s.start" % self.pidFile
    )

    pidLockURL = binding.Make(
        lambda self: "flockfile:%s.lock" % self.pidFile
    )

    processCount     = binding.Make(lambda: events.Value(0))
    desiredProcesses = binding.Make(lambda self: events.Value(self.minChildren))


    startLock = binding.Make(
        lambda self: self.lookupComponent(self.startLockURL),
        adaptTo = running.ILock
    )

    pidLock = binding.Make(
        lambda self: self.lookupComponent(self.pidLockURL),
        adaptTo = running.ILock
    )

    processes = binding.Make(dict)
    plugins   = binding.Make(list)

    eventLoop = binding.Obtain(events.IEventLoop)

    # ProcessSupervisor subcomponents may not depend on Twisted
    _no_twisted = binding.Make(lambda: False, offerAs=['peak.events.isTwisted'])

    import os

    from time import time

    def setup(self):
        self.log.debug("Beginning setup")
        template = adapt(self.template, ISupervisorPluginProvider, None)

        if template is not None:
            self.plugins.extend(template.getSupervisorPlugins(self))













    def _run(self):

        if not self.startLock.attempt():
            self.log.warning("Another process is in startup; exiting")
            return 1        # exit with errorlevel 1

        try:
            self.setup()
            self.killPredecessor()
            self.writePidFile()
        finally:
            self.startLock.release()

        self._monitorProcessCount()

        retcode = super(ProcessSupervisor,self)._run()

        if adapt(retcode,running.IExecutable,None) is not None:
            # child process, drop out to the trampoline
            return retcode

        self.desiredProcesses.set(0)    # don't restart children any more
        self.killProcesses()
        self.removePidFile()

        return retcode


    def requestStart(self):
        self.desiredProcesses.set(
            min(self.processCount()+1, self.maxChildren)
        )
        self.mainLoop.activityOccurred()








    def _monitorProcessCount(self):

        startDelay = self.eventLoop.sleep(self.startInterval)

        somethingChanged = events.AnyOf(
            self.processCount, self.desiredProcesses
        )

        while True:

            if self.processCount()<self.desiredProcesses():

                self.log.debug(
                    "%d processes desired, %d running: requesting start",
                    self.desiredProcesses(), self.processCount()
                )

                # Spawn a task to start a process as soon as possible
                self._doStart()

                # But don't start any more until start interval passes
                yield startDelay; events.resume()

            else:

                # We have enough processes, so reset desired = minimum

                if self.desiredProcesses()>self.minChildren:
                    self.log.debug(
                        "%d processes reached; resetting goal to %d",
                        self.processCount(), self.minChildren
                    )
                    self.desiredProcesses.set(self.minChildren)

                # And sleep until something relevant changes
                yield somethingChanged; events.resume()

    _monitorProcessCount = events.taskFactory(_monitorProcessCount)



    def _doStart(self):

        # ensure we're in a top-level timeslice
        yield self.eventLoop.sleep(); events.resume()

        proxy, stub = self.template.spawn(self)

        if proxy is None:
            self.abandonChildren()  # we're the child, so give up custody
            self.mainLoop.exitWith(stub)
            return

        self.mainLoop.activityOccurred()
        self.log.debug("Spawned new child process (%d)", proxy.pid)
        self._monitorChild(proxy)

        self.processes[proxy.pid] = proxy
        self.processCount.set(self.processCount()+1)

        for plugin in self.plugins:
            plugin.processStarted(proxy)

    _doStart = events.taskFactory(_doStart)


    def killProcesses(self):
        self.log.debug("Killing child processes")
        for pid,proxy in self.processes.items():
            proxy.sendSignal('SIGTERM')


    def abandonChildren(self):
        for proxy in self.processes.values():
            proxy.close()
        del self.processes






    def _monitorChild(self,proxy):

        yield proxy.isFinished | proxy.isStopped; src, evt = events.resume()
        self.mainLoop.activityOccurred()

        if src is proxy.isFinished:

            if proxy.exitedBecause():
                self.log.warning(
                    "Child process %d exited due to signal %d (%s)",
                    proxy.pid, proxy.exitedBecause(),
                    signal_names.setdefault(proxy.exitedBecause(),('?',))[0]
                )
            elif proxy.exitStatus():
                self.log.warning(
                    "Child process %d exited with errorlevel %d",
                    proxy.pid, proxy.exitStatus()
                )
            else:
                self.log.debug("Child process %d has finished", proxy.pid)

            del self.processes[proxy.pid]
            self._processCount.set(self.processCount()-1)

        elif proxy.stoppedBecause():
            self.log.error("Child process %d stopped due to signal %d (%s)",
                proxy.pid, proxy.stoppedBecause(),
                signal_names.getdefault(proxy.stoppedBecause(),('?',))[0]
            )
            self._monitorChild(proxy)   # continue monitoring

        elif proxy.isStopped():
            self.log.error("Child process %d has stopped", proxy.pid)
            self._monitorChild(proxy)   # continue monitoring

    _monitorChild = events.taskFactory(_monitorChild)





    def writePidFile(self):
        self.pidLock.obtain()
        try:
            pf = open(self.pidFile,'w')
            pf.write('%d\n' % self.os.getpid())
            pf.close()
        finally:
            self.pidLock.release()


    def readPidFile(self, func):
        self.pidLock.obtain()
        try:
            if self.os.path.exists(self.pidFile):
                pf = open(self.pidFile,'r')
                func(int(pf.readline().strip()))
                pf.close()
        finally:
            self.pidLock.release()


    def removePidFile(self):

        def removeIfMe(pid):
            if pid==self.os.getpid():
                self.log.debug("Unlinking %s", self.pidFile)
                self.os.unlink(self.pidFile)

        self.readPidFile(removeIfMe)

    def killPredecessor(self):

        def doKill(pid):
            try:
                self.log.debug("Killing predecessor (process #%d)", pid)
                self.os.kill(pid,signals['SIGTERM'])
            except:
                pass # XXX

        self.readPidFile(doKill)

