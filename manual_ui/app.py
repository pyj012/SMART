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
        self.function()    
        self.id_list=[0x31,0x32,0x33,0x34,0x35,0x36]
        self.prevdialvalues=[]
        self.sendflag=0

    def creatUI(self):
        self.setWindowTitle('Manual Control')
        self.move(0, 0)
        self.stackWidget = QStackedWidget(self)
        self.stackWidget.setGeometry(0, 0, 1920, 1080)
        self.ui = Uilist(self.stackWidget)
        
        self.stackWidget.setCurrentWidget(pages.main_page)
        self.showFullScreen()
     
    def function(self):
        self.Thread1 = refreshSignal()
        self.Thread1.signal1.connect(self.refresh) 
        self.Thread1.start()
        
        read_thread = threading.Thread(target= self.dynamixell.readserial, args=())
        read_thread.daemon=True
        read_thread.start()

    def refresh(self):
        if database.tryconnect_flag:
            self.dynamixell.connectDevice(PORT, BAUD)

        self.ui.mainui.show_connection(database.connectionState)
        
        self.dialvalues=self.ui.mainui.return_Dial_values()

        if time.time()-self.prevChangeTime>=0.01:  
            self.prevChangeTime = time.time()
            if self.prevdialvalues != self.dialvalues:
                self.prevdialvalues = self.dialvalues
                self.dynamixell.contorol_motor(self.id_list, self.dialvalues) 
                self.prevDebugTime = time.time()

        if time.time()-self.prevDebugTime>=0.1:  
            self.prevDebugTime = time.time()
            # print(dialvalues)
            self.dynamixell.contorol_motor(self.id_list, self.dialvalues)  

       
        
if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = MainApplication()
   sys.exit(app.exec_())