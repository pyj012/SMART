import socket, time, os
import threading 
import sys
import random
import json
import struct
import pickle

prevSendTime = time.time()

STX = 0x02
ETX = 0x03

CMD_CONTROL = 0xC0

CRC = 0
CRC_H = 0x00
CRC_L = 0x00

def contorol_motor(idList=[],angleList=[]):
    protocol_arry=[STX]
    id_len = len(idList)
    angle_len= len(angleList)*3
    data_len = id_len+angle_len
    length_H = (data_len)// 10 + 48
    length_L = (data_len) % 10 + 48
    protocol_arry.extend([length_H, length_L, CMD_CONTROL])
    CRC_SUM = CMD_CONTROL
    for id_num in range(len(idList)):
        place100 = angleList[id_num] // 100 + 48
        place10  = (angleList[id_num] - (angleList[id_num]//100) * 100) // 10 + 48
        place1   = angleList[id_num] % 10 + 48
        protocol_arry.append(idList[id_num]+48)    
        protocol_arry.extend([place100, place10, place1])
        CRC_SUM += idList[id_num] + 48
        CRC_SUM = CRC_SUM + place100 + place10 + place1

    CRC_SUM += 0x01
    CRC_SUM = bin(CRC_SUM)[2:]
    CRC_H = int(CRC_SUM,2) & 0xff00
    CRC_H = CRC_H>>8
    CRC_H = 0xff - CRC_H
    CRC_L = int(CRC_SUM,2) & 0x00ff

    protocol_arry.extend([CRC_H, CRC_L, ETX])

    return protocol_arry


SERVER_HOST = "192.168.20.3"
SERVER_PORT = 5051

class SocketServer():
    def __init__(self):
        # 서버 구동에 필요한 정보 세팅
        self._host = SERVER_HOST
        self._port = SERVER_PORT
        self.ai_result={}
        self._sendtime = ""
        self.client_socket =socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((SERVER_HOST, SERVER_PORT))

        self.run_server()
   
        while(1):
            pass

    def run_server(self):
        # 소켓 객체 생성
        # AF_INET : IP와 PORT를 통한 연결(TCP)
        # 무한루프
        # 클라이언트 접속 대기
        serverthread = threading.Thread(target= self._handle_client, args=(self.client_socket,))
        serverthread.daemon = True
        serverthread.start()
   
    def _handle_client(self, client_socket):
        # 데이터 처리 객체 생성
        # 멀티 프로세스 기반으로 복수의 클라이언트가 접속하기 때문에
        # 데이터의 무결성 유지 및 비즈니스 로직 수행 시 충돌을 막기 위하여
        # 메소드 호출시마다 객체 생성
        step = 0
        flag=True
        while True:
            try:
                BUFF_SIZE = 1024
                LIMIT_TIME = 10
                # send_value = sendProtocol(self.ai_result)
                send_value = contorol_motor([0x31], [100])
                print(send_value)
                send_value = [send_value, 1]
                dumped_data= pickle.dumps(send_value)
                client_socket.sendall(dumped_data)

                time.sleep(0.1)

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
        # 자식 프로세스 종료
        # os.exit(0)

if __name__ == "__main__":
    server = SocketServer()

