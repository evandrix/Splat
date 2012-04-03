from peak.api import *
from interfaces import *
from model import *
from peak.util.signature import ISignature
from kjbuckets import kjGraph, kjSet
from peak.storage.interfaces import ISQLConnection

__all__ = [
    'titleAsPropertyName', 'titleAsMethodName', 'DocumentProcessor',
    'AbstractProcessor', 'MethodChecker', 'ModelChecker', 'SQLChecker',
    'RecordChecker', 'ActionChecker', 'Summary', 'RollbackProcessor',
    'FunctionChecker', 'ItemCell',
]


def titleAsPropertyName(text):
    """Convert a string like '"Test Widget"' to '"Test.Widget"'"""
    return PropertyName.fromString(
        '.'.join(
            text.strip().replace('.',' ').split()
        )
    )

def titleAsMethodName(text):
    """Convert a string like '"Spam the Sprocket"' to '"spamTheSprocket"'"""
    text = ''.join(text.strip().title().split())
    return text[:1].lower()+text[1:]














class DocumentProcessor(binding.Component):

    """The default document processor, used to process a test document

    This processor just looks at each table and finds a processor for that
    table, using the 'peak.ddt.processors' property namespace.  It then invokes
    the processor on the corresponding table.

    If you have a project that requires special setup or configuration for the
    tests being run, you can subclass this to do that.  You'll just need to
    get the test "runner" to use your class instead of this one, which can be
    done in an .ini file with::

        [Component Factories]
        peak.ddt.interfaces.IDocumentProcessor = "my_package.MyProcessorClass"
    """

    protocols.advise(
        instancesProvide = [IDocumentProcessor, ITableProcessor]
    )

    processors = binding.Make(
        config.Namespace('peak.ddt.processors')
    )

    def processDocument(self,document):
        self.setUp(document)
        try:
            self.processTables( iter(document.tables) )
        finally:
            self.tearDown(document)

    def processTables(self,tables):
        for table in tables:
            self.processTable(table, tables)






    def processTable(self,table, tables):
        """Delegate to 'ITableProcessor' specified by table's first cell"""
        self.getProcessor(
            table.rows[0].cells[0].text
        ).processTable(table,tables)


    def getProcessor(self,text):
        """Return an 'ITableProcessor' for 'text' in a cell"""

        name = titleAsPropertyName(text)
        processor = adapt( self.processors[name], ITableProcessor )
        binding.suggestParentComponent(self,name,processor)
        return processor


    def setUp(self,document):
        from datetime import datetime
        document.summary['Run at'] = datetime.now()

    def tearDown(self,document):
        pass


class RollbackProcessor(DocumentProcessor):

    """Process document as a transaction, rolling it back at the end"""

    def setUp(self,document):
        super(RollbackProcessor,self).setUp(document)
        storage.beginTransaction(self)

    def tearDown(self,document):
        storage.abortTransaction(self)
        super(RollbackProcessor,self).tearDown(document)






class AbstractProcessor(binding.Component):

    """Processor that just iterates over table contents, doing nothing

    This is just a skeleton for you to subclass and override."""

    protocols.advise(
        instancesProvide = [ITableProcessor,IRowProcessor,ICellProcessor]
    )

    def processTable(self,thisTable,remainingTables):
        """Process 'thisTable', and optionally consume some 'remainingTables'

        The default implementation calls 'self.processRows()' after skipping
        the first row (which ordinarily just names the test processor).

        If you intend to override this method, see the docs for
        'ITableProcessor.processTable()' for details on what it can/can't do.
        """
        rows = iter(thisTable.rows)
        rows.next()     # skip first row
        self.processRows(rows)


    def processRows(self,rows):
        """Process 'rows' (an iterator of remaining rows)

        The default implementation calls 'self.processRow(row,rows)' for each
        row in 'rows', so 'processRow' can consume multiple rows by using
        'rows.next()'."""

        for row in rows:
            self.processRow(row, rows)


    def processRow(self,row,rows):
        """Calls 'self.processCells(iter(row.cells))'"""
        self.processCells(iter(row.cells))



    def processCells(self,cells):
        """Calls 'self.processCell(cell,cells)' for 'cell' in 'cells'"""
        for cell in cells:
            self.processCell(cell,cells)


    def processCell(self,cell,cells):
        """Abstract method: default does nothing"""
        pass
































