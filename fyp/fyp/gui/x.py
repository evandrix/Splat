import sip
import ImageQt
import ImageEnhance
import os
import time
import sys
import ctypes
import Image
from PyQt4 import QtGui, QtCore
from OMITGraphicsView import *
from FileTree import *
from ListWidget import *

def load_image(filename, qwidget):
    print >> sys.stderr, "load_image(%s)" % filename
    scene = QtGui.QGraphicsScene()
    if filename:
        pixmap = QtGui.QPixmap(filename)
        qgpi = QGraphicsPixmapItem(pixmap)
        scene.addItem(qgpi)
        view = OMITGraphicsView(pixmap, scene, qwidget)
    else:
        view = OMITGraphicsView(None, scene, qwidget)
    view.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
    return scene, view

        filelist = {}
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.png'):
                    filelist[file] = os.path.join(root, file)
        splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
        # pane1
        self.left = QtGui.QFrame(self)
        self.left.setFrameShape(QtGui.QFrame.StyledPanel)
        self.scene, self.view = load_image(None, self.left)
        self.view.setMinimumSize(.8*resolution.width(), resolution.height())
        splitter.addWidget(self.view)

        # pane2
        self.right = QtGui.QSplitter(QtCore.Qt.Vertical)
        label = QtGui.QLabel('   <status>', None)#parent

        self.model = QtGui.QDirModel()
        self.model.setNameFilters(['*.png'])
        self.model.setFilter(QtCore.QDir.AllDirs|QtCore.QDir.Files|QtCore.QDir.NoDotAndDotDot|QtCore.QDir.CaseSensitive)
        self.model.setSorting(QtCore.QDir.Name|QtCore.QDir.DirsFirst)
        parentIndex = self.model.index(directory)
        rows        = self.model.rowCount(parentIndex)

        self.tree = FileTree(self.scene, self.view, self.left)
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(directory))
        [self.tree.hideColumn(n) for n in xrange(1,4)]
        self.tree.header().hide()
        self.tree.setColumnWidth(0,256)
        QtCore.QObject.connect(self.tree,
            QtCore.SIGNAL("clicked(QModelIndex)"), self.listClicked)
        self.right.addWidget(self.tree)

#        listwidget = ListWidget({}, scene, view, left, label)
#        listwidget.setFlow(QtGui.QListView.TopToBottom)
#        listwidget.setLayoutMode(QtGui.QListView.SinglePass)
#        listwidget.setMovement(QtGui.QListView.Static)
#        listwidget.setResizeMode(QtGui.QListView.Adjust)
#        listwidget.setViewMode(QtGui.QListView.ListMode)
#        self.right.addWidget(listwidget)

        combobox = QtGui.QComboBox()
        combobox.addItems(filelist.keys())
        combobox.currentIndexChanged.connect(self.onCurrentIndexChanged)
#        right.addWidget(combobox)
        button = QtGui.QPushButton('Run!')
        button.setFocusPolicy(QtCore.Qt.NoFocus)
#        right.addWidget(button)
#        self.connect(button, QtCore.SIGNAL('clicked()'), self.showDialog)
#        self.button.clicked.connect(self.do_test)
        splitter.addWidget(self.right)
        self.setCentralWidget(splitter)

    def listClicked(self, index):
        if index.row() >= 0:
            crawler = index.model()
            if crawler and not os.path.isdir(crawler.filePath(index)):
                the_file = crawler.filePath(index)
                print 'Window::listClicked(%d:%s)' % (index.row(), crawler.fileName(index))
                #print crawler.fileIcon(index), crawler.fileInfo(index)
                the_image = Image.open(str(the_file))
                width, height = the_image.size
                pixmap = QtGui.QPixmap(the_file)
                qgpi   = QtGui.QGraphicsPixmapItem(pixmap)
                self.scene.clear()
                self.scene.addItem(qgpi)
                self.view = OMITGraphicsView(pixmap, self.scene, self.left)
                self.view.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
                self.view.zoomfit()
                self.view.fitInView(QtCore.QRectF(0, 0, width, height), QtCore.Qt.KeepAspectRatio)
                self.scene.update()

    def onChanged(self, text):
        print 'Window::onChanged()'
        self.status.setText(text)
        self.status.adjustSize()
    def onCurrentIndexChanged(self, arg):
        print 'Window::onCurrentIndexChanged(%s)' % arg

    def update(self):
        print 'Window::update()'

