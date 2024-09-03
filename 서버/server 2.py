import socket, time, os
import threading 
import sys
import random
import json
import struct
import pickle
import cv2

#테스트용 각도 순환
keyvalue=['1', '2', '3', '4', '5', '6']
angle= 0

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
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_HOST, SERVER_PORT))
print("HOST IP : ", host_ip)



class SocketServer():
    def __init__(self):
        # 서버 구동에 필요한 정보 세팅
        self._host = SERVER_HOST
        self._port = SERVER_PORT
        self._data = data
        self._angle = angle
        self._prestate = data
        self.ai_result={}
        self._sendtime = ""
        self.client_socket =None
        self.lpf = []
        
        self.run_server()
   
        while(1):
            pass

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
        server_socket.listen()#<- 

        # 무한루프
        # 클라이언트 접속 대기
        self.client_socket, client_address = server_socket.accept()
        serverthread = threading.Thread(target= self._handle_client, args=(self.client_socket,))
        serverthread.daemon = True
        serverthread.start()
            # player_ip=client_address[1]
            
            # player_ip=client_address[0].split(".")[3]
    

        # 실패
    
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
                send_value = contorol_motor(list(self._data.keys()), list(self._data.values()))
                send_value = [send_value, self._sendtime]
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

    def clientRead(self, client_socket):
        BUFF_SIZE= 64
        delay_data_queue = deque(maxlen=1000)

        # 최대값을 추적할 우선순위 큐
        max_heap = []

        print("soket id : ", client_socket)
        while(1):
            try:
                client_data = client_socket.recv(1024)
                decodedData = float(client_data.decode())
                delay = (time.time() - decodedData)/2

                delay_data_queue.append(delay)  # 데이터 큐에 추가

                # 최소값, 최대값 추적을 위해 데이터를 우선순위 큐에 추가
                heapq.heappush(max_heap, delay)
                while len(max_heap) > 5:
                    heapq.heappop(max_heap)

                if len(delay_data_queue) % 100==0:
                    print(len(delay_data_queue))

                if len(delay_data_queue) == 1000:
                    # 최근 1000개의 데이터를 모두 수집한 경우
                    average_delay = sum(delay_data_queue) / 1000
                    max_delay = max(delay_data_queue)
                    min_delay = min(delay_data_queue)
                    print('='*40)
                    print("delay 데이터 1000개의 평균 : ", average_delay)
                    print("delay 데이터 1000개중 최대 : ", max_delay)
                    print("delay 데이터 1000개중 최소 : ", min_delay)
                    
                    print("최대값 5개:", [-x for x in max_heap])
            except Exception as e:
                print("err code : ", e)
                pass

        
    def _close_client(self, client_socket):
        client_socket.close()
        # 자식 프로세스 종료
        # os.exit(0)

if __name__ == "__main__":
    server = SocketServer()



    # cap = cv2.VideoCapture(0)
    # Initiate holistic model
    # with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        
    #     while cap.isOpened():
    #         ret, frame = cap.read()
            
    #         # Recolor Feed
    #         image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    #         # Make Detections
    #         results = holistic.process(image)
    #         # print(results.face_landmarks)
            
    #         # face_landmarks, pose_landmarks, left_hand_landmarks, right_hand_landmarks
            
    #         # Recolor image back to BGR for rendering
    #         image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
    #         if results.pose_landmarks is not None:
    #             joint = np.zeros((33,4))
    #             for j, lm in enumerate(results.pose_landmarks.landmark):
    #                     joint[j] = [lm.x, lm.y, lm.z, lm.visibility]

    #             #z축을 사용하여 각도를 뽑아내는 것으로 추정
    #             v1 = joint[[12,13,13,13,14,14],:] # Parent joint
    #             v2 = joint[[11,11,11,15,12,16],:] # Child joint
    #             v = v2 - v1

    #             #3,4번 제거
    #             v[:, 2] = 0
    #             v = np.delete(v, 3, axis=1)
    #             #print(v)

    #             v = v / np.linalg.norm(v, axis=1)[:, np.newaxis]

                

    #             angle = np.arccos(np.einsum('nt,nt->n',
    #                     v[[0,1,2,3,4],:], 
    #                     v[[1,2,3,4,5],:])) # [15,]
                
    #             angle = np.degrees(angle) # Convert radian to degree"""
    #             #print(results.pose_landmarks)

    #             cv2.putText(image, text=str(round(angle[0],1)), org=(int(results.pose_landmarks.landmark[11].x * image.shape[1]), int(results.pose_landmarks.landmark[11].y * image.shape[0] + 20)), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(0, 0, 255), thickness=2)
    #             cv2.putText(image, text=str(round(angle[2],1)), org=(int(results.pose_landmarks.landmark[13].x * image.shape[1]), int(results.pose_landmarks.landmark[13].y * image.shape[0] + 20)), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(0, 0, 255), thickness=2)
    #             cv2.putText(image, text=str(round(angle[4],1)), org=(int(results.pose_landmarks.landmark[25].x * image.shape[1]), int(results.pose_landmarks.landmark[25].y * image.shape[0] + 20)), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(0, 0, 255), thickness=2)
            
    #             #정해진 딕셔너리 형식의 데이터로 데이터 보내기(나중에 클래스로 만들수도 있음)
    #             data = {'cmd_type':0xC0,'1': int(angle[0]),'2': int(angle[0]),'3': int(angle[2]),'4': int(angle[2]),'5': int(angle[4]),'6': int(angle[4])}
    #             #ser.write(protocol.sendProtocol(sendData))

    #         # 2. Right hand
    #         """
    #         mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS, 
    #                                 mp_drawing.DrawingSpec(color=(80,22,10), thickness=2, circle_radius=4),
    #                                 mp_drawing.DrawingSpec(color=(80,44,121), thickness=2, circle_radius=2)
    #                                 )
    #         """

    #         # 3. Left Hand
    #         """
    #         mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS, 
    #                                 mp_drawing.DrawingSpec(color=(121,22,76), thickness=2, circle_radius=4),
    #                                 mp_drawing.DrawingSpec(color=(121,44,250), thickness=2, circle_radius=2)
    #                                 )
    #         """

    #         # 4. Pose Detections
    #         mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS, 
    #                                 mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=4),
    #                                 mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)
    #                                 )
                            
            
    #         cv2.imshow('Raw Webcam Feed', image)

    #         if cv2.waitKey(10) & 0xFF == ord('q'):
    #             break

    # cap.release()
    # cv2.destroyAllWindows()
        
