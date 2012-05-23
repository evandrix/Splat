from peak.api import *
import peak.ddt.api as ddt

class ArithmeticModel(model.Element):

    """Simple arithmetic model that's testable via 'ddt.ModelChecker'"""

    class x(model.Attribute):
        referencedType = model.Integer

    class y(model.Attribute):
        referencedType = model.Integer

    def plus(self):
        return self.x+self.y

    def minus(self):
        return self.x-self.y

    def times(self):
        return self.x*self.y

    def divide(self):
        return self.x/float(self.y)

    def clear(self):
        self.x = self.y = 0














class ArithmeticDemo(ddt.MethodChecker):
    """Demo processor for http://fit.c2.com/files/arithmetic.html

    Try running::

        peak ddt.web http://fit.c2.com/files/arithmetic.html

    to view the test output in your browser, comparing the original
    text and the annotated version."""

    symbols = {'+':'plus','-':'minus','*':'times', '/':'divide'}

    def getHandler(self,text):
        text = text.strip()
        if text in self.symbols:
            return getattr(self, self.symbols[text])
        if text.endswith("()"):
            text=text[:-2]
        return getattr(self,text)

    def x(self,cell):
        self._x = int(cell.text)

    def y(self,cell):
        self._y = int(cell.text)

    def plus(self,cell):
        cell.assertEqual(self._x+self._y, model.Integer)

    def minus(self,cell):
        cell.assertEqual(self._x-self._y, model.Integer)

    def times(self,cell):
        cell.assertEqual(self._x*self._y, model.Long)

    def divide(self,cell):
        cell.assertEqual(self._x/float(self._y), model.Float)

    floating = divide


