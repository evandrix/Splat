from peak.api import *

# This is a regression test for a certain weird simulator behavior...
# Leave the next two lines in!

from types import StringType, FunctionType
StringType

# End special test


from peak.config.interfaces import *

class FooThing(binding.Component):
    protocols.advise(instancesProvide=[IConfigKey])


class Referenced:
    M1 = 'M1'

class Referencer:
    pass

class UnusedBase:
    M1 = 'M1'

class RebindSub(object):
    pass

class BaseClass:
    foo = 1

class Subclass(BaseClass):

    class Nested:
        bar = 'baz'

    class NestedSub(Nested):
        pass

aGlobal1 = 'M1'

def aFunc1():
    return aGlobal1

def aFunc2(aParam):
    return 'M1(%s)' % aParam

config.setupModule()
































