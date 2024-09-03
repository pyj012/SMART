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
import RPi.GPIO as GPIO

class refreshSignal(QThread):
    signal1 = Signal()
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
        self.motordata = dict()
        self.creatUI()
        self.function()     

        self.id_list=[0x31,0x32,0x33,0x34,0x35,0x36,0x3e,0x3f]
        self.prevdialvalues=[]
        self.sendflag=0
        self.dynamixellSerial = serial.Serial(port = '/dev/ttyS0', baudrate= 115200)
        self.ai_mode_time=0
        self.teching_time=0
        self.readvalue=None
        self.tempvalue=None
        self.playtime=0
        self.playstep=0

        GPIO.setmode(GPIO.BCM)

        GPIO.setup(LM_A, GPIO.OUT)
        GPIO.setup(LM_B, GPIO.OUT)
        GPIO.setup(RM_A, GPIO.OUT)
        GPIO.setup(RM_B, GPIO.OUT)
        GPIO.setup(LM_SPD, GPIO.OUT)
        GPIO.setup(RM_SPD, GPIO.OUT)

        self.LM_PWM = GPIO.PWM(LM_SPD, 100)
        self.RM_PWM = GPIO.PWM(RM_SPD, 100)

        self.LM_PWM.start(0)
        self.RM_PWM.start(0)

    def foward(self,l_spd = 0, r_spd=0):
        GPIO.output(LM_A, 0)
        GPIO.output(LM_B, 1)
        self.LM_PWM.ChangeDutyCycle(l_spd)

        GPIO.output(RM_A, 1)
        GPIO.output(RM_B, 0)
        self.RM_PWM.ChangeDutyCycle(r_spd)

    def backward(self, l_spd = 0, r_spd=0):
        GPIO.output(LM_A, 1)
        GPIO.output(LM_B, 0)
        self.LM_PWM.ChangeDutyCycle(l_spd)

        GPIO.output(RM_A, 0)
        GPIO.output(RM_B, 1)
        self.RM_PWM.ChangeDutyCycle(r_spd)

    def left(self, l_spd = 0, r_spd=0):
        GPIO.output(LM_A, 0)
        GPIO.output(LM_B, 1)
        self.LM_PWM.ChangeDutyCycle(l_spd)

        GPIO.output(RM_A, 0)
        GPIO.output(RM_B, 1)
        self.RM_PWM.ChangeDutyCycle(r_spd)
    def right(self, l_spd = 0, r_spd=0):
        GPIO.output(LM_A, 1)
        GPIO.output(LM_B, 0)
        self.LM_PWM.ChangeDutyCycle(l_spd)

        GPIO.output(RM_A, 1)
        GPIO.output(RM_B, 0)
        self.RM_PWM.ChangeDutyCycle(r_spd)
    def stop(self):
        self.LM_PWM.ChangeDutyCycle(0)
        self.RM_PWM.ChangeDutyCycle(0)
        GPIO.output(RM_A, 0)
        GPIO.output(RM_B, 0)
        GPIO.output(LM_A, 0)
        GPIO.output(LM_B, 0)

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
            print(sendValue)
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
        try:
            if self.recvQ.qsize()>0:
                self.motordata = self.recvQ.get()
                # print(self.motordata)

            if self.stackWidget.currentWidget() == pages.aimode_page:
                if time.time() - self.ai_mode_time >= 0.01:
                    ids = list(self.motordata.keys())
                    values = list(self.motordata.values())

                    lm_data = self.motordata[0x3e]
                    rm_data = self.motordata[0x3f]
                    print(lm_data, rm_data)
                    if lm_data == 1 and rm_data == 1:
                        self.stop()

                    elif lm_data == 0 and rm_data == 0:
                        self.foward(50,50)
                    
                    elif lm_data == 1 and rm_data == 0:
                        self.right(50,50)

                    elif lm_data == 0 and rm_data == 1:
                        self.left(50,50)
                    # self._send_dynamix(ids, values)
                    


                    # for i in range(8):
                    #     # self.ui.aimodeui.MotorStateLabelList[i].setText(str(values[i]))
                    #     # self.ui.aimodeui.ServoDialList[i].setValue(values[i])
                    #     # self.ui.aimodeui.indicateServoDial_value(i)
                    #     self.ai_mode_time = time.time()
                            # self.ui.techingui.playButton.clicked.connect(self.play_Button_clicked)    

            elif self.stackWidget.currentWidget() == pages.techingmode_page:
                if self.ui.techingui.playButton.isChecked():
                    self.ui.techingui.playButton.setStyleSheet(
                    """
                        background : Green;
                        border : solid 1px;
                        color : Black;
                    
                    """)
                    if time.time()-self.playtime>=1:
                        self.playtime= time.time()
                        values = database.layoutitemlist[self.playstep]
                        self._send_dynamix(self.id_list, values)
                        self.playstep+=1
                        if database.currentitemcount <= self.playstep:
                            self.playstep=0
                            self.ui.techingui.playButton.toggle()

                    
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
        except:
            GPIO.cleanup()
       
        
if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = MainApplication()
   sys.exit(app.exec_())