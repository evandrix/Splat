"""Zope Interface tests"""

from unittest import TestCase, makeSuite, TestSuite
from protocols import *

import protocols.zope_support
from zope.interface import Interface

# Dummy interfaces and adapters used in tests

class IA(Interface):  pass
class IB(IA): pass
class IPure(Interface):
    # We use this for pickle/copy tests because the other protocols
    # imply various dynamically created interfaces, and so any object
    # registered with them won't be picklable
    pass

class Picklable:
    # Pickling needs classes in top-level namespace
    pass

class NewStyle(object):
    pass

from checks import ImplementationChecks, makeClassTests, makeInstanceTests
from checks import ProviderChecks, BasicClassProvidesChecks
from checks import makeMetaClassProvidesTests, AdaptiveChecks

class BasicChecks(AdaptiveChecks, ImplementationChecks):
    IA = IA
    IB = IB
    Interface = Interface
    IPure = IPure

class InstanceChecks(AdaptiveChecks, ProviderChecks):
    IA = IA
    IB = IB
    Interface = Interface
    IPure = IPure

class ClassChecks(BasicClassProvidesChecks, ProviderChecks):
    IA = IA
    IB = IB
    Interface = Interface
    IPure = IPure

TestClasses = makeClassTests(BasicChecks)
TestClasses += makeMetaClassProvidesTests(ClassChecks)
TestClasses += makeInstanceTests(InstanceChecks,Picklable,NewStyle)

class IB(protocols.Interface):
    advise(protocolExtends = [IA])

class BasicChecks(AdaptiveChecks, ImplementationChecks):
    IA = IA
    IB = IB
    Interface = Interface
    IPure = IPure

class InstanceChecks(AdaptiveChecks, ProviderChecks):
    IA = IA
    IB = IB
    Interface = Interface
    IPure = IPure

class ClassChecks(AdaptiveChecks, BasicClassProvidesChecks, ProviderChecks):
    IA = IA
    IB = IB
    Interface = Interface
    IPure = IPure

TestClasses += makeClassTests(BasicChecks)
TestClasses += makeMetaClassProvidesTests(ClassChecks)
TestClasses += makeInstanceTests(InstanceChecks,Picklable,NewStyle)

def test_suite():
    return TestSuite([makeSuite(t,'check') for t in TestClasses])




