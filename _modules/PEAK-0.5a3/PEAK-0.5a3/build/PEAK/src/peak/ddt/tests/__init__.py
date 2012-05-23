"""Test DDT"""

from unittest import TestCase, makeSuite, TestSuite
from peak.api import *
from peak.tests import testRoot
from cStringIO import StringIO
from peak.ddt.api import *
from peak.ddt.html_doc import GREEN,RED,YELLOW,GREY,HTMLDocument
import sys,whrandom

sample_input = """
    <body>
    <table>
        <tr><th>test parser</th></tr>
        <tr><td>one</td><td>two</td></tr>
        <tr><td>buckle</td><td>your</td><td>shoe</td></tr>
    </table>
    </body>
"""

MY = HTMLDocument.actual('my')
SANDAL = HTMLDocument.annotation('(or sandal)')

try:
    raise NotImplementedError
except:
    dummy_exc = sys.exc_info()

ERROR = HTMLDocument.exception(dummy_exc)

sample_output = """
    <body>
    <table>
        <tr><th%(GREY)s>TESTED</th><td%(GREY)s>extra</td></tr>
        <tr><td%(GREEN)s>a one</td><td%(RED)s>&amp; a two</td></tr>
        <tr><td>buckle</td><td%(RED)s>your%(MY)s</td><td>shoe%(SANDAL)s</td></tr>
    <tr><td>extra</td><td%(YELLOW)s>stuff%(ERROR)s</td></tr></table>
    </body>
""" % locals()  #<td>extra</td>


def rowTexts(row):
    return [cell.text for cell in row.cells]

def tableTexts(table):
    return [rowTexts(row) for row in table.rows]

def docTexts(doc):
    return [tableTexts(table) for table in doc.tables]

































class SevenNumbers(model.Struct):
    class first(model.structField): referencedType = model.Integer
    class second(model.structField): referencedType = model.Integer
    class third(model.structField): referencedType = model.Integer
    class fourth(model.structField): referencedType = model.Integer
    class fifth(model.structField): referencedType = model.Integer
    class sixth(model.structField): referencedType = model.Integer
    class seventh(model.structField): referencedType = model.Integer

def makeSeven((first,second,third,fourth,fifth,sixth,seventh)):
    return SevenNumbers(
        first=first,second=second,third=third,fourth=fourth,fifth=fifth,
        sixth=sixth,seventh=seventh
    )

InterestingNumbers = [
    ( 1, 2, 3, 4, 5, 6, 7),     # "natural" numbers
    ( 1, 1, 2, 3, 5, 8,13),     # Fibonacci numbers
    ( 2, 3, 5, 7,11,13,17),     # Primes
    ( 1, 4, 9,16,25,36,49),     # Squares
    ( 1, 2, 4, 8,16,32,64),     # Powers of 2
    ( 2, 4, 6, 8,10,12,14),     # Products of 2
]

forwards = map(makeSeven,InterestingNumbers)
backwards = forwards[:]; backwards.reverse()
sorted = InterestingNumbers[:]; sorted.sort(); sorted = map(makeSeven,sorted)
revsorted = sorted[:]; revsorted.reverse()
seed = forwards[:]

random = []
while seed:
     random.append(whrandom.choice(seed))
     seed.remove(random[-1])







class NumbersApp(binding.Component):

    checker = binding.Make(
        lambda self: RecordChecker(records=self.records),
        suggestParent=False, noCache = True,
        offerAs = ['peak.ddt.processors.Interesting.Numbers']
    )

    records = forwards
