class MethodChecker(AbstractProcessor):

    """Perform tests by mapping columns to methods of the checker

    If a table has columns named 'x', 'y', and 'z', this checker will call
    'self.x(cell)' for the first cell in each row, 'self.y(cell)' for the
    second, and so on across each row.  It's up to you to define those methods
    in a subclass to do whatever is appropriate for the given cell, such
    as using it for input, using it to validate output, mark the cell "right"
    or "wrong", etc.

    You can also override various methods of this class to use different ways
    of finding the methods to be called, parse column headings differently,
    etc.  See each method's documentation for details.
    """

    handlers = ()

    def processRows(self,rows):
        """Set up methods from the heading row, then process other rows

        This method invokes 'self.setupHandlers(row,rows)' on the "heading"
        row (the row after the title row naming the processor for this table).
        It then invokes 'self.processRow(row,rows)' on the remaining rows.
        """
        row = rows.next()
        self.setupHandlers(row,rows)
        for row in rows:
            self.processRow(row, rows)












    def processRow(self,row,rows):
        """Match each cell with a handler, and invoke it

        This method matches each cell in the row with the corresponding handler
        from 'self.handlers', and then calls 'handler(cell)'.  If a handler
        raises an exception, attempt to annotate the cell with the appropriate
        error information."""

        try:
            self.beforeRow()
            for cell,handler in zip(row.cells,self.handlers):
                try:
                    handler(cell)
                except:
                    cell.exception()
        finally:
            self.afterRow()


    def setupHandlers(self,row,rows):
        """Obtain a handler (method) corresponding to each column heading

        Obtain a handler using 'self.getHandler(cell.text)' for each cell in
        the heading row, and put them in 'self.handlers' in the same order as
        they appear in the table.  If an error occurs when looking up a handler,
        the corresponding cell is annotated with error information, and the
        table's contents are skipped, by consuming the 'rows' iterator.
        """

        self.handlers = handlers = []

        for cell in row.cells:
            try:
                handlers.append(self.getHandler(cell.text))
            except:
                cell.exception()
                list(rows)  # skip remaining rows
                break



    def getHandler(self,text):
        """Get a handler using 'text' from a cell

        The default implementation computes a method name using
        'self.methodNameFor(text)', and then attempts to return
        'getattr(self,methodName)'.

        You can override this routine to return any callable object that
        accepts a 'ddt.Cell' as its sole parameter.
        """
        return getattr(self,self.methodNameFor(text))


    def beforeRow(self):
        """Perform any pre-row setup

        This method is akin to 'setUp()' in a PyUnit test case.  It gives you
        an opportunity to create objects, reset values, open files, etc. before
        starting a row in the test table.  The default implementation does
        nothing."""


    def afterRow(self):
        """Perform any post-row tear down

        This method is akin to 'tearDown()' in a PyUnit test case.  It gives
        you an opportunity to get rid of objects, reset values, close files,
        etc. after finishing a row in the test table.  The default
        implementation does nothing."""


    def methodNameFor(self,text):
        """Convert 'text' to a method name

        The default implemenation uses 'titleAsMethodName' to normalize the
        cell text to a "camel case" (e.g. 'camelCase') format."""

        return titleAsMethodName(text)



