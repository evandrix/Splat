"""Integration/acceptance tests for SEF.SimpleModel, etc."""

from unittest import TestCase, makeSuite, TestSuite
from peak.api import *
from peak.model.queries import *
from peak.util.imports import lazyModule
from peak.tests import testRoot

UML13 = lazyModule('peak.metamodels.UML13')


class UML_DM(storage.xmi.DM):

    metamodel = UML13

    UML13 = UML13

    Data_Types        = binding.Obtain('UML13/Foundation/Data_Types')
    Multiplicity      = binding.Obtain('Data_Types/Multiplicity')
    MultiplicityRange = binding.Obtain('Data_Types/MultiplicityRange')

    Package           = binding.Obtain('UML13/Model_Management/Package')
    Class             = binding.Obtain('UML13/Foundation/Core/Class')


















class UMLTest(TestCase):

    def setUp(self):
        self.m = m = UML_DM(testRoot())
        self.pkg = m.Package()

    def checkNameSet(self):
        pkg=self.pkg
        pkg.name = 'SomePackage'
        assert pkg.name=='SomePackage'

    def checkAdd(self):
        pkg = self.pkg
        Class = self.m.Class()
        assert not pkg.ownedElement
        pkg.addOwnedElement(Class)
        v = pkg.ownedElement
        assert len(v)==1
        assert v[0] is Class

    def checkDel(self):
        self.checkAdd()
        pkg = self.pkg
        oe = pkg.ownedElement
        pkg.removeOwnedElement(oe[0])
        assert len(oe)==0

    def checkImm(self):
        mr = self.m.MultiplicityRange(lower=0,upper=-1)
        m  = self.m.Multiplicity(range=[mr])
        assert m.range[0].lower==0
        assert self.m.Multiplicity().range==[]









class QueryTests(TestCase):

    def setUp(self):
        self.m = m = UML_DM(testRoot())
        self.pkg = pkg = m.Package()
        pkg.name = 'SomePackage'
        self.klass = klass = self.m.Class()
        klass.name = 'FooClass'
        pkg.addOwnedElement(klass)


    def checkNameGet(self):
        for obj in self.pkg, self.klass:
            names = list(query([obj])['name'])
            assert len(names)==1, list(names)
            assert names[0]==obj.name, (names[0],obj.name)

    def checkSelfWhere(self):
        for obj in self.pkg, self.klass:
            where = list(query([obj], ANY('name',EQ(obj.name))))
            assert len(where)==1

    def checkContentsGet(self):
        pkg = self.pkg
        klass = self.klass
        oe = list(query([pkg])['ownedElement'])
        assert len(oe)==1, oe
        ns = list(query([klass])['namespace'])
        assert len(ns)==1

    def checkContentsWhere(self):
        pkg = self.pkg
        klass = self.klass
        oe = list(query([pkg])['ownedElement'][ANY('name',EQ('FooClass'))])
        assert len(oe)==1, oe
        ns = list(query([klass])['namespace'][ANY('name',EQ('SomePackage'))])
        assert len(ns)==1




LoadedUML = None

class XMILoad(TestCase):
    filename = 'MetaMeta.xml'
    def checkLoad(self):
        global LoadedUML
        self.m = m = LoadedUML = UML_DM(testRoot())
        m.roots = storage.xmi.fromFile(
            config.fileNearModule(__name__,self.filename), testRoot()
        )

class XMITests(TestCase):

    def setUp(self):
        m = LoadedUML
        self.roots = query(m.roots)
        self.root = list(self.roots)[0]
        mm = self.mm = query([self.root])['ownedElement'][
            ANY('name',EQ('Meta-MetaModel'))
        ]

    def checkModel(self):
        assert self.root.name=='Data'

    def checkSubModel(self):
        assert list(self.mm) or list(self.mm); l = list(self.mm['namespace']['name'])
        assert l==['Data'], l

    def checkContents(self):
        assert list(self.mm['ownedElement'][ANY('name',EQ('AttributeKind'))])
        assert not list(self.mm['ownedElement'][ANY('name',EQ('foobar'))])

    def checkSuperclasses(self):
        enum = self.roots['ownedElement*'][ANY('name',EQ('enumeration'))]
        assert len(list(enum))==1
        sc = enum['superclasses']
        assert len(list(sc))==1, list(sc)
        assert list(sc['name'])==['AttributeKind']
        sc = list(enum['superclasses*']['name']); sc.sort()
        assert sc==['AttributeKind','PackageElement'], sc

class XMILoad2(XMILoad):
    filename = 'MetaMeta14.xml'


TestClasses = (
    UMLTest, QueryTests, XMILoad, XMITests, XMILoad2, XMITests
)


def test_suite():
    s = []
    for t in TestClasses:
        s.append(makeSuite(t,'check'))
    return TestSuite(s)































