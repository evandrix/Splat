"""Tests for SOX"""

from unittest import TestCase, makeSuite, TestSuite
from cStringIO import StringIO
from xml.sax import InputSource
from peak.util import SOX

def stream(str):
    inpsrc = InputSource()
    inpsrc.setByteStream(StringIO(str))
    return inpsrc


class SOXTest(TestCase):

    text = "<nothing/>"

    useNS = False

    def setUp(self):
        self.object = ob = SOX.load(stream(self.text), namespaces=self.useNS)
        self.de = ob.documentElement



















class Simple(SOXTest):

    text = """<top foo="bar" baz="spam">TE<middle/>XT</top>"""

    def checkTop(self):
        assert self.de._name == 'top'

    def checkNodelist(self):
        object = self.object
        top = object._get('top')
        assert len(top)==1
        assert object.top is top

    def checkText(self):
        t = []
        for n in self.de._allNodes:
            if n == str(n): t.append(n)
        assert ''.join(t) == 'TEXT'

    def checkAttrs(self):
        assert self.de.foo=='bar'
        assert self.de.baz=='spam'


class NSTest(SOXTest):
    text = """
        <xmi:XMI xmlns:xmi="http://omg.org/XMI/2.0" xmlns="www.zope.org">
            <xmi:model name="MOF" version="1.3"/> [0]
            <Model:Package name="foo" xmlns:Model="http://omg.org/MOF/1.3"/> [1]
            <thingy/> [2]
        </xmi:XMI>"""

    useNS = True

    def checkModel(self):
        node = self.de._subNodes[1]
        assert node.ns2uri['Model']=='http://omg.org/MOF/1.3'
        node = self.de._subNodes[2]
        assert 'Model' not in node.ns2uri
        assert node.ns2uri[''] == "www.zope.org"

TestClasses = (
    Simple, NSTest
)

def test_suite():
    s = []
    for t in TestClasses:
        s.append(makeSuite(t,'check'))

    return TestSuite(s)