class ModelChecker(MethodChecker):

    """Test a domain object by getting/setting attributes or invoking methods

    Unlike 'ddt.MethodChecker', this class can be used without subclassing.
    Just specify the 'targetClass' in the constructor, and optionally set
    'itemPerRow' to 'False' if you want one target instance to be used for
    all rows.  You can also supply 'typeInfo' to list the 'model.IType'
    types that should be used when invoking methods or checking their return
    values.  For example, you might use the following in an .ini file::

        [peak.ddt.processors]

        MyProcessor = ddt.ModelChecker(
            targetClass = importString('my_model.MyElement'),
            typeInfo = Items(
                someMethodReturningInt = model.Integer,
                someMethodTakingFloat = model.Float,
                # etc.
            )
        )

    If 'someMethodReturningInt' or 'someMethodTakingFloat' are invoked by a
    test, the cell value will be converted to/from an integer or float as
    appropriate.

    By default, 'ModelChecker' checks whether a column heading ends in ':'
    (indicating a "set" operation) or '?' (indicating a "get" operation).
    If you would like to override this, you can supply a 'columnSuffixes'
    argument to the constructor, or override it in a subclass.  See the
    'parseHeader()' method for more details.
    """

    itemPerRow = True

    typeInfo = ()

    columnSuffixes = ( (':','set'), ('?','get') )



    targetClass = binding.Require(
        """The 'peak.model.Element' subclass that is to be tested"""
    )

    targetInstance = binding.Require(
        """The specific instance currently being tested"""
    )

    _typeMap = binding.Make( lambda self: dict(self.typeInfo) )



    def getHandler(self,text):
        """Figure out whether handler should get or set, and how to do that

        The default implementation uses 'self.parseHeader()' to determine the
        kind of handler required, and then returns 'self.getGetter()' or
        'self.getSetter()' accordingly."""

        getOrSet, name = self.parseHeader(text)
        if getOrSet=='get':
            return self.getGetter(name)
        elif getOrSet=='set':
            return self.getSetter(name)
        raise ValueError("Invalid return value from parseHeader():", getOrSet)


    def beforeRow(self):
        """Create a new instance, if needed, before starting a row"""
        if self.itemPerRow or not self._hasBinding('targetInstance'):
            self.targetInstance = self.targetClass()    # note: suggests parent


    def afterRow(self):
        """Get rid of old instance, if needed, after finishing a row"""
        if self.itemPerRow:
            self._delBinding('targetInstance')




    def parseHeader(self,text):
        """Return a '(getOrSet,name)' tuple for header 'text'

        'getOrSet' should be the string '"get"' or '"set"', indicating how the
        column is to be interpreted.  'name' should be the name to be used for
        calling 'self.getSetter()' or 'self.getGetter()', respectively.

        The default implementation uses 'self.columnSuffixes' to determine the
        appropriate type.  The 'columnSuffixes' attribute must be an iterable
        of '(suffix,getOrSet)' pairs, where 'suffix' is a string to be checked
        for at the end of 'text', and 'getOrSet' is a string indicating whether
        the column should be get or set.  The suffices in 'columnSuffixes' are
        checked in the order they are provided, so longer suffixes should be
        listed before shorter ones to avoid ambiguity.  An empty string may
        be used as a suffix, to indicate the default behavior for a column, but
        should be placed last in the suffixes, if used.  If no default is
        given, and no suffixes match, an error is raised, causing the header
        to be marked in error and the table as a whole to be skipped.
        """

        text = text.strip()
        for suffix,kind in self.columnSuffixes:
            if text.endswith(suffix):
                return kind, text[:len(text)-len(suffix)]

        raise ValueError("Unable to determine column type:", text)















    def getGetter(self,name):
        """Get a "getting" handler for 'name'

        This is implemented by getting a 'ddt.ICellMapper' for the named
        feature from 'self.getMapper(name)', and returning a handler that
        performs a 'mapper.get()' operation on 'self.targetInstance' each
        time it's invoked.
        """
        get = self.getMapper(name).get
        return lambda cell: get(self.targetInstance, cell)


    def getSetter(self,name):
        """Get a "setting" handler for 'name'

        This is implemented by getting a 'ddt.ICellMapper' for the named
        feature from 'self.getMapper(name)', and returning a handler that
        performs a 'mapper.set()' operation on 'self.targetInstance' each
        time it's invoked.
        """
        set = self.getMapper(name).set
        return lambda cell: set(self.targetInstance, cell)


    def getMapper(self,name):
        """Get an 'ICellMapper' for the named feature in the target class

        This is done by retrieving the named attribute from the class (after
        applying 'titleAsMethodName()' to the name) and and adapting it to
        the 'ddt.ICellMapper' interface.  If there is an entry in
        'self.typeInfo' that indicates the datatype that should be used for
        the column, the mapper is informed of this via its 'suggestType()'
        method.
        """
        name = self.methodNameFor(name)
        mapper = adapt(getattr(self.targetClass,name), ICellMapper)
        binding.suggestParentComponent(self,name,mapper)
        mapper.suggestType(self._typeMap.get(name,model.Repr))
        return mapper


