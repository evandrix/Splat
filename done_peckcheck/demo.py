import peckcheck
from peckcheck import a_list, an_int

L = a_list(an_int)

class TestAppend(peckcheck.TestCase):
    def testReverse(self, x=L, y=L):
        z = x + y
        z.reverse()
        y.reverse()
        x.reverse()
        assert z == x + y       # deliberately failing test

class Foo(peckcheck.TestCase):
    def testArithmetic(self):
        assert 2+3 == 5

if __name__ == "__main__":
    peckcheck.main()
