import socket, time, serial
import os, threading
import re
from _thread import *
import pickle



SERVER_HOST = "192.168.20.7" ## server에 출력되는 ip를 입력해주세요 ##
SERVER_PORT = 5051

print('try Connect Server')
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_HOST, SERVER_PORT))

print("SERVER : ",client_socket)
dynamixellSerial = serial.Serial(port = '/dev/ttyAMA0', baudrate= 115200)

lock = threading.Lock()
class test():
    def __init__(self):
        self.value=None
        self.sendvalue = 0
        self.times =  0
        self.prevTime = 0

    def readserial(self):
        while(1):
            readvalue=dynamixellSerial.readline()
            # print("recv from serial : ", readvalue)
            
    def sendserial(self):
        while(1):
            if time.time()-self.prevTime>=0.1:
                lock.acquire()
                dynamixellSerial.write(bytes(self.sendvalue))
                lock.release()
                self.prevTime = time.time()

    def testing(self):
        while True:
            try:
                data = client_socket.recv(1024)
                # temp0 = data.decode()
                # temp1=temp0.replace('[','')
                # client_data=list(temp1.replace(']',''))
                self.value=pickle.loads(data)
                print(self.value[0])
                self.sendvalue= bytes(self.value[0])
                # print(self.sendvalue)
                self.times = self.value[1]
                lock.acquire()
                dynamixellSerial.write(bytes(self.sendvalue))
                lock.release()
                # sendtime = str(self.times)
                # print(sendtime)
                # client_socket.sendall(sendtime.encode())
            except Exception as e:
                print(e)
                pass
            # d
    
a= test()
read_thread = threading.Thread(target= a.readserial, args=())
read_thread.daemon=True
read_thread.start()

send_thread = threading.Thread(target= a.sendserial, args=())
send_thread.daemon=True
send_thread.start()

recv_thread = threading.Thread(target= a.testing, args=())
recv_thread.daemon=True
recv_thread.start()

while(1):
    pass
