"""N2 Main Program"""

from peak.api import *
from peak.running.commands import AbstractCommand, InvocationError
from peak.util.readline_stack import *
from peak.util.imports import importString
from peak.util.columns import lsFormat

import sys, os, code, __main__
from getopt import getopt, GetoptError

from interfaces import *
import ns, sql

class N2(AbstractCommand):

    # We put this here so help(n2) will work in the interpreter shell

    """PEAK and pdb are already imported for you.
c is bound to the object you looked up, or the initial context.

cd(x)\t\tlike c = c[x]
cd()\t\tsets c back to the original value
pwd\t\tinfo about c
ls()\t\tshow contents of c
"""

    usage = """usage: peak n2 [-e] [-p] [-I interface] [name]

-e\tif name lookup fails, go into python interactor anyway
-p\tuse python interactor even if there is a more specific interactor
-I\tadapt looked-up object to interface specified as an import string
\t(implies -e)"""

    idict = __main__.__dict__
    width = 80    # XXX screen width


    def _run(self):
        try:
            opts, args = getopt(self.argv[1:], 'epI:')
            self.opts = dict(opts)
        except GetoptError, msg:
            raise InvocationError(msg)

        if len(args) > 1:
            raise InvocationError('too many arguments')


        cprt = 'Type "copyright", "credits" or "license" for more information.'
        help = 'Type "help" or "help(n2)" for help.'

        self.banner = 'PEAK N2 (Python %s on %s)\n%s\n%s' % (
            sys.version.split(None, 1)[0], sys.platform, cprt, help)

        self.idict['n2'] = self

        exec 'from peak.api import *' in self.idict
        exec 'import pdb' in self.idict

        for cmd in ('cd','ls'):
            self.idict[cmd] = getattr(self, 'py_' + cmd)

        storage.begin(self)

        try:
            if args:
                c = naming.lookup(self, args[0])
            else:
                c = naming.InitialContext(self)

            iface = self.opts.get('-I')
            if iface is not None:
                iface = importString(iface)
                c = adapt(c, iface)
        except:
           if self.opts.has_key('-p') or self.opts.has_key('-e'):
                c = None
                sys.excepthook(*sys.exc_info()) # XXX
                print >>self.stderr
           else:
                raise

        self.idict['c'] = self.idict['__c__'] = c
        self.idict['pwd'] = `c`

        self.handle(c)

        try:
            storage.abort(self)
        except:
            pass

        return 0


    def get_pwd(self):
        return self.idict['c']


    def get_home(self):
        return self.idict['__c__']


    def execute(self, code):
        exec code in self.idict


    def getvar(self, var, default=NOT_GIVEN):
        v = self.idict.get(var, default)
        if v is NOT_GIVEN:
            raise KeyError, var
        else:
            return v


    def setvar(self, var, val):
        if var == 'c':
            raise KeyError, "can't change protected variable"

        self.idict[var] = val


    def unsetvar(self, var):
        if var == 'c':
            raise KeyError, "can't change protected variable"

        try:
            del self.idict[var]
        except:
            pass

    def listvars(self):
        return self.idict.keys()


    def do_cd(self, c):
        self.idict['c'] = c
        self.idict['pwd'] = r = `c`


    def __repr__(self):
        return self.__doc__


    def interact(self, c=NOT_GIVEN, n2=NOT_GIVEN):
        if c is NOT_GIVEN:
            c = self.get_pwd()

        if n2 is NOT_GIVEN:
            n2 = self

        b = self.banner
        if c is not None:
            b += '\n\nc = %s\n' % `c`

        pushRLHistory('.n2_history', True, None, self.environ)
        code.interact(banner=b, local=self.idict)
        popRLHistory()


    def handle(self, c):
        if self.opts.has_key('-p'):
            interactor = self
        else:
            binding.suggestParentComponent(self, None, c)
            interactor = adapt(c, IN2Interactor, self)
            binding.suggestParentComponent(self, None, interactor)

        interactor.interact(c, self)


    # Extra builtins in the python shell

    def py_cd(self, arg=None):
        if arg is None:
            c = self.idict['__c__']
        else:
            c = self.idict['c']
            c = c[arg]

        self.do_cd(c)

        print >>self.stdout, 'c = %s' % self.idict['pwd']


    def py_ls(self):
        c = self.idict['c']
        c = adapt(c, naming.IReadContext, None)
        if c is None:
            print >>self.stderr, "c doesn't support the IReadContext interface."
        else:
            for k in c.keys():
                print >>self.stdout, str(k)


    def printColumns(self, stdout, l, sort=True, rev=False):
        stdout.writelines(lsFormat(self.width, l, sort=sort, reverse=rev))
