from peak.api import *

__all__ = [
    'ICellProcessor', 'IDocumentProcessor', 'IRowProcessor', 'ITableProcessor',
    'ICellMapper',
]


class IDocumentProcessor(protocols.Interface):

    def processDocument(document):
        """Process a document, updating it with test results

        Note that this method (and anything it calls) should not interact with
        the document's DM or transaction context.  Typically this method would
        simply iterate over the document's tables, invoking an appropriate
        'ITableProcessor' for each one."""


class ITableProcessor(protocols.Interface):

    def processTable(thisTable,remainingTables):
        """Process 'thisTable', and optionally consume some 'remainingTables'

        'remainingTables' is an iterator over the remaining tables in the same
        document, if any.  Any tables consumed from this iterator will be
        skipped by the calling document processor.  This allows a table
        processor to take control of processing for subsequent tables in a
        document, e.g. when multiple tables are needed to process a single
        test."""











class IRowProcessor(protocols.Interface):

    def processRow(thisRow,remainingRows):
        """Process 'thisRow', and optionally consume some 'remainingRows'

        'remainingRows' is an iterator over the remaining rows in the same
        table, if any.  Any rows consumed from this iterator will be
        skipped by the calling table processor.  This allows a row
        processor to take control of processing for subsequent rows in a
        table, e.g. when multiple rows need to be processed by the same
        processor."""


class ICellProcessor(protocols.Interface):

    def processCell(cell):
        """Process 'cell', using it for input or output as needed"""
























class ICellMapper(protocols.Interface):

    """Provide a uniform getter/setter interface for processing cell data

    There are two default implementations of this; one for features of
    domain model classes, and one for instance methods.  Features map get and
    set to getting or setting the attribute, while methods map "get" to
    checking the return value of the method called with no argument, and "set"
    to calling the method with one argument, whose value is provided by the
    cell."""

    def get(targetInstance, cell):
        """Get data from the 'targetInstance' and compare it to 'cell'

        This method should mark the cell right/wrong, perform any necessary
        annotations, etc."""

    def set(targetInstance, cell):
        """Pass data from 'cell' to 'targetInstance'

        In general, this method shouldn't do anything to the cell, except
        perhaps to record an exception if there is a problem passing the
        data."""

    def invoke(targetInstance,cell):
        """Invoke the feature on the 'targetInstance', with no arguments

        If the invocation raises an exception, record it in 'cell'.  If the
        feature does not support invocation, record an error in 'cell'."""

    def parse(cell):
        """Interpret 'cell.text' according to datatype, and return the value

        If an error occurs, mark the cell with an exception, and return 'None'.
        """

    def format(targetInstance):
        """Return 'extract(targetInstance)' as a formatted string"""



    def extract(targetInstance):
        """Return the value of the feature for targetInstance"""

        
    def suggestType(dataType):
        """Suggest the 'model.IType' to be used for parsing/formatting cells

        If a cell mapper already knows the correct data type, it may ignore the
        type supplied by this method.  If a cell mapper does not know what type
        to use, it should default to 'model.String' unless this method is
        called."""






























