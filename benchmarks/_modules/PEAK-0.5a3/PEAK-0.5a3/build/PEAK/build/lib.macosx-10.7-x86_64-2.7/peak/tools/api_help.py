"""Implements the 'peak help' command"""

from peak.api import *
from peak.running.commands import AbstractCommand, InvocationError
from peak.util.imports import importString


class APIHelp(AbstractCommand):

    usage = """Usage: peak help name [name2 name3...]

For example, 'peak help core api' displays help on the
'peak.core' and 'peak.api' modules."""

    def _run(self):
        if len(self.argv)>1:
            for arg in self.argv[1:]:
                help(self.find(arg))
        else:
            raise InvocationError("No name(s) specified")





















    def find(self, name):
        if naming.URLMatch(name):
            ob = self.lookupComponent(name, NOT_FOUND)
            if ob is not NOT_FOUND:
                return ob
        try:
            name = str(PropertyName(name.replace(':','.')))
        except exceptions.InvalidName:
            raise InvocationError("Invalid format for argument %r" % name)

        for prefix in ('peak.api.','peak.',''):
            try:
                return importString(prefix+name)
            except ImportError:
                pass

        for prefix in ('peak.running.shortcuts.','peak.help.'):
            ob = self.lookupComponent(
                PropertyName('peak.running.shortcuts.'+name),
                NOT_FOUND
            )
            if ob is not NOT_FOUND:
                return ob

        raise InvocationError("Can't find help on %r" % name)
















