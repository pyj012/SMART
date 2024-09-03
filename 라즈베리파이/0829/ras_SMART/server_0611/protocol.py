import serial
import threading
import time

#ser = serial.Serial('COM3', 9600, timeout=1)
data = {'cmd_type':0xC0,'1': 0,'2': 0,'3': 0,'4': 0,'5': 0,'6': 0}
angle0 = {'cmd_type':0xC0,'1': 0,'2': 0,'3': 0,'4': 0,'5': 0,'6': 0}
angle150 = {'cmd_type':0xC0,'1': 150,'2': 150,'3': 150,'4': 150,'5': 150,'6': 150}
angle1 = {'cmd_type':0xC0,'0':0,'1':10,'2':20,'3':30,'4':40,'5':50,'6':60,'7':70,'8':80,'9':90,'10':100,'11':110,'12':120,'13':130,'14':140,'15':150}
angle2 = {'cmd_type':0xC0,'7':70,'8':80,'9':90,'10':100,'11':110,'12':120,'13':130,'14':140,'15':150}
angle3 = {'cmd_type':0xA0,'0':0,'1':10,'2':20,'3':30,'4':40,'5':50,'6':60,'7':70}
angle4 = {'cmd_type':0xA0,'0':0,'2':20,'4':40,'6':60,'8':80,'10':100,'12':120,'14':140}

STX = 0x02
ETX = 0x03

CONTROL_CMD = 0xC0

angle=[0x30,0x30,0x30]

CRC = 0
CRC_H = 0x00
CRC_L = 0x00
class smart():
    def __init__(self):
        self.data = 0
        self.parsing_flag = False
        self.parsing_step = 0
        self.dataLength = 0
        self.dataCMD = 0xA0
    def packet_parsing(self, list):
        if self.parsing_step == 0:
            if list[0] == STX:
                self.parsing_step+=1

        if self.parsing_step == 1:
            if list[-1] == ETX:
                self.parsing_step+=1
            
        if self.parsing_step == 2:
            length_H = int(chr(list[1]))*10
            length_L = int(chr(list[2]))
            self.dataLength = length_H + length_L
            self.parsing_step+=1
            self.dataCMD = list[3]

        if self.parsing_step == 3:
            dataPacket = list[4:self.dataLength]
            print("read : ", dataPacket)

def sendProtocol(data: dict):
    #CONTROL_CMD = data['cmd_type']
    #del data['cmd_type']
    CRC = CONTROL_CMD

    protocol = [STX]
    length_f = ((len(data)-1) * 4) // 10 + 0x30
    length_b = ((len(data)-1) * 4) % 10 + 0x30
    protocol = protocol + [length_f,length_b]
    protocol = protocol + [CONTROL_CMD]

    for i in range(1,len(data)):
        n = list(data.keys())
        place100 = data[n[i]] // 100 + 48
        place10  = (data[n[i]] - (data[n[i]]//100) * 100) // 10 + 48
        place1   = data[n[i]] % 10 + 48
        id = 0x30 + int(n[i])
        protocol = protocol + [id, place100,place10,place1]
        CRC = CRC + id + place100 + place10 + place1

    CRC = CRC + 0x01
    CRC = bin(CRC)[2:]
    CRC_H = int(CRC,2) & 0xff00
    CRC_H = CRC_H>>8
    CRC_H = 0xff - CRC_H
    CRC_L = int(CRC,2) & 0x00ff

    protocol = protocol + [CRC_H,CRC_L,ETX]
    '''for i in protocol:
        h = hex(i)
        h = h[2:]
        print(h,end=' ')
    print("")'''
    return protocol

def sendt():
    while True:
        send_value = sendProtocol(data)
        #print("sendvlaue:", send_value)
        try:
            ser.write(send_value)
        except Exception as e:
            print("Error occurred:", e)
        time.sleep(1)

def receivet():
    while True:
        #print("im read:",ser.readline())
        time.sleep(0.001)


if __name__ == "__main__":
    
    time.sleep(3)
    readthread = threading.Thread(target= receivet, args=())
    readthread.daemon= True
    readthread.start()

    sendthread = threading.Thread(target= sendt, args=())
    sendthread.daemon= True
    sendthread.start()

    while True:
        if data == angle0:
            data = angle150
        else:
            data = angle0
        print(data)
        time.sleep(3)

