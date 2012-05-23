from protocols import Interface, Attribute, declareAdapter
from peak.api import PropertyName, NOT_GIVEN
from peak.binding.interfaces import IComponentFactory, IComponent
import sys, os

CLUSTER = PropertyName('peak.running.cluster')

ARGV    = PropertyName('peak.running.argv')
STDIN   = PropertyName('peak.running.stdin')
STDOUT  = PropertyName('peak.running.stdout')
STDERR  = PropertyName('peak.running.stderr')
ENVIRON = PropertyName('peak.running.environ')


__all__ = [

    'CLUSTER', 'ARGV', 'STDIN', 'STDOUT', 'STDERR', 'ENVIRON',

    'IExecutable', 'ICmdLineAppFactory', 'ICmdLineApp', 'IRerunnable',

    'IPeriodicTask', 'ITaskQueue', 'IMainLoop', 'IRerunnableCGI',

    'IAdaptiveTask', 'IAdaptiveTaskSPI', 'ILock',

    'IBasicReactor', 'ITwistedReactor', 'ICheckableResource',

    'ISignalManager', 'IProcessProxy', 'IMainCmdFactory', 'IProcessTemplate',

]












class IExecutable(Interface):

    """Object which can be executed as a "main program" or "subcommand"

    Certain 'peak.running' facilities require the use of an "executable"
    object.  Executable objects are objects which implement one of the
    following interfaces (listed in descending preference order):

    * 'ICmdLineAppFactory' - supports I/O redirection, environment override,
      command line arguments, and returned exit level

    * 'IRerunnable' - supports I/O redirection, environment override,
      command line arguments, and returned exit level

    * 'ICmdLineApp' - redirection and overrides are attempted via 'sys' and
      'os' but not guaranteed to work; 'run()' return value is used as
      exit level.

    * Any object callable with no arguments; redirection and overrides are
      attempted via 'sys' and 'os' but not guaranteed to work; return value
      of called object used as exit level.

    Objects which implement any of these interfaces can be invoked as
    subcommands by 'peak.running.commands' classes like 'Bootstrap' and
    'IniInterpreter'.  Notice that callables and 'ICmdLineApp' instances
    can't be completely controlled by their invoker, so if you want to
    create a component that can have its I/O redirected by a controlling
    component, you should create an 'IRerunnable' or 'ICmdLineAppFactory'.

    Note that 'IExecutable' is an "abstract interface" for documentation
    purposes only.  Declaring that you implement 'IExecutable' directly
    is meaningless; you must implement one of the three explicit
    sub-interfaces or be a callable object to be "executable".
    """







class ICmdLineAppFactory(IComponentFactory, IExecutable):

    """Class interface for creating ICmdLineApp components

    A command-line app object is created with keyword arguments for 'stdin',
    'stdout', 'stderr', 'environ', and 'argv'.  It is free to use default
    values for items not supplied, but it must *not* bypass or override any
    values which *are* supplied.  E.g. it should *never* write to 'sys.stdin'.
    The purpose of this encapsulation is to allow application objects to
    be composed by other application objects, and to also allow "server"
    invocations of applications, as is needed for protocols like FastCGI
    and ReadyExec."""

    def __call__(parentComponent, componentName=None,

        argv  = sys.argv,

        stdin = sys.stdin,
        stdout = sys.stdout,
        stderr = sys.stderr,

        environ = os.environ, **otherAttrs):

        """Create a new "command-line" application instance"""



class ICmdLineApp(IComponent, IExecutable):

    """Encapsulate a "commandline-style" app for reusability/composability"""

    def run():
        """Perform the functionality of the application; return exit code

        Note that the intent is for this method to be called once and only
        once; an 'ICmdLineApp' is not required to be re-runnable.  Implement
        'IRerunnable' (which supports passing environment arguments to 'run()')
        if multiple runs are desired."""



class IMainCmdFactory(IExecutable):

    """Callable that can create a "main" 'ICmdLineApp' w/out further input"""

    def __call__():
        """Return a ready-to-run 'ICmdLineApp'"""


class IRerunnable(IExecutable):

    """Like a command-line app, but serially reusable

    This interface is for "stateless" commands that can run without having
    their execution environment as part of their state."""

    def run(stdin,stdout,stderr,environ,argv=[]):
        """Perform function and return exit code"""


class IRerunnableCGI(Interface):

    """Like an IRerunnable, but specifically for CGI"""

    def runCGI(stdin,stdout,stderr,environ,argv=()):
        """Perform function and return exit code"""


def CGIFromComponent(ob,proto):
    """Turn PEAK components into publishable web apps"""
    from peak.web.publish import CGIPublisher
    return CGIPublisher.fromApp(ob,proto)

declareAdapter(CGIFromComponent,
    provides=[IRerunnableCGI], forProtocols=[IComponent]
)






