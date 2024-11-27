import sys, time
import os
from utils_V3 import DLT, get_projection_matrix, calculate_3d
from ValueControlFilter import ValueControlFilter
os.add_dll_directory('C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v11.8/bin')
os.add_dll_directory('C:/opencv/build/install/x64/vc16/bin')
os.add_dll_directory('C:/opencv/build/bin')
import cv2
from functools import partial
from PyQt5.QtCore import QThread, Qt
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QStackedWidget
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont, QPixmap, QImage
from ui import Uilist
from definse import *
from images import *
import multiprocessing
from multiprocessing import Process, Queue
from process import *
import numpy as np
from itertools import chain
from vidstab import VidStab, layer_overlay, download_ostrich_video
def map(x,input_min,input_max,output_min,output_max):
    return int((x-input_min)*(output_max-output_min)/(input_max-input_min)+output_min) #map()함수 정의.

class refreshSignal(QThread):
    signal1 = pyqtSignal()
    def __init__(self):
        super().__init__()      
   
    def run(self):
        while True:
            self.signal1.emit()
            time.sleep(0.0001)
    
class MainApplication(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('robot ARM')
        self.move(0, 0)
        self.stackWidget = QStackedWidget(self)
        self.stackWidget.setGeometry(0, 0, 1920, 1080)
        self.ui = Uilist(self.stackWidget)
        self.stackWidget.setCurrentWidget(pages.main_page)
     
        self.Thread1 = refreshSignal()
        self.Thread1.signal1.connect(self.refresh) 
        self.Thread1.start()
    
        
        self.clientIMG_QManager = multiprocessing.Manager()
        self.clientState_QManager = multiprocessing.Manager()
        self.client_Mod_QManager = multiprocessing.Manager()
        self.client_IMG_Queue = self.clientIMG_QManager.Queue()
        self.client_State_Queue = self.clientState_QManager.Queue()
        self.client_Mod_Queue = self.client_Mod_QManager.Queue()

        self.client_Mod_Queue.put(1) # 추가해야할지도

        self.client_process = Process(target=SocketServer, args = (5050, self.client_IMG_Queue, self.client_State_Queue, self.client_Mod_Queue))
        self.client_process.daemon = True
        self.stateFlag = 0

        self.cameraQManager = multiprocessing.Manager()
        self.camera_Queue = self.cameraQManager.Queue()
        self.camera_process = Process(target=SocketServer, args = (5053, self.camera_Queue))
        self.camera_process.daemon = True

        self.client_process.start()
        self.camera_process.start()
        
        self.ledindex = 0
        self.CameraRefreshTime=0.001
        self.prevCameraRefreshTime=0
        self.prevIndicatorTime=0
        self.time=0
        self.stabilizer = VidStab()
        self.ui.mainui.ServerConnectB.clicked.connect(partial(self.serverConnect_clicked))
        
        self.ui.mainui.ModselectCB.activated.connect(partial(self.ModOptionSelected))
        self.showFullScreen()

    def serverConnect_clicked(self):
        self.stateFlag = not self.stateFlag
        if self.stateFlag:
            self.ui.mainui.ServerConnectB.setText("Try To Disconnect")
            self.ui.mainui.StateL.setText("Server Connected")
            
        else :
            self.ui.mainui.ServerConnectB.setText("Try To Connect")
            self.ui.mainui.StateL.setText("Server Disconnected")

        self.client_State_Queue.put(self.stateFlag)
    
    def ModOptionSelected(self,index):
        # print(index)
        self.client_Mod_Queue.put(index)

    # Convert an opencv image to QPixmap
    def convertCvImage2QtImage(self, cv_img, rotate= 0):
        (h, w) = cv_img.shape[:2]
        (cX, cY) = (w // 2, h // 2)
        image = None
        if rotate :
            M = cv2.getRotationMatrix2D((cX, cY), -180, 1.0)
            rotated_180 = cv2.warpAffine(cv_img, M, (w, h))
            image =QImage(rotated_180, rotated_180.shape[1],rotated_180.shape[0], rotated_180.shape[1] * 3, QImage.Format_BGR888)
        else : 
                image =QImage(cv_img, cv_img.shape[1],cv_img.shape[0], cv_img.shape[1] * 3, QImage.Format_BGR888)
        return(QPixmap(image)) 

    def Indicator_fill(self, gauge=0):
        img = np.zeros((40, 270, 3), dtype=np.uint8)
        green = 0
        red = 0
        blue = 0
        indicate_gauge= map(gauge, 0, 100, 0, 270)
        if gauge >= 0 and gauge <= 25:
            green = 255
            red =  0
            blue = 0
        elif gauge >= 26  and gauge <= 50:
            green = 255
            red =  255
            blue = 0
        elif gauge >= 51 and gauge <= 75:
            green = 88
            red =  255
            blue = 26
        else :
            green = 0
            red =  255
            blue = 0   

        cv2.rectangle(img, (0, 0), (indicate_gauge, 40), (blue, green,red), -1)

        return img


    def refresh(self):
        # if self.stackWidget.currentWidget() == pages.main_page:
        if self.camera_Queue.qsize()>0:
            
            data = self.camera_Queue.get()
            img_dict= data[0]
            self.ledindex= data[1]
            for index in img_dict:
                if img_dict[index] is not None:
                    if index == 4:
                        pixmap = self.convertCvImage2QtImage(img_dict[index] )
                        self.ui.mainui.refresh_Camera(self.ui.mainui.CameraFrame_list[0], pixmap)

                    elif index == 12:
                        pixmap = self.convertCvImage2QtImage(img_dict[index])
                        self.ui.mainui.refresh_Camera(self.ui.mainui.CameraFrame_list[1], pixmap)
                    
                    elif index == 0:
                        pixmap = self.convertCvImage2QtImage(img_dict[index],1)
                        self.ui.mainui.refresh_Camera(self.ui.mainui.CameraFrame_list[2], pixmap)

        if self.client_IMG_Queue.qsize()>0:
            img_list = self.client_IMG_Queue.get()
           
            i = 3 
            for index in range(0,len(img_list)):
                if img_list[index] is not None:
                    pixmap = self.convertCvImage2QtImage(img_list[index])
                    self.ui.mainui.refresh_Camera(self.ui.mainui.CameraFrame_list[i], pixmap)
                i+=1
        if time.time() - self.prevIndicatorTime >= 0.5:
            self.prevIndicatorTime = time.time()
            ledlevel = map(self.ledindex, 0 ,15, 0,100)
            self.ui.mainui.IndicatorL.setPixmap(self.convertCvImage2QtImage(self.Indicator_fill(ledlevel)))
        
            # # print(img)
            # try:

            #             cv2.imshow(str(index), img[index])

            #         key = cv2.waitKey(1)

            #         if key == 27:
            #             break
                    
            # except Exception as e:
            #     cv2.destroyAllWindows()
                # self.ui.mainui.refresh_Camera(img)

            # if self.client_Queue.qsize()>0:
            #     self.client_data = self.client_Queue.get() 

            # if time.time()-self.time >= 0.001:
            #     self.time = time.time()
            #     print("PC : ", self.pc_data, "CONRL : ", self.controllor_data)
            
if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = MainApplication()
   sys.exit(app.exec_())