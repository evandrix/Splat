#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Image
import ImageQt
import ImageEnhance
import time
import sys
import ctypes
from PyQt4.Qt import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QApplication, QMainWindow, QGraphicsView, QGraphicsScene
from PyQt4.QtGui import QPixmap, QGraphicsPixmapItem, QAction, QKeySequence
import sip

class SingleApplication(QtGui.QApplication):
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

    def isRunning(self):
        return self._running

class SingleApplicationWithMessaging(SingleApplication):
    def __init__(self, argv, key):
        SingleApplication.__init__(self, argv, key)
        self._key = key
        self._timeout = 1000
        self._server = QtNetwork.QLocalServer(self)
        if not self.isRunning():
            self._server.newConnection.connect(self.handleMessage)
            self._server.listen(self._key)

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

class OMITGraphicsView(QtGui.QGraphicsView):
    def __init__(self, pixmap, scene, parent, *args):
        QGraphicsView.__init__(self, scene)
        self.zoomLevel= 1.0
        self.win= parent
        self.img= pixmap
        self.setupActions()

    def setupActions(self):
        # a factory to the right!
        zoomfit= QAction(self)
        zoomfit.setShortcuts([QKeySequence.fromString('F1')])
        zoomfit.triggered.connect(self.zoomfit)
        self.addAction(zoomfit)

        zoom200= QAction(self)
        zoom200.setShortcuts([QKeySequence.fromString('F2')])
        zoom200.triggered.connect(self.zoom200)
        self.addAction(zoom200)

    def zoomfit(self, *ignore):
        winSize= self.size()
        imgSize= self.img.size()
        print winSize, imgSize
        hZoom= 1.0*winSize.width ()/imgSize.width ()
        vZoom= 1.0*winSize.height()/imgSize.height()
        zoomLevel= min(hZoom, vZoom)
        print zoomLevel
        self.zoomTo(zoomLevel)

    def zoom200(self, *ignore):
        self.zoomTo(2.0)

    def zoomTo(self, zoomLevel):
        scale= zoomLevel/self.zoomLevel
        print "scaling", scale
        self.scale(scale, scale)
        self.zoomLevel= zoomLevel

