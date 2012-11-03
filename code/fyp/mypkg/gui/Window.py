import sip
import ImageQt
import ImageEnhance
import os
import time
import sys
import ctypes
import Image
from PyQt4 import QtGui, QtCore
from FileTree import *
from GraphicsView import *

class Window(QtGui.QMainWindow):
    def __init__(self, parent=None):
        print >> sys.stderr, 'Window::init()'
        QtGui.QMainWindow.__init__(self, None, QtCore.Qt.Tool|QtCore.Qt.FramelessWindowHint)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setAttribute(QtCore.Qt.WA_QuitOnClose, True)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowTitle('FYP module 2012')
        self.select_img_folder()

    def select_img_folder(self):
        fd = QtGui.QFileDialog(caption="Select image folder")
        tree = fd.findChild(QtGui.QTreeView)
        tree.setRootIsDecorated(True)
        tree.setItemsExpandable(True)
        fd.setFileMode(QtGui.QFileDialog.Directory)
        fd.setViewMode(QtGui.QFileDialog.Detail)
        if fd.exec_():
            self.init_ui(str(fd.selectedFiles()[0]))
        else:
            sys.exit(0)

    def init_ui(self, directory):
        # UI style
        QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('macintosh'))
        # UI position
        self.move(0, 0)
        self.resolution = QtGui.QDesktopWidget().availableGeometry()
        self.setGeometry(self.resolution)
        self.showFullScreen()

        # UI components
        self.splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
        # pane1
        self.left = QtGui.QFrame(self)
        self.left.setFrameShape(QtGui.QFrame.StyledPanel)

        self.scene = QtGui.QGraphicsScene()
        self.view = GraphicsView(None, self.scene, self.left)
        self.view.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
        self.view.setMinimumSize(.8*self.resolution.width(),
            self.resolution.height())
        self.view.setCacheMode(QtGui.QGraphicsView.CacheBackground)
        self.view.setViewportUpdateMode(QtGui.QGraphicsView.BoundingRectViewportUpdate)
        self.splitter.addWidget(self.view)

        # pane2
        self.right = QtGui.QSplitter(QtCore.Qt.Vertical)
        self.right_top_model = QtGui.QDirModel()
        self.right_top_model.setNameFilters(['*.png'])
        self.right_top_model.setFilter(QtCore.QDir.AllDirs|QtCore.QDir.Files|
            QtCore.QDir.NoDotAndDotDot|QtCore.QDir.CaseSensitive)
        self.right_top_model.setSorting(QtCore.QDir.Name|QtCore.QDir.DirsFirst)
        self.right_top_tree = FileTree(self.right_top_model, directory)
        QtCore.QObject.connect(self.right_top_tree,
            QtCore.SIGNAL("clicked(QModelIndex)"), self.right_top_clicked)
        self.right.addWidget(self.right_top_tree)
        self.right_bottom_tree = FileTree(None, directory)
        QtCore.QObject.connect(self.right_bottom_tree,
            QtCore.SIGNAL("clicked(QModelIndex)"), self.right_bottom_clicked)
        self.right.addWidget(self.right_bottom_tree)
        self.splitter.addWidget(self.right)
        self.setCentralWidget(self.splitter)

    def load_image(self, filename, qwidget):
        print >> sys.stderr, "Window::load_image(%s)" % filename
        self.filename = filename
        self.qwidget = qwidget
        if filename and os.path.isfile(filename) \
            and os.path.splitext(filename)[1].endswith('.png'):
            [self.scene.removeItem(item) for item in self.scene.items()]
            self.image = Image.open(str(filename))
            width, height = self.image.size
            self.pixmap = QtGui.QPixmap(filename)
            self.qgpi = QtGui.QGraphicsPixmapItem(self.pixmap)
            self.scene.addItem(self.qgpi)
            self.scene.setSceneRect(self.scene.itemsBoundingRect())
            self.view.centerOn(self.view.size().width()/2,
                self.view.size().height()/2)
            assert len(self.scene.items()) == 1
            self.view.scene  = self.scene
            self.view.pixmap = self.pixmap
#            print >> sys.stderr, self.left.size(), self.view.size(), self.scene.sceneRect(), self.scene.itemsBoundingRect(), (width, height)

    def right_top_clicked(self, index):
        print >> sys.stderr, 'Window::right_top_clicked()'
        if index and index.isValid() and index.row() >= 0:
            model = index.model()
            if model:
                path = str(model.filePath(index))
                if os.path.isfile(path) \
                    and os.path.splitext(path)[1].endswith('.png'):
                    print >> sys.stderr, 'Window::show_image(%s)' % path
                    self.load_image(path, self.left)

                    self.right_bottom_tree.setModel(None)
                elif os.path.isdir(path) and model.isDir(index):
                    print >> sys.stderr, 'Window::show_dir(%s)' % path

                    self.model = QtGui.QDirModel()
                    self.model.setNameFilters(['*.png'])
                    self.model.setFilter(QtCore.QDir.Files|
                        QtCore.QDir.NoDotAndDotDot|QtCore.QDir.CaseSensitive)
                    self.model.setSorting(QtCore.QDir.Name)

                    self.right_bottom_tree.setModel(self.model)
                    self.right_bottom_tree.setRootIndex(self.model.index(path))
                    [self.right_bottom_tree.hideColumn(n) for n in xrange(1,4)]
                    self.right_bottom_tree.header().hide()
                    self.right_bottom_tree.setColumnWidth(0,256)

                    # clear image loaded
    def right_bottom_clicked(self, index):
        if index and index.isValid() and index.row() >= 0:
            model = index.model()
            if model:
                path = str(model.filePath(index))
                if os.path.isfile(path) \
                    and os.path.splitext(path)[1].endswith('.png'):
                        print >> sys.stderr, 'Window::right_bottom_clicked(%s)' % path
                        self.load_image(path, self.left)

    def keyPressEvent(self, event):
        if isinstance(event, QtGui.QKeyEvent):
            event.accept()
        else:
            event.ignore()
        if event.key() == QtCore.Qt.Key_Q \
            and QtGui.QMessageBox.question(self, 'Question',
                "Exit application?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No,
                QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
                self.close()
                sys.exit(0)
        QtGui.QMainWindow.keyPressEvent(self,event)
    def handleMessage(self, message):
        print >> sys.stderr, 'Window::handleMessage(%s)' % message

    def closeEvent(self, event):
        QtGui.QApplication.instance().quit()

