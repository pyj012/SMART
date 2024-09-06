import sys, time, cv2
from PySide2.QtCore import QThread, Qt
from PySide2.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QStackedWidget
from PySide2.QtCore import QObject,Signal, Slot
from PySide2.QtGui import QFont, QPixmap

from ui import Uilist
from definse import *
from images import *
from function import *
from protocol import *
from multiprocessing import Process, Queue
from process import *
import numpy as np
from itertools import chain
# database.camera = cv2.VideoCapture(0)
# database.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
# database.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

class refreshSignal(QThread):
    signal1 = Signal()
    def __init__(self):
        super().__init__()      
   
    def run(self):
        while True:
            self.signal1.emit()
            time.sleep(0.0005)
    
class MainApplication(QWidget):
    def __init__(self):
        super().__init__()
        self.createUI()
        self.function()
        self.CameraRefreshTime=0.001
        self.prevCameraRefreshTime=0


        print(database.camera)

    def createUI(self):
        self.setWindowTitle('robot ARM')
        self.move(0, 0)
        self.stackWidget = QStackedWidget(self)
        self.stackWidget.setGeometry(0, 0, 1920, 1200)
        self.ui = Uilist(self.stackWidget)
        self.stackWidget.setCurrentWidget(pages.main_page)
        self.show()
     
    def function(self):
        self.Thread1 = refreshSignal()
        self.Thread1.signal1.connect(self.refresh) 
        self.Thread1.start()
        self.cameraRecvQ = Queue()
        self.cameraSendQ = Queue()
        # self.cameraprocess = Process(target=cameraProcess, args = (self.cameraRecvQ, self.cameraSendQ))
        # self.cameraprocess.daemon = True
        # self.cameraprocess.start()
        self.AngleSendQ1 = Queue()
        self.AngleSendQ2 = Queue()
        self.serverprocess = Process(target=SocketServer, args = (self.AngleSendQ1, self.AngleSendQ2))
        self.serverprocess.daemon = True
        self.serverprocess.start()

        self.SendQ1 = Queue()
        self.SendQ2 = Queue()
        self.servoprocess = Process(target=servocontrol, args = (self.SendQ1, self.SendQ2))
        self.servoprocess.daemon = True
        self.servoprocess.start()

        self.motordata1={}
        self.motordata2={}
        
        self.time=0
        # self.cameraprocess.join()
        # self.serverprocess.join()
                
            
    def refresh(self):
        if self.stackWidget.currentWidget() == pages.main_page:
            if self.cameraRecvQ.qsize()>0:
                img = self.cameraRecvQ.get()
                self.ui.mainui.refresh_Camera(img)
            
            if self.AngleSendQ1.qsize()>0:
                self.motordata1 = self.AngleSendQ1.get()
                # print("control", self.motordata1)
            if self.AngleSendQ2.qsize()>0:
                self.motordata2 = self.AngleSendQ2.get()
                # print("robot", self.motordata2)
            
            if time.time()-self.time>=0.001:
                self.time = time.time()
                self.SendQ1.put(self.motordata1)
                self.SendQ2.put(self.motordata2)
                
                # print(self.motordata1, self.motordata2)
                # while self.AngleRecvQ.qsize()>0:
                #     self.AngleRecvQ.get()

        # if self.stackWidget.currentWidget() == pages.main_page:
        #     if time.time()-self.prevCameraRefreshTime >=self.FPS:
        #         ret, frame = database.camera.read()
        #         self.ui.mainui.refresh_Camera(frame)
        #         print(self.FPS_MS)
        #         print(round((time.time() - self.prevCameraRefreshTime),4))
        #         self.prevCameraRefreshTime = time.time()
                
            pass
        
if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = MainApplication()
   sys.exit(app.exec_())