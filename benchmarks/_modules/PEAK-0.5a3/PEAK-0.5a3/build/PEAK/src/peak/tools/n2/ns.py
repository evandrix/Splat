"""
Namespace Interactor
"""

from peak.api import *
from commands import *
from interfaces import *
from peak.util.readline_stack import *





class NamingInteractor(binding.Component):

    """A shell-like interactor for namespaces"""

    shell = binding.Obtain('..')
    width = binding.Obtain('shell/width')

    def interact(self, object, shell):
        binding.suggestParentComponent(shell, None, object)

        self.run = 1

        pushRLHistory('.n2ns_history', self.complete, None, self.shell.environ)

        while self.run:
            try:
                cl = raw_input('[n2] ')
            except:
                print >>shell.stdout
                popRLHistory()
                return

            cl = cl.strip()
            if not cl or cl[0] == '#':
                continue

            cmdinfo = parseCmd(cl, shell)
            cmd = cmdinfo['argv'][0]

            cmdobj = getattr(self, 'cmd_' + cmd, None)
            if cmdobj is None:
                print >>cmdinfo['stderr'], "n2: %s: command not found. Try 'help'." % cmd
            else:
                cmdobj.run(
                    cmdinfo['stdin'], cmdinfo['stdout'], cmdinfo['stderr'],
                    cmdinfo['environ'], cmdinfo['argv']
                )

            # let files get closed, etc
            del cmdinfo

        popRLHistory()


    def stop(self):
        self.run = 0


    def command_names(self):
        return [k[4:] for k in dir(self) if k.startswith('cmd_')]


    def command(self, cmdname):
        return getattr(self, 'cmd_' + cmdname, None)


    def lookupRel(self, name, adaptTo, base=None):
        shell = self.shell

        if base is None:
            base = shell.get_pwd()

        if name is None:
            ob = base
        elif name[0] == '$':
            o = shell.getvar(name[1:])
            if type(o) is str:
                ob = base[name]
            else:
                ob = o
        else:
            ob = base[name]

        binding.suggestParentComponent(shell, None, ob)

        if adaptTo is None:
            aob = ob
        else:
            aob = adapt(ob, adaptTo, None)

        if aob is not None:
            binding.suggestParentComponent(shell, None, aob)

        return ob, aob


    class cmd_cd(ShellCommand):
        """cd [name-or-$var] -- change directory

        with name, change current context to one named
        without name, change current context back to startup context"""

        args = ('', 0, 1)

        def cmd(self, cmd, args, stderr, **kw):
            shell = self.shell
            interactor = self.interactor
            last = shell.get_pwd()

            if not args:
                c = shell.get_home()
                ob = adapt(c, naming.IBasicContext, None)
            else:
                try:
                    c, ob = interactor.lookupRel(args[0], naming.IBasicContext)
                except KeyError:
                    print >>stderr, '%s: %s: no such variable' % (cmd, args[0])
                    return
                except exceptions.NameNotFound:
                    print >>stderr, '%s: %s: not found' % (cmd, args[0])
                    return

            if ob is None:
                print >>stderr, '(not a context... using alternate handler)\n'

                shell.do_cd(c)
                shell.handle(c)
                shell.do_cd(last)
            else:
                shell.do_cd(ob)

    cmd_cd = binding.Make(cmd_cd)


    class ls_common(ShellCommand):
        """ls [-1|-l] [-s] [-R] [-r] [name-or-$var] -- list namespace contents

-1\tsingle column format
-l\tlong format (show object repr)
-R\trecursive listing
-r\treverse order
-s\tdon't sort list
name\tlist object named, else current context"""

        args = ('1lRrs', 0, 1)

        def cmd(self, cmd, opts, args, stdout, stderr, ctx=None, **kw):
            shell = self.shell
            interactor = self.interactor

            name = None
            if args:
                name = args[0]

            try:
                ob, ctx = interactor.lookupRel(name, naming.IReadContext, base=ctx)
            except KeyError:
                print >>stderr, '%s: %s: no such variable' % (cmd, args[0])
                return
            except exceptions.NameNotFound:
                print >>stderr, '%s: %s not found' % (cmd, args[0])
                return

            if ctx is None:
                if args:
                    print >>stdout, `ob`
                else:
                    print >>stderr, \
                        "naming.IReadContext interface not supported by object"
                return

            if '-l' in opts:
                w = self.shell.width
                l = [(str(k), `v`) for k, v in ctx.items()]
                if '-s' not in opts: l.sort()
                if '-r' in opts: l.reverse()
                kl = max([len(x[0]) for x in l])
                vl = max([len(x[1]) for x in l])
                if kl+vl >= w:
                    if kl < 40:
                        vl = w - kl - 2
                    elif vl < 40:
                        kl = w - vl - 2
                    else:
                        kl = 30; vl = w - kl - 2

                for k, v in l:
                    print >>stdout, k.ljust(kl)[:kl] + ' ' + v.ljust(vl)[:vl]

            elif '-1' in opts:
                l = [str(x) for x in ctx.keys()]
                if '-s' not in opts: l.sort()
                if '-r' in opts: l.reverse()
                print >>stdout, '\n'.join(l)
            else:
                l = [str(x) for x in ctx.keys()]
                shell.printColumns(stdout, l, '-s' not in opts, '-r' in opts)

            if '-R' in opts:
                for k, v in ctx.items():
                    v = adapt(v, naming.IReadContext, None)
                    if v is not None:
                        print >>stdout, '\n%s:\n' % str(k)

                        self.cmd(cmd, opts, [], stdout, stderr, ctx)

    class cmd_l(ls_common):
        """l [-s] [-R] [-r] [name] -- shorthand for ls -l. 'help ls' for more."""

        args = ('Rrs', 0, 1)

        def cmd(self, cmd, opts, args, stdout, stderr, **kw):
            opts['-l'] = None
            self.interactor.ls_common.cmd(
                self, cmd, opts, args, stdout, stderr, **kw)


    cmd_dir = binding.Make(ls_common)
    cmd_ls = binding.Make(ls_common)
    cmd_l = binding.Make(cmd_l)


    class cmd_pwd(ShellCommand):
        """pwd -- display current context"""

        def cmd(self, **kw):
            print `self.shell.get_pwd()`

    cmd_pwd = binding.Make(cmd_pwd)


    class cmd_python(ShellCommand):
        """python -- enter python interactor"""

        def cmd(self, **kw):
            self.shell.interact()

    cmd_py = binding.Make(cmd_python)
    cmd_python = binding.Make(cmd_python)


    class cmd_help(ShellCommand):
        """help [cmd] -- help on commands"""

        args = ('', 0, 1)

        def cmd(self, stdout, stderr, args, **kw):
            if args:
                c = self.interactor.command(args[0])
                if c is None:
                    print >>stderr, 'help: no such command: ' + args[0]
                else:
                    print c.__doc__
            else:
                print >>stdout, 'Available commands:\n'
                self.shell.printColumns(
                    stdout, self.interactor.command_names(), sort=1)


    cmd_help = binding.Make(cmd_help)


    class cmd_rm(ShellCommand):
        """rm name -- unbind name from context"""

        args = ('', 1, 1)

        def cmd(self, cmd, stderr, args, **kw):
            c = self.shell.get_pwd()
            c = adapt(c, naming.IWriteContext, None)
            if c is None:
                print >>stderr, '%s: context is not writeable' % cmd
                return

            try:
                del c[args[0]]
            except exceptions.NameNotFound:
                print >>stderr, '%s: %s: not found' % (cmd, args[0])

    cmd_rm = binding.Make(cmd_rm)


    class cmd_bind(ShellCommand):
        """bind name objectname-or-$var -- bind name in context to object"""

        args = ('', 2, 2)

        def cmd(self, cmd, stderr, args, **kw):
            c = self.shell.get_pwd()
            c = adapt(c, naming.IWriteContext, None)
            if c is None:
                print >>stderr, '%s: context is not writeable' % cmd
                return

            try:
                ob, aob = self.interactor.lookupRel(args[1], None)
            except KeyError:
                print >>stderr, '%s: %s: no such variable' % (cmd, args[1])
                return
            except exceptions.NameNotFound:
                print >>stderr, '%s: %s not found' % (cmd, args[1])
                return

            c.bind(args[0], ob)

    cmd_bind = binding.Make(cmd_bind)


    class cmd_ln(ShellCommand):
        """ln -s target name -- create LinkRef from name to target"""

        args = ('s', 2, 2)

        def cmd(self, cmd, stderr, args, **kw):
            c = self.shell.get_pwd()
            c = adapt(c, naming.IWriteContext, None)
            if c is None:
                print >>stderr, '%s: context is not writeable' % cmd
                return

            if '-s' not in args:
                print >>stderr, '%s: only symbolic links (LinkRefs) are supported' % (cmd, args[1])
                return

            c.bind(args[1], naming.LinkRef(args[2]))

    cmd_ln = binding.Make(cmd_ln)


    class cmd_mv(ShellCommand):
        """mv oldname newname -- rename oldname to newname"""

        args = ('', 2, 2)

        def cmd(self, cmd, stderr, args, **kw):
            c = self.shell.get_pwd()
            c = adapt(c, naming.IWriteContext, None)
            if c is None:
                print >>stderr, '%s: context is not writeable' % cmd
                return

            c.rename(args[0], args[1])

    cmd_mv = binding.Make(cmd_mv)


    class cmd_quit(ShellCommand):
        """quit -- leave n2 naming shell"""

        def cmd(self, **kw):
            self.interactor.stop()

    cmd_quit = binding.Make(cmd_quit)


    class cmd_ll(ShellCommand):
        """ll name -- lookupLink name"""

        args = ('', 1, 1)

        def cmd(self, stdout, args, **kw):
            c = self.shell.get_pwd()
            r = c.lookupLink(args[0])
            print `r`

    cmd_ll = binding.Make(cmd_ll)


    class cmd_commit(ShellCommand):
        """commit -- commit current transaction and begin a new one"""

        def cmd(self, **kw):
            storage.commit(self.shell)
            storage.begin(self.shell)

    cmd_commit = binding.Make(cmd_commit)


    class cmd_abort(ShellCommand):
        """abort -- roll back current transaction and begin a new one"""

        def cmd(self, **kw):
            storage.abort(self.shell)
            storage.begin(self.shell)

    cmd_abort = binding.Make(cmd_abort)


    class cmd_mksub(ShellCommand):
        """mksub name -- create a subcontext"""

        args = ('', 1, 1)

        def cmd(self, cmd, stderr, args, **kw):
            c = self.shell.get_pwd()
            c = adapt(c, naming.IWriteContext, None)
            if c is None:
                print >>stderr, '%s: context is not writeable' % cmd
                return

            c.mksub(args[0])

    cmd_md = binding.Make(cmd_mksub)
    cmd_mkdir = binding.Make(cmd_mksub)
    cmd_mksub = binding.Make(cmd_mksub)


    class cmd_rmsub(ShellCommand):
        """rmsub name -- remove a subcontext"""

        args = ('', 1, 1)

        def cmd(self, cmd, stderr, args, **kw):
            c = self.shell.get_pwd()
            c = adapt(c, naming.IWriteContext, None)
            if c is None:
                print >>stderr, '%s: context is not writeable' % cmd
                return

            c.rmsub(args[0])

    cmd_rd = binding.Make(cmd_rmsub)
    cmd_rmdir = binding.Make(cmd_rmsub)
    cmd_rmsub = binding.Make(cmd_rmsub)


    class cmd_show(ShellCommand):
        """show [varname] -- show variable varname, or list variables"""

        args = ('', 0, 1)

        def cmd(self, cmd, stdout, stderr, args, **kw):
            if args:
                try:
                    ob = self.shell.getvar(args[0])
                except KeyError:
                    print >>stderr, '%s: %s: no such variable' % (cmd, args[0])
                    return

                stdout.write(`ob` + '\n')
            else:
                self.shell.printColumns(
                    stdout, self.shell.listvars(), sort=1)

    cmd_show = binding.Make(cmd_show)


    class cmd_unset(ShellCommand):
        """unset varname -- delete variable"""

        args = ('', 1, 1)

        def cmd(self, cmd, stderr, args, **kw):
            self.shell.unsetvar(args[0])

    cmd_unset = binding.Make(cmd_unset)


    class cmd_set(ShellCommand):
        """set [-n] varname [$var|name|string] -- set variable
-n\ttreat non-variable value as a name to look up instead of as a string

An unspecified value sets varname to the current context."""

        args = ('n', 1, 2)

        def cmd(self, cmd, stderr, args, opts, **kw):
            if len(args) == 1 or args[1] == '$' or opts.has_key('-n'):
                try:
                    ob, aob = self.interactor.lookupRel((args + [None])[1], None)
                except KeyError:
                    print >>stderr, '%s: %s: no such variable' % (cmd, args[1])
                    return
                except exceptions.NameNotFound:
                    print >>stderr, '%s: %s not found' % (cmd, args[1])
                    return
            else:
                ob = args[1]

            try:
                self.shell.setvar(args[0], ob)
            except KeyError:
                print >>stderr, '%s: %s may not be set' % (cmd, args[0])

    cmd_set = binding.Make(cmd_set)



    def complete(self, s, state):
        if state == 0:
            import readline
            lb = readline.get_line_buffer()
            lbl = lb.lstrip()
            bidx = readline.get_begidx()
            if bidx <= (len(lb) - len(lbl)):
                self.matches = self.command_names()
            else:
                c = adapt(self.shell.get_pwd(), naming.IReadContext, None)
                if c is None:
                    self.matches = []
                else:
                    self.matches = [str(x) for x in c.keys()]

            self.matches = [x for x in self.matches if x.startswith(s)]

        try:
            return self.matches[state]
        except IndexError:
            return None




protocols.declareAdapter(
    lambda ns, proto: NamingInteractor(),
    provides = [IN2Interactor],
    forProtocols = [naming.IBasicContext]
)
