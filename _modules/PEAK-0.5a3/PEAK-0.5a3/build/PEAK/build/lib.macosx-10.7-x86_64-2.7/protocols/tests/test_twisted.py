"""Twisted Interface tests"""

from unittest import TestCase, makeSuite, TestSuite
from protocols import *

import protocols.twisted_support

from twisted.python.components import Interface

# Dummy interfaces and adapters used in tests

class IA(Interface):  pass
class IB(IA): pass
class IPure(Interface):
    # We use this for pickle/copy tests because the other protocols
    # imply various dynamically created interfaces, and so any object
    # registered with them won't be picklable
    pass

from checks import InstanceImplementationChecks, makeClassTests, ProviderChecks
from checks import makeInstanceTests, SimpleAdaptiveChecks

class Picklable:
    # Pickling needs classes in top-level namespace
    pass

class NewStyle(object):
    pass

class BasicChecks(SimpleAdaptiveChecks, InstanceImplementationChecks):
    IA = IA
    IB = IB
    Interface = Interface
    IPure = IPure

class InstanceChecks(ProviderChecks):
    IA = IA
    IB = IB
    Interface = Interface
    IPure = IPure

TestClasses = makeClassTests(BasicChecks)
TestClasses += makeInstanceTests(InstanceChecks,Picklable,NewStyle)

class IB(protocols.Interface):
    advise(protocolExtends = [IA])

class BasicChecks(InstanceImplementationChecks):
    IA = IA
    IB = IB
    Interface = Interface
    IPure = IPure

class InstanceChecks(ProviderChecks):
    IA = IA
    IB = IB
    Interface = Interface
    IPure = IPure

TestClasses += makeClassTests(BasicChecks)
TestClasses += makeInstanceTests(InstanceChecks,Picklable,NewStyle)

def test_suite():
    return TestSuite([makeSuite(t,'check') for t in TestClasses])


















