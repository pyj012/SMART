import socket, time, serial
import os, threading
import re
from _thread import *
import pickle

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
            print("recv from serial : ", readvalue)
            
    def sendserial(self):
        while(1):
            if time.time()-self.prevTime>=0.1:
                lock.acquire()
                dynamixellSerial.write(bytes(self.sendvalue))
                lock.release()
                self.prevTime = time.time()

    
a= test()
read_thread = threading.Thread(target= a.readserial, args=())
read_thread.daemon=True
read_thread.start()



while(1):
    pass
   