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


SERVER_HOST = "192.168.20.2" ## server에 출력되는 ip를 입력해주세요 ##
SERVER_PORT = 5051
lock = threading.Lock()
class SocketServer():
    def __init__(self, sendQ1, sendQ2):
        # 서버 구동에 필요한 정보 세팅
        self._host = SERVER_HOST
        self._port = SERVER_PORT
        self.ai_result={}
        self._sendtime = ""
        self.lpf = []
        self.robotclient = None
        self.controllerclient =None
        self.value=None
        self.sendvalue = 0
        self.times =  0
        self.prevTime = 0
        self.motorAngles={}
        self.robotprevTime = time.time()
        self.sendQ1 = sendQ1
        self.sendQ2= sendQ2
        self.prevAngleValue =[]
        self.controllerDict={}
        self.RobotDict ={}
        self.datadict={}
        self.verbose= False
        
        print('Server Start')
        
        self.lock = threading.Lock()
        
        self.run_server()


    def run_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_address = (self._host, self._port)
        print('Strat up on {} port {}'.format(*server_address))
        self.server_socket.bind(server_address)
        self.server_socket.listen()
        while True:
            try:
                temp_client_socket, client_address = self.server_socket.accept()
                player_ip=int(client_address[0].split(".")[3])
                if player_ip == 100:
                    print("Controller connected : ", player_ip)
                    self.controllerclient = temp_client_socket
                    controllor_thread = threading.Thread(target= self._handle_controller, args=(self.controllerclient,))
                    controllor_thread.daemon = True
                    controllor_thread.start()
                    

                else :
                    print("Robot connected : ", player_ip)
                    self.robotclient = temp_client_socket
                    serverthread = threading.Thread(target= self._handle_robot, args=(self.robotclient,))
                    serverthread.daemon = True
                    serverthread.start()
            except Exception as e:  
                pass


    def _handle_controller(self, client_socket):
        while True:
            try:
                controller_data = client_socket.recv(22)
                data=controller_data.decode()
                self.controllerDict= eval(data)
                self.sendQ1.put(self.controllerDict)
            except socket.timeout as err:
                print('self.self.client_socket Timeout Error')
                
                # 추가적인 예외처리 로직 구성...
                self._close_client(client_socket)
                break
            except socket.error as err:
                self._close_client(client_socket)
                break   

    def _handle_robot(self, client_socket):
        while True:
            try:
                robot_data = client_socket.recv(90)
                data=str(robot_data,'utf-8')
                self.RobotDict=eval(data)
                
                self.sendQ2.put(self.RobotDict)

                time.sleep(0.001)

            except socket.timeout as err:
                print('self.self.client_socket Timeout Error')
                
                # 추가적인 예외처리 로직 구성...
                self._close_client(client_socket)
                break
            except socket.error as err:
                self._close_client(client_socket)
                break   

    def _close_client(self, client_socket):
        client_socket.close()

class servocontrol():
    def __init__(self, recvQ1, recvQ2):
        self.recvQ1= recvQ1
        self.recvQ2= recvQ2
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
                print(self.angle1, self.angle2)
                # (0x35,0x3B,0x3E,0x3F) angle1
                # (0x31,0x32,0x33,0x34,0x36,0x37,0x38,0x39,0x3A,0x3C) angle2

                for id in self.dynamixel.DXL_LIST:
                    current_id = id+48
                    if current_id in self.angle1:
                        self.dynamixel.GoalPosition(id, self.angle1[current_id])
                        print("angle1")
                    elif current_id in self.angle2:
                        self.dynamixel.GoalPosition(id, self.angle2[current_id]) 
                        print("angle2")
                
            except Exception as e:
                print(e)
                pass

    def working(self):
        while True:
            if self.recvQ1.qsize()>0:
                self.angle1=self.recvQ1.get()

            if self.recvQ2.qsize()>0:
                self.angle2=self.recvQ2.get()    




if __name__ == "__main__":
    server = SocketServer()

   