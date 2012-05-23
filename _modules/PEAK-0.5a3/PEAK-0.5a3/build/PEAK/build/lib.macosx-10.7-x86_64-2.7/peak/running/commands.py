"""Base classes for Main Programs (i.e. processes invoked from the OS)"""
from __future__ import generators
from peak.api import *
from interfaces import *
from peak.util.imports import importObject
from os.path import isfile
import sys, os
from types import ClassType, FunctionType

__all__ = [
    'AbstractCommand', 'AbstractInterpreter', 'IniInterpreter', 'EventDriven',
    'ZConfigInterpreter', 'Bootstrap', 'rerunnableAsFactory',
    'callableAsFactory', 'appAsFactory', 'InvocationError', 'CGICommand',
    'CGIInterpreter', 'FastCGIAcceptor', 'Alias', 'runMain',
    'lookupCommand', 'NoSuchSubcommand', 'InvalidSubcommandName',
    'ErrorSubcommand',
]


class InvocationError(Exception):
    """Problem with command arguments or environment"""


def lookupCommand(component,name,default,acceptURLs=False):

    """Lookup 'name' as a command shortcut or URL; may raise InvalidName"""

    if not naming.URLMatch(name):
        # may raise exceptions.InvalidName
        name = PropertyName('peak.running.shortcuts.'+name)

    elif not acceptURLs:
        raise exceptions.InvalidName("URL not allowed")

    return adapt(name, binding.IComponentKey).findComponent(
        component, default
    )




def runMain(factory):
    """Use 'factory' to create and run a "main" program

    'factory' must be adaptable to 'ICmdLineApp', 'ICmdLineAppFactory', or
    'IMainCmdFactory'.  In each case, it will be used to create and run a
    "main program", whose 'run()' method's return code will be passed to
    'sys.exit()'.  Example usage::

        from peak.running import commands

        class MyCommand(commands.AbstractCommand):
            def _run(self):
                print "Hello world!"

        if __name__ == '__main__':
            commands.runMain(MyCommand)

    To support "child processes" created with PEAK's process management tools,
    this function will check the 'run()' method's return code to see if it is
    another 'ICmdLineApp', 'ICmdLineAppFactory', or 'IMainCmdFactory'.  If so,
    it will create and run a new "main program" based on that result, after
    allowing the previous "main program" to be garbage collected.  This looping
    will continue until 'run()' returns a non-command object."""

    try:
        factory = adapt(factory,IMainCmdFactory)

        while True:
            result = factory().run()
            factory = adapt(result,IMainCmdFactory,None)

            if factory is None:
                # Not an app, so don't tail-recurse
                sys.exit(result)

            result = None   # allow result to be GC'd

    finally:
        # Ensure that commands don't leak
        result = factory = None

def appAsMainFactory(ob,proto):
    """Build 'IMainCmdFactory' that just returns an existing app object"""
    factory = lambda: ob
    protocols.adviseObject(factory, provides=[IMainCmdFactory])
    return factory

protocols.declareAdapter(
    appAsMainFactory,
    provides=[IMainCmdFactory],
    forProtocols=[ICmdLineApp]
)


def factoryAsMainFactory(ob,proto):
    """Build 'IMainCmdFactory' that creates a config root per-invocation"""
    factory = lambda: ob(config.makeRoot())
    protocols.adviseObject(factory, provides=[IMainCmdFactory])
    return factory

protocols.declareAdapter(
    factoryAsMainFactory,
    provides=[IMainCmdFactory],
    forProtocols=[ICmdLineAppFactory]
)

















