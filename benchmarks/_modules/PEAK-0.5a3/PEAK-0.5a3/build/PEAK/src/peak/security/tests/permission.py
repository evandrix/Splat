"""Permission tests

TODO

 - Simple permission checks

 - Delegated permission

 - Varying algorithm by subject class

 - Global permission grant overrides local

"""

from unittest import TestCase, makeSuite, TestSuite
from peak.api import *
from peak.tests import testRoot


class ITestPermissionChecker(protocols.Interface):

    """Permission protocol for the tests"""

    protocols.advise(
        protocolIsSubsetOf = [security.IPermissionChecker]
    )


class TestInteraction(security.Interaction):
    user = None
    permissionProtocol = ITestPermissionChecker










class SimpleTests(TestCase):

    def setUp(self):
        self.interaction = TestInteraction()

    def checkUniversals(self):
        assert self.interaction.allows(
            None, permissionNeeded=security.Anybody
        )
        assert not self.interaction.allows(
            None, permissionNeeded=security.Nobody
        )





























class ManageAsset(security.Permission): pass
class ManageBatch(security.Permission): pass

class Worker(security.Permission): pass
class Manager(security.Permission): pass
class Shipper(security.Permission): pass
class Receiver(security.Permission): pass
class Owner(security.Permission): pass
class SelfOrManager(security.Permission): pass
class ShipmentViewer(security.Permission): pass

class Facility(object):

    security.allow(
        viewShipments = ShipmentViewer,
        manageWorkers = Manager,
    )

class Batch(object):
    security.allow(
        edit = ManageBatch,
        delete = Owner,
    )

class Shipment(Batch):
    security.allow(
        receiveShipment = Receiver,
        cancelShipment = Shipper
    )

class Asset(object):
    security.allow(
        edit = ManageAsset
    )

class Person(object):
    security.allow(
        edit = SelfOrManager
    )


class EquipmentRules(security.RuleSet):

    rules = Items(
        checkWorkerForShipment = [Worker.of(Shipment)],
        checkSupervisor = [Manager.of(Person)],
        checkSelfOrManager = [SelfOrManager],
        checkWorkerOrManager = [ManageAsset, ShipmentViewer],
        checkManageBatch = [ManageBatch],
        checkPermissionsInPlace = [Worker, Manager],
    )

    def checkWorkerForShipment(klass, attempt):
        return attempt.allows(attempt.subject.fromFacility,
            permissionNeeded=Worker
        ) or   attempt.allows(attempt.subject.toFacility,
            permissionNeeded=Worker
        ) or security.Denial(
            "You need to be a worker at either the origin or destination"
            " facility for this shipment."
        )

    def checkSupervisor(klass, attempt):
        return attempt.user is attempt.subject.supervisor

    def checkSelfOrManager(klass, attempt):
        return attempt.user in (attempt.subject,attempt.subject.supervisor)

    def checkWorkerOrManager(klass, attempt):
        return attempt.allows(
            permissionNeeded=Worker
        ) or attempt.allows(permissionNeeded=Manager) or security.Denial(
            "You need to be a worker or manager at the relevant facility"
        )








    def checkManageBatch(klass, attempt):
        return (
            attempt.allows(permissionNeeded=Owner) or
            attempt.allows(permissionNeeded=Worker) or
            attempt.allows(permissionNeeded=Manager) or
            security.Denial(
                "You must be the batch's owner, or a worker or manager at"
                " the relevant facility."
            )
        )

    def checkPermissionsInPlace(klass, attempt):
        return attempt.allows(
            attempt.subject.location    # check same permission for location
        )


























    rules += Items(
        checkShipper = [Shipper.of(Shipment)],
        checkReceiver = [Receiver.of(Shipment)],
        checkWorkerForFacility = [Worker.of(Facility)],
        checkManagerForFacility = [Manager.of(Facility)],
        checkBatchOwner = [Owner.of(Batch)],
        checkOtherOwner = [Owner],
    )

    def checkShipper(klass, attempt):
        return attempt.allows(attempt.subject.fromFacility,
            permissionNeeded=Worker
        )

    def checkReceiver(klass, attempt):
        return attempt.allows(attempt.subject.toFacility,
            permissionNeeded=Worker
        )

    def checkWorkerForFacility(klass, attempt):
        return attempt.user.facility is attempt.subject

    def checkManagerForFacility(klass, attempt):
        return attempt.user in attempt.subject.managers or security.Denial(
            "You must be a manager at the relevant facility"
        )

    def checkBatchOwner(klass, attempt):
        return attempt.user is attempt.subject.owner or security.Denial(
            "You must be the batch's owner"
        )

    def checkOtherOwner(klass, attempt):
        # Only batches have owners
        return False

