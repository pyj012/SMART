import sys, time
from css import *
from PyQt5.QtCore import QThread, Qt
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QStackedWidget, QDial, QVBoxLayout
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont, QPixmap
from functools import partial
from definse import *
from images import image

class Uilist():
    def __init__(self, stacklist):
        self.mainui=MainUi(stacklist)
        self.aimodeui=AImodeUi(stacklist)
        self.techingui=TechingUi(stacklist)
class TechingUi():
    def __init__(self, stacklist):
        self.ServoDial_X_dict={1:1180-350, 2:1180-350, 3:1200-350, 4:780-350, 5:960-350, 6:510-350}
        self.ServoDial_Y_dict={1:850+70, 2:650+70, 3:20+70, 4:20+70, 5:325+70, 6:170+70}
        self.ServoUpBtn_X_dict={1:1300-350, 2:1300-350, 3:1320-350, 4:900-350, 5:1060-350, 6:620-350}
        self.ServoUpBtn_Y_dict={1:880+70, 2:675+70, 3:45+70, 4:45+70, 5:350+70, 6:195+70}
        self.ServoDownBtn_X_dict={1:1360-350, 2:1360-350, 3:1380-350, 4:960-350, 5:1120-350, 6:680-350}
        self.ServoDownBtn_Y_dict={1:880+70, 2:675+70, 3:45+70, 4:45+70, 5:350+70, 6:195+70}
        self.ServoUpBtn_width = 50
        self.ServoUpBtn_height = 50
        self.ServoDownBtn_width = 50
        self.ServoDownBtn_height = 50
        self.ServoDial_width = 100
        self.ServoDial_height = 100
        self.ServoDialValue_height = 50

        self.torqueButtonWidth = 375
        self.torqueButtonHeight = 150
        self.torqueButtonX= 1145
        self.torqueButtonY = 1020

        self.saveButtonWidth = 375
        self.saveButtonHeight = 150
        self.saveButtonX= 1535
        self.saveButtonY = 1020

        self.verticalLayoutLabelWidth = 760
        self.verticalLayoutLabelHeight = 1000
        self.verticalLayoutLabelX = 1145
        self.verticalLayoutLabelY = 0

        self.itemsWidth = 710
        self.itemsHeight = 80

        self.stacklist= stacklist
        self.widget = QWidget(self.stacklist)
        pages.techingmode_page = self.widget

        self.main_background = QLabel(self.widget)
        self.main_background.setGeometry(0, 0, 1920, 1200)
        self.main_background.setStyleSheet(BackGroundStyle)

        self.robotArmPicure = QLabel(self.widget)
        self.robotArmPicure.setGeometry(0, 0, 1130, 1200)
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
                Dial.setValue(2)

            elif id == 4 :
                Dial.setValue(14)

            elif id == 5 :
                Dial.setValue(16)
            
            elif id == 6:
                Dial.setValue(125)
                
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

    
        self.layoutwidget = QWidget(self.widget)
        self.layoutwidget.setGeometry(self.verticalLayoutLabelX,self.verticalLayoutLabelY ,self.verticalLayoutLabelWidth ,self.verticalLayoutLabelHeight)
        self.layout = QVBoxLayout()
        for i in range(4):
            label = QLabel()
            label.setText("GHG")
            label.setAlignment(Qt.AlignCenter)
            label.setFixedHeight(self.itemsHeight)
            label.setFixedWidth(self.itemsWidth)
            label.setStyleSheet(itemsStyle)
            self.layout.addWidget(label)
        self.layout.addStretch(1)
        self.layoutwidget.setLayout(self.layout)

        self.torqueButton = QPushButton(self.widget)
        self.torqueButton.setGeometry(self.torqueButtonX, self.torqueButtonY, self.torqueButtonWidth, self.torqueButtonHeight)
        self.torqueButton.setText("Torque OFF")
        self.torqueButton.setCheckable(True)
        self.torqueButton.setFont(QFont('Arial',40))
        self.torqueButton.setStyleSheet("""
                background : Red;
                border : solid 1px;
                color : White;
            }
            """
)
        self.torqueButton.clicked.connect(self.torque_Button_clicked)

        self.saveButton = QPushButton(self.widget)
        self.saveButton.setGeometry(self.saveButtonX, self.saveButtonY, self.saveButtonWidth, self.saveButtonHeight)
        self.saveButton.setText("SAVE")
        self.saveButton.setFont(QFont('Arial',40))
        self.saveButton.setStyleSheet(ButtonStyle)
        self.saveButton.clicked.connect(self.save_Button_clicked)

        self.stacklist.addWidget(self.widget)  

    def torque_Button_clicked(self):
        if self.torqueButton.isChecked() :
            self.torqueButton.setStyleSheet(
            """
                background : Green;
                border : solid 1px;
                color : Black;
            
            """)
            self.torqueButton.setText("Touque ON")

        else:
            self.torqueButton.setText("Torque OFF")
            self.torqueButton.setStyleSheet("""
                    background : Red;
                    border : solid 1px;
                    color : White;
                
                """)
            
    def save_Button_clicked(self):
        pass

    def show_connection(self, state):
        if state:
            self.torqueStateLabel.setPixmap(QPixmap(image.connected))
        else:
            self.torqueStateLabel.setPixmap(QPixmap(image.disconnected))

    def indicateServoDial_value(self, id): 
        self.ServoDialValueList[id].setText(str(self.ServoDialList[id].value()))

    def return_Dial_values(self):
        values=[125,0,0,0,0,125]
        for id in range(6):
            values[id]=self.ServoDialList[id].value()
        return values
    
    def indicateServoDial_value(self, id): 
        self.ServoDialValueList[id].setText(str(self.ServoDialList[id].value()))

    def upbtnCliked(self, id):
        currentValue = self.ServoDialList[id].value()+2
        self.ServoDialList[id].setValue(currentValue)

    def downbtnCliked(self, id):
        currentValue = self.ServoDialList[id].value()-2
        self.ServoDialList[id].setValue(currentValue)

