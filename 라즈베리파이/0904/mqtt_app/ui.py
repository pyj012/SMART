import sys, time, os,cv2
from css import *
from PySide2.QtCore import QThread, Qt
from PySide2.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QStackedWidget, QDial, QVBoxLayout
from PySide2.QtCore import QObject, QSize
from PySide2.QtGui import QFont, QPixmap, QIcon, QColor, QPainter, QBrush, QImage
from functools import partial
from definse import *
from images import image

def deleteItems(layout):
    if layout is not None:
        while layout.count():
            item= layout.takeAt(0)
            widget=item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                deleteItems(item.layout())

def IMGrounder(rad=30, img=None):
    pixmap = QPixmap(img)
    radius = rad
    # # create empty pixmap of same size as original 
    rounded = QPixmap(pixmap.size())
    rounded.fill(QColor("transparent"))
    painter = QPainter(rounded)
    painter.setBrush(QBrush(pixmap))
    painter.drawRoundedRect(pixmap.rect(), radius, radius)

    return rounded

class Uilist():
    def __init__(self, stacklist):
        self.mainui=MainUi(stacklist)

class MainUi():
    def __init__(self, stacklist):

        self.BackGroundLW= 1920
        self.BackGroundLH = 1080
        self.BackGroundLX = 0
        self.BackGroundLY = 0

        self.CameraFrameLW = 1280
        self.CameraFrameLH = 720
        self.CameraFrameLX = 320
        self.CameraFrameLY = 20

        self.ConnectionStateLW = 100
        self.ConnectionStateLH = 100
        self.ConnectionStateLX = 50
        self.ConnectionStateLY = 20

        self.ExitBW = 60
        self.ExitBH = 60
        self.ExitBX = 1850
        self.ExitBY = 20

        self.stacklist= stacklist
        self.pixmap=QPixmap()
        self.widget = QWidget(self.stacklist)


        pages.main_page = self.widget
        self.BackGroundL = QLabel(self.widget)
        self.BackGroundL.setGeometry(self.BackGroundLX, self.BackGroundLY, self.BackGroundLW, self.BackGroundLH)
        self.BackGroundL.setStyleSheet(BackGroundStyle)

        self.CameraFrameL = QLabel(self.widget)
        self.CameraFrameL.setGeometry(self.CameraFrameLX, self.CameraFrameLY, self.CameraFrameLW, self.CameraFrameLH)
        self.CameraFrameL.setStyleSheet(IMGStyle)
        self.CameraFrameL.setScaledContents(True)
        self.CameraFrameL.setPixmap(self.pixmap)


        self.ConnectionStateL = QLabel(self.widget)
        self.ConnectionStateL.setGeometry(self.ConnectionStateLX, self.ConnectionStateLY, self.ConnectionStateLW, self.ConnectionStateLH)
        self.ConnectionStateL.setStyleSheet(IMGStyle)
        self.ConnectionStateL.setScaledContents(True)
        self.ConnectionStateL.setPixmap(QPixmap(image.DISCONNECTED_IMG))

        self.ExitB = QPushButton(self.widget)
        self.ExitB.setGeometry(self.ExitBX, self.ExitBY, self.ExitBW, self.ExitBH)
        self.ExitB.setStyleSheet(IMGStyle)
        self.ExitB.setIcon(QIcon(image.EXIT_IMG))
        self.ExitB.setIconSize(QSize(self.ExitBW, self.ExitBH))
        self.ExitB.clicked.connect(self.ExitB_clicked)
        self.stacklist.addWidget(self.widget)  

    def refresh_Camera(self, img):
        height, width, channel = img.shape
        bytesPerLine = 3 * width
        qImg = QImage(img.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()

        # img= cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        # h,w,c = img.shape
        # qImg=QImage(img.data,w,h,w*c,QImage.Format_RGB888)
        # pixmap=QPixmap.fromImage(qImg)

        rimg = IMGrounder(30, qImg)
        self.pixmap=rimg
        self.CameraFrameL.setPixmap(rimg)
        
    def ExitB_clicked(self):
        # database.camera.release()
        sys.exit()
