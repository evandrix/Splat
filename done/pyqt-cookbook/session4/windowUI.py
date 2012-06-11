# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'window.ui'
#
# Created: Fri May 25 14:02:16 2012
#      by: PyQt4 UI code generator 4.8.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(340, 460)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/todo.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.list = QtGui.QTreeWidget(self.centralwidget)
        self.list.setAlternatingRowColors(True)
        self.list.setRootIsDecorated(False)
        self.list.setUniformRowHeights(True)
        self.list.setAllColumnsShowFocus(True)
        self.list.setObjectName(_fromUtf8("list"))
        self.horizontalLayout.addWidget(self.list)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 340, 27))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuTask = QtGui.QMenu(self.menubar)
        self.menuTask.setObjectName(_fromUtf8("menuTask"))
        MainWindow.setMenuBar(self.menubar)
        self.toolBar = QtGui.QToolBar(MainWindow)
        self.toolBar.setObjectName(_fromUtf8("toolBar"))
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.actionDelete_Task = QtGui.QAction(MainWindow)
        self.actionDelete_Task.setEnabled(False)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/delete.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionDelete_Task.setIcon(icon1)
        self.actionDelete_Task.setObjectName(_fromUtf8("actionDelete_Task"))
        self.menuTask.addAction(self.actionDelete_Task)
        self.menubar.addAction(self.menuTask.menuAction())
        self.toolBar.addAction(self.actionDelete_Task)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Todo", None, QtGui.QApplication.UnicodeUTF8))
        self.list.setSortingEnabled(True)
        self.list.headerItem().setText(0, QtGui.QApplication.translate("MainWindow", "Task", None, QtGui.QApplication.UnicodeUTF8))
        self.list.headerItem().setText(1, QtGui.QApplication.translate("MainWindow", "Date", None, QtGui.QApplication.UnicodeUTF8))
        self.list.headerItem().setText(2, QtGui.QApplication.translate("MainWindow", "Tags", None, QtGui.QApplication.UnicodeUTF8))
        self.menuTask.setTitle(QtGui.QApplication.translate("MainWindow", "&Task", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))
        self.actionDelete_Task.setText(QtGui.QApplication.translate("MainWindow", "Delete Task", None, QtGui.QApplication.UnicodeUTF8))
        self.actionDelete_Task.setShortcut(QtGui.QApplication.translate("MainWindow", "Del", None, QtGui.QApplication.UnicodeUTF8))



if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

