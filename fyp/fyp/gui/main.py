#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Application import *
from Window import *

def main():
    app = Application(sys.argv, key='FYP')
    if app.isRunning():
        app.sendMessage('Warning: application is already running!')
    window = Window()
    window.show()
    app.setApplicationName('FYP')
    app.setQuitOnLastWindowClosed(True)
    app.processEvents(QtCore.QEventLoop.AllEvents)
    app.connect(app, QtCore.SIGNAL('messageAvailable'), window.handleMessage)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