class AbstractCommand(binding.Component):
    """Simple, commandline-driven process"""

    protocols.advise(
        instancesProvide = [ICmdLineApp],
        classProvides    = [ICmdLineAppFactory]
    )

    argv    = binding.Obtain(ARGV,    offerAs=[ARGV])
    stdin   = binding.Obtain(STDIN,   offerAs=[STDIN])
    stdout  = binding.Obtain(STDOUT,  offerAs=[STDOUT])
    stderr  = binding.Obtain(STDERR,  offerAs=[STDERR])
    environ = binding.Obtain(ENVIRON, offerAs=[ENVIRON])
    commandName = None

    def _run(self):
        """Override this in subclasses to implement desired behavior"""
        raise NotImplementedError

    usage = """
Either this is an abstract command class, or somebody forgot to
define a usage message for their subclass.
"""

    def showHelp(self):
        """Display usage message on stderr"""
        print >>self.stderr, self.usage
        return 0


    def isInteractive(self):
        """True if 'stdin' is a terminal"""
        try:
            isatty = self.stdin.isatty
        except AttributeError:
            return False
        else:
            return isatty()

    isInteractive = binding.Make(isInteractive)

    def getSubcommand(self, executable, **kw):

        """Return a 'ICmdLineApp' with our environment as its defaults

        Any 'IExecutable' may be supplied as the basis for creating
        the 'ICmdLineApp'.  'NotImplementedError' is raised if the
        supplied object is not an 'IExecutable'.
        """

        factory = adapt(executable,ICmdLineAppFactory)

        for k in 'argv stdin stdout stderr environ'.split():
            if k not in kw:
                kw[k]=getattr(self,k)

        if 'parentComponent' not in kw:
            kw['parentComponent'] = self.getCommandParent()

        return factory(**kw)


    def _invocationError(self, msg):

        """Write msg and usage to stderr if interactive, otherwise re-raise"""

        if self.isInteractive:
            self.showHelp()
            print >>self.stderr, '\n%s: %s\n' % (self.argv[0], msg)
            # XXX output last traceback frame?
            return 1    # exit errorlevel
        else:
            raise   # XXX is this really appropriate?

    def getCommandParent(self):
        """Get or create a component to be used as the subcommand's parent"""
        # Default is to use the interpreter as the parent
        return self




    def run(self):

        """Run the command"""

        try:
            return self._run() or 0

        except SystemExit, v:
            return v.args[0]

        except InvocationError, msg:
            return self._invocationError(msg)



class ErrorSubcommand(AbstractCommand):
    """Subcommand that displays an error/usage message"""

    usage = binding.Obtain('usage', default="")

    msg = "Undefined error"

    def _run(self):
        raise InvocationError(self.msg)


class NoSuchSubcommand(ErrorSubcommand):
    """Subcommand that says there's no such command"""

    msg = "No such subcommand"


class InvalidSubcommandName(ErrorSubcommand):
    """Subcommand that says its command name is invalid"""

    msg = "Invalid subcommand name"





class AbstractInterpreter(AbstractCommand):

    """Creates and runs a subcommand by interpreting 'argv[1]'"""

    subCmdArgs = binding.Make(
        lambda self: self.argv[1:], offerAs=[ARGV]
    )

    def _run(self):
        """Interpret argv[1] and run it as a subcommand"""

        if len(self.argv)<2:
            raise InvocationError("missing argument(s)")

        return self.interpret(self.argv[1]).run()


    def interpret(self, argument):
        """Interpret the argument and return a subcommand object"""
        raise NotImplementedError


    def getSubcommand(self, executable, **kw):
        """Same as for AbstractCommand, but with shifted 'argv'"""

        if 'argv' not in kw:
            kw['argv'] = self.subCmdArgs

        return super(AbstractInterpreter,self).getSubcommand(executable, **kw)


    def commandName(self):
        """Basename of the file being interpreted"""    # XXX ???
        from os.path import basename
        return basename(self.argv[1])

    commandName = binding.Make(commandName)




    def __call__(klass, *__args, **__kw):

        """(Meta)class method: try to return the interpreted subcommand"""

        # First, create the instance we'd ordinarily return:
        cmd = klass.__new__(klass, *__args, **__kw)
        cmd.__init__(*__args, **__kw)

        if len(cmd.argv)<2:
            # No args, we can't do this.  Return the actual
            # command instance, which will then fail at _run()
            # time.  A bit kludgy, but it works.
            return cmd

        # Return the subcommand instance in place of the interpreter instance
        try:
            return cmd.interpret(cmd.argv[1])
        except InvocationError:
            return cmd

    __call__ = binding.classAttr(__call__)




















