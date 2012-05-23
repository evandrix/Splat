"""Tests for uuid"""

from unittest import TestCase, makeSuite, TestSuite
from peak.util.uuid import *


class UUIDTests(TestCase):

    def checkUnique(self):

        generated = {}

        for i in range(100):

            u = UUID()
            assert u not in generated
            generated[u]=1


    def checkCompare(self):

        assert NIL_UUID == '00000000-0000-0000-0000-000000000000'
        assert DNS_NS   == '6ba7b810-9dad-11d1-80b4-00c04fd430c8'
        assert URL_NS   == '6ba7b811-9dad-11d1-80b4-00c04fd430c8'
        assert OID_NS   == '6ba7b812-9dad-11d1-80b4-00c04fd430c8'
        assert X500_NS  == '6ba7b814-9dad-11d1-80b4-00c04fd430c8'


    def checkForced(self):
        u = UUID(nodeid='deaf1234feed')
        assert u.endswith('deaf1234feed')










    def checkNS(self):

        # Verify that NS-generated UUIDs are consistent for
        # a namespace and name, and that they don't collide
        # within or across namespaces.  This is far from an
        # exhaustive test, but it'll do for detecting any
        # obvious breakage in the uuid module.

        keys = globals().keys()
        last = {}

        ns1, ns2 = UUID(), UUID()

        for t in range(5):

            all = {}
            this = {}

            for ns in URL_NS, DNS_NS, OID_NS, X500_NS, NIL_UUID, ns1, ns2:

                for k in keys:

                    u = UUID(name=k, ns=URL_NS)

                    # check collisions against any namespace
                    assert u not in all

                    if last:
                        # check consistent generation
                        assert last[k,ns]==u

                    this[k,ns] = u

            last = this







TestClasses = (
    UUIDTests,
)

def test_suite():
    return TestSuite([makeSuite(t,'check') for t in TestClasses])



































