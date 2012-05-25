from PySide import QtGui  
from PySide import QtCore
from PySide import QtUiTools

class MyWidget(QtGui.QMainWindow):
    def __init__(self, *args):  
       apply(QtGui.QMainWindow.__init__, (self,) + args)

       loader = QtUiTools.QUiLoader()
       file = QtCore.QFile("pyside_ui_qtdesigner_form_test.ui")
       file.open(QtCore.QFile.ReadOnly)
       self.myWidget = loader.load(file, self)
       file.close()

       self.setCentralWidget(self.myWidget)

if __name__ == '__main__':  
   import sys  
   import os
   print("Running in " + os.getcwd() + " .\n")

   app = QtGui.QApplication(sys.argv)  

   win  = MyWidget()  
   win.show()

   app.connect(app, QtCore.SIGNAL("lastWindowClosed()"),
               app, QtCore.SLOT("quit()"))
   app.exec_()