class IniInterpreter(AbstractInterpreter):

    """Interpret an '.ini' file as a command-line app

    The supplied '.ini' file must supply a 'running.IExecutable' as the
    value of its 'peak.running.app' property.  The supplied 'IExecutable'
    will be run with the remaining command line arguments."""

    def interpret(self, filename):

        """Interpret file as an '.ini' and run the command it specifies"""

        if not isfile(filename):
            raise InvocationError("Not a file:", filename)

        cfg = config.ServiceArea(self.getCommandParent())
        config.loadConfigFile(cfg, filename)

        # Set up a command factory based on the configuration setting

        executable = importObject(
            config.lookup(cfg, 'peak.running.app', None)
        )

        if executable is None:
            raise InvocationError(
                "%s doesn't specify a 'peak.running.app'"% filename
            )

        # Now create and return the subcommand
        return self.getSubcommand(executable,parentComponent=cfg)










    usage="""
Usage: peak runIni CONFIG_FILE arguments...

CONFIG_FILE should be a file in the format used by 'peak.ini'.  (Note that
it does not have to be named with an '.ini' extension.)  The file should
define a 'running.IExecutable' for the value of its 'peak.running.app'
property.  The specified 'IExecutable' will then be run with the remaining
command-line arguments.
"""



class ZConfigInterpreter(AbstractInterpreter):

    """Load a ZConfig schema and run it as a sub-interpreter"""

    def interpret(self, filename):

        from peak.naming.factories.openable import FileURL
        url = naming.toName(filename, FileURL.fromFilename)

        return self.getSubcommand(
            self.lookupComponent('zconfig.schema:'+str(url))
        )

















class CallableAsCommand(AbstractCommand):

    """Adapts callables to 'ICmdLineApp'"""

    invoke = binding.Require("Any callable")

    def _run(self):

        old = sys.stdin, sys.stdout, sys.stderr, os.environ, sys.argv

        try:
            # Set the global environment to our local environment
            for v in 'stdin stdout stderr argv'.split():
                setattr(sys,v,getattr(self,v))

            os.environ = self.environ
            return self.invoke()

        finally:
            # Ensure it's back to normal when we leave
            sys.stdin, sys.stdout, sys.stderr, os.environ, sys.argv = old


class RerunnableAsCommand(AbstractCommand):

    """Adapts 'IRerunnable' to 'ICmdLineApp'"""

    runnable = binding.Require("An IRerunnable")

    def _run(self):
        return self.runnable.run(
            self.stdin, self.stdout, self.stderr, self.environ, self.argv
        )








def callableAsFactory(ob,proto=None):

    """Convert a callable object to an 'ICmdLineAppFactory'"""

    if not callable(ob):
        return None

    def factory(parentComponent=NOT_GIVEN, componentName=None, **kw):
        if parentComponent is not NOT_GIVEN:
            kw['parentComponent']=parentComponent
        if componentName is not None:
            kw['componentName']=componentName
        kw.setdefault('invoke',ob)
        return CallableAsCommand(**kw)

    protocols.adviseObject(factory, provides=[ICmdLineAppFactory])
    return factory


def appAsFactory(app,proto=None):

    """Convert an 'ICmdLineApp' to an 'ICmdLineAppFactory'"""

    def factory(parentComponent=NOT_GIVEN, componentName=None, **kw):
        if parentComponent is not NOT_GIVEN:
            kw['parentComponent']=parentComponent
        if componentName is not None:
            kw['componentName']=componentName
        kw.setdefault('invoke',app.run)
        return CallableAsCommand(**kw)

    protocols.adviseObject(factory, provides=[ICmdLineAppFactory])
    return factory








def rerunnableAsFactory(runnable,proto=None):

    """Convert an 'IRerunnable' to an 'ICmdLineAppFactory'"""

    def factory(parentComponent=NOT_GIVEN, componentName=None, **kw):
        if parentComponent is not NOT_GIVEN:
            kw['parentComponent']=parentComponent
        if componentName is not None:
            kw['componentName']=componentName
        kw.setdefault('runnable',runnable)
        return RerunnableAsCommand(**kw)

    protocols.adviseObject(factory, provides=[ICmdLineAppFactory])
    return factory


protocols.declareAdapter(
    callableAsFactory,
    provides=[ICmdLineAppFactory],
    forTypes=[object]
)

protocols.declareAdapter(
    appAsFactory,
    provides=[ICmdLineAppFactory],
    forProtocols=[ICmdLineApp]
)

protocols.declareAdapter(
    rerunnableAsFactory,
    provides=[ICmdLineAppFactory],
    forProtocols=[IRerunnable]
)








