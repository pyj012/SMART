import socket, time, os
import threading 
import sys
import random
import json
import struct
import pickle
# import cv2
# import mediapipe as mp
import numpy as np
from collections import deque
import heapq
# from LowPassFilterTest import LowPassFilter
from protocol import *

angle= 0
prevSendTime = time.time()
lock = threading.Lock()
SERVER_HOST = "192.168.20.2"
SERVER_PORT = 5051



class SocketServer():
    def __init__(self):
        # 서버 구동에 필요한 정보 세팅
        self._host = SERVER_HOST
        self._port = SERVER_PORT
        self._data = data
        self._angle = angle
        self._prestate = data
        self.ai_result={}
        self._sendtime = ""
        self.client_socket =None
        self.lpf = []
        self.SMART = smartprotocol()
        self.client_socket =socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY,1)
        self.client_socket.connect((SERVER_HOST, SERVER_PORT))
        
        serverthread = threading.Thread(target= self._handle_client, args=(self.client_socket,))
        serverthread.daemon = True
        serverthread.start()

        while(1):
            # self.aitest()
            pass


    def _handle_client(self, client_socket):
        step = 0
        flag=True
        value = 0


        while True:
            try:
                BUFF_SIZE = 1024
                LIMIT_TIME = 10
                # send_value = self.SMART.contorol_motor([0x31,0x32,0x33,0x34,0x35,0x36,0x37,0x38,0x39,0x3A,0x3B,0x3C,0x3D],[value,value,value,value,value,value,value,value,value,value,value,value,value])
                send_value =(str({0x31:value,0x32:value,0x33:value,0x35:value,0x36:value,0x37:value,0x38:value,0x39:value,0x3B:value,0x3C:value}))
                # send_value = self.SMART.contorol_motor([0x31],[1])
                # data = pickle.dumps(send_value, protocol=pickle.HIGHEST_PROTOCOL)
                value += 1
                value %=200

                if len(send_value) <90:
                    for i in range(0, 90-len(send_value)):
                        send_value+=' '

                client_socket.sendall(bytes(send_value,'utf-8'))
                print(send_value, len((send_value)))
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

if __name__ == "__main__":
    server = SocketServer()