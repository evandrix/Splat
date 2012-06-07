#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Image
import ImageQt
import ImageEnhance
import os
import time
import sys
import ctypes
import sip
from PyQt4 import QtGui, QtCore, QtNetwork
from PyQt4.Qt import *
from PyQt4.QtCore import *
from PyQt4.QtGui import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QPixmap, QGraphicsPixmapItem, QAction, QKeySequence

class OMITGraphicsView(QtGui.QGraphicsView):
    def __init__(self, pixmap, scene, parent, *args):
        QtGui.QGraphicsView.__init__(self, scene)
        self.zoomLevel = 1.0
        self.win = parent
        self.img = pixmap
        self.setupActions()
        QtCore.QMetaObject.connectSlotsByName(self)

    def setupActions(self):
        zoomfit = QAction(self)
        zoomfit.setShortcuts([QKeySequence.fromString('1')])
        zoomfit.triggered.connect(self.zoomfit)
        self.addAction(zoomfit)
        zoom200 = QAction(self)
        zoom200.setShortcuts([QKeySequence.fromString('2')])
        zoom200.triggered.connect(self.zoom200)
        self.addAction(zoom200)

    def zoomfit(self, *ignore):
        winSize = self.size()
        imgSize = self.img.size()
        hZoom = 1.0*winSize.width ()/imgSize.width ()
        vZoom = 1.0*winSize.height()/imgSize.height()
        zoomLevel = min(hZoom, vZoom)
        self.zoomTo(zoomLevel)

    def zoom200(self, *ignore):
        self.zoomTo(1.0)

    def zoomTo(self, zoomLevel):
        scale = zoomLevel/self.zoomLevel
        self.scale(scale, scale)
        self.zoomLevel = zoomLevel

	def resizeEvent(self, event):
		size = event.size()
		item = self.items()[0]
		# using current pixmap after n-resizes would get really blurry image
		#pixmap = item.pixmap()
		pixmap = self.origPixmap
		pixmap = pixmap.scaled(size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
		self.centerOn(1.0, 1.0)
		item.setPixmap(pixmap)

def load_image(filename, qwidget):
    if filename:
        pixmap = QtGui.QPixmap(filename)
        qgpi = QGraphicsPixmapItem(pixmap)
        scene = QtGui.QGraphicsScene()
        scene.addItem(qgpi)
        view = OMITGraphicsView(pixmap, scene, qwidget)
        view.setDragMode(QGraphicsView.ScrollHandDrag)
    else:
        scene = QtGui.QGraphicsScene()
        view = OMITGraphicsView(None, scene, qwidget)
        view.setDragMode(QGraphicsView.ScrollHandDrag)
    return scene, view

class Application(QtGui.QApplication):
    def __init__(self, argv, key):
        QtGui.QApplication.__init__(self, argv)
        self._memory = QtCore.QSharedMemory(self)
        self._memory.setKey(key)
        if self._memory.attach():
            self._running = True
        else:
            self._running = False
            if not self._memory.create(1):
                raise RuntimeError(
                    self._memory.errorString().toLocal8Bit().data())
        self._key = key
        self._timeout = 1000
        self._server = QtNetwork.QLocalServer(self)
        if not self.isRunning():
            self._server.newConnection.connect(self.handleMessage)
            self._server.listen(self._key)

    def isRunning(self):
        return self._running

    def handleMessage(self):
        socket = self._server.nextPendingConnection()
        if socket.waitForReadyRead(self._timeout):
            self.emit(QtCore.SIGNAL('messageAvailable'),
                      QtCore.QString.fromUtf8(socket.readAll().data()))
            socket.disconnectFromServer()
        else:
            QtCore.qDebug(socket.errorString().toLatin1())

    def sendMessage(self, message):
        if self.isRunning():
            socket = QtNetwork.QLocalSocket(self)
            socket.connectToServer(self._key, QtCore.QIODevice.WriteOnly)
            if not socket.waitForConnected(self._timeout):
                print(socket.errorString().toLocal8Bit().data())
                return False
            socket.write(unicode(message).encode('utf-8'))
            if not socket.waitForBytesWritten(self._timeout):
                print(socket.errorString().toLocal8Bit().data())
                return False
            socket.disconnectFromServer()
            return True
        return False

class ListWidget(QtGui.QListWidget):
    def __init__(self, filelist, scene, view, qwidget, lbl_status):
        QtGui.QListWidget.__init__(self)
        self.scene = scene
        self.view = view
        self.qwidget = qwidget
        self.lbl_status = lbl_status
        self.filelist = filelist
        self.add_items(filelist)
        self.itemClicked.connect(self.item_click)

    def add_items(self, filelist):
        self.addItems(sorted(filelist.keys()))

    def item_click(self, item):
        print item
        self.lbl_status.setText(str(item.text()))
        file = self.filelist[str(item.text())]
        img = Image.open(file)
        w, h = img.size
        pixmap = QtGui.QPixmap(file)
        qgpi = QGraphicsPixmapItem(pixmap)
        self.scene.clear()
        self.scene.addItem(qgpi)
        self.view = OMITGraphicsView(pixmap, self.scene, self.qwidget)
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.view.zoomfit()
        self.view.fitInView(QRectF(0, 0, w, h), Qt.KeepAspectRatio)
        self.scene.update()

class Window(QtGui.QMainWindow):
    def __init__(self, parent=None):
        print 'Window::init()'
        QtGui.QWidget.__init__(self, parent)
        self.initUI()

    def initUI(self):
        directory = '/Users/lwy08/Downloads/fyp/fyp/pygraph-pngs'
        filelist = {}
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.png'):
                    filelist[file] = os.path.join(root, file)

        splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)

        # pane1
        left = QtGui.QFrame(self)
        left.setFrameShape(QtGui.QFrame.StyledPanel)
        scene, view = load_image(None, left)
        view.setMinimumSize(1024, 0)
        splitter.addWidget(view)

        # pane2
        right = QtGui.QSplitter(QtCore.Qt.Vertical)
        label = QtGui.QLabel('   <status>', right)
        listwidget = ListWidget(filelist, scene, view, left, label)
