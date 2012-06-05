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

class Window(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
#        uic.loadUi(os.path.join(os.getcwd(), "ui/window.ui"), self) 
        scene = QtGui.QGraphicsScene()

        node1 = QGraphicsEllipseItem(0, 0, 200, 100)
        node2 = QGraphicsEllipseItem(0, 300, 200, 100)
        edge = QGraphicsLineItem(100, 100 , 100, 300)

        scene.addItem(node1)
        scene.addItem(node2)
        scene.addItem(edge)
        
        view = QtGui.QGraphicsView(scene)
        vbox = QtGui.QVBoxLayout(self)
        vbox.addWidget(view)
        self.setGeometry(0, 0, 1680, 1050)
        self.show()

        time.sleep(1)
        scene.removeItem(edge)
        scene.removeItem(node2)
        time.sleep(2)
        node1.setRect(0, 0, 300, 300)

        time.sleep(3)
        scene.removeItem(node1)

    
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = Window()
    sys.exit(app.exec_())
