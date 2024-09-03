import socket, time,  select
import os, threading
import re
from _thread import *
import pickle
from protocol import *
from multiprocessing import Process, Queue
from customserial import *
SERVER_HOST = "192.168.20.3" ## server에 출력되는 ip를 입력해주세요 ##
SERVER_PORT = 5051

class SocketServer():
    def __init__(self):
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
        self.SMART = smartprotocol()
        print('Server Start')
        self.dynamixellSerial = customserial()
        self.dynamixellSerial_process= Process(target= self.dynamixellSerial._start(), args=())
        self.dynamixellSerial_process.start()
        self.dynamixellSerial_process.join()
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
            self.client_socket, client_address = self.server_socket.accept()
            player_ip=int(client_address[0].split(".")[3])
            
            if player_ip == 100: 
                print("Controller connected : ", player_ip)
                self.controllerclient = self.client_socket
                controllor_thread = threading.Thread(target= self._handle_controller, args=(self.controllerclient,))
                controllor_thread.daemon = True
                controllor_thread.start()

            # elif player_ip == 3:
            #     print("robot connected : ", player_ip)
            #     self.robotclient = self.client_socket
            #     serverthread = threading.Thread(target= self._handle_robot, args=(self.robotclient,))
            #     serverthread.daemon = True
            #     serverthread.start()
            else:
                print("robot connected : ", player_ip)
                self.robotclient = self.client_socket
                serverthread = threading.Thread(target= self._handle_robot, args=(self.robotclient,))
                serverthread.daemon = True
                serverthread.start()

    def _handle_controller(self, client_socket):
            while True:
                try:
                    BUFF_SIZE = 1024
                    LIMIT_TIME = 10
                    client_data = client_socket.recv(1)
                    data = int.from_bytes(client_data,'big')
                    self.SMART.parsingprotocol(data)
                    if self.SMART.debug :
                        idlist= self.SMART.packetfilter(self.SMART.idList)
                        vallist=[]
                        for i in range(10):
                            temp_list= self.SMART.valueList[i]
                            result = self.SMART.packetfilter(temp_list)
                            if len(result) >0:
                                d100=int(chr(result[0]))*100
                                d10=int(chr(result[1]))*10
                                d1=int(chr(result[2]))
                                value = d100 + d10 + d1
                                vallist.append(value)
                        self.SMART.debug=0
                        sendValue = (self.SMART.contorol_motor(idlist,vallist))
                        # print("controler",sendValue,"BYTE : ", bytes(sendValue) )
                        if time.time()-self.prevTime>=0.01:
                            self.prevTime = time.time()
                            self.dynamixellSerial._send(sendValue)

                    # self.SMART.readData()

                    time.sleep(0.001)

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
        while True:
            try:
                BUFF_SIZE = 1024
                LIMIT_TIME = 10

                data = client_socket.recv(1024)
                # temp0 = data.decode()
                # temp1=temp0.replace('[','')
                # client_data=list(temp1.replace(']',''))
                value=pickle.loads(data)
                sendvalue= bytes(value[0])
                print("robot", sendvalue)
                self.dynamixellSerial._send(bytes(self.sendvalue))

            except socket.timeout as err:
                print('self.self.client_socket Timeout Error')
                
                # 추가적인 예외처리 로직 구성...
                self._close_client(client_socket)
                break
            except socket.error as err:
                self._close_client(client_socket)
                break

    def _read_dynamix(self):
        print('RAED START')
        while(1):
            readvalue=self.dynamixellSerial.readline()
            print("recv from serial : ", readvalue)

    def _send_dynamix(self):
        while(1):
            self.dynamixellSerial.write("HELLO".encode())

    def _close_client(self, client_socket):
        client_socket.close()

if __name__ == "__main__":
    server = SocketServer()