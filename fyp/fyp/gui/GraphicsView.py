import sys
from PyQt4 import QtGui, QtCore

class GraphicsView(QtGui.QGraphicsView):
    def __init__(self, pixmap, scene, parent, *args):
        print >> sys.stderr, "GraphicsView::init()"
        QtGui.QGraphicsView.__init__(self, scene)
        self.scene     = scene
        self.pixmap    = pixmap
        self.win       = parent
        self.zoomLevel = 1.0
        self.setupActions()
        QtCore.QMetaObject.connectSlotsByName(self)

    def setupActions(self):
        """
            1: zoom fit
            2: zoom org
        """
        zoom_fit = QtGui.QAction(self)
        zoom_fit.setShortcuts([QtGui.QKeySequence.fromString('1')])
        zoom_fit.triggered.connect(self.zoom_fit)
        self.addAction(zoom_fit)
        zoom_org = QtGui.QAction(self)
        zoom_org.setShortcuts([QtGui.QKeySequence.fromString('2')])
        zoom_org.triggered.connect(self.zoom_org)
        self.addAction(zoom_org)

    def zoom_fit(self, *ignore):
        print >> sys.stderr, "GraphicsView::zoom_fit(#1)"
        if self.pixmap:
            winSize, imgSize = self.size(), self.pixmap.size()
            hZoom     = 1.0*winSize.width ()/imgSize.width ()
            vZoom     = 1.0*winSize.height()/imgSize.height()
            zoomLevel = min(hZoom, vZoom)
            scaleFactor = zoomLevel/self.zoomLevel
            self.scale(scaleFactor, scaleFactor)
            self.centerOn(0, 0)
            self.zoomLevel = zoomLevel
            print >> sys.stderr, "GraphicsView::zoom_fit(#1, %f)" % self.zoomLevel

    def zoom_org(self, *ignore):
        scaleFactor = 1.0/self.zoomLevel
        self.scale(scaleFactor, scaleFactor)
        self.centerOn(0, 0)
        self.zoomLevel = 1.0
        print >> sys.stderr, "GraphicsView::zoom_org(#2, %f)" % self.zoomLevel

    def resizeEvent(self, event):
        print >> sys.stderr, "GraphicsView::resizeEvent()"