class TestRunner(CallableAsCommand):

    defaultTest = 'peak.tests.test_suite'
    testModule  = None

    def invoke(self):

        from unittest import main

        main(
            module = self.testModule,
            argv = self.argv,
            defaultTest = self.defaultTest
        )

        return 0

























class Bootstrap(AbstractInterpreter):

    """Invoke and use an arbitrary 'IExecutable' object

    This class is designed to allow specification of an arbitrary
    name or URL on the command line to retrieve and invoke the
    designated object.

    If the name is not a scheme-prefixed URL, it is first converted to
    a name in the 'peak.running.shortcuts' configuration property namespace,
    thus allowing simpler names to be used.  For example, 'runIni' is a
    shortcut for '"import:peak.running.commands:IniInterpreter"'.  If you
    use a sitewide PEAK_CONFIG file, you can add your own shortcuts to
    the 'peak.running.shortcuts' namespace.  (See the 'peak.ini' file for
    current shortcuts, and examples of how to define them.)

    The object designated by the name or URL in 'argv[1]' must be an
    'IExecutable'; that is to say it must implement one of the 'IExecutable'
    sub-interfaces, or else be callable without arguments.  (See the
    'running.IExecutable' interface for more details.)

    Here's an example bootstrap script (which is installed as the 'peak'
    script by the PEAK distribution on 'posix' operating systems)::

        #!/usr/bin/env python2.2

        from peak.running.commands import Bootstrap
        from peak.api import config
        import sys

        sys.exit(
            Bootstrap(
                config.makeRoot()
            ).run()
        )

    The script above will look up its first supplied command line argument,
    and then invoke the found object as a command, supplying the remaining
    command line arguments.
    """

    acceptURLs = True

    def interpret(self, name):

        try:
            factory = lookupCommand(
                self, name, default=NoSuchSubcommand,
                acceptURLs=self.acceptURLs
            )
        except exceptions.InvalidName:
            factory = InvalidSubcommandName

        try:
            return self.getSubcommand(factory)

        except NotImplementedError:
            raise InvocationError(
                "Invalid command object", factory, "found at", name
            )






















    usage = """
Usage: peak NAME_OR_URL arguments...

The 'peak' script bootstraps and runs a specified command object or command
class.  The NAME_OR_URL argument may be a shortcut name defined in the
'peak.running.shortcuts' property namespace, or a URL of a type
supported by 'peak.naming'.  For example, if you have a class 'MyAppClass'
defined in 'MyPackage', you can use:

    peak import:MyPackage.MyAppClass

to invoke it.  Arguments to the found object are shifted left one position,
so in the example above it will see 'import:MyPackage.MyAppClass' as its
'argv[0]'.

The named object must implement one of the 'peak.running' command interfaces,
or be callable.  See the 'Bootstrap' class in 'peak.running.commands' for
more details on creating command objects for use with 'peak'.  For the
list of available shortcut names, see '%s'""" % config.fileNearModule(
        'peak','peak.ini'
    )

    if 'PEAK_CONFIG' in os.environ:
        usage += " and '%s'" % os.environ['PEAK_CONFIG']

    usage += ".\n"


    def showHelp(self):
        """Display usage message on stderr"""
        print >>self.stderr, self.usage
        from peak.util.columns import lsFormat

        print >>self.stderr, "Available commands:"
        print >>self.stderr
        self.stderr.writelines(lsFormat(80,config.Namespace('peak.running.shortcuts',self).keys()))
        print >>self.stderr
        return 0



class Alias(binding.Component):

    """A factory for executables that aliases some other command"""

    protocols.advise(
        instancesProvide = [ICmdLineAppFactory]
    )

    command = binding.Require("list of args to prepend")

    def __call__(self, parentComponent=NOT_GIVEN, componentName=None, **kw):

        argv = list(kw.setdefault('argv',sys.argv)[:])
        argv[1:1] = list(self.command[:])   # insert alias
        kw['argv'] = argv

        return Bootstrap(parentComponent, componentName, **kw)
