EquipmentRules.declareRulesFor(ITestPermissionChecker)




NewYork = Facility()
NewYork.name = 'New York'
MrSmythe = Person()
Mickey = Person()

MrSmythe.name = 'Smythe'
MrSmythe.facility = NewYork
MrSmythe.supervisor = None

Mickey.name = 'Mickey D'
Mickey.facility = NewYork
Mickey.supervisor = MrSmythe

Paris = Facility()
Paris.name = 'Paris'
JeanPierre = Person()
BobChien = Person()

JeanPierre.name = 'J.P.'
JeanPierre.facility = Paris
JeanPierre.supervisor = None

BobChien.name = 'Bob le Chien'
BobChien.facility = Paris
BobChien.supervisor = JeanPierre

NewYork.managers = MrSmythe,
Paris.managers = JeanPierre,













Batch123 = Batch()
Batch123.name = 'Batch 123'
Batch123.location = NewYork
Batch123.owner = Mickey

MegaMachine = Asset()
MegaMachine.name = 'Mega Machine'
MegaMachine.location = Batch123

MegaDrive = Asset()
MegaDrive.name = 'Mega Drive'
MegaDrive.location = MegaMachine

Shipment16 = Shipment()
Shipment16.name = 'Shipment 16'
Shipment16.location = Paris
Shipment16.fromFacility = Paris
Shipment16.toFacility = NewYork
Shipment16.owner = BobChien

Thingy = Asset()
Thingy.name = 'Thingy'
Thingy.location = Shipment16


















scenarios = [

    (NewYork, 'viewShipments', [MrSmythe,Mickey]),
    (NewYork, 'manageWorkers', [MrSmythe]),
    (Paris, 'viewShipments', [JeanPierre,BobChien]),
    (Paris, 'manageWorkers', [JeanPierre]),

    (MrSmythe,'edit',[MrSmythe]),
    (Mickey,'edit',[Mickey,MrSmythe]),
    (JeanPierre,'edit',[JeanPierre]),
    (BobChien,'edit',[BobChien,JeanPierre]),

    (Shipment16,'cancelShipment',[JeanPierre,BobChien]),
    (Shipment16,'receiveShipment',[MrSmythe,Mickey]),
    (Shipment16,'edit',[MrSmythe, Mickey, JeanPierre, BobChien]),
    (Shipment16,'delete',[BobChien]),
    (Shipment16,'undefined',[]),

    (Thingy, 'edit', [MrSmythe, Mickey, JeanPierre, BobChien]),
    (MegaDrive, 'edit', [MrSmythe, Mickey]),
    (MegaMachine, 'edit', [MrSmythe, Mickey]),

    (Batch123, 'delete', [Mickey]),
    (Batch123, 'edit', [MrSmythe, Mickey]),
]

class ScenarioTests(TestCase):

    def assertAllowed(self, subject, name, users):
        for person in MrSmythe, Mickey, JeanPierre, BobChien:
            allowed = TestInteraction(user=person).allows(subject,name)
            assert not allowed==(person not in users), (
                "%s fails for %s.%s" % (person.name, subject.name, name)
            )

    def checkScenarios(self):
        for s in scenarios:
            self.assertAllowed(*s)



TestClasses = (
    SimpleTests, ScenarioTests
)


def test_suite():
    return TestSuite([makeSuite(t,'check') for t in TestClasses])


































