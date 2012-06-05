"""Unit tests for relational algebra"""

from unittest import TestCase, makeSuite, TestSuite
from peak.api import *
from peak.tests import testRoot
from peak.query.api import *
from peak.query.algebra import BasicJoin, Not, And, Or, Table, PhysicalDB, \
     function, aggregate, Parameter, SQLWriter, Cmp
from kjbuckets import kjSet


def getSQL(rv):
    ctx = SQLWriter()
    ctx.writeSelect(rv)
    return ctx.data()[0]

def getSQLParams(rv):
    ctx = SQLWriter()
    ctx.writeSelect(rv)
    return ctx.data()





















class SimpleFixtures(TestCase):

    A_Columns = ('aa','ab','ac')
    B_Columns = ('b1','b2')
    C_Columns = ('CC','DD','EE')
    D_Columns = ('d',)

    def setUp(self):
        self.rvA = A = Table('A',self.A_Columns)
        self.rvB = B = Table('B',self.B_Columns)
        self.rvC = C = Table('C',self.C_Columns)
        self.rvD = D = Table('D',self.D_Columns)
        self.condX = A.aa.eq(B.b1)
        self.condY = B.b1.eq(C.CC)
        self.condZ = C.CC.eq(D.d)

    db = PhysicalDB(
        tables = Items(
            Branch = (
                'headempnr','branchnr','cityname','statecode','country'
            ),
            Employee = (
                'empnr','empname','branchnr','salary','cityname','statecode',
                'country', 'supervisor_empnr', 'mainphone', 'otherphone'
            ),
            Speaks = ('empnr','languagename'),
            Drives = ('empnr','carregnr'),
            Car = ('carregnr','carmodelname','color'),
            LangUse = ('languagename','country'),
        )
    )










