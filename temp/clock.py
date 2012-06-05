import os,sys,time
from PyQt4 import Qt
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.uic import loadUi
from random import randint, shuffle

class Main(QtGui.QWidget):
    radius = 200

    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.ui=loadUi(os.path.join(os.getcwd(), "clock.ui"), self) 
        self.scene=QtGui.QGraphicsScene()
        self.scene.setSceneRect(0,0,640,480)
        self.ui.view.setScene(self.scene)
        self.populate()
        self.setWindowState(QtCore.Qt.WindowMaximized)

        self.animator=QtCore.QTimer()
        self.animator.timeout.connect(self.animate)
        self.animate()

    def populate(self):
        import pydot
        g = pydot.Dot('temp', graph_type='digraph', prog='neato')
        prev_node = None
        for i in xrange(4):
            node = pydot.Node('node%d'%i)
            if i == 2 and prev_node is None:
                prev_node = node
            g.add_node( node )
            if i > 2:
                g.add_edge(pydot.Edge(prev_node, node))

        g.write_png('/Users/lwy08/Downloads/temp.png')
        graphWithPositions = pydot.graph_from_dot_data(g.create_dot())
        node_positions = [(g.get_name(), float(g.get_pos()[1:-1].split(",")[0]), 100-float(g.get_pos()[1:-1].split(",")[1]),float(g.get_width()[1:-1]),float(g.get_height()[1:-1]),g) for g in graphWithPositions.get_nodes()[3:]]
        edge_positions = [e.get_pos() for e in graphWithPositions.get_edges()]

        font=QtGui.QFont('White Rabbit')
        font.setPointSize(16)
        for n,x,y,w,h,_ in node_positions:
            item=QtGui.QGraphicsTextItem(n)
            item.setFont(font)
            item.setPos(x,y)
            self.scene.addItem(item)
            width = w*72
            height = h*72
            self.scene.addEllipse(x-width/2.0,y-height/2.0,width,height)

    def animate(self):
        self.animations=range(0,60)
        def animate_to(t,item,x,y,angle):
            animation=QtGui.QGraphicsItemAnimation()
            timeline=QtCore.QTimeLine(1000)
            timeline.setFrameRange(0,100)
            animation.setPosAt(t,QtCore.QPointF(x,y))
            animation.setRotationAt(t,angle)
            animation.setItem(item)
            animation.setTimeLine(timeline)
            return animation
        self.animator.start(1000)

def main():
    app = QtGui.QApplication(sys.argv)
    window=Main()
    window.show()
    sys.exit(app.exec_())
if __name__ == "__main__":
    main()
