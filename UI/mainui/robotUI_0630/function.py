from definse import *
import serial
import threading
import time
PORT='/dev/cu.usbmodem114401'
BAUD = 115200
class Dynamixell():
    def __init__(self, debug=False):
        self.dynamixellSerial = None
        self.debug= debug
        self.connectDevice(PORT, BAUD)

    def debugPrint(self, data):
        if self.debug:
            print(data)

    def connectDevice(self, com=None, baud=None):
        try:
            if self.dynamixellSerial== None:
                self.dynamixellSerial = serial.Serial(port = com, baudrate= baud)
                self.debugPrint(self.dynamixellSerial)
                database.connectionState = 1
                time.sleep(1)

        except Exception as e:
            print("Device connect fail",e)
            self.dynamixellSerial=None
            database.connectionState = 0
            pass
        
    def createpacket(self, idList=[],angleList=[]):
        protocol_arry=[protocol.STX]
        id_len = len(idList)
        angle_len= len(angleList)*3
        data_len = id_len+angle_len
        length_H = (data_len)// 10 + 48
        length_L = (data_len) % 10 + 48
        protocol_arry.extend([length_H, length_L, protocol.CMD_CONTROL])
        CRC_SUM = protocol.CMD_CONTROL
        for id_num in range(len(idList)):
            place100 = angleList[id_num] // 100 + 48
            place10  = (angleList[id_num] - (angleList[id_num]//100) * 100) // 10 + 48
            place1   = angleList[id_num] % 10 + 48
            protocol_arry.append(idList[id_num])    
            protocol_arry.extend([place100, place10, place1])
            CRC_SUM += idList[id_num]
            CRC_SUM = CRC_SUM + place100 + place10 + place1

        CRC_SUM += 0x01
        CRC_SUM = bin(CRC_SUM)[2:]
        CRC_H = int(CRC_SUM,2) & 0xff00
        CRC_H = CRC_H>>8
        CRC_H = 0xff - CRC_H
        CRC_L = int(CRC_SUM,2) & 0x00ff

        protocol_arry.extend([CRC_H, CRC_L, protocol.ETX])
        return bytes(protocol_arry)
    
    def writeDynamixcell(self, bytesarry = []):
        self.dynamixellSerial.write(bytesarry)

    def readDynamixcell(self):
        readvalue=self.dynamixellSerial.readline()
        return readvalue
    
    def contorol_motor(self, idList=[],angleList=[]):
        try:
            packet = self.createpacket(idList,angleList)
            # self.debugPrint(packet)
            self.writeDynamixcell(packet)

        except Exception as e:
            print("Serial Send Fail", e)
            self.dynamixellSerial=None
            self.connectDevice(PORT, BAUD)

            pass

    def readserial(self):
        while(1):
            try:
                readvalue=self.readDynamixcell()
                print("recv from serial : ", readvalue)

            except Exception as e:
                print("Serial Read Fail", e)
                self.dynamixellSerial=None
                time.sleep(5)
                pass