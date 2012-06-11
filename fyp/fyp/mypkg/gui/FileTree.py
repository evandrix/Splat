import os
import sys
from PyQt4 import QtGui, QtCore

class FileTree(QtGui.QTreeView):
    def __init__(self, model, directory, parent=None):
        print >> sys.stderr, 'FileTree::init()'
        QtGui.QTreeView.__init__(self)

        if model:
            self.model = model
            self.setModel(model)
            self.setRootIndex(model.index(directory))
            self.header().hide()
            self.setColumnWidth(0,256)
            [self.hideColumn(n) for n in xrange(1,4)]
        else:
            self.model = None
            self.setModel(None)

    def keyPressEvent(self, event):
        if not self.selectedIndexes():
            return

        current_index = self.selectedIndexes()[0]
        if event.key() == QtCore.Qt.Key_Up:
            print >> sys.stderr, 'FileTree::keypress(UP)'
            index = self.indexAbove(current_index)
            self.emit(QtCore.SIGNAL("clicked(QModelIndex)"), index)
        elif event.key() == QtCore.Qt.Key_Down:
            print >> sys.stderr, 'FileTree::keypress(DOWN)'
            index = self.indexBelow(current_index)
            self.emit(QtCore.SIGNAL("clicked(QModelIndex)"), index)
        QtGui.QTreeView.keyPressEvent(self, event)
