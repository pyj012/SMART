import sys, time, os,cv2
from css import *
from PyQt5.QtCore import QThread, Qt
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QStackedWidget, QDial, QVBoxLayout, QComboBox
from PyQt5.QtCore import QObject, QSize,QRect 
from PyQt5.QtGui import QFont, QPixmap, QIcon, QColor, QPainter, QBrush, QImage , QPalette
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
    painter.setPen(QColor("transparent"))
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

        self.SmartLogoLW = 200
        self.SmartLogoLH = 120
        self.SmartLogoLX = 8
        self.SmartLogoLY = 0

        self.DongYangLogoLW = 120
        self.DongYangLogoLH = 120
        self.DongYangLogoLX = 230
        self.DongYangLogoLY = 0

        self.RadLogoLW = 120
        self.RadLogoLH = 120
        self.RadLogoLX = 400
        self.RadLogoLY = 0

        self.CameraFrameLW = 640
        self.CameraFrameLH = 480

        self.ServerConnectBW = 300
        self.ServerConnectBH = 70
        self.ServerConnectBX = 1500
        self.ServerConnectBY = 30

        self.ExitBW = 60
        self.ExitBH = 60
        self.ExitBX = 1850
        self.ExitBY = 20

        self.StateLW=350
        self.StateLH=70
        self.StateLX=880
        self.StateLY=30

        self.ModselectCBW=200
        self.ModselectCBH=70
        self.ModselectCBX=1250
        self.ModselectCBY=30

        self.IndicatorGraphLW=300
        self.IndicatorGraphLH=103
        self.IndicatorGraphLX=550
        self.IndicatorGraphLY=7

        self.IndicatorLW=270
        self.IndicatorLH=40
        self.IndicatorLX=565
        self.IndicatorLY=15
        self.stacklist= stacklist
        self.pixmap=QPixmap()
        self.widget = QWidget(self.stacklist)

        pages.main_page = self.widget

        self.BackGroundL = QLabel(self.widget)
        self.BackGroundL.setGeometry(self.BackGroundLX, self.BackGroundLY, self.BackGroundLW, self.BackGroundLH)
        self.BackGroundL.setStyleSheet(BackGroundStyle)

        self.StateL = QLabel("Server Disconnected",self.widget)
        self.StateL.setGeometry(self.StateLX, self.StateLY, self.StateLW, self.StateLH)
        self.StateL.setStyleSheet(LabelStyle)
        self.StateL.setAlignment(Qt.AlignCenter)
        self.StateL.setFont(QFont("Arial", 24))

        self.SmartLogoL = QLabel(self.widget)
        self.SmartLogoL.setGeometry(self.SmartLogoLX, self.SmartLogoLY, self.SmartLogoLW, self.SmartLogoLH)
        self.SmartLogoL.setStyleSheet(IMGStyle)
        self.SmartLogoL.setScaledContents(True)
        self.SmartLogoL.setPixmap(QPixmap(image.SMART_LOGO))

        self.DongYangLogoL = QLabel(self.widget)
        self.DongYangLogoL.setGeometry(self.DongYangLogoLX, self.DongYangLogoLY, self.DongYangLogoLW, self.DongYangLogoLH)
        self.DongYangLogoL.setStyleSheet(IMGStyle)
        self.DongYangLogoL.setScaledContents(True)
        self.DongYangLogoL.setPixmap(QPixmap(image.DONG_YANG_LOGO))
       
        self.RadLOGOL = QLabel(self.widget)
        self.RadLOGOL.setGeometry(self.RadLogoLX, self.RadLogoLY, self.RadLogoLW, self.RadLogoLH)
        self.RadLOGOL.setStyleSheet(IMGStyle)
        self.RadLOGOL.setScaledContents(True)
        self.RadLOGOL.setPixmap(QPixmap(image.RAD_LOGO))

        self.IndicatorGraphL = QLabel(self.widget)
        self.IndicatorGraphL.setGeometry(self.IndicatorGraphLX, self.IndicatorGraphLY, self.IndicatorGraphLW, self.IndicatorGraphLH)
        self.IndicatorGraphL.setStyleSheet(IMGStyle)
        self.IndicatorGraphL.setScaledContents(True)
        self.IndicatorGraphL.setPixmap(QPixmap(image.INDICATOR))

        self.IndicatorL = QLabel(self.widget)
        self.IndicatorL.setGeometry(self.IndicatorLX, self.IndicatorLY, self.IndicatorLW, self.IndicatorLH)
        self.IndicatorL.setStyleSheet(IMGStyle)
        self.IndicatorL.setScaledContents(True)
        # self.IndicatorL.setPixmap(QPixmap(image.INDICATOR))

        self.CameraFrameLX = 0
        self.CameraFrameLY = 120
        self.CameraFrame_list=[]

        for frame in range(0, 6):
            CameraFrameL = QLabel(str(frame),self.widget)
            CameraFrameL.setGeometry(self.CameraFrameLX, self.CameraFrameLY, self.CameraFrameLW, self.CameraFrameLH)
            CameraFrameL.setStyleSheet(IMGStyle)
            CameraFrameL.setScaledContents(True)
            qimg =IMGrounder(12, image.WHITE)
            CameraFrameL.setPixmap(QPixmap(qimg))

            self.CameraFrameLX+=640
            self.CameraFrameLX%=1920
            if frame >=2:
                self.CameraFrameLY=600
            self.CameraFrame_list.append(CameraFrameL)

        self.ServerConnectB = QPushButton("Try To Connect", self.widget)
        self.ServerConnectB.setGeometry(QRect(self.ServerConnectBX, self.ServerConnectBY,self.ServerConnectBW, self.ServerConnectBH))
        self.ServerConnectB.setStyleSheet(BackButtonStyle)
        self.ServerConnectB.setFont(QFont("Arial", 24))
        # palette = self.ServerConnectB.palette()
        # palette.setColor(QPalette.Button, QColor('White'))
        # self.ServerConnectB.setPalette(palette)
        
        self.ModselectCB = QComboBox(self.widget)
        self.ModselectCB.setGeometry(self.ModselectCBX, self.ModselectCBY, self.ModselectCBW, self.ModselectCBH)
        self.ModselectCB.addItems(["실시간 제어", "동작1", "동작2", "동작3"])
        self.ModselectCB.setFont(QFont("Arial", 24))
        # self.ModselectCB.setCurrentText("동작1") # 있는 옵션 내에서만 되네

        self.ExitB = QPushButton(self.widget)
        self.ExitB.setGeometry(self.ExitBX, self.ExitBY, self.ExitBW, self.ExitBH)
        self.ExitB.setStyleSheet(IMGStyle)
        self.ExitB.setIcon(QIcon(image.EXIT_IMG))
        self.ExitB.setIconSize(QSize(self.ExitBW, self.ExitBH))
        self.ExitB.clicked.connect(self.ExitB_clicked)
        self.stacklist.addWidget(self.widget)  


    def refresh_Camera(self, frame, img):
        # height, width, channel = img.shape
        # bytesPerLine = 3 * width
        # qImg = QImage(img.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()

        # # img= cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        # # h,w,c = img.shape
        # # qImg=QImage(img.data,w,h,w*c,QImage.Format_RGB888)
        # # pixmap=QPixmap.fromImage(qImg)

        # rimg = IMGrounder(30, qImg)
        # self.pixmap=rimg
        qimg =IMGrounder(30, img)
        frame.setPixmap(QPixmap(qimg))
        
    def ExitB_clicked(self):
        # database.camera.release()
        sys.exit()