class MainUi():
    def __init__(self, stacklist):

        self.BackGroundLabelWidth = 1920
        self.BackGroundLabelHeight = 1200
        self.BackGroundLabelX = 0
        self.BackGroundLabelY = 0

        self.AImodeButtonWidth = 800
        self.AImodeButtonHeight = 800
        self.AImodeButtonX = 120
        self.AImodeButtonY = 230

        self.TechingModeButtonWidth = 800
        self.TechingModeButtonHeight = 800
        self.TechingModeButtonX = 1000
        self.TechingModeButtonY = 230

        self.stacklist= stacklist
        self.widget = QWidget(self.stacklist)
        
        pages.main_page = self.widget
        self.main_background_Label = QLabel(self.widget)
        self.main_background_Label.setGeometry(self.BackGroundLabelX, self.BackGroundLabelY, self.BackGroundLabelWidth, self.BackGroundLabelWidth)
        self.main_background_Label.setStyleSheet(BackGroundStyle)

        self.AI_Mode_Button = QPushButton(self.widget)
        self.AI_Mode_Button.setGeometry(self.AImodeButtonX, self.AImodeButtonY, self.AImodeButtonWidth, self.AImodeButtonHeight)
        self.AI_Mode_Button.setText("AI")
        self.AI_Mode_Button.setFont(QFont('Arial',180))
        self.AI_Mode_Button.setStyleSheet(ButtonStyle)

        self.AI_Mode_Button.clicked.connect(self.AI_Mode_Button_clicked)

        self.Teching_Mode_Button = QPushButton(self.widget)
        self.Teching_Mode_Button.setGeometry(self.TechingModeButtonX, self.TechingModeButtonY, self.TechingModeButtonWidth, self.TechingModeButtonHeight)
        self.Teching_Mode_Button.setText("Teching")
        self.Teching_Mode_Button.setFont(QFont('Arial',160))
        self.Teching_Mode_Button.setStyleSheet(ButtonStyle)
        self.Teching_Mode_Button.clicked.connect(self.Teching_Mode_Button_clicked)
        self.stacklist.addWidget(self.widget)  

    def Teching_Mode_Button_clicked(self):
        self.stacklist.setCurrentWidget(pages.techingmode_page)

    def AI_Mode_Button_clicked(self):
        self.stacklist.setCurrentWidget(pages.aimode_page)

class AImodeUi():
    def __init__(self, stacklist):

        self.BackGroundLabelWidth = 1920
        self.BackGroundLabelHeight = 1200
        self.BackGroundLabelX = 0
        self.BackGroundLabelY = 0

        self.CameraLabelWidth = 1080    
        self.CameraLabelHeight = 1080
        self.CameraLabelX = 1080
        self.CameraLabelY = 1080

        self.MotorStateLabelWidth = 620
        self.MotorStateLabelHeight = 120
        self.MotorStateLabelX = 1230
        self.MotorStateLabelY = 50

        self.BackButtonWidth = 80
        self.BackButtonHeight = 80
        self.BackButtonX = 1830
        self.BackButtonY = 10

        self.MotorStateLabelList=[]
        self.stacklist= stacklist
        self.widget = QWidget(self.stacklist)
        
        pages.aimode_page = self.widget
        self.main_background_Label = QLabel(self.widget)
        self.main_background_Label.setGeometry(self.BackGroundLabelX, self.BackGroundLabelY, self.BackGroundLabelWidth, self.BackGroundLabelWidth)
        self.main_background_Label.setStyleSheet(BackGroundStyle)

        self.Camera_Label = QLabel(self.widget)
        self.Camera_Label.setGeometry(self.CameraLabelX, self.CameraLabelY, self.CameraLabelWidth, self.CameraLabelHeight)
        self.Camera_Label.setScaledContents(True)
        self.Camera_Label.setStyleSheet(CameraStyle)

        for i in range(6):
            Motor_state_label = QLabel(self.widget)
            Motor_state_label.setGeometry(self.MotorStateLabelX, self.MotorStateLabelY, self.MotorStateLabelWidth, self.MotorStateLabelHeight)
            Motor_state_label.setText("0")
            Motor_state_label.setAlignment(Qt.AlignCenter)
            Motor_state_label.setFont(QFont('Arial',80))
            Motor_state_label.setStyleSheet(LabelStyle)
            self.MotorStateLabelList.append(Motor_state_label)
            self.MotorStateLabelY+=190

        self.Teching_Mode_Button = QPushButton(self.widget)
        self.Teching_Mode_Button.setGeometry(self.BackButtonX, self.BackButtonY, self.BackButtonWidth, self.BackButtonHeight)
        self.Teching_Mode_Button.setStyleSheet(BackButtonStyle)
        self.Teching_Mode_Button.clicked.connect(self.Back_Button_clicked)

        self.stacklist.addWidget(self.widget)  

    def refresh_camera(self, pic):
        self.Camera_Label.setPixmap(pic)

    # def AI_Mode_Button_clicked(self):
    #     self.stacklist.setCurrentWidget(pages.aimode_page)

    def Back_Button_clicked(self):
        self.stacklist.setCurrentWidget(pages.main_page)