class ImageView(QtGui.QGraphicsView):
	def __init__(self, parent=None, origPixmap=None):
		super(ImageView, self).__init__(parent)
		self.origPixmap = origPixmap
		QtCore.QMetaObject.connectSlotsByName(self)

	def resizeEvent(self, event):
		size = event.size()
		item =  self.items()[0]
		# using current pixmap after n-resizes would get really blurry image
		#pixmap = item.pixmap()
		pixmap = self.origPixmap
		pixmap = pixmap.scaled(size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
		self.centerOn(1.0, 1.0)
		item.setPixmap(pixmap)

class MyLineEdit(QtGui.QLineEdit):
    def __init__(self, *args):
        QLineEdit.__init__(self, *args)
    def event(self, event):
        if (event.type()==QEvent.KeyPress) and (event.key()==Qt.Key_Tab):
            self.emit(SIGNAL("tabPressed"))
            return True
        return QLineEdit.event(self, event)

class Window(QtGui.QWidget):    # QtGui.QMainWindow
    def handleMessage(self, message):
        self.edit.setText(message)

    def update(self):
        print 'update()'

    def keyPressEvent(self, event):
        if type(event) == QtGui.QKeyEvent:
            print 'event.key() =', event.key()
            event.accept()
        else:
            event.ignore()

        if event.key() == Qt.Key_Q:
            self.close()

        if event.modifiers() & QtCore.Qt.ShiftModifier:
            print 'Shift!'
            if event.key() == Qt.Key_K:
                msg = QtGui.QMessageBox(
                    QtGui.QMessageBox.Information,
                    'w00t','You pressed +k')
            msg.exec_()
#            reply = QtGui.QMessageBox.question(self, 'Message',
#                        "Are you sure to quit?", QtGui.QMessageBox.Yes |
#                        QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        # call base class keyPressEvent
        QtGui.QWidget.keyPressEvent(self, event)

    def __init__(self, parent=None):
        print 'Window::init()'
        super(Window, self).__init__(parent)
        self.connect(self, SIGNAL("tabPressed"), self.update)

        self.edit = MyLineEdit(self)
        self.edit.setMinimumWidth(300)

#        self.label = QtGui.QLabel(self)
#        self.label.setMinimumSize(512, 512)
#        self.comboBox = QtGui.QComboBox(self)
#        self.comboBox.addItems(["Image.{}".format(i) for i in range(2)])

        pixmap = QtGui.QPixmap('f1.png')
        qgpi = QGraphicsPixmapItem(pixmap)
        scene = QtGui.QGraphicsScene()
        scene.addItem(qgpi)
        view= OMITGraphicsView(pixmap, scene, self)
        view.setDragMode(QGraphicsView.ScrollHandDrag)
#        view.show()
#        grview = ImageView(origPixmap=pic)
#        scene.addPixmap(pic)
#        grview.setScene(scene)
#        grview.show()

        vbox = QtGui.QVBoxLayout(self)
#        vbox.addWidget(self.label)
#        vbox.addWidget(self.comboBox)
        vbox.addWidget(view)
        vbox.addWidget(self.edit)

#        self.initImages()
#        self.comboBox.currentIndexChanged.connect(self.onCurrentIndexChanged)

#        cal = QtGui.QCalendarWidget(self)
#        cal.setGridVisible(True)
#        cal.move(20, 20)
#        cal.clicked[QtCore.QDate].connect(self.showDate)
#        date = cal.selectedDate()
#        self.lbl = QtGui.QLabel(self)
#        self.lbl.setText(date.toString())
#        self.lbl.move(130, 260)

        self.setGeometry(0, 0, 1680, 1050)
        self.setWindowTitle('FYP')
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.showFullScreen()
        self.show()

    def showDate(self, date):
        self.lbl.setText(date.toString())

    def onCurrentIndexChanged(self, index):
        self.label.setPixmap(QtGui.QPixmap.fromImage(self.images[index]))

    def initImages(self):
        self.images = []
        self.colorTable = [QtGui.qRgb(i, i, i) for i in range(256)]
        self.createImage0()
        self.createImage1()
        self.label.setPixmap(QtGui.QPixmap.fromImage(self.images[0]))

    def createImage0(self):
        image = QtGui.QImage(512, 512,  QtGui.QImage.Format_Indexed8)
        image.setColorTable(self.colorTable)
        buff = ctypes.create_string_buffer('\xFF'*512*16, 512*16)
        buff2 = ctypes.create_string_buffer('\x1f'*512*32, 512*32)
        img_ptr = image.bits()
        ctypes.memmove(int(img_ptr),  buff,  buff._length_)
        ctypes.memmove(int(img_ptr)+buff._length_,  buff2,  buff2._length_)
        ctypes.memmove(int(img_ptr)+buff._length_+buff2._length_,  buff,  buff._length_)
        self.images.append(image)

    def createImage1(self):
        self.buff = ctypes.create_string_buffer('\x7F'*512*512)
        image = QtGui.QImage(sip.voidptr(ctypes.addressof(self.buff)), 512, 512,  QtGui.QImage.Format_Indexed8)
        image.setColorTable(self.colorTable)
        self.images.append(image)

def load_image(filename, qwidget):
    pixmap = QtGui.QPixmap(filename)
    qgpi = QGraphicsPixmapItem(pixmap)
    scene = QtGui.QGraphicsScene()
    scene.addItem(qgpi)
    view = OMITGraphicsView(pixmap, scene, qwidget)
    view.setDragMode(QGraphicsView.ScrollHandDrag)
    return view

class Example(QtGui.QWidget):
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Q:
            self.close()

    def __init__(self):
        super(Example, self).__init__()
        self.initUI()

    def initUI(self):
        hbox = QtGui.QHBoxLayout(self)

        topleft = QtGui.QFrame(self)
        topleft.setFrameShape(QtGui.QFrame.StyledPanel)

        topright = QtGui.QFrame(self)
        topright.setFrameShape(QtGui.QFrame.StyledPanel)

        bottom = QtGui.QFrame(self)
        bottom.setFrameShape(QtGui.QFrame.StyledPanel)

        splitter1 = QtGui.QSplitter(QtCore.Qt.Horizontal)
        splitter1.addWidget(topleft)
        splitter1.addWidget(topright)
        splitter1.addWidget(load_image('f1.png', self))

        splitter2 = QtGui.QSplitter(QtCore.Qt.Vertical)
        splitter2.addWidget(splitter1)
        splitter2.addWidget(bottom)
        splitter2.addWidget(load_image('f2.png', self))

        hbox.addWidget(splitter2)
        self.setLayout(hbox)
        QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))
        self.setGeometry(0, 0, 1680, 1050)
        self.setWindowTitle('QtGui.QSplitter')

    def onChanged(self, text):
        self.lbl.setText(text)
        self.lbl.adjustSize()

    def handleMessage(self, message):
        print message

class TestWidget(QWidget):
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Q:
            self.close()
            sys.exit(0)

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.button = QPushButton("Run!")
        layout = QVBoxLayout()
        layout.addWidget(self.button)
        layout.addWidget(self.view)
        self.setLayout(layout)
        self.button.clicked.connect(self.do_test)

    def do_test(self):
        img = Image.open('tyrael.jpg')
        enhancer = ImageEnhance.Brightness(img)
        for i in range(1, 8):
            img = enhancer.enhance(i)
            self.display_image(img)
            QCoreApplication.processEvents()  # let Qt do his work
            time.sleep(0.5)

    def display_image(self, img):
        self.scene.clear()
        w, h = img.size
        self.imgQ = ImageQt.ImageQt(img)  # we need to hold reference to imgQ, or it will crash
        pixMap = QPixmap.fromImage(self.imgQ)
        self.scene.addPixmap(pixMap)
        self.view.fitInView(QRectF(0, 0, w, h), Qt.KeepAspectRatio)
        self.scene.update()

def main():
#    app = QtGui.QApplication(sys.argv)
    key = 'FYP'
    if len(sys.argv) > 1:
        app = SingleApplicationWithMessaging(sys.argv, key)
        if app.isRunning():
            app.sendMessage('app is already running')
    else:
        app = SingleApplication(sys.argv, key)
        if app.isRunning():
            print('app is already running')

#    widget = TestWidget()
#    widget.resize(640, 480)
#    widget.show()

    window = Example() # QMainWindow()
    app.connect(app, QtCore.SIGNAL('messageAvailable'), window.handleMessage)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
