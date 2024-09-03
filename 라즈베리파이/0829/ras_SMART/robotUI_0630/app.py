import sys, time
from PySide2.QtCore import QThread, Qt
from PySide2.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QStackedWidget
from PySide2.QtCore import QObject, Signal, Slot
from PySide2.QtGui import QFont
from ui import Uilist
from definse import *
from images import image
from function import *
from protocol import *
from multiprocessing import Process, Queue
from server import *
import numpy as np
import math

class refreshSignal(QThread):
    signal1 = Signal()
    def __init__(self):
        super().__init__()      
   
    def run(self):
        while True:
            self.signal1.emit()
            time.sleep(0.001)
class LowPassFilter(object):
    def __init__(self, cut_off_freqency, ts):
    	# cut_off_freqency: 차단 주파수
        # ts: 주기
        
        self.ts = ts
        self.cut_off_freqency = cut_off_freqency
        self.tau = self.get_tau()

        self.prev_data = 0.
        
    def get_tau(self):
        return 1 / (2 * np.pi * self.cut_off_freqency)

    def filter(self, data):
        val = (self.ts * data + self.tau * self.prev_data) / (self.tau + self.ts)
        self.prev_data = val
        
        return round(val)
    
class MainApplication(QWidget):
    def __init__(self):
        super().__init__()
        self.prevDebugTime=0
        self.prevChangeTime=0
        self.dialvalues=[]
        self.motordata = dict()
        self.creatUI()
        self.function()     

        self.id_list=[0x31,0x32,0x33,0x34,0x35,0x36]
        self.prevdialvalues=[]
        self.sendflag=0
        self.dynamixellSerial = serial.Serial(port = '/dev/ttyS0', baudrate= 115200)
        self.ai_mode_time=0
        self.teching_time=0
        self.readvalue=None
        self.tempvalue=None
        self.playtime=0
        self.playstep=0
        self.playtimecheck=10
        self.lpf1 = LowPassFilter(0.05, 0.1)
        self.lpf2 = LowPassFilter(0.05, 0.1)
        self.lpf3 = LowPassFilter(0.05, 0.1)
        self.lpf4 = LowPassFilter(0.05, 0.1)
        self.lpf5 = LowPassFilter(0.05, 0.1)
        self.lpf6 = LowPassFilter(0.05, 0.1)
        self.lpf1_check =0
        self.lpf2_check =0
        self.lpf3_check =0
        self.lpf4_check =0
        self.lpf5_check =0
        self.lpf6_check =0
    def _read_dynamixvalue(self):
        SMART = smartprotocol()
        sendValue=SMART.makepacket(REQUEST_CMD, self.id_list)
        self._send(sendValue)
        self._read()
        decodedValue = str(self.tempvalue.decode())
        stripvalue=decodedValue.strip()
        valuelist=stripvalue.split(',')
        resultlist = ' '.join(valuelist).split()

        returnlist = []
        for i in resultlist:
            returnlist.append(int(i))
        self.readvalue = returnlist
        
    def _setTorqueOff(self):
        SMART = smartprotocol()
        sendValue=SMART.makepacket(CMD_TORQUEOFF,self.id_list)
        self._send(sendValue)

    def _setTorqueOn(self):
        SMART = smartprotocol()
        sendValue=SMART.makepacket(CMD_TORQUEON,self.id_list)
        self._send(sendValue)

    def _send_dynamix(self, ids=[], values=[]):
        SMART = smartprotocol()
        try:
            sendValue = (SMART.contorol_motor(ids,values))
            for i in  sendValue: 
              print(hex(i),end='')
              print(', ',end='')
            print('')
            self._send(sendValue)
        except Exception as e:
            print(e)

    def _send(self, data):
        self.dynamixellSerial.write(data)

    def _read(self):
        self.tempvalue=self.dynamixellSerial.readline()
        

    def creatUI(self):
        self.setWindowTitle('robot ARM')
        self.move(0, 0)
        self.stackWidget = QStackedWidget(self)
        self.stackWidget.setGeometry(0, 0, 1920, 1200)
        self.ui = Uilist(self.stackWidget)

        self.ui.techingui.torqueButton.clicked.connect(self.torque_Button_clicked)

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

    def torque_Button_clicked(self):
        if self.ui.techingui.torqueButton.isChecked() :
            self._setTorqueOff()
            self.ui.techingui.torqueButton.setStyleSheet(
            """
                background : Green;
                border : solid 1px;
                color : Black;
            
            """)
            self.ui.techingui.torqueButton.setText("Touque ON")

        else:
            self._send_dynamix(self.id_list, self.readvalue)
            self._setTorqueOn()

            self.ui.techingui.torqueButton.setText("Torque OFF")
            self.ui.techingui.torqueButton.setStyleSheet("""
                    background : Red;
                    border : solid 1px;
                    color : White;
                
                """)
            
    def refresh(self):
        if self.recvQ.qsize()>0:
            self.motordata = self.recvQ.get()
            # print(self.motordata)

        if self.stackWidget.currentWidget() == pages.aimode_page:
            if time.time() - self.ai_mode_time >= 0.01:
                ids = list(self.motordata.keys())
                values = list(self.motordata.values())
                #print(values)
                self._send_dynamix(ids, values)
                for i in range(6):
                    self.ui.aimodeui.MotorStateLabelList[i].setText(str(values[i]))
                    self.ui.aimodeui.ServoDialList[i].setValue(values[i])
                    self.ui.aimodeui.indicateServoDial_value(i)
                self.ai_mode_time = time.time()
                        # self.ui.techingui.playButton.clicked.connect(self.play_Button_clicked)    

        elif self.stackWidget.currentWidget() == pages.techingmode_page:
            if self.ui.techingui.playButton.isChecked():
                self.ui.techingui.playButton.setStyleSheet(
                """
                    background : Green;
                    border : solid 1px;
                    color : Black;
                
                """)
                if self.playtimecheck>=10:
                    self.playtimecheck= 0
                    values = database.layoutitemlist[self.playstep]
                    print("현재 목표 ", values)
                    self.lpf1.prev_data=values[0]
                    self.lpf2.prev_data=values[1]
                    self.lpf3.prev_data=values[2]
                    self.lpf4.prev_data=values[3]
                    self.lpf5.prev_data=values[4]
                    self.lpf6.prev_data=values[5]
                    self.playstep+=1
                    self.passtoken = 0
                    if database.currentitemcount <= self.playstep:
                        self.playstep=0
                        self.ui.techingui.playButton.toggle()
                    
                else:
                    if time.time()-self.playtime>=0.05:
                        self.playtime= time.time()
                        values = database.layoutitemlist[self.playstep]
                        print("다음 목표 ", values)
                        filterd_value =[self.lpf1.filter(values[0]), self.lpf2.filter(values[1]), self.lpf3.filter(values[2]), 
                        self.lpf4.filter(values[3]), self.lpf5.filter(values[4]), self.lpf6.filter(values[5])]
                        print("필터된 목표 ", filterd_value)
                        if (values[0] <= filterd_value[0]+1):
                            self.lpf1_check = 1
                        if (values[1] <= filterd_value[1]+1):
                            self.lpf2_check = 1
                        if (values[2] <= filterd_value[2]+1):
                            self.lpf3_check = 1
                        if (values[3] <= filterd_value[3]+1):
                            self.lpf4_check = 1
                        if (values[4] <= filterd_value[4]+1):
                            self.lpf5_check = 1
                        if (values[5] <= filterd_value[5]+1): 
                            self.lpf6_check = 1 

                        self._send_dynamix(self.id_list, filterd_value)
                        print("gelo",filterd_value)

                        if self.lpf1_check and self.lpf2_check and self.lpf3_check and self.lpf4_check and self.lpf5_check and self.lpf6_check:
                            self.playtimecheck +=1
                            self.lpf1_check = 0
                            self.lpf2_check = 0
                            self.lpf3_check = 0
                            self.lpf4_check = 0
                            self.lpf5_check = 0
                            self.lpf6_check = 0
            else :
                self.ui.techingui.playButton.setStyleSheet("""
                    background : Red;
                    border : solid 1px;
                    color : White;
                
                """)
                if time.time() - self.teching_time >= 0.1:
                    try:
                        self._read_dynamixvalue()
                        for i in range(6):
                            value = self.readvalue[i]
                            self.ui.techingui.ServoDialList[i].setValue(value)
                            self.ui.techingui.indicateServoDial_value(i)

                    except Exception as e:
                        print(e)
                    self.teching_time = time.time() 

            

    
        # self._read_dynamixvalue(self)

        # if database.tryconnect_flag:
        #     self.dynamixell.connectDevice(PORT, BAUD)

        # self.ui.mainui.show_connection(database.connectionState)
        
        # self.dialvalues=self.ui.mainui.return_Dial_values()

        # if time.time()-self.prevChangeTime>=0.01:  
        #     self.prevChangeTime = time.time()
        #     if self.prevdialvalues != self.dialvalues:
        #         self.prevdialvalues = self.dialvalues
        #         self.dynamixell.contorol_motor(self.id_list, self.dialvalues) 
        #         self.prevDebugTime = time.time()

        # if time.time()-self.prevDebugTime>=0.1:  
        #     self.prevDebugTime = time.time()
        #     # print(dialvalues)
        #     self.dynamixell.contorol_motor(self.id_list, self.dialvalues)  

       
        
if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = MainApplication()
   sys.exit(app.exec_())
