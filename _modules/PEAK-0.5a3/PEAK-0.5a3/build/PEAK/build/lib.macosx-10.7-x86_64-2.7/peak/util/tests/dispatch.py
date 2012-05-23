"""Test generic functions

    Credits: This test suite is based heavily on the test suite from
    Aric Coady's 'multimethod-0.1.1' package.  Although we have our own,
    entirely different implementation for multimethods themselves, Aric's
    package had a really cool test suite.  Too bad our multimethods don't
    quite support all of the tested features!"""

from unittest import TestCase, makeSuite, TestSuite

import operator, string

from peak.util.dispatch import *


class bracket(str):

    "Open/close delimiter."

    def __new__(cls, s):
        if len(s) <> 2:
            raise ValueError, 'bracket must be a pair of characters'
        return str.__new__(cls, s)

    def join(seq, self):
        return self[0] + (self[1] + self[0]).join(seq) + self[1]

    join = staticmethod(join)


class natural(int):

    def __new__(cls, value=0):
        return int.__new__(cls, abs(value))







class animal(object):

    def same(next, self, other):
        return "They're both animals."

    same = staticmethod(same)


class vertebrate(animal):

    def different(next, self, other):
        s = next()(next, self, other)
        return s + "  One of them has a backbone."

    different = staticmethod(different)

    def same(next, self, other):
        s = animal.same(next, self, other)
        return s + "  They both have backbones."

    same = staticmethod(same)


class invertebrate(animal):

    def different(next, self, other):
        s = next()(next, self, other)
        return s + "  One of them does not have a backbone."

    different = staticmethod(different)

    def same(next, self, other):
        s = animal.same(next, self, other)
        return s + "  Neither of them have backbones."

    same = staticmethod(same)





class GenericTest(TestCase):

    def checkInterface(self):

        m = Dispatch()
        m[Signature(LookupError)] = 1
        m[Signature(StandardError)] = 0
        m[Signature(IndexError)] = 2
        m[Signature(KeyError)] = 2

        assert m[(StandardError,)].next()   == 0
        assert m[(LookupError,)].next()     == 1
        assert m[(IndexError,)].next()      == 2
        assert m[(KeyError,)].next()        == 2

        m = Dispatch()
        m[Signature(StandardError)] = 0
        m[Signature(IndexError)] = 2
        m[Signature(KeyError)] = 2

        assert m[(KeyError,)].next() == 2

        try:
            m[(Exception,)].next()
        except KeyError:
            pass
        else:
            raise AssertionError, 'should have failed lookup'













    def checkSimple(self):
        """Basic overriding of second argument."""

        join = GenericFunction() # String join in the old order
        join[Signature(object, str)] =  string.join
        join[Signature(object, bracket)] = bracket.join

        assert join(['a', 'b'], ',') == 'a,b'
        assert join(['a', 'b'], '<>') == 'a<>b'
        assert join(['a', 'b'], bracket('<>')) == '<a><b>'

        try:
            join([], None)
        except NoMatchError:
            pass
        else:
            raise AssertionError, 'should have failed lookup'
























    def checkAdvanced(self):
        """Sophisticated next() usage."""

        # This doesn't quite work, as it relies on ambiguous method
        # order, and we don't currently support that.  Perhaps the
        # 'compareRules' and 'iterMatches' dispatch functions should
        # become methods of the dispatcher, and therefore customizable.

        compare = MultiMethod()  # Compare and contrast two animals.

        compare[Signature(animal, animal)] = animal.same
        compare[Signature(vertebrate, vertebrate)] = vertebrate.same
        compare[Signature(invertebrate, invertebrate)] = invertebrate.same

        compare[Signature(vertebrate, animal)] = vertebrate.different
        compare[Signature(animal, invertebrate)] = invertebrate.different

        compare[Signature(invertebrate, animal)] = invertebrate.different
        compare[Signature(animal, vertebrate)] = vertebrate.different

        compare[Signature(invertebrate, vertebrate)] = invertebrate.different
        compare[Signature(vertebrate, invertebrate)] = vertebrate.different

        mammal = vertebrate()
        insect = invertebrate()

        assert compare(mammal, mammal) == \
            "They're both animals.  They both have backbones."
        assert compare(insect, insect) == \
            "They're both animals.  Neither of them have backbones."

        #assert compare(mammal, insect) == \
#            "They're both animals.  \
#One of them does not have a backbone.  One of them has a backbone."
        #assert compare(insect, mammal) == "They're both animals.  \
#One of them has a backbone.  One of them does not have a backbone."





    def checkCustomization(self):
        "Alternative method resolution."

        add = GenericFunction()

        add[Signature(object, int)] = operator.add
        add[Signature(natural, object)] = operator.add

        try:
            add(natural(-1), natural(-2))
        except AmbiguousRulesError:
            pass
        else:
            raise AssertionError, 'should have complained about ambiguity'


TestClasses = (
    GenericTest,
)

def test_suite():
    s = []
    for t in TestClasses:
        s.append(makeSuite(t,'check'))

    return TestSuite(s)















