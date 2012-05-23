from peak.api import *
from time import sleep

__all__ = [
    'IProcedure', 'ITaskSwitch', 'IEventSource', 'IEventSink', 'IReadableSource',
    'IWritableSource', 'IValue', 'IConditional', 'ISemaphore', 'ITask',
    'IScheduledTask', 'ITaskState', 'IScheduler', 'ISignalSource',
    'ISelector', 'IEventLoop', 'Interruption', 'TimeoutError', 'IWritableValue',
    'IPausableSource',
]


class Interruption(Exception):
    """A task was interrupted by an asynchronous event"""


class TimeoutError(Interruption):
    """A timeout occurred"""


class IProcedure(protocols.Interface):

    """Iterator suitable for use in a task, such as a generator-iterator"""

    def __iter__():
        """*Must* return the 'IProcedure'; i.e. iterator not iterable"""

    def next():
        """Return an 'ITaskSwitch', or value to be yielded to previous task"""












class ITaskSwitch(protocols.Interface):

    """What a task yields control to

    'IProcedure' objects running in a task yield 'ITaskSwitch' objects to
    control the task's flow and co-operation.

    In addition to PEAK-supplied event sources like 'Value', 'Semaphore', and
    'Condition', generator-iterators and other 'IProcedure' objects are also
    adaptable to 'ITaskSwitch', thus allowing one to e.g.
    'yield someGenerator(someArgs)' in a task.  This allows the nested
    generator to run as the next procedure for the task.
    """


    def nextAction(task=None, state=None):
        """Return true if task should continue

        If supplied, 'task' and 'state' are an 'ITask' and 'ITaskState',
        respectively, and the task switch may perform any needed actions with
        them, such as arranging to call back 'task.step()', or performing
        an action such as 'state.YIELD(value)' or 'state.CALL(task)'.
        """


















class IEventSource(ITaskSwitch):

    """Thing you can receive notifications from, as well as task-switch on

    Note that every event source can control task switching, but not every
    task switcher is an event source.  Generators, for example, can control
    task flow, but do not really produce any "events".

    Event callbacks must *not* raise errors, as event sources are not required
    to ensure that all callbacks are executed when a callback raises an error.
    """

    def addCallback(func):
        """Call 'func(source,event)' the next time this event occurs

        If this method is called from within a callback, 'func' must *not* be
        invoked until the *next* occurrence of the event.

        Note also that callbacks will be called at most once for each time
        they are registered; adding a callback does not result in an ongoing
        "subscription" to the event source.
        """


class IEventSink(protocols.Interface):

    """Signature for callables passed to 'IEventSource.addCallback()'"""

    def __call__(source, event):
        """Accept 'event' from an 'IEventSource' ('source')

        This method should return 'True' if the callback wishes to "consume"
        the event (i.e. prevent other callbacks from receiving it).  However,
        the event source is free to ignore the callback's return value.  The
        "consume an event" convention is normally used only by "stream" event
        sources such as distributors and semaphores, and by event sources with
        ongoing listeners/handlers (as opposed to one-time callbacks).
        """



class IPausableSource(IEventSource):

    """An event source whose firing can be temporarily disabled

    Calls to 'disable()' and 'enable()' may be nested, so the number of
    'enable()' calls must match the number of 'disable()' calls in order for
    the event source to resume firing.

    Events occuring while the source is disabled may be buffered.  Readable
    sources will normally buffer only their last value, and therefore send
    at most one event when re-enabled.  Non-readable sources such as
    'Broadcast' and 'Distributor' typically will buffer as many events as there
    are currently registered callbacks for, and raise an error if more events
    occur, in order to avoid growing the buffer indefinitely.
    """

    def disable():
        """Stop events from firing"""

    def enable():
        """Reenable events, and fire any that accumulated in the meanwhile"""


