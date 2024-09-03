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


SERVER_HOST = "192.168.20.8" ## server에 출력되는 ip를 입력해주세요 ##
SERVER_PORT = 5051
lock = threading.Lock()
class SocketServer():
    def __init__(self, sendQ, recvQ):
        # 서버 구동에 필요한 정보 세팅
        self._host = SERVER_HOST
        self._port = SERVER_PORT
        self.ai_result={}
        self._sendtime = ""
        self.client_socket =None
        self.lpf = []
        self.robotclient = None
        self.controllerclient =None
        self.value=None
        self.sendvalue = 0
        self.times =  0
        self.prevTime = 0
        self.motorAngles={}
        self.robotprevTime = time.time()
        self.recvQ = recvQ
        self.sendQ = sendQ
        self.prevAngleValue =[]
        print('Server Start')
 

        self.lock = threading.Lock()
        # readdynamix = threading.Thread(target= self._read, args=())
        # readdynamix.daemon = True
        # readdynamix.start()

        # self.debugthread = threading.Thread(target= self.sendQueue, args=())
        # self.debugthread.daemon=True
        # self.debugthread.start()
        self.run_server()

    def sendQueue(self):
        while (1):
            lock.acquire()
            currentAngleValue = list(self.motorAngles.values())
            if self.prevAngleValue != currentAngleValue:
            # if len(list(self.motorAngles.keys()))>0:
                self.prevAngleValue = currentAngleValue
                self.sendQ.put(self.motorAngles)
                # print("CHANGE")
            lock.release()
            time.sleep(0.001)

    def run_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_address = (self._host, self._port)
        print('Strat up on {} port {}'.format(*server_address))
        self.server_socket.bind(server_address)
        self.server_socket.listen()

        while True:
            self.client_socket, client_address = self.server_socket.accept()
            player_ip=int(client_address[0].split(".")[3])
            print("robot connected : ", player_ip)
            self.robotclient = self.client_socket
            serverthread = threading.Thread(target= self._handle_robot, args=(self.robotclient,))
            serverthread.daemon = True
            serverthread.start()
            break

        while True:
            # currentAngleValue = list(self.motorAngles.values())
            # if self.prevAngleValue != currentAngleValue:
            # # if len(list(self.motorAngles.keys()))>0:
            #     self.prevAngleValue = currentAngleValue
            self.sendQ.put(self.motorAngles)
                # print("CHANGE")
            time.sleep(0.001)
            # if player_ip == 100: 
            #     print("Controller connected : ", player_ip)
            #     self.controllerclient = self.client_socket
            #     controllor_thread = threading.Thread(target= self._handle_controller, args=(self.controllerclient,))
            #     controllor_thread.daemon = True
            #     controllor_thread.start()

            # else:
            #     print("robot connected : ", player_ip)
            #     self.robotclient = self.client_socket
            #     serverthread = threading.Thread(target= self._handle_robot, args=(self.robotclient,))
            #     serverthread.daemon = True
            #     serverthread.start()

    def _handle_controller(self, client_socket):
            SMART = smartprotocol()
            SMART.verbose=True
            while True:
                try:
                    BUFF_SIZE = 1024
                    LIMIT_TIME = 10
                    client_data = client_socket.recv(1)
                    data = int.from_bytes(client_data,'big')
                    SMART.parsingprotocol(data)
                    if SMART.debug :
                        idlist= SMART.packetfilter(SMART.idList)
                        vallist=[]
                        for i in range(len(SMART.valueList)):
                            temp_list= SMART.valueList[i]
                            result = SMART.packetfilter(temp_list)
                            if len(result) >0:
                                d100=int(chr(result[0]))*100
                                d10=int(chr(result[1]))*10
                                d1=int(chr(result[2]))
                                value = d100 + d10 + d1
                                vallist.append(value)
                        SMART.debug=0
                        for i in range(len(idlist)):
                            id = idlist[i]
                            value = vallist[i]
                            lock.acquire()
                            self.motorAngles[id]=value
                            lock.release()
                except socket.timeout as err:
                    print('self.self.client_socket Timeout Error')
                    # 추가적인 예외처리 로직 구성...
                    self._close_client(client_socket)
                    break

                except socket.error as err:
                    print('self.self.client_socket Timeout Error')
                    self._close_client(client_socket)
                    break

    def _handle_robot(self, client_socket):
        SMART = smartprotocol()
        SMART.verbose=False
        prev_data=None
        value=0
        while True:
            try:
                client_data = client_socket.recv(1024)
                pickledata = pickle.loads(client_data)
                
                for data in pickledata:
                    # _ = int.from_bytes(data,'big')
                    SMART.parsingprotocol(data)

                if SMART.debug :
                    value+=1
                    # print(value)
                    idlist= SMART.packetfilter(SMART.idList)
                    vallist=[]
                    for i in range(len(SMART.valueList)):
                        temp_list= SMART.valueList[i]
                        result = SMART.packetfilter(temp_list)
                        if len(result) >0:
                            d100=int(chr(result[0]))*100
                            d10=int(chr(result[1]))*10
                            d1=int(chr(result[2]))
                            value = d100 + d10 + d1
                            vallist.append(value)
                    SMART.debug=0
                    for i in range(len(idlist)):
                        id = idlist[i]
                        value = vallist[i]
                        lock.acquire()
                        self.motorAngles[id]=value
                        lock.release()

            except socket.timeout as err:
                print('self.self.client_socket Timeout Error')
                
                # 추가적인 예외처리 로직 구성...
                self._close_client(client_socket)
                break
            except socket.error as err:
                self._close_client(client_socket)
                break           
    # def _handle_robot(self, client_socket):
    #     SMART = smartprotocol()
    #     while True:
    #         try:
    #             client_data = client_socket.recv(1)
    #             data = int.from_bytes(client_data,'big')
    #             SMART.parsingprotocol(data)
    #             if SMART.debug :
    #                 idlist= SMART.packetfilter(SMART.idList)
    #                 vallist=[]
    #                 for i in range(len(SMART.valueList)):
    #                     temp_list= SMART.valueList[i]
    #                     result = SMART.packetfilter(temp_list)
    #                     if len(result) >0:
    #                         d100=int(chr(result[0]))*100
    #                         d10=int(chr(result[1]))*10
    #                         d1=int(chr(result[2]))
    #                         value = d100 + d10 + d1
    #                         vallist.append(value)
    #                 SMART.debug=0
    #                 for i in range(len(idlist)):
    #                     id = idlist[i]
    #                     value = vallist[i]
    #                     self.motorAngles[id]=value
    #         except socket.timeout as err:
    #             print('self.self.client_socket Timeout Error')
                
    #             # 추가적인 예외처리 로직 구성...
    #             self._close_client(client_socket)
    #             break
    #         except socket.error as err:
    #             self._close_client(client_socket)
    #             break


    def _close_client(self, client_socket):
        client_socket.close()

if __name__ == "__main__":
    server = SocketServer()

   