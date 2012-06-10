import sys
from PyQt4 import QtGui, QtCore

class GraphicsView(QtGui.QGraphicsView):
    def __init__(self, pixmap, scene, parent, *args):
        print >> sys.stderr, "GraphicsView::init()"
        QtGui.QGraphicsView.__init__(self, scene)
        self.zoomLevel = 1.0
        self.win = parent
        self.pixmap = pixmap
        QtCore.QMetaObject.connectSlotsByName(self)
        self.setupActions()

    def setupActions(self):
        zoomfit = QtGui.QAction(self)
        zoomfit.setShortcuts([QtGui.QKeySequence.fromString('1')])
        zoomfit.triggered.connect(self.zoomfit)
        self.addAction(zoomfit)

        zoom200 = QtGui.QAction(self)
        zoom200.setShortcuts([QtGui.QKeySequence.fromString('2')])
        zoom200.triggered.connect(self.zoom200)
        self.addAction(zoom200)

    def zoomfit(self, *ignore):
        print >> sys.stderr, "GraphicsView::zoomfit()"
        if self.pixmap:
            winSize = self.size()
            imgSize = self.pixmap.size()
            hZoom = 1.0*winSize.width ()/imgSize.width ()
            vZoom = 1.0*winSize.height()/imgSize.height()
            zoomLevel = min(hZoom, vZoom)
            self.zoomTo(zoomLevel)

    def zoom200(self, *ignore):
        print >> sys.stderr, "GraphicsView::zoom200()"
        self.zoomTo(1.0)

    def zoomTo(self, zoomLevel):
        scale = zoomLevel/self.zoomLevel
        self.scale(scale, scale)
        self.zoomLevel = zoomLevel

    def resizeEvent(self, event):
        if self.pixmap:
            pixmap = self.pixmap.scaled(event.size(),
                Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.centerOn(1.0, 1.0)
            self.pixmap = pixmap