#        listwidget.setViewMode(QtGui.QListView.IconMode)
#        listwidget.setLayoutMode(QtGui.QListView.SinglePass)
#        listwidget.setResizeMode(QtGui.QListView.Adjust)
#        listwidget.setGridSize(QtCore.QSize(75, 75))
        right.addWidget(listwidget)

        combobox = QtGui.QComboBox()
        combobox.addItems(filelist.keys())
#        combobox.currentIndexChanged.connect(self.onCurrentIndexChanged)
        right.addWidget(combobox)

        button = QtGui.QPushButton('Run!', self)
        button.setFocusPolicy(QtCore.Qt.NoFocus)
#        self.connect(button, QtCore.SIGNAL('clicked()'), self.showDialog)
#        self.button.clicked.connect(self.do_test)
        right.addWidget(button)

        splitter.addWidget(right)
        self.setCentralWidget(splitter)

        QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))
        self.move(0, 0)
        self.setGeometry(0, 0, 1680, 1050)
        self.setWindowTitle('FYP module 2012')
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.showFullScreen()

    def handleMessage(self, message):
        print 'Window::handleMessage()'
        self.status.setText(message)
        self.status.adjustSize()
    def onChanged(self, text):
        print 'Window::onChanged()'
        self.status.setText(text)
        self.status.adjustSize()

    def update(self):
        print 'Window::update()'

    def keyPressEvent(self, event):
        if isinstance(event, QtGui.QKeyEvent):
            event.accept()
        else:
            event.ignore()

        if event.key() == Qt.Key_Q:
            if QtGui.QMessageBox.question(self,
                'Question',
                "Are you sure to quit?",
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
                self.close()
                sys.exit(0)
        elif event.modifiers() & QtCore.Qt.ShiftModifier and event.key() == Qt.Key_Z:
            msg = QtGui.QMessageBox(
                QtGui.QMessageBox.Information,
                'Information','Shift+z was pressed')
            msg.exec_()

        QtGui.QMainWindow.keyPressEvent(self,event)

def main():
    app = Application(sys.argv, key='FYP')
    if app.isRunning():
        app.sendMessage('warning: app is already running!')
    window = Window()
    window.show()
    app.connect(app, QtCore.SIGNAL('messageAvailable'), window.handleMessage)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