class EventDriven(AbstractCommand):

    """Run an event-driven main loop after setup"""

    stopAfter = binding.Obtain(
        PropertyName('peak.running.stopAfter'),   default=0
    )
    idleTimeout = binding.Obtain(
        PropertyName('peak.running.idleTimeout'), default=0
    )
    runAtLeast = binding.Obtain(
        PropertyName('peak.running.runAtLeast'),  default=0
    )

    mainLoop = binding.Obtain(IMainLoop)

    # Placeholder to allow adding components via ZConfig
    components = binding.Make(lambda: None)

    def _run(self):

        """Perform setup, then run the event loop until done"""

        return self.mainLoop.run(
            self.stopAfter,
            self.idleTimeout,
            self.runAtLeast
        )

        # XXX we should probably log start/stop events











class FastCGIAcceptor(binding.Component):

    """Accept FastCGI connections"""

    command  = binding.Require("IRerunnableCGI command object")
    eventLoop= binding.Obtain(events.IEventLoop)
    mainLoop = binding.Obtain(IMainLoop)
    ping     = binding.Obtain('mainLoop/activityOccurred')
    log      = binding.Obtain('logger:fastcgi')
    fcgi     = binding.Obtain('import:fcgiapp')
    accept   = binding.Obtain('fcgi/Accept')
    finish   = binding.Obtain('fcgi/Finish')


    def __onStart(self):

        readable = self.eventLoop.readable(0)   # FastCGI is always on 'stdin'

        while True:

            yield readable; events.resume()

            self.ping()
            i,o,e,env = self.accept()

            try:
                self.command.runCGI(i,o,e,dict(env))

            except:
                self.log.exception("Unexpected error handling request:")

            self.finish()
            self.ping()

    __onStart = binding.Make(events.taskFactory(__onStart), uponAssembly=True)






class CGICommand(EventDriven):

    """Run CGI/FastCGI in an event-driven loop

    If the 'fcgiapp' module is available and 'sys.stdin' is a socket, this
    command will listen for FastCGI connections and process them as they
    arrive.  Otherwise, it will assume that it is being run as a CGI, and
    use its environment attributes as the environment for the CGI command.

    Note that if running in CGI mode, 'CGICommand' will exit immediately
    upon completion of the request, without running an event loop at all.

    To use this class, you must define the value of 'cgiCommand', which must
    be an 'IRerunnableCGI'.
    """

    cgiCommand = binding.Require(
        "IRerunnableCGI to invoke on each hit", adaptTo = IRerunnableCGI
    )

    newAcceptor  = FastCGIAcceptor


    def _run(self):

        if self.isFastCGI():
            # Create the acceptor
            self.newAcceptor(self, command=self.cgiCommand)

            # and run the event loop
            return super(CGICommand,self)._run()

        else:
            # do plain CGI
            return self.cgiCommand.runCGI(
                self.stdin, self.stdout, self.stderr, self.environ, self.argv
            )




    def isFastCGI(self):

        """Check for 'fcgiapp' and whether 'sys.stdin' is a listener socket"""

        try:
            import fcgiapp
        except ImportError:
            return False    # Assume no FastCGI if module not present

        import socket, sys

        for family in (socket.AF_UNIX, socket.AF_INET):
            try:
                s=socket.fromfd(self.stdin.fileno(),family,socket.SOCK_STREAM)
                if not s.getsockname():
                    # Socket doesn't have an address; it might be a BSD-style
                    # socketpair() pipe, as used on Mac OS/X and others
                    continue
            except:
                pass
            else:
                return True

        return False

















class CGIInterpreter(Bootstrap):
    """Run an application as a CGI, by adapting it to IRerunnableCGI"""

    cgiWrapper = CGICommand
    usage = """
Usage: peak CGI NAME_OR_URL arguments...

Run NAME_OR_URL as a CGI application, by adapting it to the
'running.IRerunnableCGI' interface, and then using a 'commands.CGICommand'
to invoke it.
"""

    def interpret(self,filename):

        name = filename

        ob = lookupCommand(
            self, name, default=NOT_FOUND, acceptURLs=self.acceptURLs
        )

        if ob is NOT_FOUND:
            raise InvocationError("Name not found: %s" % name)

        # Is it a component factory?  If so, try to instantiate it first.
        factory = adapt(ob, binding.IComponentFactory, None)

        if factory is ob:   # XXX ???
            ob = factory(self, 'cgi')

        cgi = adapt(ob, IRerunnableCGI, None)

        if cgi is not None:
            return self.cgiWrapper(self, cgiCommand = cgi, argv=self.argv[:1])

        raise InvocationError(
            "Can't convert", ob, "to CGI; found at", name
        )