class FunctionChecker(ModelChecker):

    """Verify return values from a function called with keyword arguments

    Column names specify either the names of keyword arguments, except for the
    last column, whose contents are always the expected return value.  The only
    required constructor keyword for 'FunctionChecker' is 'testFunction', which
    must be the callable whose return value is being checked."""

    testFunction = binding.Require("Callable whose return value is tested")

    columnSuffixes = ( ('','set'), )    # always treat columns as 'set'

    targetClass = dict  # assemble keyword arguments in a dictionary


    def setupHandlers(self,row,rows):
        """Set up handlers, always treating the last column as the output"""
        super(FunctionChecker,self).setupHandlers(row,rows)
        self.handlers[-1] = self.invokeFunction


    def getMapper(self,name):
        """Map column names to dictionary keys (keyword args)"""
        name = name.strip()
        mapper = ItemCell(name)
        mapper.suggestType(self._typeMap.get(name,model.Repr))
        return mapper


    def invokeFunction(self,cell):
        """Invoke the function and verify the result"""
        # XXX support some sort of 'error' return for exceptions?
        try:
            cell.assertEqual(
                self.testFunction(**self.targetInstance), model.Repr
            )
        except:
            cell.exception()


class RecordChecker(ModelChecker):

    """Verify that table contents match a computed recordset

    The records may be supplied via the 'records' constructor keyword, or by
    defining a binding for 'records' in a subclass.  Records must be instances
    of 'self.targetClass', but by default the 'targetClass' is taken from the
    class of the first item in 'records', if any.

    The checker will compare the contents of the supplied table with the
    list of records, mark missing rows, add extra rows, and compare cells of
    matching rows automatically.
    """

    def mappers(self):
        """List of 'ICellMapper' objects corresponding to table columns"""
        mappers = []
        for cell in self.headings:
            try:
                mappers.append(self.getMapper(cell.text))
            except:
                cell.exception()
                return []        # don't process any rows

        return mappers

    mappers = binding.Make(mappers)

    columns = binding.Make(
        lambda self: [titleAsMethodName(cell.text) for cell in self.headings]
    )

    headings = binding.Require("The table row containing headers")
    records  = binding.Require("The records to be validated")

    # Default class is class of first record
    targetClass = binding.Make(lambda self: self.records[0].__class__)




    def processRows(self,rows):

        """Compare contents against generated data"""

        row = rows.next()
        self.headings = row.cells

        table = row.table

        try:
            # We don't want to run a comparison if there was an error computing
            # the mappers.  But, there may be an error computing the mappers if
            # there are no records (since we can't get 'targetClass' then).
            # So, if there are no records, we just go ahead because the
            # comparison doesn't use the mappers.  But, if there *are* records,
            # we want to make sure that we *can* get the mappers, and if not,
            # don't bother comparing the contents.  Thus, these many lines of
            # comments to explain 'not self.records or self.mappers'.  :)

            if not self.records or self.mappers:

                missing, extra = self.compare(list(rows), self.records)

                for row in missing:
                    row.cells[0].annotation = "missing"
                    row.cells[0].wrong()

                for record in extra:
                    newRow = table.newRow(
                        cells = [
                            table.newCell(text=mapper.format(record))
                                for mapper in self.mappers
                        ]
                    )
                    newRow.cells[0].annotation = "extra"
                    newRow.cells[0].wrong()
                    table.addRow(newRow)
        finally:
            self.tearDown() # do any cleanup needed


    def compareRow(self,row,record):
        """Compare a single row against a single record, marking results"""

        for cell,mapper in zip(row.cells, self.mappers):
            try:
                mapper.get(record,cell)    # verify contents
            except:
                cell.exception()


    def tearDown(self):
        """Perform any post-comparison cleanup"""





























    def compare(self,rows,data,column=0):
        """Compare 'rows' and 'data' beginning at 'column' -> 'missing,extra'

        Return value is a tuple '(missingRows,extraRecords)' containing the
        'rows' not found in 'data', and the 'data' not present in 'rows',
        respectively.  This works by successively partitioning the data on
        each column from left to right, until either one of 'rows' or 'data'
        is empty, or both contain only a single item.  (In the latter case,
        the items are compared field-by-field, with the differences marked.)
        """

        if not rows or not data:
            # One list is empty, so other is "missing" (or extra) by definition
            return rows,data

        elif len(rows)==1 and len(data)==1:
            self.compareRow(rows[0],data[0])    # do 1-to-1 comparison
            return [],[]                        # no missing or extra rows

        else:
            # Partition the data into subsets based on current column,
            # then assemble missing/extra data by recursing on subsets
            mapper = self.mappers[column]
            extract = mapper.extract
            parse = mapper.parse

            recordMap = kjGraph([(extract(record),record) for record in data])
            rowMap = kjGraph([(parse(row.cells[column]),row) for row in rows])

            column += 1
            missing, extra = [], []
            for key in kjSet(rowMap.keys()+recordMap.keys()).items():
                m,e = self.compare(
                    rowMap.neighbors(key), recordMap.neighbors(key), column
                )
                missing.extend(m)
                extra.extend(e)

            return missing,extra


