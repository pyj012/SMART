import sys, time
from PyQt5.QtCore import QThread, Qt
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QStackedWidget
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont, QPixmap

from ui import Uilist
from definse import *
from images import image
from function import *
from protocol import *
from multiprocessing import Process, Queue
from server import *
import numpy as np

class refreshSignal(QThread):
    signal1 = pyqtSignal()
    def __init__(self):
        super().__init__()      
   
    def run(self):
        while True:
            self.signal1.emit()
            time.sleep(0.001)
    
class MainApplication(QWidget):
    def __init__(self):
        super().__init__()

        self.createUI()

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
        self.recvQ = Queue()
        self.sendQ = Queue()
        self.serverprocess = Process(target=SocketServer, args = (self.recvQ, self.sendQ))
        self.serverprocess.daemon = True
        self.serverprocess.start()
                
            
    def refresh(self):
        if self.recvQ.qsize()>0:
            self.motordata = self.recvQ.get()
            # print(self.motordata)

        if self.stackWidget.currentWidget() == pages.aimode_page:
            if time.time() - self.ai_mode_time >= 0.01:
                self.ai_mode_time = time.time()

        
if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = MainApplication()
   sys.exit(app.exec_())