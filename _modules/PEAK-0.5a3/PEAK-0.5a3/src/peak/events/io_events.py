from __future__ import generators
from peak.core import protocols, adapt, binding, NOT_GIVEN, PropertyName
from interfaces import *
from peak.util.EigenData import AlreadyRead
from weakref import WeakValueDictionary, ref
import sources
from event_threads import resume, taskFactory
from errno import EINTR
from time import sleep

try:
    import signal

except ImportError:
    SIG_DFL = None
    signals = {}
    signal_names = {}
    signal = lambda *args: None
    original_signal_handlers = {}

else:
    SIG_DFL = signal.SIG_DFL

    signals = dict(
        [(name,number)
            for (name,number) in signal.__dict__.items()
                if name.startswith('SIG') and not name.startswith('SIG_')
        ]
    )

    signal_names = {}
    for signame,signum in signals.items():
        signal_names.setdefault(signum,[]).append(signame)

    original_signal_handlers = dict(
        [(signum,signal.getsignal(signum)) for signum in signal_names.keys()]
    )

    signal = signal.signal


class SignalEvents(binding.Singleton):

    """Global signal manager"""

    protocols.advise( classProvides = [ISignalSource] )

    _events = {None: lambda x=sources.Broadcaster(): x }

    def signals(self,*signames):
        """'IEventSource' that triggers whenever any of named signals occur"""

        if len(signames)==1:
            signum = signals.get(signames[0])
            try:
                return self._events[signum]()
            except KeyError:
                e = sources.Broadcaster()
                self._events[signum] = ref(
                    e, lambda ref: self._rmSignal(signum)
                )
                signal(signum, self._fire)
                return e
        else:
            return sources.AnyOf(*[self.signals(n) for n in signames])


    def haveSignal(self,signame):
        """Return true if signal named 'signame' exists"""
        return signame in signals

    def _fire(self, signum, frame):
        if signum in self._events:
            self._events[signum]().send((signum,frame))

    def __call__(self,*args):
        return self

    def _rmSignal(self,signum):
        del self._events[signum]
        signal(signum, original_signal_handlers[signum])

class EventLoop(binding.Component):

    """All-in-one event source and loop runner"""

    protocols.advise( instancesProvide = [IEventLoop] )

    sigsrc = binding.Obtain(ISignalSource)
    haveSignal = signals = binding.Delegate('sigsrc')

    scheduler = binding.Obtain(IScheduler)
    spawn = now = tick = sleep = until = timeout = time_available \
        = binding.Delegate('scheduler')

    selector  = binding.Obtain(ISelector)
    readable = writable = exceptional = binding.Delegate('selector')

    log = binding.Obtain('logger:peak.events.loop')
























    def runUntil(self, eventSource, suppressErrors=False, idle=sleep):

        running = [True]
        exit = []
        tick = self.tick
        time_available = self.time_available

        adapt(eventSource,IEventSource).addCallback(
            lambda s,e: [running.pop(),exit.append(e)]
        )

        if suppressErrors:
            def tick(exit,doTick=tick):
                try:
                    doTick(exit)
                except:
                    self.log.exception("Unexpected error in event loop:")

        while running:
            tick(exit)
            if running:
                delay = time_available()
                if delay is None:
                    raise StopIteration("Nothing scheduled to execute")
                if delay>0:
                    idle(delay)

        return exit.pop()













class Selector(binding.Component):

    """Simple task-based implementation of an ISelector"""

    protocols.advise( instancesProvide = [ISelector] )

    sigsrc = binding.Obtain(ISignalSource)
    haveSignal = signals = binding.Delegate('sigsrc')


    cache = binding.Make( [dict,dict,dict] )
    rwe   = binding.Make( [dict,dict,dict] )
    count = binding.Make( lambda: sources.Semaphore(0) )
    scheduler = binding.Obtain(IScheduler)

    checkInterval = binding.Obtain(
        PropertyName('peak.running.reactor.checkInterval')
    )

    sleep   = binding.Obtain('import:time.sleep')
    select  = binding.Obtain('import:select.select')
    _error  = binding.Obtain('import:select.error')


    def readable(self,stream):
        """'IEventSource' that fires when 'stream' is readable"""
        return self._getEvent(0,stream)

    def writable(self,stream):
        """'IEventSource' that fires when 'stream' is writable"""
        return self._getEvent(1,stream)

    def exceptional(self,stream):
        """'IEventSource' that fires when 'stream' is in error/out-of-band"""
        return self._getEvent(2,stream)






    def monitor(self):

        r,w,e = self.rwe
        count = self.count
        sleep = self.scheduler.sleep()
        time_available = self.scheduler.time_available
        select = self.select
        error = self._error

        while True:
            yield count; resume()   # wait until there are selectables
            yield sleep; resume()   # ensure we are in top-level loop

            delay = time_available()
            if delay is None:
                delay = self.checkInterval

            try:
                rwe = self.select(r.keys(),w.keys(),e.keys(),delay)
            except error, v:
                if v.args[0]==EINTR:
                    continue    # signal received during select, try again
                else:
                    raise

            for fired,events in zip(rwe,self.rwe):
                for stream in fired:
                    events[stream]().send(True)


    monitor = binding.Make(taskFactory(monitor), uponAssembly=True)










    def _getEvent(self,rwe,stream):
        if hasattr(stream,'fileno'):
            key = stream.fileno()
        else:
            key = int(stream)

        try:
            return self.cache[rwe][key]()
        except KeyError:
            e = self._mkEvent(rwe,key)
            self.cache[rwe][key] = ref(e, lambda ref: self._rmEvent(rwe,key))
            return e

    def _mkEvent(self,rwe,key):
        ob = _IOEvent()
        ob._activate = lambda ob: self._activate(rwe,key,ob)
        ob._deactivate = lambda: self._deactivate(rwe,key)
        return ob

    def _rmEvent(self,rwe,key):
        del self.cache[rwe][key]
        self._deactivate(rwe,key)

    def _activate(self,rwe,key,src):
        if key not in self.rwe[rwe]:
            self.rwe[rwe][key] = ref(src)
            self.count.put()

    def _deactivate(self,rwe,key):
        if key in self.rwe[rwe]:
            del self.rwe[rwe][key]
            self.count.take()









class _IOEvent(sources.Broadcaster):

    __slots__ = '_activate','_deactivate'

    def addCallback(self,func):
        super(_IOEvent,self).addCallback(func)
        if self._callbacks:
            self._activate(self)

    def _fire(self,event):
        self._deactivate()
        super(_IOEvent,self)._fire(event)





























