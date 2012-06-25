# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'editor.ui'
#
# Created: Fri May 25 13:59:08 2012
#      by: PyQt4 UI code generator 4.8.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(345, 270)
        self.verticalLayout = QtGui.QVBoxLayout(Form)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(Form)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.task = QtGui.QLineEdit(Form)
        self.task.setObjectName(_fromUtf8("task"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.task)
        self.done = QtGui.QCheckBox(Form)
        self.done.setObjectName(_fromUtf8("done"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.done)
        self.label_2 = QtGui.QLabel(Form)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_2)
        self.dateTime = QtGui.QDateTimeEdit(Form)
        self.dateTime.setCalendarPopup(True)
        self.dateTime.setObjectName(_fromUtf8("dateTime"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.dateTime)
        self.label_3 = QtGui.QLabel(Form)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.label_3)
        self.tags = QtGui.QLineEdit(Form)
        self.tags.setObjectName(_fromUtf8("tags"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.tags)
        self.verticalLayout.addLayout(self.formLayout)
        self.label.setBuddy(self.task)
        self.label_2.setBuddy(self.dateTime)
        self.label_3.setBuddy(self.tags)

        self.retranslateUi(Form)
        QtCore.QObject.connect(self.dateTime, QtCore.SIGNAL(_fromUtf8("dateTimeChanged(QDateTime)")), Form.save)
        QtCore.QObject.connect(self.done, QtCore.SIGNAL(_fromUtf8("stateChanged(int)")), Form.save)
        QtCore.QObject.connect(self.task, QtCore.SIGNAL(_fromUtf8("textChanged(QString)")), Form.save)
        QtCore.QObject.connect(self.tags, QtCore.SIGNAL(_fromUtf8("textChanged(QString)")), Form.save)
        QtCore.QMetaObject.connectSlotsByName(Form)
        Form.setTabOrder(self.task, self.done)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Form", "&Task:", None, QtGui.QApplication.UnicodeUTF8))
        self.done.setText(QtGui.QApplication.translate("Form", "&Finished", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Form", "&Due Date:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Form", "T&ags:", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Form = QtGui.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

