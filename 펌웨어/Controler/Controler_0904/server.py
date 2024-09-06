import socket, time, os
import threading 
import sys
import socket

lock = threading.Lock()
SERVER_HOST = "192.168.0.171"
SERVER_PORT = 5051


class SocketServer():
    def __init__(self):
        # 서버 구동에 필요한 정보 세팅
        self._host = SERVER_HOST
        self._port = SERVER_PORT
        self.run_server()

    def run_server(self):
        # 소켓 객체 생성
        # AF_INET : IP와 PORT를 통한 연결(TCP)
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # 소켓 연결 정보 세팅
        server_address = (self._host, self._port)
        print('Strat up on {} port {}'.format(*server_address))
        # 소켓 연결 정보 바인딩
        server_socket.bind(server_address)
        # 가동
        server_socket.listen()

        # 무한루프
        while True:
            # 클라이언트 접속 대기
            client_socket, client_address = server_socket.accept()
            # player_ip=client_address[1]
            print(client_address)
            # 클라이언트 접속 시 멀티 프로세스를 위한 fork() 수행
            # fork() 리턴 : 0 = 자식, -1 = 실패, 0 이상 = 부모 프로세스
            pid = os.fork()
            # 자식 프로세스
            if pid == 0:
                # 데이터 수령 및 전달 메소드 호출
                self._handle_client(client_socket)
            
            # 실패
            elif pid == -1:
                print('Child process fail')
                # 필요시 추가적인 예외처리 로직 구현....
                
                # 클라이언트 소켓 종료
                client_socket.close()
                    
            # 부모프로세스
            else:
                time.sleep(1)
                # 자식 프로세스에 client_socket 접속 할당 후 부모프로세스에서 종료
                client_socket.close()
    
    
    def _handle_client(self, client_socket):
        # 데이터 처리 객체 생성
        # 멀티 프로세스 기반으로 복수의 클라이언트가 접속하기 때문에
        # 데이터의 무결성 유지 및 비즈니스 로직 수행 시 충돌을 막기 위하여
        # 메소드 호출시마다 객체 생성
        while True:
            try:
                BUFF_SIZE = 1024
                # LIMIT_TIME = 10
                # 타임아웃 지정
                # client_socket.settimeout(LIMIT_TIME)
                # 데이터 수령(버퍼 크기 지정)
                clientRead = client_socket.recv(BUFF_SIZE)
                # 데이터가 없을 경우 예외 처리
                try:
                    if not clientRead:
                        pass
                except Exception as e:
                    print("client RecvERR : ", e)
                    self._close_client(client_socket)
                    break
                clientData = clientRead.decode()
                # print("Read :",  clientData)
                parsingdata = clientData.split(',')
                parsingdata= list(filter(None, parsingdata))
                parsingdata=list(map(int, parsingdata))
                parsingdata=list(map(hex, parsingdata))
                print("read: ", parsingdata)
                # for i in clientData:
                #     print(i, end='')
             
                # try:
                #     client_socket.sendall("A00B\n".encode())
                # except Exception  as e:
                #     print("client sendERR : ",player_ip, e)
                #     self._close_client(client_socket, player_ip)
                #     break

            except socket.timeout as err:
                print('client_socket Timeout Error')
                # 추가적인 예외처리 로직 구성....
                self._close_client(client_socket)
                break

            except socket.error as err:
                print(err)
                self._close_client(client_socket)
                break


    def _close_client(self, client_socket):
        # 소켓 연결 종료
        client_socket.close()
        # 자식 프로세스 종료
        # os.exit(0)

if __name__ == "__main__":
    server = SocketServer()
    
