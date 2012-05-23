from peak.api import *
from peak.config.interfaces import *

import testM1

__bases__ = testM1,

class FooThing:
    protocols.advise(
        instancesProvide=[IRule]
    )


class Referenced:
    M2 = 'M2'

class Referencer:
    containedClass = Referenced


class UnusedBase:
    M2 = 'M2'

from UserList import UserList

class RebindSub(UnusedBase, UserList):
    # This is a regression check for the previous behavior which would only
    # allow introduction of a single externally defined class into the
    # bases of a class...  It's also a check for failure to rebind a reference
    # to a base class which is defined in both a base and derived module, but
    # is used as a base class only in the derived module.  In other words,
    # testM2.RebindSub would inherit from the *uncombined* testM2.UnusedBase
    # when it should have inherited from the *combined* testM2.UnusedBase.
    pass


class BaseClass:
    foo = 2

class Subclass:

    class NestedSub:
        spam = 'Nested'




aGlobal1 = 'M2'

def aFunc2(aParam):
    return 'after(%s)' % __proceed__('before(%s)' % aParam)

config.setupModule()