class IReadableSource(IEventSource):

    """An event source whose current value or state is readable

    Note that the firing behavior of an 'IReadableSource' is undefined.  See
    'IValue' and 'IConditional' for two possible kinds of firing behavior.
    """

    def __call__():
        """Return the current value, condition, or event"""

    def derive(func):
        """Return a derived 'IValue', computed using 'func(source())'"""





class IWritableSource(IReadableSource):

    """An event source whose current value or state can be read or changed"""

    def set(value,force=False):
        """Set the current state to 'value', possibly triggering an event

        If the 'force' parameter is a true value, and the event source would
        not have fired an event due to a lack of change in value, the event
        source should fire the event anyway.  (The firing may be suppressed
        for other reasons, such as falsehood in the case of an 'IConditional'
        or 'ISemaphore'.)"""


class IValue(IReadableSource):

    """A readable event source that fires when changed"""

    isTrue = protocols.Attribute(
        """'IConditional' indicating truth of value"""
    )

    isFalse = protocols.Attribute(
        """'IConditional' indicating untruth of value"""
    )



class IWritableValue(IWritableSource,IValue):

    """A writable event source that fires when changed"""










class IConditional(IReadableSource):

    """An event source that fires when (or resumes while) its value is true

    Note that callbacks added to an 'IConditional' with a true value should be
    called immediately."""

    value = protocols.Attribute(
        """'IValue' for the value the conditional is based on

        If you want to wait for the condition to become false, you need to
        wait on this, instead of on the conditional itself.  Conditionals fire
        when true, but values fire when changed.
        """
    )

    def conjuncts():
        """Return the sequence of conjuncts of this condition

        For an "and" operation, this should return the and-ed conditions.
        For most other operations, this should return a one-element sequence
        containing the condition object itself."""

    def disjuncts():
        """Return the sequence of disjuncts of this condition

        For an "or" operation, this should return the or-ed conditions.
        For most other operations, this should return a one-element sequence
        containing the condition object itself."""

    def __invert__():
        """Return the inverse ("not") of this condition"""

    def __and__(cond):
        """Return the conjunction ("and") of this condition with 'cond'"""

    def __or__(expr):
        """Return the disjunction ("or") of this expression with 'expr'"""



    def __cmp__(other):
        """Conditionals must be comparable to each other"""

    def __hash__(other):
        """Conditionals must be hashable"""


protocols.declareAdapter(
    lambda o,p: o.value, provides=[IValue], forProtocols=[IConditional]
)


class ISemaphore(IWritableSource,IConditional):

    """An event source that allows 'n' tasks to proceed at once

    Unlike a conditional or value, a semaphore distributes its events to at
    most one accepting callback.  This ensures that tasks waiting for the
    semaphore are not awakened if other tasks remove all available tokens
    first."""

    def put():
        """Increase the number of runnable tasks by 1"""

    def take():
        """Decrease the number of runnable tasks by 1"""















class ITask(IEventSource):

    """Task that can be paused and resumed based on event occurences

    Tasks maintain a stack of "currently executing procedures".  The topmost
    procedure's 'next()' method is invoked repeatedly to obtain 'ITaskSwitch'
    instances that determine whether the task will continue, invoke a nested
    procedure (by pushing it on the stack), or be suspended (by returning from
    the 'step()' method.  When an procedure's iteration is exhausted, it's
    popped from the stack, and the next-highest procedure is resumed.  This
    simple "virtual machine" allows linear Python code to co-operatively
    multitask on the basis of arbitrary events.

    Procedures used in tasks must call 'events.resume()' immediately after
    each 'yield' statement (or at the beginning of their 'next()' method, if
    not a generator), in order to ensure that errors are handled properly.  If
    the event source or generator that was yielded sends a value or event
    back to the task, that value will be returned by 'resume()'.

    Procedures may send values back to their calling iterators by yielding
    values that do not implement 'ITaskSwitch'.  If there is no calling
    iterator, the yielded value is sent to any callbacks that have been added
    to the task itself.  (Tasks are event sources, so they may be yielded on,
    or have callbacks added to them to receive values yielded by the task's
    outermost procedure.)  Note that when a nested procedure terminates,
    'NOT_GIVEN' is returned from 'events.resume()' in the calling procedure.

    Finally, note that event sources may send values back to a task by passing
    them as events to the task's 'step()' callback method."""

    def step(source=None,event=NOT_GIVEN):
        """Run until task is suspended by an 'ITaskSwitch' or finishes

        If the task's current generator calls 'events.resume()', it will
        receive 'event' as the return value.
        """

    isFinished = protocols.Attribute(
        """'IConditional' that fires when the task is completed"""
    )

