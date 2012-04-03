from __future__ import generators
from config import VersionStore
from peak.api import *
from peak.running.commands import AbstractCommand, InvocationError
from getopt import getopt, GetoptError
import os.path

class VersionConfig(AbstractCommand):

    """A version configuration, comprising version schemes and modules"""

    modules = binding.Require('modules for versioning')
    schemes = binding.Require('list of version schemes used by modules')

    schemeMap = binding.Make(
        lambda self: dict(
            [(scheme.name.lower(), scheme) for scheme in self.schemes]
        )
    )

    datafile = binding.Make(
        lambda self: os.path.join(os.path.dirname(self.argv[0]),'version.dat')
    )

    versionStore = binding.Make(
        lambda self: VersionStore(self, filename = self.datafile)
    )

    parsedArgs = binding.Make(
        lambda self: getopt(
            self.argv[1:], 'nvhm:', ['dry-run', 'module=', 'verbose', 'help']
        )
    )

    options = binding.Make(lambda self: dict(self.parsedArgs[0]))
    args    = binding.Make(lambda self: self.parsedArgs[1])





    verbose = binding.Make(
        lambda self: '-v' in self.options or '--verbose' in self.options
    )

    dry_run = binding.Make(
        lambda self:
            '-n' in self.options or '--dry-run' in self.options or self.help
    )

    with_module = binding.Make(
        lambda self: self.options.get('-m') or self.options.get('--module')
    )

    help = binding.Make(
        lambda self: '-h' in self.options or '--help' in self.options
    )

    commands = ('show', 'check', 'incr', 'set')























    def _run(self):

        args = self.args

        if not args:
            if self.help:
                self.showHelp()
                return 0
            else:
                cmd = 'show'
        else:
            cmd = args[0]
            args = args[1:]

        if cmd not in self.commands:
            raise InvocationError("No such command: %s" % cmd)
        elif self.help:
            print >>self.stderr, getattr(self, cmd+'_usage')
            return 0

        storage.beginTransaction(self)
        try:
            getattr(self,cmd)(args)
        except:
            storage.abortTransaction(self)
            raise
        else:
            if self.dry_run:
                storage.abortTransaction(self)
            else:
                storage.commitTransaction(self)


    def iterModules(self):
        with_module = self.with_module
        for module in self.modules:
            if with_module and module.name != with_module:
                continue
            yield module


    def show(self, args):
        if not args:
            format = None
        elif len(args)>1:
            raise InvocationError("'show' command takes at most one format")
        else:
            format, = args

        for module in self.iterModules():
            version = module.currentVersion
            if format:
                version = version[format]
            if self.verbose or not self.with_module:
                print >>self.stdout, module.name, version
            else:
                self.stdout.write(str(version))


    def incr(self, args):
        if len(args)!=1:
            raise InvocationError("Must specify *one* part name to increment")
        for module in self.iterModules():
            print >>self.stderr, "Incrementing", module.name,
            print >>self.stderr, "from", module.currentVersion,
            module.incrVersion(args[0])
            print >>self.stderr, "to", module.currentVersion


    def check(self, args):
        if args:
            raise InvocationError("'check' command doesn't take arguments")
        for module in self.iterModules():
            print >>self.stderr, "Verifying", module.name,
            print >>self.stderr, "is at", module.currentVersion
            module.checkFiles()






    def set(self, args):

        if not args or [arg for arg in args if '=' not in arg]:
            raise InvocationError(
                "'set' requires 'name=value' arguments for each part"
                " you want to set."
            )

        items = [arg.split('=',1) for arg in args]
        for module in self.iterModules():
            print >>self.stderr, "Updating", module.name,
            print >>self.stderr, "from", module.currentVersion,
            module.setVersion(items)
            print >>self.stderr, "to", module.currentVersion


    options_help = """
Options:
    -h, --help                  show help for command
    -n, --dry-run               don't actually change any files
    -mMODULE, --module=MODULE   operate only on the module named MODULE
"""

    usage= binding.Make(
        lambda self: ("""
Usage: %s [options] command [arguments]
""" % self.cmdName) + self.options_help + ("""
Commands:
    show         display current version(s)
    check        verify version stamps in current files
    incr PART    increment version part named PART

    set PART=VALUE PART=VALUE...
        set version parts to specified values

For more help on a specific command, try '%s --help commandname'

""" % self.cmdName)
    )


    show_usage = binding.Make(
        lambda self: ("""
Usage: %s [options] show [format]
""" % self.cmdName) + self.options_help +
"""    -v, --verbose               display module names as well as versions

Display the current version(s) of all modules.  If a MODULE is specified
via -m or --module, display only that module's version info.

If the '-v' or '--verbose' flag is given (or no MODULE is specified), the
module name and a space will be output before each version, with a newline
after.  Otherwise, the version will be output by itself, without a newline,
so that it will be easier to use as input to another program.

If a format name is supplied as an argument to the 'show' command, module
versions will be displayed using that format.  Otherwise, module versions are
displayed using the default format for the module's version scheme.
""")

    check_usage = binding.Make(
        lambda self: ("""
Usage: %s [options] check
""" % self.cmdName) + self.options_help + """
Check all files containing version numbers, to verify that their contents are
as expected, given the current version of the module(s) concerned.
""")

    incr_usage = binding.Make(
        lambda self: ("""
Usage: %s [options] incr PART
""" % self.cmdName) + self.options_help + """
Increment the version part named PART, and update all files with the new
version information.
""")







    set_usage =  binding.Make(
        lambda self: ("""
Usage: %s [options] set PART=VALUE [PART=VALUE...]
""" % self.cmdName) + self.options_help + """
Set each named version part to the corresponding value, and update all files
with the new version information.
""")

    cmdName = binding.Make( lambda self: self.argv[0] )
































