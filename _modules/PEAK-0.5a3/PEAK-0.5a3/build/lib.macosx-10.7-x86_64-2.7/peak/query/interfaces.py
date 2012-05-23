"""Query Interfaces"""

from protocols import Interface

__all__ = [
    'IRelationVariable', 'IRelationCondition', 'IBooleanExpression',
    'IRelationAttribute', 'IRelationComparison', 'ISQLDriver',
    'IDomainVariable', 'ISQLRenderable', 'ISQLWriter',
]

class IBooleanExpression(Interface):

    def conjuncts():
        """Return the sequence of conjuncts of this expression

        For an 'and' operation, this should return the and-ed expressions.
        For most other operations, this should return a one-element sequence
        containing the expression object itself."""

    def disjuncts():
        """Return the sequence of disjuncts of this expression

        For an 'or' operation, this should return the or-ed expressions.
        For most other operations, this should return a one-element sequence
        containing the expression object itself."""

    def __cmp__(other):
        """Boolean expressions must be comparable to each other"""

    def __hash__(other):
        """Boolean expressions must be hashable"""

    def __invert__():
        """Return the inverse ("not") of this expression"""

    def __and__(expr):
        """Return the conjunction ("and") of this expression with 'expr'"""

    def __or__(expr):
        """Return the disjunction ("or") of this expression with 'expr'"""

class IRelationCondition(IBooleanExpression):

    """A boolean condition in relational algebra"""

    def appliesTo(attrNames):
        """Does condition depend on any of the named columns?"""

    def rejectsNullsFor(attrNames):
        """Does condition require a non-null value for any named column?

        This method is used to determine whether an outer join can be reduced
        to a regular join, due to a requirement that an outer-joined column be
        non-null.  (Note that for 'rejectsNullsFor()' to be true for an 'or'
        condition, it must be true for *all* the 'or'-ed subconditions.)"""

    # XXX need some way to return renamed version

class IDomainVariable(Interface):
    """A domain variable in relational algebra"""

    def isAggregate():
        """Return true if DV represents an aggregate function"""

class IRelationAttribute(IDomainVariable):
    """A domain variable that's a simple column reference"""

    def getName():
        """Return this column's original name in its containing table"""

    def getRV():
        """Return the relvar representing this column's containing table"""

    def getDB(self):
        """Return the database this column belongs to"""


class IRelationComparison(IRelationCondition):
    """A comparison operator in relational algebra"""
    # XXX Don't know what we need here yet


class ISQLWriter(Interface):

    """A smart stream used to create SQL statements"""

    def write(text):
        """Write 'text' to the SQL output"""

    def writeCond(ob):
        """Write 'ob' as an SQL condition"""

    def writeExpr(ob):
        """Write 'ob' as an SQL expression"""

    def writeSelect(ob):
        """Write 'ob' as an SQL 'SELECT' statement"""

    def writeTable(RV):
        """Write 'RV' as an SQL table reference (e.g. "Foo AS F1")"""

    def writeAlias(RV):
        """Write 'RV' as an SQL table alias (e.g. the 'F1' in 'F1.Bar')"""

    def namedParam(param):
        """Add the parameter object to the statement being written"""

    def getAlias(rv):
        """XXX"""

    def assignAlias(rv):
        """XXX"""

    def assignAliasesFor(rvs):
        """XXX"""








    def separator(sep):
        """Return a callable that writes a separator (except first time)

        This method is used for writing comma-separated lists, or lists of
        AND/OR expressions, e.g.::

            sep = writer.separator(', ')
            for item in someExprs:
                sep()
                writer.writeExpr(item)

        The callable returned by this method will *not* write the separator
        the first time it's called, so that the separator will only be written
        between items.  Note that this means you must call this method to get
        a new separator callable for each list you want to output.
        """

    def prepender(prefix):
        """Return a new 'ISQLWriter' that will write 'prefix' before any output

        This method is used when writing optional WHERE/HAVING clauses, by
        obtaining a new writer with e.g.::

            writer.prepender(" WHERE ").writeCond(someCondition)

        If the new writer has any text written to it, it will write the prefix
        once, before any subsequent output.  Note that you should not mix use
        of the new writer with use of the old writer.  Once you're done with
        the new writer, throw it away and go back to the previous writer.
        """











class ISQLRenderable(Interface):

    """Object that can render itself as SQL to an 'ISQLWriter'"""

    def sqlCondition(writer):
        """Render self as a SQL boolean expression to writer.write()"""

    def sqlExpression(writer):
        """Render self as a SQL expression to writer.write()"""

    def sqlSelect(writer):
        """Return self as an SQL 'SELECT' statement"""

    def sqlTableRef(writer):
        """Return self as an SQL table reference, suitable for aliasing"""


























class IRelationVariable(Interface):

    """A relation variable (RV) in relational algebra"""

    def __call__(where=None,join=(),outer=(),rename=(),keep=(),calc=(),groupBy=()):
        """Return a new RV based on select/project/join operations as follows:

        'where' -- specify a condition that all rows of the new RV must meet
        (equivalent to the relational algebra 'select' operation).

        'join' -- an iterable of RV's that will be inner-joined with this RV
        (if no 'where' is supplied, this is a cartesian product.)

        'outer' -- an iterable of RV's that will be outer-joined with this RV's
        inner-joined portions.

        'keep' -- a sequence of the names of the columns that should be kept in
        the new RV.  Supplying a non-empty value here is equivalent to the
        relational algebra 'project' operation.

        'rename' -- a sequence of '(oldName,newName)' tuples specifying columns
        to be renamed.  The old columns are automatically "kept", so if you
        mix 'rename' and 'keep', you do not need to list renamed columns in the
        'keep' argument.

        'calc' -- a sequence of '(name,DV)' pairs specifying computed columns
        to include in the new RV.  These columns are always added under the
        given names, so 'keep' and 'rename' have no effect on the new columns.

        'groupBy' -- a sequence of the names of the columns that the resulting
        RV should be summarized on.  These columns will be automatically
        "kept", so if you mix 'groupBy' and 'keep', you do not need to list
        group-by columns in the 'keep' argument.  Note that when using
        'groupBy', you should only keep or calculate columns that represent
        aggregates, or else an error will occur.
        """

    def clone():
        """Return a deepcopy()-like clone of the RV"""


    def keys():
        """Return a sequence of column names"""

    def __getitem__(columnName):
        """Return the IRelationAttribute for the named column"""

    def attributes():
        """Return a kjGraph mapping names->relation attributes"""

    def getDB():
        """Return an object indicating the responsible DB, or None if mixed"""

    def getInnerRVs():
        """Return sequence of inner-join RV's, or (self,) if not a join"""

    def getOuterRVs():
        """Return sequence of outer-join RV's, or () if not outer join"""

    def getCondition():
        """Return any select() or join condition applying to this RV"""

    def getReferencedRVs():
        """Return sequence of all RVs used in this RV (eg: joins,subqueries)"""

    def __cmp__(other):
        """Relation variables must be comparable to each other"""

    def __hash__(other):
        """Relation variables must be hashable"""


class ISQLDriver(Interface):
    """Helper object for SQL generation"""








