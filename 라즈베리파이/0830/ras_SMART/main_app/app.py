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
        self.cameraprocess = Process(target=cameraProcess, args = (self.cameraRecvQ, self.cameraSendQ))
        self.cameraprocess.daemon = True
        self.cameraprocess.start()
        self.AngleRecvQ = Queue()
        self.AngleSendQ = Queue()
        self.serverprocess = Process(target=SocketServer, args = (self.AngleRecvQ, self.AngleSendQ))
        self.serverprocess.daemon = True
        self.serverprocess.start()

        # self.cameraprocess.join()
        # self.serverprocess.join()
                
            
    def refresh(self):
        if self.stackWidget.currentWidget() == pages.main_page:
            if self.cameraRecvQ.qsize()>0:
                img = self.cameraRecvQ.get()
                self.ui.mainui.refresh_Camera(img)
            
            if self.AngleRecvQ.qsize()>0:
                self.motordata = self.AngleRecvQ.get()
                print(self.motordata)
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