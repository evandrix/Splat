"""Tests for default IOpenProvider (etc.) adapters

  TODO:

    - Test Zope interface registrations

"""

from unittest import TestCase, makeSuite, TestSuite
from protocols import *
from checks import ProviderChecks, AdaptiveChecks, ClassProvidesChecks
from checks import makeClassProvidesTests, makeInstanceTests
from checks import makeMetaClassProvidesTests

class IA(Interface):  pass
class IB(IA): pass
class IPure(Interface):
    # We use this for pickle/copy tests because the other protocols
    # imply various dynamically created interfaces, and so any object
    # registered with them won't be picklable
    pass


class BasicChecks(AdaptiveChecks, ProviderChecks):

    """Checks to be done on every object"""

    IA = IA
    IB = IB
    Interface = Interface
    IPure = IPure


class ClassChecks(ClassProvidesChecks, BasicChecks):

    """Checks to be done on classes and types"""





class InstanceConformChecks:
    """Things to check on adapted instances"""

    def checkBadConform(self):
        def __conform__(proto):
            pass
        self.ob.__conform__ = __conform__
        self.assertBadConform(self.ob, [self.IA], __conform__)


    def assertBadConform(self, ob, protocols, conform):
        try:
            adviseObject(ob, provides=protocols)
        except TypeError,v:
            assert v.args==(
                "Incompatible __conform__ on adapted object", ob, conform
            ), v.args
        else:
            raise AssertionError("Should've detected invalid __conform__")


class ClassConformChecks(InstanceConformChecks):
    """Things to check on adapted classes"""

    def checkInheritedConform(self):
        class Base(self.ob):
            def __conform__(self,protocol): pass

        class Sub(Base): pass
        self.assertBadConform(Sub, [self.IA], Base.__conform__.im_func)


    def checkInstanceConform(self):

        class Base(self.ob):
            def __conform__(self,protocol): pass

        b = Base()
        self.assertBadConform(b, [self.IA], b.__conform__)


class AdviseMixinInstance(BasicChecks):

    def setUp(self):
        self.ob = ProviderMixin()


# Notice that we don't test the *metaclass* of the next three configurations;
# it would fail because the metaclass itself can't be adapted to an open
# provider, because it has a __conform__ method (from ProviderMixin).  For
# that to work, there'd have to be *another* metalevel.

class AdviseMixinMultiMeta1(BasicChecks):

    def setUp(self):
        class Meta(ProviderMixin, type): pass
        class Test(ProviderMixin,object): __metaclass__ = Meta
        self.ob = Test()


class InstanceTestsBase(BasicChecks, InstanceConformChecks):
    pass

class ClassTestsBase(ClassChecks, ClassConformChecks):
    pass

class Picklable:
    # Pickling needs classes in top-level namespace
    pass

class NewStyle(object):
    pass

TestClasses = (
    AdviseMixinInstance, AdviseMixinMultiMeta1,
)

TestClasses += makeMetaClassProvidesTests(ClassChecks)
TestClasses += makeClassProvidesTests(ClassTestsBase)
TestClasses += makeInstanceTests(InstanceTestsBase,Picklable,NewStyle)


def test_suite():
    return TestSuite([makeSuite(t,'check') for t in TestClasses])







































