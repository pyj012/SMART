import sys, time
from PyQt5.QtCore import QThread, Qt
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QStackedWidget
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont
from ui import Uilist
from definse import *
from images import image
from function import *
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
        self.prevDebugTime=0
        self.prevChangeTime=0
        self.dialvalues=[]
        self.dynamixell=Dynamixell(debug=1)
        
        self.creatUI()
        self.id_list=[0x31,0x32,0x33,0x34,0x35,0x36]
        self.prevdialvalues=[]
        self.sendflag=0

    def creatUI(self):
        self.setWindowTitle('Test')
        self.move(0, 0)
        self.setGeometry(0,0,300,150)
        self.testBtn = QPushButton(self)
        self.testBtn.setGeometry(0,0, 300,120) 
        self.testBtn.setText("Test")

        self.ablebtn = QPushButton(self)
        self.ablebtn.setGeometry(0, 116, 145, 34)
        self.ablebtn.setText("Enable")

        self.disablebtn = QPushButton(self)
        self.disablebtn.setGeometry(155, 116, 145, 34)
        self.disablebtn.setText("Disable")
        self.show()
     


       
        
if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = MainApplication()
   sys.exit(app.exec_())