class SimplificationAndEquality(SimpleFixtures):

    """Verify that boolean expressions are equal to their simpler forms

    Relational algebra is at its best when conditions are expressed in
    conjunctive normal form.  That is, all conditions are and-ed together in
    as flat a structure as possible.  Apart from that, conditions should be
    as simple as possible.  So, we want the following transformations to
    occur wherever possible:

        * NOT(OR(x,y)) -> AND(NOT(x),NOT(y))

        * AND(x,AND(y,z)) -> AND(x,y,z)

        * OR(x,OR(y,z)) -> OR(x,y,z)

        * NOT(NOT(x)) -> x

        * NOT(EQ(x,y)) -> NE(x,y) (and similar for all comparison ops)

    The test cases in this class will verify that expressions are as simple
    as possible, but no simpler.  :)
    """

    def testBooleanCommutativity(self):
        x,y,z = self.condX, self.condY, self.condZ
        self.assertEqual( (x & y & z), (z & y & x) )
        self.assertNotEqual( (x & y & z), (x & y) )
        self.assertEqual( (x|y|z), (z|y|x) )
        self.assertNotEqual( (x|y|z), (x|y) )

    def testBooleanEqualities(self):
        x,y,z = self.condX, self.condY, self.condZ
        self.assertNotEqual( (x&y), (x|y) )
        self.assertEqual(x,x)
        self.assertNotEqual(x,y)
        self.assertEqual( (x|x), x )
        self.assertEqual( (x&x), x )
        self.assertEqual( (x&y)&(x&y&z), (x&y&z) )


    def testBooleanAssociativity(self):
        x,y,z = self.condX, self.condY, self.condZ
        self.assertEqual( (x&(y&z)), ((x&y)&z) )
        self.assertNotEqual( (x|(y&z)), (x&y)|z )
        self.assertEqual( (x|(y|z)), ((x|y)|z) )
        self.assertNotEqual( (x&(y|z)), ((x|y)&z) )


    def testNegation(self):
        x,y,z = self.condX, self.condY, self.condZ

        self.assertEqual( ~x, ~~~x)
        self.assertEqual( x, ~~x)
        self.assertNotEqual( x, ~x)

        self.assertNotEqual( ~(x&y), (x&y) )
        self.assertNotEqual( ~(x&y), (x|y) )
        self.assertEqual( ~(x&y), (~x|~y) )
        self.assertEqual( ~~(x&y), (x&y) )
        self.assertEqual(~((x|y)&z), (~(x|y)|~z) )
        self.assertEqual((~(x&y)&~z), ~((x&y)|z) )


    def testJoinCommutativity(self):

        x,y,z = self.condX, self.condY, self.condZ
        A,B,C,D = self.rvA, self.rvB, self.rvC, self.rvD

        self.assertEqual(A(join=[B],where=x), B(join=[A],where=x))
        self.assertEqual(A(join=[B,C],where=x&y), B(join=[A,C],where=x&y))
        self.assertEqual(A(join=[B,C],where=x&y), C(join=[B,A],where=x&y))










    def testJoinAssociativity(self):

        x,y,z = self.condX, self.condY, self.condZ
        A,B,C,D = self.rvA, self.rvB, self.rvC, self.rvD

        self.assertEqual(
            A(join=[B],where=x)(join=[C],where=y),
            A(join=[B,C],where=x&y)
        )

        self.assertEqual(
            A(join=[B],where=x)(join=[C(join=[D],where=z)],where=y),
            A(join=[B,C,D],where=x&y&z)
        )


    def testSignatures(self):
        x,y,z = self.condX, self.condY, self.condZ
        A,B,C,D = self.rvA, self.rvB, self.rvC, self.rvD
        self.assertRaises(TypeError,Or)         # too few args
        self.assertRaises(TypeError,And)
        self.assertRaises(TypeError,Not)
        self.assertRaises(TypeError,BasicJoin)
        self.assertRaises(TypeError,BasicJoin,x)
        self.assertRaises(TypeError,Not,x,y)    # too many args
















    def testSelectionAssociativity(self):

        A,B,C,D = self.rvA, self.rvB, self.rvC, self.rvD
        x,y,z = self.condX, A.ab.eq(27), A.ac.eq(42)

        self.assertEquals(
            A(join=[B],where=x)(where=y),
            A(join=[B],where=x&y)
        )

        self.assertEquals(
            A(where=y)(where=z),
            A(where=y&z)
        )

        self.assertEquals(
            A(where=z)(where=y),
            A(where=y&z)
        )

        self.assertEquals(
            A(join=[B],where=x)(where=y)(where=z),
            A(join=[B],where=x&y&z)
        )

        self.assertEquals(
            A(where=y)(join=[B],where=x),
            A(join=[B],where=x&y)
        )












    def testOuterJoinInequalities(self):

        x,y,z = self.condX, self.condY, self.condZ
        A,B,C,D = self.rvA, self.rvB, self.rvC, self.rvD

        self.assertNotEqual( A(outer=[B],where=x), B(outer=[A],where=x) )
        self.assertNotEqual( A(outer=[C],where=x), A(outer=[B],where=x) )
        self.assertNotEqual( A(outer=[B],where=x), A(join=[B],where=x) )

        self.assertEqual(
            A(outer=[B],where=x)(outer=[C],where=y),
            A(outer=[C],where=y)(outer=[B],where=x)
        )

        self.assertEqual(
            A(join=[B],where=x)(outer=[C],where=y),
            B(join=[A],where=x)(outer=[C],where=y)
        )

        self.assertEqual(
            A(outer=[C],where=y)(join=[B],where=x),
            A(join=[B],where=x)(outer=[C],where=y)
        )


















    def testColumns(self):
        x,y,z = self.condX, self.condY, self.condZ
        A,B,C,D = self.rvA, self.rvB, self.rvC, self.rvD

        self.assertEqual( kjSet(A.keys()), kjSet(self.A_Columns) )
        self.assertEqual( kjSet(B.keys()), kjSet(self.B_Columns) )
        self.assertEqual( kjSet(C.keys()), kjSet(self.C_Columns) )
        self.assertEqual( kjSet(D.keys()), kjSet(self.D_Columns) )

        self._verifyJoinedColumns(A,x,B)
        self._verifyJoinedColumns(C,y,D)
        self._verifyJoinedColumns(B,z,C)
        self._verifyJoinedColumns(A(join=[B],where=x),y,C(join=[D],where=z))

    def _verifyJoinedColumns(self,base,cond,*relvars):
        AB = base(join=relvars, where=cond)
        AB_cols = AB.attributes()
        AplusB  = base.attributes()
        for rv in relvars:
            AplusB += rv.attributes()
        self.assertEqual(AB_cols, AplusB)




















    def testRVReuseNotAllowed(self):
        # The same RV may not appear more than once in a single expression

        x,y,z = self.condX, self.condY, self.condZ
        A,B,C,D = self.rvA, self.rvB, self.rvC, self.rvD

        self.assertRaises(ValueError, B, join=[A,A])
        self.assertRaises(ValueError, B, outer=[A,A])
        self.assertRaises(ValueError, B(join=[C]), join=[C(join=[D])])


    def testComparison(self):
        A,B,C,D = self.rvA, self.rvB, self.rvC, self.rvD
        x = A.aa.eq(B.b1)
        A(join=[B],where=x)
        self.assertEqual(x, A.aa.eq(B.b1))
        self.assertEqual(~x, A.aa.ne(B.b1))
        self.assertEqual(x, ~A.aa.ne(B.b1))
        self.assertEqual(A.aa.lt(B.b1), ~A.aa.ge(B.b1))
        self.assertEqual(~A.aa.lt(B.b1), A.aa.ge(B.b1))
        self.assertEqual(A.aa.gt(B.b1), ~A.aa.le(B.b1))
        self.assertEqual(~A.aa.gt(B.b1), A.aa.le(B.b1))

        self.assertNotEqual(A.aa.lt(B.b1),A.aa.gt(B.b1))
        self.assertNotEqual(A.aa.le(B.b1),A.aa.eq(B.b1))
















    def testProjection(self):
        x,y,z = self.condX, self.condY, self.condZ
        A,B,C,D = self.rvA, self.rvB, self.rvC, self.rvD

        # B and A have no common attrs
        self.failIf( A(keep=self.B_Columns).keys() )

        # columns in A(join=[B],where=x)(keep=B.attributes()) == B.attributes()
        AB = A(join=[B],where=x)
        self.assertEqual(
            AB(keep=self.B_Columns).attributes(),
            B.attributes()
        )

        # columns in A(outer=[B],where=x)(keep=B.attributes()) == B.attributes()
        AB = A(outer=[B],where=x)
        self.assertEqual(
            AB(keep=self.B_Columns).attributes(),
            B.attributes()
        )

        # A.proj(a)(join=[B.proj(b)],where=x) == A(join=[B],where=x).proj(a+b)
        self.assertEqual(
            A(join=[B],where=x)(keep=self.A_Columns[:2]+self.B_Columns[:2]),
            A(keep=self.A_Columns[:2])(join=[B(keep=self.B_Columns[:2])],where=x)
        )















    def testRename(self):

        x,y,z = self.condX, self.condY, self.condZ
        A,B,C,D = self.rvA, self.rvB, self.rvC, self.rvD

        for colNum in range(len(self.A_Columns)):
            theColumn = self.A_Columns[colNum]
            Arenamed = A(rename=[(theColumn,'theColumn')])

            self.assertEqual(
                A[theColumn], Arenamed.theColumn
            )
            self.assertEqual(
                kjSet(Arenamed.keys()),
                kjSet(
                    ('theColumn',) + self.A_Columns[:colNum]
                                   + self.A_Columns[colNum+1:]
                )
            )

        for abcd in [ A(join=[B,C,D],where=x), A(outer=[B,C,D],where=x) ]:

            ABCD = abcd(
                rename=[(n,n.upper()) for n in abcd.keys()]
            )

            self.assertEqual(
                kjSet([n.upper() for n in abcd.keys()]),
                kjSet(ABCD.keys())
            )