class BasicTests(TestCase):

    def testScoreArithmetic(self):
        self.assertEqual(Error, Zeros+Error)
        self.assertEqual(Right, Zeros+Right)
        self.assertEqual(Wrong, Zeros+Wrong)
        self.assertEqual(Ignored, Zeros+Ignored)
        self.assertEqual(Error, Error-Zeros)
        self.assertEqual(Right, Right-Zeros)
        self.assertEqual(Wrong, Wrong-Zeros)
        self.assertEqual(Ignored, Ignored-Zeros)

    def testCellScoring(self):
        d=Document()
        d.tables=[Table()]
        d.tables[0].rows=[Row()]
        cells = [Cell(),Cell(),Cell(),Cell()]
        d.tables[0].rows[0].cells = cells
        self.assertEqual(d.score, Zeros)
        cells[0].right()
        self.assertEqual(d.score, Right)
        cells[1].wrong("actual")
        self.assertEqual(cells[1].actual,"actual")
        self.assertEqual(d.score, Right+Wrong)
        cells[2].ignore()
        self.assertEqual(d.score, Right+Wrong+Ignored)
        cells[3].exception((1,2,3))
        self.assertEqual(cells[3].exc_info,(1,2,3))
        self.assertEqual(d.score, Right+Wrong+Ignored+Error)
        self.assertEqual(d.score, Score(right=1,wrong=1,ignored=1,exceptions=1))

        # Shouldn't allow us to change state on these
        self.assertRaises(ValueError,cells[0].wrong)
        self.assertRaises(ValueError,cells[1].right)
        self.assertRaises(ValueError,cells[2].exception)
        self.assertRaises(ValueError,cells[3].ignore)





    def testParsing(self):

        dm = HTMLDocument(testRoot(), text=sample_input)

        storage.beginTransaction(dm)

        try:
            self.assertEqual(
                docTexts(dm.document),
                [# doc
                    [# table 1
                        ['test parser'],
                        ['one','two'],
                        ["buckle","your","shoe"]
                    ]
                ]
            )

        finally:
            storage.abortTransaction(dm)





















    def testWord(self):

        dm = HTMLDocument(
            testRoot(),
            text=open(
                config.fileNearModule(__name__,'word_test.html')
            ).read(),
        )

        storage.beginTransaction(dm)

        try:
            self.assertEqual(
                docTexts(dm.document),
                [# doc
                    [# table 1
                        ['sample.fixture1'],
                        ["one","buckle","shoe","four"],
                        ["two","your","three","je t'adore"]
                    ]
                ]
            )

        finally:
            storage.abortTransaction(dm)
















    def testRecords(self):

        # Test recordchecker with lots of variants of the same data

        app = NumbersApp(testRoot())
        from peak.ddt.runners import HTMLRunner

        testURL   = 'pkgfile:peak.ddt.tests/RecordChecker_Tests.html'
        resultURL = 'pkgfile:peak.ddt.tests/RecordChecker_Results.html'

        output = app.lookupComponent(resultURL).open('t').read()

        for records in forwards,backwards,sorted,revsorted,random:
            app.records = records
            runner = HTMLRunner(
                app, argv=['ddt',testURL],
                stdout = StringIO(), stderr = StringIO(),
            )
            runner.run()
            self.assertEqual(
                runner.stdout.getvalue().replace('\r\n','\n'),
                output.replace('\r\n','\n')
            )


















    def testRunner(self):

        # Test a file runner, action processor, and model processor

        from peak.ddt.runners import HTMLRunner

        runner = HTMLRunner(
            testRoot(),
            argv=['ddt','pkgfile:peak.ddt.tests/Action_Test.html'],
            stdout = StringIO(),
            stderr = StringIO(),
        )
        runner.run()

        self.assertEqual(
            runner.stderr.getvalue().strip(),
            "23 right, 1 wrong, 0 ignored, 1 exceptions"
        )























    def testOutput(self):

        s = StringIO()
        dm = HTMLDocument(testRoot(), text=sample_input, stream=s)

        storage.beginTransaction(dm)

        try:
            doc = dm.document
            table, = doc.tables
            r1,r2,r3 = table.rows
            r1.cells[0].ignore()
            r1.cells[0].text = 'TESTED'
            r2.cells[0].right(); r2.cells[0].text="a one"
            r2.cells[1].wrong(); r2.cells[1].text="& a two"
            r3.cells[1].assertEqual('my');
            r3.cells[2].annotation="(or sandal)"
            r1.addCell(dm.newItem(Cell))
            r1.cells[-1].text = 'extra'
            r1.cells[-1].ignore()
            r4 = dm.newItem(Row)
            table.addRow(r4)
            r4.addCell(dm.newItem(Cell))
            r4.addCell(dm.newItem(Cell))
            r4.cells[0].text = 'extra'
            r4.cells[1].text = 'stuff'; r4.cells[1].exception(dummy_exc)
            storage.commitTransaction(dm)
        except:
            storage.abortTransaction(dm)
            raise

        self.assertEqual(s.getvalue(), sample_output)









TestClasses = (
    BasicTests,
)

def test_suite():
    s = []
    for t in TestClasses:
        s.append(makeSuite(t,'test'))

    return TestSuite(s)