class SQLChecker(RecordChecker):

    """Check records from a database

    This RecordChecker subclass checks results from an SQL query.  In its
    simplest form, it performs a 'SELECT * FROM table' query if you supply it
    with a 'testTable' constructor argument.  Alternatively, you can supply a
    'testSQL' argument to specify the SQL to execute.

    By default, the SQL will be run against a connection object found under the
    'peak.ddt.testDB' property name.  You should define this property in a
    '[Named Services]' section of your test configuration file(s).

    Alternatively, you can supply a connection object as the 'testDB'
    constructor argument, or supply a 'dbKey' constructor argument to change
    the configuration key to something other than 'peak.ddt.testDB'.
    """

    records  = binding.Make(
        lambda self: list(self.testDB(self.testSQL))
    )

    testSQL = binding.Make(
        lambda self: "SELECT * FROM " + self.testTable
    )

    testTable = binding.Require("Name of the table/view to check")
    testDB    = binding.Obtain(naming.Indirect('dbKey'))
    dbKey     = PropertyName('peak.ddt.testDB')


    def methodNameFor(self,text):
        return text.strip()


    def getMapper(self,name):
        mapper = super(SQLChecker,self).getMapper(name)
        mapper.suggestType(model.Repr)
        return mapper


class ActionChecker(ModelChecker):

    """Test a domain object using a "script" of actions

    This 'ModelChecker' subclass reads actions from a table with three or
    more columns.  The first cell in each row is a "command", such as "start",
    "enter", "press", or "check", that is used to look up a method on the
    action processor itself.  The invoked method can then use the remaining
    cells from the row to obtain its arguments.  See the docs for the 'start',
    'enter', 'press', and 'check' methods for more details.

    Note that tables used with 'ActionChecker' must *not* include column
    headings, as 'ActionChecker' does not parse them.  (As a result, it also
    has no need for a 'columnSuffix' attribute or 'parseHeader()' method.)

    Unlike 'ModelChecker', 'ActionChecker' should not be given a specific
    'targetClass' to use.  Instead, the 'start' command is used to create an
    instance of a specified class, which is then used until another 'start'
    command is executed.  Also, 'ActionChecker' does not use the
    'columnSuffixes' attribute, because it does not parse column headings.
    """

    # XXX suggestType handling???

    # our class is the class of whatever our instance is, at any point in time
    targetClass = binding.Obtain('targetInstance/__class__', noCache=True)
    fixtures = binding.Make( config.Namespace('peak.ddt.models') )

    def processRows(self,rows):
        """Just process rows; no column headings are required or wanted."""
        for row in rows:
            self.processRow(row, rows)

    def processRow(self,row,rows):
        """Process a row using 'self.getCommand(firstCell.text)(otherCells)'"""
        try:
            self.getCommand(row.cells[0].text)(row.cells[1:])
        except:
            row.cells[0].exception()


    def getCommand(self,text):
        """Lookup 'text' as a method of this processor

        You can override this if you want to use a different strategy for
        obtaining commands.  The returned command must be a callable that
        takes one parameter: a list of cells.  The cells the command receives
        will be the remainder of the row that contained the command; typically
        this means 'row.cells[1:]'.
        """
        return getattr(self, titleAsMethodName(text))


    def mapCell(self,mapperCell,mappedCell,mapMethod):

        """Convenience method for two-argument mapping commands"""

        try:
            mapMethod = getattr(self.getMapper(mapperCell.text),mapMethod)
        except:
            mapperCell.exception()
        try:
            mapMethod(self.targetInstance, mappedCell)
        except:
            mappedCell.exception()

















    # Basic commands

    def start(self,cells):
        """Obtain an instance of the specified type and use it from here on
        """
        try:
            name = titleAsPropertyName(cells[0].text)
            self.targetInstance = self.fixtures[name]
            # XXX if processor, pass extra cells?
        except:
            cells[0].exception()


    def enter(self,cells):
        """Look up a field name, and then set it to value
        """
        self.mapCell(cells[0],cells[1],'set')


    def press(self,cells):
        """Invoke specified method/button/whatever
        """
        self.mapCell(cells[0],cells[0],'invoke')


    def check(self,cells):
        """Look up a field name, and check if value matches
        """
        self.mapCell(cells[0],cells[1],'get')












