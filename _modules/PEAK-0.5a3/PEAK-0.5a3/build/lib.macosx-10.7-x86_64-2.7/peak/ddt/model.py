from peak.api import *
import sys

__all__ = [
    'Score', 'Zeros', 'Right', 'Wrong', 'Error', 'Ignored',
    'Document', 'Table', 'Row', 'Cell'
]


































class Score(model.Struct):

    """Test result statistics"""

    class right(model.structField):
        referencedType = model.Integer
        defaultValue = 0

    class wrong(model.structField):
        referencedType = model.Integer
        defaultValue = 0

    class ignored(model.structField):
        referencedType = model.Integer
        defaultValue = 0

    class exceptions(model.structField):
        referencedType = model.Integer
        defaultValue = 0

    def __add__(self,other):
        return Score(
            right       = self.right      + other.right,
            wrong       = self.wrong      + other.wrong,
            ignored     = self.ignored    + other.ignored,
            exceptions  = self.exceptions + other.exceptions,
        )

    def __sub__(self,other):
        return Score(
            right       = self.right      - other.right,
            wrong       = self.wrong      - other.wrong,
            ignored     = self.ignored    - other.ignored,
            exceptions  = self.exceptions - other.exceptions,
        )

    def __str__(self):
        return "%d right, %d wrong, %d ignored, %d exceptions" % (
            self.right, self.wrong, self.ignored, self.exceptions
        )

    def __nonzero__(self):
        return (self.right or self.wrong or self.ignored or self.exceptions)<>0


Zeros = Score()
Right = Score(right=1)
Wrong = Score(wrong=1)
Ignored = Score(ignored=1)
Error = Score(exceptions=1)
































class Item(model.Element):

    """Abstract base for all items"""

    mdl_isAbstract = True

    class document(model.Attribute):
        referencedType = 'Document'

    def newRow(self,**kw):
        row = self.getParentComponent().newItem(Row)
        row.document = self.document
        for k,v in kw.items(): setattr(row,k,v)
        return row

    def newCell(self,**kw):
        cell = self.getParentComponent().newItem(Cell)
        cell.document = self.document
        for k,v in kw.items(): setattr(cell,k,v)
        return cell


class children(model.Collection):
    """An attribute that manages child nodes' document links"""

    def _onLink(feature,element,item,posn):
        item.document = element.document

    def _onUnlink(feature,element,item,posn):
        if item.document is element:
            item.document = None










class Document(Item):

    """A document describing tests to be performed, and the results"""

    class tables(children):
        referencedType = 'Table'
        singularName = 'table'

    class score(model.Attribute):
        referencedType = Score
        defaultValue = Zeros

    class summary(model.Attribute):
        """Dictionary of data to be added to output summaries"""

    class document(model.Attribute):

        isDerived = True

        def get(feature,element):
            return element

    def getParent(self):
        return None


class Table(Item):

    """A table ("test fixture") describing some test data or actions"""

    class rows(children):
        referencedType = 'Row'
        referencedEnd  = 'table'
        singularName = 'row'

    def getParent(self):
        return self.document




class Row(Item):

    """A row of a table"""

    class cells(children):
        referencedType = 'Cell'
        referencedEnd = 'row'
        singularName = 'cell'

    class table(model.Attribute):
        referencedType = Table
        referencedEnd  = 'rows'

    def getParent(self):
        return self.table


























class Cell(Item):
    """An individual data value or action, with concrete results"""

    class row(model.Attribute):
        referencedType = Row
        referencedEnd = 'cells'

    class text(model.Attribute):
        """Text contents of the cell (read-only)"""
        referencedType = model.String

    class score(model.Attribute):
        """This cell's status"""
        referencedType = Score
        defaultValue   = Zeros

        # Whenever score is changed, update document score

        def _onLink(feature,element,item,posn):
            if item<>Zeros:
                element.document.score += item

        def _onUnlink(feature,element,item,posn):
            if item<>Zeros:
                element.document.score -= item

    class exc_info(model.Attribute):
        """A 'sys.exc_info()' tuple for the exception occuring in this cell"""
        defaultValue = None

    class actual(model.Attribute):
        """The actual output for this cell, as opposed to expected"""
        referencedType = model.String

    class annotation(model.Attribute):
        referencedType = model.String
        defaultValue = ''

    def getParent(self):
        return self.row

    def assertEqual(self, value, dataType=model.String):
        """Check that text matches 'value', using 'dataType' for conversions

        If the value doesn't match, the cell will be flagged as "wrong",
        and the actual value is added to the cell."""
        if dataType is model.String: value = str(value) # hack
        if dataType.mdl_normalize(value)<>dataType.mdl_fromString(self.text):
            self.wrong(dataType.mdl_toString(value))
        else:
            self.right()

    def right(self):
        """Flag the cell as correct"""

        self._assertUnscored()
        self.score = Right

    def wrong(self,*actual):
        """Flag the cell as incorrect, w/optional actual value"""

        self._assertUnscored()
        self.score = Wrong

        if actual:
            self.actual, = actual

    def ignore(self):
        """Flag the cell as ignored"""
        self._assertUnscored()
        self.score = Ignored

    def exception(self, exc_info=None):
        """Flag the cell as producing an error, w/traceback info"""

        if exc_info is None:
            exc_info = sys.exc_info()
        self._assertUnscored()
        self.score = Error
        self.exc_info = exc_info


    def _assertUnscored(self):
        if self.score:
            raise ValueError("Cell already scored", self)






































