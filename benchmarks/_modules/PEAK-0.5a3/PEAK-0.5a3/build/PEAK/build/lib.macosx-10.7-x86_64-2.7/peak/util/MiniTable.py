"""An even more primitive and lightweight data table than even TinyTables..."""

from UserList import UserList
from kjbuckets import *


class Table(UserList):

    """Table( tupleOfColNames, listOfRowTuples )

        Tables are 'UserList' objects, so you can iterate over them, access
        rows by row number, take slices, etc.  Each row is a 'kjbuckets.kjDict'
        mapping object, with column names mapping to values.  Mass 'SELECT',
        'UPDATE', and 'DELETE' operations are also available.  Note that since
        rows are mutable, modifying rows in row slices or 'SELECT' slices will
        modify the original table.  'DELETE', however, affects only the table
        it is applied to.  See the 'INSERT_ROWS' method for an explanation of
        the initial load format.
    """

    def __init__(self, colNames=(), rowList=(), rawData=None):

        UserList.__init__(self,rawData)

        if rowList and colNames:
            self.INSERT_ROWS(colNames, rowList)


    def INSERT(self, items):

        """table.INSERT(Items(field1=value1, field2=value2...))

            Insert a row with the supplied field values.  Affects only the
            specific table it is called upon.
        """

        self.data.append(kjDict(items))




    def SELECT(self, whereItems):

        """table.SELECT(Items(field1=value1, field2=value2...)) -> Table slice

            'SELECT' returns a new table which is the subset of rows from the
            original table which match the field values asserted by the keyword
            arguments to 'SELECT'.  You can then iterate over the new table, or
            perform an 'UPDATE' on it to make changes.
        """

        where = kjDict(whereItems); matches = where.subset
        return self.__class__(
            rawData = [d for d in self.data if matches(d)]
        )


    def UPDATE(self, setItems):

        """table.UPDATE(Items(setCol1=setVal1, setCol2=setVal2...))

            Sets the specified column values for all rows in the table.
            This is most useful in conjunction with 'SELECT', e.g.::

                table.SELECT(Items(foo=27)).UPDATE(Items(bar=50))

            The above would set 'bar=50' on all rows of the original table
            where the 'foo' value was equal to 27.  Note that updates
            affect the value of rows in any tables that contain them, since
            the row objects are shared between tables.
        """

        for d in self.data:
            map(d.add,setItems)








    def INSERT_ROWS(self, colNames, rowList):

        """table.INSERT_ROWS(colnames tuple, rowlist)

            Insert 'rowlist' of tuples, where 'colNames' is a tuple
            containing the names of the columns used in the row tuples.
            Example::

                table.INSERT_ROWS(
                    ('foo','bar','baz'), [
                    (    1,    2,    3),
                    (    4,    5,    6),
                ])

            The above is equivalent to::

                table.INSERT(foo=1,bar=2,baz=3)
                table.INSERT(foo=4,bar=5,baz=6)

        """

        self.data.extend( [kjUndump(colNames,row) for row in rowList] )


    def DELETE(self, whereItems):

        """table.DELETE(Items(field1=value1, field2=value2...))

            Delete rows which match the field values asserted in the keyword
            arguments.  Affects only the specific table it is called upon.
        """

        where = kjDict(whereItems)
        matches = where.subset
        self.data = [d for d in self.data if not matches(d)]






    def SET(self, whereItems, setItems):

        """table.SET( Items(key1=val1,...), Items(setfield1=setval1,...) )

            Find a row matching 'whereItems' and update it with the values in
            'setItems'.  If a matching row isn't found, insert a row
            constructed from the fields in both 'whereItems' and 'setItems'.
        """

        where = kjDict(whereItems)
        matches = where.subset

        for d in self.data:
            if matches(d):
                map(d.add, setItems)
                break
        else:
            self.INSERT(whereItems+setItems)