class IScheduledTask(ITask):

    """A task that relies on a scheduler for ongoing execution

    Scheduled tasks do not run when their 'step()' methods are called, but
    instead simply put themselves on the scheduler's schedule for later
    execution.  This means that scheduled tasks do not run during operations
    that cause callbacks, and so they cannot raise errors in apparently-unrelated
    code.  They also are less likely to cause unintended or unexpected
    side-effects due to their executing between 'yield' statements in other
    tasks.  And finally, scheduled tasks can reliably signal that they
    were aborted due to an uncaught exception, via their 'aborted' attribute.

    There are some drawbacks, however.  First, scheduled tasks require a
    scheduler, and the scheduler must 'tick()' repeatedly as long as one wishes
    the tasks to continue running.  Second, scheduled tasks can take
    slightly longer to task switch than unscheduled ones, because multiple
    callbacks are required.

    Last, but far from least, when a scheduled task is resumed, it cannot be
    guaranteed that another task or callback has not already contravened
    whatever condition the task was waiting for.  This is true even if only
    one task is waiting for that condition, since non-task callbacks or
    other code may be executed between the triggering of the event, and the
    time at which the task's resumption is scheduled.
    """


    def step(source=None,event=NOT_GIVEN):
        """Schedule task to resume during its scheduler's next 'tick()'"""


    aborted = protocols.Attribute(
        """'IConditional' that fires if the task is aborted"""
    )






class ITaskState(protocols.Interface):

    """Control a task's behavior

    This interface is made available only to 'ITaskSwitch' objects via their
    'nextAction()' method, so you don't need to know about this unless you're
    writing a new kind of event source or task switch.  Even then, 90% of the
    time the 'YIELD()' method is the only one you'll need.  The rest should be
    considered "internal" methods that can break things if you don't know
    precisely what you're doing and why.
    """

    def YIELD(value):
        """Supply 'value' to next 'resume()' call"""

    def CALL(iterator):
        """Cause task to execute 'iterator' next"""

    def RETURN():
        """Silently abort the currently-running iterator"""

    def THROW():
        """Reraise 'sys.exc_info()' when current iterator resumes"""

    def CATCH():
        """Don't reraise 'sys.exc_info()' until next 'THROW()'"""


    lastEvent = protocols.Attribute(
        """Last value supplied to 'YIELD()', or 'NOT_GIVEN'"""
    )

    handlingError = protocols.Attribute(
        """True between 'THROW()' and 'CATCH()'"""
    )

    stack = protocols.Attribute(
        """List of running iterators"""
    )


class IScheduler(protocols.Interface):

    """Time-based conditions"""

    def spawn(iterator):
        """Return a new 'IScheduledTask' based on 'iterator'"""

    def alarm(iterator, timeout, errorType=TimeoutError):
        """Run 'iterator', interrupting w/'errorType' after 'timeout' secs"""

    def now():
        """Return the current time"""

    def tick(stop=None):
        """Invoke scheduled callbacks whose time has arrived, until 'stop'

        If you may want 'tick' to exit before all scheduled callbacks have been
        invoked, you may supply a mutable object as the 'stop' parameter.  If
        it is changed to a true value during the 'tick()' execution, 'tick()'
        will return without executing any additional callbacks.  (Note that
        schedulers based on Twisted will raise 'NotImplementedError' if the
        'stop' parameter is supplied.)"""

    def sleep(secs=0):
        """'IEventSource' that fires 'secs' after each callback/task switch

        The object returned is reusable: each time you yield it or add a
        callback to it, the task/callback will be delayed 'secs' from the
         time that the task switch was requested or the callback added.  More
        than one task/callback may wait on the same 'sleep()' object, but
        each "wakes" at a different time, according to when it "slept"."""

    def until(time):
        """Get an 'IConditional' that fires when 'scheduler.now() >= time'"""

    def timeout(secs):
        """Get an 'IConditional' that will fire 'secs' seconds from now"""

    def time_available():
        """Return number of seconds until next scheduled callback"""

    isEmpty = protocols.Attribute(
        """'IConditional' indicating whether the scheduler is empty"""
    )






































