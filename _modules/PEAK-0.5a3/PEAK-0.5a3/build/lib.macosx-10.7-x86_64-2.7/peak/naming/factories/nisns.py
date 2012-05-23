from __future__ import generators
from peak.api import *
import nis


class nisURL(naming.URL.Base):

    supportedSchemes = 'nis',
    nameAttr = 'body'


class nisURLContext(naming.NameContext):

    protocols.advise(
        instancesProvide=[naming.IReadContext]
    )

    schemeParser = nisURL


    def __iter__(self):
        for map in nis.maps():
            yield self.compoundParser(map)


    def _get(self, name, retrieve=1):

        if not name:
            return self

        elif str(name) in nis.maps():
            return nisMapContext(
                namingAuthority = self.namingAuthority,
                nameInContext   = self.nameInContext + name,
            )

        else:
            return NOT_FOUND



class nisMapContext(naming.NameContext):

    protocols.advise(
        instancesProvide = [naming.IReadContext]
    )

    mapname = binding.Make(lambda self: str(self.nameInContext))


    def __iter__(self):
        for key in nis.cat(self.mapname):
            yield self.compoundParser(key)


    def _get(self, name, retrieve=1):

        try:
            return nis.match(str(name), self.mapname)

        except nis.error:
            return NOT_FOUND




















