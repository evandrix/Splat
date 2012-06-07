class Window(QtGui.QWidget):    # QtGui.QMainWindow
    def __init__(self, parent=None):
        self.connect(self, SIGNAL("tabPressed"), self.update)
#        view.show()
#        grview = ImageView(origPixmap=pic)
#        scene.addPixmap(pic)
#        grview.setScene(scene)
#        grview.show()
#        self.initImages()

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

class TestWidget(QWidget):
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