class CloningTests(SimpleFixtures):

    def testRVClone(self):

        testRVs = [
            self.rvA,           # table w/out DB
            self.db.Employee,   # table w/DB
            self.db.Employee(join=[self.rvA]),      # simple join
            self.db.Employee(groupBy=['branchnr'])  # group-by
        ]

        for rv in testRVs:

            clone = rv.clone()

            # RV is equal to its clone, but not the same object
            self.assertEqual(rv,clone)
            self.failIf(rv is clone)

            # RV has identical DB to its clone (i.e. DB is not cloned)
            self.failIf(rv.getDB() is not clone.getDB())

    # Needed tests:
    # * join-level cond (even subqs) referring to ambiguous table should fail
    # * EXISTS() and IN() subqueries are unique
















class DatabaseTests(SimpleFixtures):

    def setUp(self):
        pass


    def testPhysicalDB(self):

        db = self.db
        Branch = db.Branch
        Employee = db.Employee

        x = Branch.branchnr.eq(Employee.branchnr)
        A = Table('X',('foo','bar'))

        self.assertEqual(
            Branch(join=[Employee],where=x), Employee(join=[Branch],where=x)
        )

        # Single-db join should have the same DB
        self.failUnless(Branch(join=[Employee],where=x).getDB() is db)

        # Mixed-db joins should have a DB of None (for now)
        self.failUnless(Branch(join=[A],where=x).getDB() is None)

        for tbl in 'Branch','Employee','Speaks','Drives','Car','LangUse':

            tbl = db[tbl]

            # table's db should be db
            self.failUnless(tbl.getDB() is db)

            # a projection of table should still have the same DB
            self.failUnless(
                tbl(keep=tbl.keys()[:-1]).getDB() is db
            )

            for colName in tbl.keys():
                self.failUnless(tbl[colName].getRV() is tbl)
                self.failUnless(tbl[colName].getDB() is db)

    def testSimpleSQL(self):

        db = self.db
        Branch = db.Branch
        Employee = db.Employee

        self.assertEqual(getSQL(Branch), "SELECT * FROM Branch")
        self.assertEqual(getSQL(Employee), "SELECT * FROM Employee")

        EmployeesByBranch = Branch(
            join=[Employee],
            where=Branch.branchnr.eq(Employee.branchnr)
        )

        self.assertEqual(
            getSQL(EmployeesByBranch),
            "SELECT B1.*, E2.* FROM Branch AS B1, Employee AS E2"
            " WHERE B1.branchnr=E2.branchnr"
        )

        self.assertEqual(
            getSQL(Branch(where=Branch.branchnr.eq(42))),
            "SELECT B1.* FROM Branch AS B1 WHERE B1.branchnr=42"
        )

        self.assertEqual(
            getSQL(Employee(where=Employee.empnr.eq(42),keep=['empname'])),
            "SELECT E1.empname FROM Employee AS E1 WHERE E1.empnr=42"
        )

        self.assertEqual(
            getSQL(
                Employee(
                    where=Employee.empnr.eq(42), keep=['empname','salary'],
                    rename=Items(empname='Name')
                )
            ),
            "SELECT E1.empname AS Name, E1.salary"
            " FROM Employee AS E1 WHERE E1.empnr=42"
        )

    def testFunctions(self):

        Employee = self.db.Employee
        SQRT = function('SQRT')
        sqrtSal = SQRT(Employee.salary)

        self.assertEqual(
            getSQL(Employee(calc=Items(salroot=sqrtSal))),
            "SELECT E1.*, SQRT(E1.salary) AS salroot FROM Employee AS E1"
        )

        self.assertEqual(
            getSQL(Employee(where=sqrtSal.gt(200))),
            "SELECT E1.* FROM Employee AS E1 WHERE SQRT(E1.salary)>200"
        )

        self.assertEqual(
            getSQL(
                Employee(
                    calc=Items(salroot=sqrtSal), where=sqrtSal.lt(300)
                )
            ),
            "SELECT E1.*, SQRT(E1.salary) AS salroot FROM Employee AS E1"
            " WHERE SQRT(E1.salary)<300"
        )
















    def testConditions(self):

        Employee = self.db.Employee

        self.assertEqual(
            getSQL(
                Employee(where=Employee.empnr.eq(42) | Employee.empnr.eq(23))
            ),
            "SELECT E1.* FROM Employee AS E1"
            " WHERE (E1.empnr=23 OR E1.empnr=42)"
        )

        self.assertEqual(
            getSQL(
                Employee(where=~(Employee.empnr.eq(42)|Employee.empnr.eq(23)))
            ),
            "SELECT E1.* FROM Employee AS E1"
            " WHERE E1.empnr<>23 AND E1.empnr<>42"
        )

        self.assertEqual(
            getSQL(
                Employee(where=~Cmp(Employee.empname,' LIKE ',"Bob"))
            ),
            "SELECT E1.* FROM Employee AS E1"
            " WHERE NOT (E1.empname LIKE 'Bob')"
        )














    def testAggregates(self):

        MIN = aggregate('MIN')
        MAX = aggregate('MAX')
        SQRT = function('SQRT')
        COMPLEX = function('COMPLEX')

        salary = self.db.Employee.salary

        # An aggregate function of a non-aggregate, is an aggregate expression
        self.failUnless( MIN(salary).isAggregate() )
        self.failUnless( MAX(SQRT(salary)).isAggregate() )

        # A non-aggregate function of aggregate(s), is an aggregate expression
        self.failUnless( SQRT(MAX(salary)).isAggregate() )
        self.failUnless( COMPLEX(MAX(salary),MIN(salary)).isAggregate() )

        # A non-aggregate function of a non-aggregate, is a non-aggregate
        self.failIf( SQRT(salary).isAggregate() )
        self.failIf( COMPLEX(salary,SQRT(salary)).isAggregate() )

        # An aggregate of an aggregate is an error
        self.assertRaises(TypeError, MAX, MAX(salary))

        # Function of mixed aggregate and non-aggregates is an error
        self.assertRaises(TypeError, COMPLEX, salary, MAX(salary))















    def testGroupBy(self):

        Employee = self.db.Employee
        Branch = self.db.Branch
        AVG = aggregate('AVG')
        COUNT = aggregate('COUNT')

        empCount = COUNT(Employee.empnr)
        EmpByBranch = Employee(
            calc=Items(employees=empCount),
            groupBy=['branchnr']
        )

        self.assertEqual(
            getSQL(EmpByBranch),
            "SELECT E1.branchnr, COUNT(E1.empnr) AS employees"
            " FROM Employee AS E1 GROUP BY E1.branchnr"
        )

        self.assertEqual(
            getSQL(EmpByBranch(where=empCount.gt(10))),
            "SELECT E1.branchnr, COUNT(E1.empnr) AS employees"
            " FROM Employee AS E1 GROUP BY E1.branchnr"
            " HAVING COUNT(E1.empnr)>10"
        )

        self.assertEqual(
            getSQL(
                EmpByBranch(
                    join=[Branch],
                    where=Branch.branchnr.eq(EmpByBranch.branchnr)
                )
            ),
            "SELECT x1.*, B2.*"
            " FROM (SELECT E3.branchnr, COUNT(E3.empnr) AS employees"
            " FROM Employee AS E3 GROUP BY E3.branchnr"
            ") AS x1, Branch AS B2 WHERE B2.branchnr=x1.branchnr"
        )



        # All non-groupby columns of a grouping must be aggregates

        self.assertRaises(TypeError,Employee,
            calc=Items(employees=COUNT(Employee.empnr)),
            groupBy=['branchnr'],keep=['empnr']
        )


    def testParameters(self):
        param = Parameter('test_param')
        Employee = self.db.Employee
        COMPLEX = function('COMPLEX')

        salary = self.db.Employee.salary

        self.assertEqual(
            getSQLParams( Employee(where=Employee.empnr.eq(param)) ),
            ("SELECT E1.* FROM Employee AS E1 WHERE E1.empnr=?", [param])
        )

        self.assertEqual(
            getSQLParams(
                Employee(calc=Items(crazy=COMPLEX(Employee.empnr,param)))
            ),
            ("SELECT E1.*, COMPLEX(E1.empnr,?) AS crazy FROM Employee AS E1",
                [param]
            )
        )













TestClasses = (
    SimplificationAndEquality, CloningTests, DatabaseTests,
)


def test_suite():
    s = []
    for t in TestClasses:
        s.append(makeSuite(t,'test'))
    return TestSuite(s)































