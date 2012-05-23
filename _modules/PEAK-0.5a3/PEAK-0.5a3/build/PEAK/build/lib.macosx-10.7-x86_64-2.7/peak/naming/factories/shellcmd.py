from peak.api import *
import os


class ShellCommandURL(naming.URL.Base):

    supportedSchemes = 'shellcmd',

    def __call__(self):
        return os.system(self.body)


class ShellCommandCtx(naming.AddressContext):

    schemeParser = ShellCommandURL

    def _get(self, name, retrieve=True):
        # All syntactically valid addresses exist in principle
        return name



