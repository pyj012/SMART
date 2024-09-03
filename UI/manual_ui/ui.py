import sys, time
from PyQt5.QtCore import QThread, Qt
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QStackedWidget, QDial
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont, QPixmap
from functools import partial
from definse import *
from images import image

class Uilist():
    def __init__(self, stacklist):
        self.mainui=MainUi(stacklist)

class MainUi():
    def __init__(self, stacklist):
        self.ServoDial_X_dict={1:1180, 2:1180, 3:1200, 4:780, 5:960, 6:510}
        self.ServoDial_Y_dict={1:850, 2:650, 3:20, 4:20, 5:380, 6:170}
        self.ServoUpBtn_X_dict={1:1300, 2:1300, 3:1320, 4:900, 5:1060, 6:620}
        self.ServoUpBtn_Y_dict={1:880, 2:675, 3:45, 4:45, 5:350, 6:195}
        self.ServoDownBtn_X_dict={1:1360, 2:1360, 3:1380, 4:960, 5:1120, 6:680}
        self.ServoDownBtn_Y_dict={1:880, 2:675, 3:45, 4:45, 5:350, 6:195}
        self.ServoUpBtn_width = 50
        self.ServoUpBtn_height = 50

        self.ServoDownBtn_width = 50
        self.ServoDownBtn_height = 50

        self.ServoDial_width = 100
        self.ServoDial_height = 100

        self.ServoDialValue_height = 50
        self.connectionState_x = 1800
        self.connectionState_y = 20
        self.connectionState_width = 100
        self.connectionState_height = 100
        self.tryConnect_x = 20
        self.tryConnect_y = 20
        self.tryConnect_width = 300
        self.tryConnect_height = 150

        self.stacklist= stacklist
        self.widget = QWidget(self.stacklist)
        pages.main_page = self.widget
        self.main_background = QLabel(self.widget)
        self.main_background.setGeometry(0, 0, 1920, 1080)
        self.main_background.setStyleSheet(
            """
                background : White;
                border : None;
            """
        )

        self.robotArmPicure = QLabel(self.widget)
        self.robotArmPicure.setGeometry(378, 10, 1130, 1080)
        self.robotArmPicure.setPixmap(QPixmap(image.background))
        self.robotArmPicure.setScaledContents(True)
        self.robotArmPicure.setStyleSheet(
            """
                background : transparent;
                border : None;
            """
        )

        def CDial(x, y, w, h):
            Dial = QDial(self.widget)
            Dial.setGeometry(x , y, w, h)
            Dial.setNotchesVisible(True)
            Dial.setValue(0)
            return Dial
        
        self.ServoDialList=[]
        for id in range(1, 7):
            Dial = CDial(self.ServoDial_X_dict[id], self.ServoDial_Y_dict[id], self.ServoDial_width, self.ServoDial_height)
            if id == 1:
                Dial.setRange(0, 251)
                Dial.setValue(125)

            else:
                Dial.setRange(0, 300)

            if id == 3 :
                Dial.setValue(0)

            elif id == 4 :
                Dial.setValue(125)

            elif id == 5 :
                Dial.setValue(125)
            
            elif id == 6:
                Dial.setValue(0)
                
            Dial.valueChanged.connect(partial(self.indicateServoDial_value, id-1))
            self.ServoDialList.append(Dial)

        def CLabel(x, y, w, h):
            ServoDial_Value = QLabel(self.widget)
            ServoDial_Value.setText("0")
            ServoDial_Value.setGeometry(x, y, w, h)
            ServoDial_Value.setAlignment(Qt.AlignCenter)
            ServoDial_Value.setFont(QFont('Arial',25))
            ServoDial_Value.setStyleSheet(
                """
                
                    background : White;
                    border : solid 1px;
                    color : black;
                """
            )
            return ServoDial_Value
        
        self.ServoDialValueList=[]
        for id in range(1, 7):
            DialValue = CLabel(self.ServoDial_X_dict[id], self.ServoDial_Y_dict[id]+110, self.ServoDial_width, self.ServoDialValue_height)
            self.ServoDialValueList.append(DialValue)

        def CBtn(text, x, y, w, h):
            Btn = QPushButton(self.widget)
            Btn.setGeometry(x,y,w,h)
            Btn.setText(text)
            Btn.setStyleSheet(
                """
                QPushButton{
                    background : Grey;
                    border : solid 1px;
                    color : black;
                }
                QPushButton:pressed{
                     background : Black;
                     border : solid 1px;
                     color : White;
                }                
                """
                # """
                # QPushButton:{
                #     background : Red;
                #     border : solid 1px;
                #     color : black;
                # }
                # QPushButton:pressed{
                #     background : Black;
                #     border : solid 1px;
                #     color : White;
                # }
                # """
            )
            return Btn
        
        self.ServoUpBtnList=[]
        for id in range(1, 7):
            Upbtn = CBtn("UP",self.ServoUpBtn_X_dict[id], self.ServoUpBtn_Y_dict[id], self.ServoUpBtn_width, self.ServoUpBtn_height)
            Upbtn.clicked.connect(partial(self.upbtnCliked, id-1))
            self.ServoUpBtnList.append(Upbtn)

        self.ServoDownBtnList=[]
        for id in range(1, 7):
            Downbtn = CBtn("DOWN",self.ServoDownBtn_X_dict[id], self.ServoDownBtn_Y_dict[id], self.ServoDownBtn_width, self.ServoDownBtn_height)
            Downbtn.clicked.connect(partial(self.downbtnCliked, id-1))
            self.ServoDownBtnList.append(Downbtn)

        ##
        self.connectionStateLabel = CLabel(self.connectionState_x, self.connectionState_y, self.connectionState_width, self.connectionState_height)
        self.connectionStateLabel.setText("")
        self.connectionStateLabel.setStyleSheet(
                """
                    background : transparent;
                    border : None;
                """
        )
        self.connectionStateLabel.setPixmap(QPixmap(image.disconnected))
        self.connectionStateLabel.setScaledContents(True)

        self.tryConnectBtn = QPushButton(self.widget)
        self.tryConnectBtn.setGeometry(self.tryConnect_x, self.connectionState_y, self.tryConnect_width, self.tryConnect_height)
        self.tryConnectBtn.setText("TRY CONNECT")
        self.tryConnectBtn.setStyleSheet(
            """
                background : Gray;
                border : solid 1px;
                color : black;
            """
        )
        self.tryConnectBtn.released.connect(self.tryConnectBtn_released)
        self.tryConnectBtn.pressed.connect(self.tryConnectBtn_pressed)
        self.tryConnectBtn.clicked.connect(self.tryConnectBtn_clicked)

        self.stacklist.addWidget(self.widget)  

    def show_connection(self, state):
        if state:
            self.connectionStateLabel.setPixmap(QPixmap(image.connected))
        else:
            self.connectionStateLabel.setPixmap(QPixmap(image.disconnected))

    def indicateServoDial_value(self, id): 
        self.ServoDialValueList[id].setText(str(self.ServoDialList[id].value()))

    def return_Dial_values(self):
        values=[125,0,0,125,125,0]
        for id in range(6):
            values[id]=self.ServoDialList[id].value()
        return values
    
    def tryConnectBtn_released(self):
        self.tryConnectBtn.setStyleSheet(
            """
                background : Gray;
                border : solid 1px;
            """
        )

    def tryConnectBtn_pressed(self):
        self.tryConnectBtn.setStyleSheet(
            """
                background : Green;
                border : solid 1px;
            """
        )

    def tryConnectBtn_clicked(self):
        database.tryconnect_flag = 1

    def indicateServoDial_value(self, id): 
        self.ServoDialValueList[id].setText(str(self.ServoDialList[id].value()))

    def upbtnCliked(self, id):
        currentValue = self.ServoDialList[id].value()+2
        self.ServoDialList[id].setValue(currentValue)

    def downbtnCliked(self, id):
        currentValue = self.ServoDialList[id].value()-2
        self.ServoDialList[id].setValue(currentValue)