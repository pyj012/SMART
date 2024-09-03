import serial,time
import os, threading

class customserial():
    def __init__(self):
        self.serial = serial.Serial(port = '/dev/ttyAMA0', baudrate= 115200)

    def _start(self):
        readdynamix = threading.Thread(target= self._read, args=())
        readdynamix.daemon = True
        readdynamix.start()

        # senddynamix = threading.Thread(target= self._send, args=())
        # senddynamix.daemon = True
        # senddynamix.start()

    def _send(self, data):
        self.serial.write(data)

    def _read(self):
        while(1):
            readvalue=self.serial.readline()
            print("recv from serial : ", readvalue)