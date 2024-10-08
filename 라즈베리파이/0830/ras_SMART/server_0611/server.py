import socket, time, serial, select
import os, threading
import re
from _thread import *
import pickle
from protocol import *
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
        self.SMART = smart()
        print('Server Start')

        self.dynamixellSerial = serial.Serial(port = '/dev/ttyAMA0', baudrate= 115200)
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
            
            if player_ip == 3:
                print("robot connected : ", player_ip)
                self.robotclient = self.client_socket
                serverthread = threading.Thread(target= self._handle_robot, args=(self.robotclient,))
                serverthread.daemon = True
                serverthread.start()

            elif player_ip == 100: 
                print("Controller connected : ", player_ip)
                self.controllerclient = self.client_socket
                # self.controllerclient.setblocking(0)
                # self.controllerclient.timeout(10)
                controllor_thread = threading.Thread(target= self._handle_controller, args=(self.controllerclient,))
                controllor_thread.daemon = True
                controllor_thread.start()

        # 실패
    def _handle_controller(self, client_socket):
            while True:
                try:
                    BUFF_SIZE = 1024
                    LIMIT_TIME = 10
                    # read_ready, _, _ = select.select([client_socket], [], [], 1)
                    # if client_socket in read_ready:
                    #     buf=[]
                    #     try:
                    #         data = client_socket.recv(1024)
                    #         print(data, end='')
                    #         # buf.append(data)
                    #     except socket.error as e:
                    #         print(e)
                    client_data = client_socket.recv(BUFF_SIZE)
                    client_data= client_data.decode()
                    parsingdata = client_data.split(',')
                    parsingdata= list(filter(None, parsingdata))
                    parsingdata=list(map(int, parsingdata))
                    parsingdata=list(map(hex, parsingdata))
                    print("read: ", parsingdata)
                    # self.SMART.packet_parsing(parsingdata)
                    # if time.time()-self.prevTime>=0.1:
                    # self.lock.acquire()
                    # self.dynamixellSerial.write(bytes(self.sendvalue))
                    # self.lock.release()
                    # self.prevTime = time.time()
                    time.sleep(0.1)

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
                # client_socket.sendall(dumped_data)

                time.sleep(0.1)

            except socket.timeout as err:
                print('self.self.client_socket Timeout Error')
                
                # 추가적인 예외처리 로직 구성...
                self._close_client(client_socket)
                break
            except socket.error as err:
                self._close_client(client_socket)
                break

    def _read_dynamix(self):
        while(1):
            readvalue=self.dynamixellSerial.readline()
            print("recv from serial : ", readvalue)

    def _close_client(self, client_socket):
        client_socket.close()

if __name__ == "__main__":
    server = SocketServer()





    # def testing(self):
    #     while True:
    #         try:
    #             data = client_socket.recv(1024)
    #             # temp0 = data.decode()
    #             # temp1=temp0.replace('[','')
    #             # client_data=list(temp1.replace(']',''))
    #             self.value=pickle.loads(data)
    #             self.sendvalue= bytes(self.value[0])
    #             self.times = self.value[1]
    #             self.lock.acquire()
    #             self.dynamixellSerial.write(bytes(self.sendvalue))
    #             self.lock.release()
    #             # sendtime = str(self.times)
    #             # print(sendtime)
    #             # client_socket.sendall(sendtime.encode())
    #         except Exception as e:
    #             print(e)
                                                                                     