class ISignalSource(protocols.Interface):

    """Signal events"""

    def signals(*signames):
        """'IEventSource' that triggers whenever any of named signals occur

        Note: signal callbacks occur from within a signal handler, so it's
        usually best to yield to an 'IScheduler.sleep()' (or use a scheduled
        task) in order to avoid doing anything that might interfere with
        running code.

        Also note that signal event sources are only active so long as a
        reference to them exists.  If all references go away, the signal
        handler is deactivated, and no callbacks will be sent, even if they
        were already registered.
        """

    def haveSignal(signame):
        """Return true if signal named 'signame' exists"""


class ISelector(ISignalSource):

    """Like a reactor, but supplying 'IEventSources' instead of callbacks

    May be implemented using a callback on 'IScheduler.now' that calls a
    reactor's 'iterate()' method with a delay of 'IScheduler.time_available()'
    seconds.  Note that all returned event sources are active only so long
    as a reference to them is kept.  If all references to an event source go
    away, its tasks/callbacks will not be called."""

    def readable(stream):
        """'IEventSource' that fires when 'stream' is readable"""

    def writable(stream):
        """'IEventSource' that fires when 'stream' is writable"""

    def exceptional(stream):
        """'IEventSource' that fires when 'stream' is in error/out-of-band"""

class IEventLoop(IScheduler, ISelector):

    def runUntil(eventSource, suppressErrors=False, idle=sleep):
        """'tick()' repeatedly until 'eventSource' fires, returning event

        If 'suppressErrors' is true, this method will trap and log all errors
        without allowing them to reach the caller.  Note that event loop
        implementations based on Twisted *require* that 'suppressErrors' be
        used, and should raise a 'NotImplementedError' if it is set to False.

        Note that if the event loop's scheduler becomes empty (i.e., there are
        no active tasks/callbacks remaining), and 'eventSource' has not fired,
        this method *may* raise 'StopIteration' to indicate this.  If you would
        prefer that 'runUntil()' simply exit when that happens, just use the
        event loop's 'isEmpty' condition as part of an 'events.AnyOf()'
        condition passed into 'runUntil()'.  Or, if you'd prefer that the event
        loop continue indefinitely despite the lack of any active tasks (e.g.
        in GUI programs), you may schedule something to be executed in the far
        future, or use a task that looks something like:

            oneDay = eventLoop.sleep(86400)
            while True:
                yield oneDay; events.resume()

        Such a task will only execute once per day, but is sufficient to
        ensure that 'runUntil()' does not exit due to an empty schedule.  Note
        that if you are using a Twisted reactor, you don't need to do this
        as an event loop based on a Twisted reactor will only raise
        'StopIteration' if 'reactor.stop()' is called directly (i.e. not via
        triggering of 'eventSource').

        If 'idle' is supplied, it is called with a single argument
        representing a 'float' number of seconds that the event loop intends
        to be idle for, each time the event loop is idle.  The default
        for 'idle' is 'time.sleep', so that the process sleeps between
        events.

        Note that the 'idle' function will probably never be called when there
        are tasks waiting for I/O, when there are tasks that reschedule
        themselves at short intervals, or when using Twisted."""