class IPeriodicTask(Interface):

    """Thing that does work periodically"""

    def __call__():
        """Do whatever work is required; return truth if useful work done

        This method should update the task's 'pollInterval' if needed.  To
        request that the task should no longer be recurrently scheduled,
        raise 'exceptions.StopRunning'."""

    pollInterval = Attribute(
        """Number of seconds till next desired invocation"""
    )

    priority = Attribute("""Integer priority value; higher=more important""")

    def __cmp__(other):
        """Compare to another daemon on the basis of priority"""






















class ITaskQueue(Interface):

    """Schedule and run prioritized periodic tasks using the system reactor

    When more than one task is available for execution, the highest priority
    one is executed.  (Equal priority tasks are scheduled in round-robin
    fashion.)  A task is considered available for execution when it is first
    added, and when its 'pollInterval' elapses after its last execution.

    Whenever the queue is enabled (the default state), tasks are executed
    and scheduled.  When disabled, execution and scheduling stops until
    re-enabled.  Enabling and disabling do not affect the task schedule
    in any way, although while the queue is disabled, tasks may pile up
    in the "available" state.  (Note: a task queue is allowed to let the
    system reactor hold onto waiting tasks, so if the reactor's state is
    reset, queue contents may be lost whether the queue is enabled or not.)

    Unlike many scheduling-related components, you may have as many of
    these as you like, but each must have access to an 'IBasicReactor'
    and an 'IMainLoop'.

    Note, by the way, that this interface does not include a way to
    remove tasks from the queue.  A task may remove itself from the
    queue by raising 'StopRunning' when it is invoked."""


    def addTask(ptask):
        """Add 'IPeriodicTask' instance 'ptask' to the priority queue"""

    def enable():
        """Allow all added tasks to run (default state)"""

    def disable():
        """Stop executing tasks after the current task completes"""







class IMainLoop(Interface):

    """Run the reactor event loop, with activity monitoring and timeouts

    This is typically used to control the lifetime of an event-driven
    application.  The application invokes 'run()' with the desired parameters
    once the system reactor is ready to run.

    Reactor-driven components should invoke the 'activityOccurred()' method
    on this interface whenever I/O or useful processing occurs, in order to
    prevent inactivity timeouts."""


    def activityOccurred():
        """Call this periodically to prevent inactivity timeouts."""


    lastActivity = Attribute(
        """'events.IReadable' giving the 'time()' that 'activityOccurred()' was
        last called, or the start of the current 'run()', whichever is later.
        If 'run()' is not currently executing, the value is 'None'."""
    )


    def run(stopAfter=0, idleTimeout=0, runAtLeast=0):

        """Loop polling for IO, GUI, and scheduled events

        'stopAfter' -- No scheduled actions will be invoked after this
                       many seconds.  'run()' will exit soon afterward.
                       (Zero means "run until the reactor stops".)

        'idleTimeout' -- If 'activityOccurred()' is not called for this
                         many seconds, stop and return from 'run()'.
                         (Zero means, "don't check for inactivity".)

        'runAtLeast' -- run at least this many seconds before an 'idleTimeout'
                        is allowed to occur.  (Zero means, "idle timeouts
                        may occur any time after the run starts.")
        """

    def exitWith(self, exitCode):
        """Exit the mainloop immediately, returning 'exitCode'"""



class IAdaptiveTask(IPeriodicTask):

    """Periodic task with tunable polling interval"""

    runEvery = Attribute(
       """Base value for 'pollInterval' when daemon has no work waiting"""
    )

    increaseIdleBy = Attribute(
        """Add this to 'pollInterval' each time there's no work"""
    )

    multiplyIdleBy = Attribute(
        """Multiply 'pollInterval' by this each time there's no work"""
    )

    maximumIdle = Attribute(
        """Never let 'pollInterval' get bigger than this"""
    )

    minimumIdle = Attribute(
        """'pollInterval' used when daemon has work to do"""
    )













class IAdaptiveTaskSPI(Interface):

    """Things you implement when subclassing the AdaptiveTask abstract base"""

    def getWork():
        """Return a "job" (true value) for 'doWork()', or a false value"""

    def doWork(job):
        """Do work described by 'job'; return a true value if successful"""

    lock = Attribute(
        """An optional lock object to wrap calls to 'getWork()/doWork()'"""
    )

    def lockMe():
        """Override this for custom locking: return True if lock acquired"""

    def unlockMe():
        """Override this for custom locking: ensure lock released"""


class ILock(Interface):

    def attempt():
        """try to obtain the lock, return boolean success"""

    def obtain():
        """wait to obtain the lock, returns None"""

    def release():
        """release an obtained lock, returns None"""

    def locked():
        """returns True if any thread IN THIS PROCESS
        has obtained the lock, else False"""