class Summary(AbstractProcessor):

    """Add rows to a table summarizing the test results so far"""

    key = "Counts"

    def processTable(self,table,tables):
        from datetime import datetime
        document = table.document
        summary = document.summary
        summary[self.key] = table.document.score
        summary['Run for'] = datetime.now() - summary['Run at']
        items = summary.items(); items.sort()

        for k,v in items:
            row = table.newRow(
                cells=[table.newCell(text=k),table.newCell(text=str(v))]
            )
            table.addRow(row)

            if k==self.key:
                self.reportCounts(row.cells[1])

    def reportCounts(self,cell):

        before = cell.document.score

        if before.wrong or before.exceptions:
            cell.wrong()
        else:
            cell.right()

        # Put the score back to what it was
        cell.document.score = before







class PropertyAsCellMapper(object):

    """Cell mapping support for 'property' and other data descriptors"""

    protocols.advise(
        instancesProvide=[ICellMapper],
        asAdapterForTypes=[property]
    )

    def __init__(self,ob,proto):
        self.subject = ob
        self.extract = ob.__get__
        self._set = ob.__set__

    dataType = model.String

    def suggestType(self,dataType):
        self.dataType = dataType

    def get(self,instance,cell):
        value = self.extract(instance)
        cell.assertEqual(value, self.dataType)

    def set(self,instance,cell):
        value = self.parse(cell)
        self._set(instance, value)

    def invoke(self,instance,cell):
        try:    raise TypeError("Descriptors can't be invoked", self.subject)
        except: cell.exception()

    def parse(self,cell):
        try:    return self.dataType.mdl_fromString(cell.text)
        except: cell.exception()

    def format(self,instance):
        return self.dataType.mdl_toString(self.extract(instance))




class ItemCell(PropertyAsCellMapper):

    """Treat mapping key as a cell mapper"""

    def __init__(self,key):
        self.subject = key

    def extract(self,ob):
        return ob[self.subject]

    def _set(self,ob,value):
        ob[self.subject] = value





























class CallableAsCellMapper(PropertyAsCellMapper):

    """Cell mapping support for methods"""

    protocols.advise(
        instancesProvide=[ICellMapper],
        asAdapterForProtocols=[ISignature]
    )

    def __init__(self,ob,proto):
        self.subject = ob
        self.extract = self._set = ob.getCallable()


    def invoke(self,instance,cell):
        try:
            self.extract(instance)
        except:
            cell.exception()


def descriptorAsCellMapper(ob,proto):
    if hasattr(ob,'__set__') and hasattr(ob,'__get__'):
        return PropertyAsCellMapper(ob,proto)


protocols.declareAdapter(
    descriptorAsCellMapper, provides=[ICellMapper], forTypes=[object]
)












class FeatureAsCellMapper(PropertyAsCellMapper):

    """Cell mapping support for 'model.IFeature' descriptors"""

    protocols.advise(
        instancesProvide=[ICellMapper],
        asAdapterForProtocols=[model.IFeature]
    )

    def __init__(self,ob,proto):
        self._parse = ob.parse
        self._format = ob.format
        super(FeatureAsCellMapper,self).__init__(ob,proto)

    def suggestType(self,dataType):
        pass    # we know our datatype, so we don't care about this

    def get(self,instance,cell):
        value = self.extract(instance)
        cellval = self.parse(cell)

        if not cell.score:  # only process if not already scored
            if cellval == value:
                cell.right()
            else:
                try:
                    cell.wrong(self._format(value))
                except:
                    cell.exception()

    def parse(self,cell):
        try:
            return self._parse(cell.text)
        except:
            cell.exception()

    def format(self,instance):
        return self._format(self.extract(instance))



