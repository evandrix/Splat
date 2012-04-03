"""Tests for EigenData"""

from unittest import TestCase, makeSuite, TestSuite
from peak.util.EigenData import *


class CheckEmpty(TestCase):

    emptyCell = CollapsedCell

    def checkExistence(self):

        cell = self.emptyCell

        assert not cell.exists()
        cell.unset()

        try:
            cell.get()
        except AttributeError:
            pass
        else:
            raise AssertionError("Empty cell should not have value")


class CheckEmpty2(CheckEmpty):

    emptyCell = EigenCell()


class CheckUnset(CheckEmpty):

    def setUp(self):
        self.emptyCell = cell = EigenCell()
        for i in range(5):
            cell.set(i)
        cell.unset()




class CheckFull(TestCase):

    def setUp(self):
        self.cell = EigenCell()

    def checkSet(self):
        cell = self.cell
        for i in range(50):
            cell.set(i)

    def checkGet(self):
        cell = self.cell

        for i in range(10):
            cell.set(i)

        assert cell.get()==9
        assert cell.exists()

        try:
            cell.set(10)
        except AlreadyRead:
            pass
        else:
            raise AssertionError("Should not be able to set read cell")
















dictData = { 'a':1, 'b':2, 'c':3 }
multData = { 'a':9, 'b':18, 'c': 27 }

class CheckDict(TestCase):

    def setUp(self):
        self.ed = ed = EigenDict()

        for i in range(10):
            for k,v in dictData.items():
                ed[k]=v*i

    def checkCopyAndClear(self):

        assert self.ed.copy() == multData

        try:
            self.ed.clear()
        except AlreadyRead:
            pass
        else:
            raise AssertionError("Shouldn't be able to clear copy'd EigenDict")


    def checkClearUnlocked(self):
        # should work, because no cells have been read
        self.ed.clear()


    def checkDelAfterContains(self):
        assert 'a' in self.ed
        del self.ed['b']
        del self.ed['b']

        try:
            del self.ed['a']
        except AlreadyRead:
            pass
        else:
            raise AssertionError("Shouldn't be able to delete read key")

    def checkGetWithFactory(self):
        ed = self.ed
        self.assertEqual(ed.get('a',None), 9)
        self.assertEqual(ed.get('a',factory=lambda:27), 9)
        self.assertEqual(ed.get('q',None), None)
        self.assertEqual(ed.get('z',factory=lambda:42), 42)
        ed.keys() # lock it
        self.assertEqual(ed.get('x',factory=lambda:59), None)


TestClasses = (
    CheckEmpty, CheckEmpty2, CheckUnset, CheckFull, CheckDict,
)

def test_suite():
    return TestSuite([makeSuite(t,'check') for t in TestClasses])

























