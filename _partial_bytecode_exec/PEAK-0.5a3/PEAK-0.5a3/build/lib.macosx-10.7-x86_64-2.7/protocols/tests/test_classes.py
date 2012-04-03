"""Tests for implementor declarations (i.e. instancesProvides)"""

from unittest import TestCase, makeSuite, TestSuite
from protocols import *
from checks import ImplementationChecks, AdaptiveChecks,  makeClassTests

class IA(Interface):  pass
class IB(IA): pass
class IPure(Interface):
    # We use this for pickle/copy tests because the other protocols
    # imply various dynamically created interfaces, and so any object
    # registered with them won't be picklable
    pass

class BasicChecks(AdaptiveChecks, ImplementationChecks):

    """PyProtocols-only class-instances-provide checks"""

    IA = IA
    IB = IB
    Interface = Interface
    IPure = IPure

    def checkChangingBases(self):

        # Zope and Twisted fail this because they rely on the first-found
        # __implements__ attribute and ignore a class' MRO/__bases__

        M1, M2 = self.setupBases(self.klass)
        m1 = self.make(M1)
        m2 = self.make(M2)
        declareImplementation(M1, instancesProvide=[self.IA])
        declareImplementation(M2, instancesProvide=[self.IB])
        self.assertM1ProvidesOnlyAandM2ProvidesB(m1,m2)
        self.assertChangingBasesChangesInterface(M1,M2,m1,m2)

TestClasses = makeClassTests(BasicChecks)

def test_suite():
    return TestSuite([makeSuite(t,'check') for t in TestClasses])

