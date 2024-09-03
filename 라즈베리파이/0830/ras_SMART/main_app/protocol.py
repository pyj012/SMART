import threading
import time
STX = 0x02
ETX = 0x03
REQUEST_CMD = 0xA0
CONTROL_CMD = 0xC0
CMD_TORQUEOFF =0xC1
CMD_TORQUEON =0xC2
CMD_ANSWER =0xA0
angle=[0x30,0x30,0x30]

CRC = 0
CRC_H = 0x00
CRC_L = 0x00
class smartprotocol():
    def __init__(self):
        self.data = 0
        self.dataLength = 0
        self.parsingSenq=0
        self.parsingStep=0
        self.dataLength_10 = 0
        self.dataLength_1  = 0
        self.currentPacketLen=0
        self.totalDataLength=0
        self.idNum=0
        self.idcnt=0
        self.valueNum=0
        self.debug=0
        self.CAL_CRC_H = 0x0
        self.CAL_CRC_L = 0x0 
        self.CRC_H = 0x0
        self.CRC_L = 0x0
        self.SUM_CRC = 0x0
        self.controlByte = 0x0
        self.preParsingList=[]
        self.dataLength=[]
        self.dataList=[]
        self.idList=[]
        self.valueList=[]
        self.sendpaket=[]
        self.temmlist=[]
        self.verbose = 1

    def reset(self):
        self.data = 0
        self.dataLength = 0
        self.parsingSenq=0
        self.parsingStep=0
        self.dataLength_10 = 0
        self.dataLength_1  = 0
        self.currentPacketLen=0
        self.totalDataLength=0
        self.idNum=0
        self.idcnt=0
        self.valueNum=0
        self.CAL_CRC_H = 0x0
        self.CAL_CRC_L = 0x0 
        self.CRC_H = 0x0
        self.CRC_L = 0x0
        self.SUM_CRC = 0x0
        self.controlByte = 0x0
        self.preParsingList=[]
        self.dataLength=[]
        self.sendpaket=[]

    def printverbos(self,data):
        if self.verbose:
            print(data)

    def parsingprotocol(self, readByte):
        if self.parsingStep == 0:
            if readByte == STX:
                self.parsingSenq=0
                self.preParsingList=[]
                self.dataLength=[]
                self.dataList=[]
                self.parsingStep=1
                self.printverbos("FIND STX")

        if self.parsingStep == 1:
            self.preParsingList.append(readByte)
            self.parsingSenq+=1
            if readByte == ETX:
                self.parsingStep=2
                self.printverbos("FIND ETX")

        if self.parsingStep == 2:
            self.dataLength.append(self.preParsingList[1])
            self.dataLength.append(self.preParsingList[2])
            self.dataLength_10 = int(chr(self.dataLength[0]))*10
            self.dataLength_1  = int(chr(self.dataLength[1]))
            
            self.totalDataLength = self.dataLength_10 + self.dataLength_1
            if self.parsingSenq-7 == self.totalDataLength:
                self.parsingStep=3

            else:
                self.parsingStep = -1
                self.printverbos("totalLength err")

        if self.parsingStep == 3:
            self.controlByte = self.preParsingList[3]
            self.SUM_CRC = self.controlByte
            for i in range(self.totalDataLength):
                self.dataList.append(self.preParsingList[i+4])
                self.SUM_CRC += self.dataList[i]
            self.SUM_CRC += 0x01
            
            self.CAL_CRC_H = 0xff-(self.SUM_CRC >> 8)
            self.CAL_CRC_L = self.SUM_CRC & 0xff
            self.CRC_H = self.preParsingList[self.totalDataLength+4]
            self.CRC_L = self.preParsingList[self.totalDataLength+5]
            if(self.CAL_CRC_H == self.CRC_H) and (self.CAL_CRC_L == self.CRC_L):
                self.parsingStep =4

            else:
                self.parsingStep = -1
                self.printverbos("CRC err")

        if self.parsingStep == 4:
            self.idNum = 0
            self.idcnt = 0
            self.valueNum = 0
            self.debug = 1
            self.tempList = []
            for i in range(self.totalDataLength):
                if i%4 == 0:
                    self.idNum = self.dataList[i]
                    self.idList.append(self.idNum)
                    self.idcnt+=1
                    
                else:
                    self.tempList.append(self.dataList[i])
                    if len(self.tempList)>=3:
                        self.valueList.append(self.tempList)
                        self.valueNum+=1
                        self.valueNum%=3
                        self.tempList=[]


            self.reset()

        if self.parsingStep == -1:
            self.reset()
            self.debug=0

    def readData(self):
        try:
            if self.debug:
                print("-"*40)
                print("CMD : ", end='')
                print(hex(self.controlByte))
                for i in range(5):
                    print("ID : ", end='')
                    print(hex(self.idList[i]))
                    print("VALUE : ", end='')
                    for n in range(3):
                        print(int(chr(self.valueList[i][n])), end='')
                    print()
                self.debug=0
        except Exception as e:
            pass

    def contorol_motor(self, idList=[],angleList=[]):
        protocol_arry=[(STX)]
        id_len = len(idList)
        angle_len= len(angleList)*3
        data_len = id_len+angle_len
        length_H = ((data_len)// 10 + 0x30)
        length_L = ((data_len) % 10 + 0x30)
        protocol_arry.extend([length_H, length_L, (CONTROL_CMD)])
        CRC_SUM = CONTROL_CMD
        for id_num in range(len(idList)):
            place100 = angleList[id_num] // 100 + 48
            place10  = (angleList[id_num] - (angleList[id_num]//100) * 100) // 10 + 48
            place1   = angleList[id_num] % 10 + 48
            CRC_SUM += idList[id_num]
            CRC_SUM = CRC_SUM + place100 + place10 + place1
            place100=(place100)
            place10= (place10)
            place1= (place1)
            protocol_arry.append((idList[id_num]))    
            protocol_arry.extend([place100, place10, place1])


        CRC_SUM += 0x01
        CRC_SUM = bin(CRC_SUM)[2:]
        CRC_H = int(CRC_SUM,2) & 0xff00
        CRC_H = CRC_H>>8
        CRC_H = (0xff - CRC_H)
        CRC_L = (int(CRC_SUM,2) & 0x00ff)

        protocol_arry.extend([CRC_H, CRC_L, (ETX)])

        return protocol_arry  
    
    def request_info(self, idList=[]):
        protocol_arry=[(STX)]
        id_len = len(idList)
        data_len = id_len
        length_H = ((data_len)// 10 + 0x30)
        length_L = ((data_len) % 10 + 0x30)
        protocol_arry.extend([length_H, length_L, (REQUEST_CMD)])
        CRC_SUM = REQUEST_CMD
        for id_num in range(len(idList)):
            CRC_SUM += idList[id_num]
            CRC_SUM = CRC_SUM
            protocol_arry.append((idList[id_num]))    

        CRC_SUM += 0x01
        CRC_SUM = bin(CRC_SUM)[2:]
        CRC_H = int(CRC_SUM,2) & 0xff00
        CRC_H = CRC_H>>8
        CRC_H = (0xff - CRC_H)
        CRC_L = (int(CRC_SUM,2) & 0x00ff)

        protocol_arry.extend([CRC_H, CRC_L, (ETX)])

        return protocol_arry  
    
    def makepacket(self, cmd=CONTROL_CMD, idList=[],angleList=None):
        protocol_arry=[(STX)]
        id_len = len(idList)
        if angleList==None:
            angleList=[]
            for i in range(id_len):
                angleList.append(0)
        angle_len= len(angleList)*3
        data_len = id_len+angle_len
        length_H = ((data_len)// 10 + 0x30)
        length_L = ((data_len) % 10 + 0x30)
        protocol_arry.extend([length_H, length_L, cmd])
        CRC_SUM = cmd
        for id_num in range(len(idList)):
            place100 = angleList[id_num] // 100 + 48
            place10  = (angleList[id_num] - (angleList[id_num]//100) * 100) // 10 + 48
            place1   = angleList[id_num] % 10 + 48
            CRC_SUM += idList[id_num]
            CRC_SUM = CRC_SUM + place100 + place10 + place1
            place100=(place100)
            place10= (place10)
            place1= (place1)
            protocol_arry.append((idList[id_num]))    
            protocol_arry.extend([place100, place10, place1])


        CRC_SUM += 0x01
        CRC_SUM = bin(CRC_SUM)[2:]
        CRC_H = int(CRC_SUM,2) & 0xff00
        CRC_H = CRC_H>>8
        CRC_H = (0xff - CRC_H)
        CRC_L = (int(CRC_SUM,2) & 0x00ff)

        protocol_arry.extend([CRC_H, CRC_L, (ETX)])

        return protocol_arry  

    def packetfilter(self,datalist):
        temp_list = datalist
        temp_list[:] = (value for value in temp_list if value != 0)
        return temp_list
    
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