class IBasicReactor(Interface):

    """I/O Scheduler -- 'twisted.internet.reactor' or a substitute

    Twisted reactors actually do a lot more than this, but this is all
    we need for basic "running" operations that don't involve support
    for specialized protocols.  This is a simple enough set of operations
    that we should be able to provide an "unTwisted" implementation."""

    def run(installSignalHandlers=True):
        """Loop polling for IO or GUI events and calling scheduled funcs"""

    def crash():
        """Cause 'run()' to exit at the earliest possible moment"""

    def stop():
        """Cause 'run()' to exit after pending scheduled calls are finished"""

    def callLater(delay, callable, *args, **kw):
        """Invoke 'callable' after 'delay' seconds with '*args, **kw'"""

    def addReader(reader):
        """Register 'reader' file descriptor to receive 'doRead()' calls

        'reader' must have a 'fileno()' method and a 'doRead()' method."""

    def addWriter(writer):
        """Register 'writer' file descriptor to receive 'doWrite()' calls

        'writer' must have a 'fileno()' method and a 'doWrite()' method."""

    def removeReader(reader):
        """Unregister 'reader'"""

    def removeWriter(writer):
        """Unregister 'writer'"""

    def iterate(delay=0):
        """Handle scheduled events, then do I/O for up to 'delay' seconds"""


class ITwistedReactor(IBasicReactor):

    """Ask for this if you really need Twisted

    For the "rest" of this interface's documentation, see
    'twisted.internet.interfaces' and look at the various 'IReactor*'
    interfaces.

    The purpose of this interface in PEAK is to let a component ask for
    a Twisted reactor if it really needs one.
    """






























class ISignalManager(Interface):

    """DEPRECATED - Please use 'events.ISignalSource' instead!

    A signal handler is any weakly-referenceable object with 'SIG*()' methods
    (e.g. 'SIGKILL()', 'SIGCHLD()', etc.).  Handlers are automatically removed
    if they are no longer referenced outside the signal manager.

    For signals with installed handlers, the default behavior is replaced by
    calling the appropriately named method on each handler.  So, if there are
    five handlers registered for e.g. SIGCHLD, then when SIGCHLD occurs, those
    five handlers' 'SIGCHLD()' methods will be called with the signal number
    and stack frame, as though they had been directly registered for the
    signal.

    If a given signal does not have any handlers, it will have its default
    behavior (SIG_DFL) restored.  Note that due to the global nature of signals
    in Python programs, direct use of the Python 'signal' module is not
    recommended and may produce unexpected results.

    Also note that there is no guaranteed order in which handlers for a given
    signal are called, and the order may not be consistent from one invocation
    to the next.  Last, but not least, remember that Python calls signal
    handlers only from the "main thread", so handlers should use locks to
    protect access to resources that may be modified or used by other threads.
    """

    def addHandler(handler):
        """Add 'handler' to handlers called for appropriate signals

        Adding a handler more than once has no effect."""

    def removeHandler(handler):
        """Remove 'handler' from signal handlers

        Removing a handler that was not added, has no effect."""





class IProcessProxy(Interface):
    """Object that represents a child process

    Attributes whose name begins with 'is' are 'events.IConditional' objects,
    and the other listed attributes are 'events.IValue' objects."""

    def sendSignal(signal):
        """Send 'signal' (name or number) to process, return success flag"""

    def close():
        """Stop monitoring this process"""

    isOpen = Attribute(
        """'close()' has not been called and not 'isFinished()'"""
    )

    isFinished = Attribute(
        """Has the process exited? (WIFSIGNALED or WIFEXITED)"""
    )

    isStopped  = Attribute(
        """Is the process currently stopped/suspended? (WIFSTOPPED)"""
    )

    isRunning  = Attribute(
        """Is the process running? (not isFinished and not isStopped)"""
    )

    exitStatus = Attribute(
        """Returncode of the process, if finished (WEXITSTATUS)"""
    )

    stoppedBecause = Attribute(
        """Signal that stopped the process, or None (WSTOPSIG)"""
    )

    exitedBecause  = Attribute(
        """Signal that killed the process, or None (WTERMSIG)"""
    )


class IProcessTemplate(Interface):

    """Object that is used to spawn a particular type of child process"""

    def spawn(parentComponent):
        """Return 'proxy,stub' pair after forking child process

        In the parent process, this method returns 'proxy,None', where 'proxy'
        is an 'IProcessProxy' for the child process.  The 'proxy' object is
        given 'parentComponent' as its component context.

        In the child process, this method returns 'None,stub', where 'stub' is
        the command that should be returned from the current command's 'run()'
        method, in order to start up the child process.

        Note that the parent component for a process template should usually be
        a new configuration root, so that the parent and child process do not
        share any components unintentionally.  Example usage::

            template = SomeProcessTemplate(config.makeRoot())
            proxy, stub = template.spawn(self)
            if proxy is None:
                self.mainLoop.exitWith(stub)
            else:
                # ... do something with the proxy
        """















class ICheckableResource(Interface):

    """Objects that can be checked for availability/proper functioning."""

    def checkResource():

        """Check whether a resource is up/functioning correctly

        Return either None or a string describing the problem"""
































