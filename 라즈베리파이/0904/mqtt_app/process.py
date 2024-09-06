import sys, os,cv2, time,threading
from definse import *
import socket, time,  select
import os, threading
import re
from _thread import *
import pickle
from protocol import *
from multiprocessing import Process, Queue
from customserial import *
import json
from itertools import chain
import paho.mqtt.client as mqtt

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dynamixel_sdk.dynamixel import *

class cameraProcess():
    def __init__(self, sendQ, recvQ):

        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
        self.recvQ = recvQ
        self.sendQ = sendQ
        self.FPS = 1/30
        self.FPS_MS = int(self.FPS * 1000)
        self.read()

    def read(self):
        while (1):
            if self.camera != None:
                ret, frame = self.camera.read()
                if frame != None:
                    self.sendQ.put(frame)
            time.sleep(self.FPS)

class mqttSub():
    def __init__(self, sendQ, type=1):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_subscribe = self.on_subscribe
        self.client.on_message = self.on_message
        self.type = "robot"
        if type == 1:
            self.type = "robot"
        elif type == 2:
            self.type = "leftController"
        elif type == 3:
            self.type = "rightController"
  

        self.client.connect('localhost',1883)
        self.client.subscribe(self.type,1)
        self.data = {}
        self.sendQ= sendQ
        self.client.loop_forever()

    def on_connect(self, client, userdata, flags ,rc):
        if rc==0:
            print("connected OK")
        else:
            print("bad connection")

    def on_disconnect(self, client, userdata, flags, rc=0):
        print(str(rc))

    def on_subscribe(self, client, userdata, mid, granted_qos):
        print("sub = " +str(mid)+" "+ str(granted_qos))

    def on_message(self, client, userdata, msg):
        self.data = eval(msg.payload.decode("utf-8"))
        self.sendQ.put(self.data)


class servocontrol():
    def __init__(self, robot_data, left_controller_data, right_controller_data):
        self.robot_data= robot_data
        self.left_controller_data= left_controller_data
        self.right_controller_data = right_controller_data
        self.dynamixel = DynamixelSDK()
        self.dynamixel.OpenPort()
        self.dynamixel.Find(30)
        for id in self.dynamixel.MX_LIST:
            # self.dynamixel.ControlTorque(id, OFF)
            # self.dynamixel.SetOperationMode(POSITON_MODE)
            # self.dynamixel.ControlTorque(id, ON)
            # self.dynamixel.GoalPosition(id ,0)
            self.dynamixel.ControlTorque(id, OFF)
            self.dynamixel.SetOperationMode(MULTI_TURN_MODE)
            self.dynamixel.ControlTorque(id, ON)

        for id in self.dynamixel.RX_LIST:
            self.dynamixel.ControlTorque(id, ON)
            self.dynamixel.GoalPosition(id ,0)
        
        self.angle1={}
        self.angle2={}
        self.angle3={}

        self.dict={}
        self.refreshTime= 0
        self.dxtime=0
        serverthread = threading.Thread(target= self.servocontrol, args=())
        serverthread.daemon = True
        serverthread.start()
        self.working()

    def servocontrol(self):
        while True:
            try:
                print(self.angle1, self.angle2, self.angle3)
                # print(type(self.angle1), type(self.angle2), type(self.angle3))

                # (0x35,0x3B,0x3E,0x3F) angle1
                # (0x31,0x32,0x33,0x34,0x36,0x37,0x38,0x39,0x3A,0x3C) angle2

                # for id in self.dynamixel.DXL_LIST:
                # for current_id in self.angle1:
                #     # id = int(ord(chr(int(current_id))))-48
                # print(self.angle1['57'])
                self.dynamixel.GoalPosition(9, self.angle1['57'])

                # for current_id in self.angle2:
                #     # id = int(ord(chr(int(current_id))))-48
                #     self.dynamixel.GoalPosition(id, self.angle2[current_id]) 

                # for current_id in self.angle3:
                #     # id = int(ord(chr(int(current_id))))-48
                #     self.dynamixel.GoalPosition(id, self.angle3[current_id]) 

            except Exception as e:
                print(e)
                pass

    def working(self):
        while True:
            if self.robot_data.qsize()>0:
                self.angle1=self.robot_data.get()

            if self.left_controller_data.qsize()>0:
                self.angle2=self.left_controller_data.get()    

            if self.right_controller_data.qsize()>0:
                self.angle3=self.right_controller_data.get()    


   