import os
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
os.add_dll_directory('C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v11.8/bin')
os.add_dll_directory('C:/opencv/build/install/x64/vc16/bin')
os.add_dll_directory('C:/opencv/build/bin')


import mediapipe as mp
from utils_V3 import DLT, get_projection_matrix, calculate_3d
from ValueControlFilter import ValueControlFilter

import socket, time, json, math
import threading 
import sys
import random
import struct
import pickle
import numpy as np
from collections import deque
import heapq
from definse import *
import cv2 as cv


#사용할 키포인트
pose_keypoints = [19, 20, 16, 14, 12, 11, 13, 15, 24, 23, 25, 26, 27, 28]

#그리퍼 값
GRAP_VAL = 70
DROP_VAL = 20

#인식 전 초기값
data = {0x31:0, 0x32:0, 0x33:0, 0x34:0, 0x36:DROP_VAL}

prevSendTime = time.time()

lock = threading.Lock()
SERVER_HOST = "192.168.0.250"
CLIENT_PORT = 5050
CAMERA_PORT = 5053

class SocketServer():
    def __init__(self, port, sendQ1, sendQ2 = None, sendQ3 = None):
        # 서버 구동에 필요한 정보 세팅
        self._host = SERVER_HOST
        self._port = port
        self.sendQ1 = sendQ1
        self.sendQ2 = sendQ2   
        self.sendQ3 = sendQ3
        self.mod = 0
        self.once = 1 
        self.disconnect_flag = 1
        self.connected = False  # 초기 연결 상태
        self._data = 0
        self._prestate = 0
        self._sendtime = ""
        self.pre_arm_angle = [0,0,0,0,0,0,0,0]
        self.ai_result={}
        self._sendtime = ""
        self.img_dict={}
        self.send_time = 0
        self.decoded_img={}
        self.cameraClient = None
        self.vcf = dict()
        self.client_socket = None
        self.fps = 1/30
        self.prevTime =0
        self.ledindex = 0
        self.retry_connect_server=0
        self.server_flag=0
        if self._port == CLIENT_PORT:

            self.client_socket =socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY,1)
            # self.client_socket.connect((SERVER_HOST, self._port))
            self.client_socket.setblocking(False)
            
            # 필터 : 일단 개별 각도의 변동이 작은경우, 큰 경우 무시하는걸로 만들었는데 끝점 좌표가 많이 변하면 제한하는 방식이 나을지도?
            self.vcf = dict()
            self.vcf[1] = ValueControlFilter(prev_data = 0, dev = 10, dev_Limit= 50, limit_low = -30, limit_high = 110)
            self.vcf[2] = ValueControlFilter(prev_data = 0, dev = 10, dev_Limit= 50, limit_low = 0, limit_high = 120)
            self.vcf[3] = ValueControlFilter(prev_data = 0, dev = 5, limit_low = 0, limit_high = 120)
            self.vcf[4] = ValueControlFilter(prev_data = 0, dev = 10, limit_low = 0, limit_high = 110)
            # self.lpf[6] = LowPassFilter(cut_off_freqency= 0.5, ts= 0.1)
            
            self.vcf[7] = ValueControlFilter(prev_data = 0, dev = 10, dev_Limit= 50, limit_low = -30, limit_high = 110)
            self.vcf[8] = ValueControlFilter(prev_data = 0, dev = 10, dev_Limit= 50, limit_low = 0, limit_high = 120)
            self.vcf[9] = ValueControlFilter(prev_data = 0, dev = 5, limit_low = 0, limit_high = 120)
            self.vcf[10] = ValueControlFilter(prev_data = 0, dev = 30, limit_low = 0, limit_high = 110)
            # self.lpf[12] = LowPassFilter(cut_off_freqency= 0.5, ts= 0.1)

            #미디어파이프 카메라 초기 세팅
            input_stream0 = 1#'media/cam0_test_half_speed.mp4'
            input_stream1 = 3#'media/cam1_test_half_speed.mp4'
            input_stream2 = 2
            
            # 테스트용
            input_stream0 = 0
            input_stream1 = 1
            input_stream2 = 2

            P0 = get_projection_matrix(10)
            P1_L = get_projection_matrix(11)
            P1_R = get_projection_matrix(12)
            # 추가
            P2 = get_projection_matrix(13)
            
            self.run_mp(input_stream0, input_stream1, input_stream2, P0, P1_L, P1_R, P2)
                

        elif self._port == CAMERA_PORT:
            while True:
                try:
                    # for index in self.img_dict:
                    #     # print(type(self.img_dict[index]), self.img_dict[index])
                    #     img = np.ndarray(self.img_dict[index])
                    #     if img is not None:
                    #         cv2.imshow(str(index), img)
                    if time.time() - self.prevTime >= self.fps:
                        self.prevTime = time.time()
                        cameraClient =socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        cameraClient.connect((SERVER_HOST,  self._port))
                        
                        length = self.recvall(cameraClient, 16)
                        temp = self.recvall(cameraClient, int(length))
                        decoded_temp = temp.decode("utf-8")
                        data_dict = eval(decoded_temp)

                        for index in data_dict:
                            if index == 'l':
                                self.ledindex = data_dict[index]
                            else:
                                data = np.frombuffer(data_dict[index], dtype='uint8')
                                self.decoded_img[index]= cv.imdecode(data,1)

                        self.sendQ1.put([self.decoded_img, self.ledindex])
                        cameraClient.close()
                    # for index in self.decoded_img:
                    #     if self.decoded_img[index] is not None:
                    #         cv.imshow(str(index), self.decoded_img[index])

                    # key = cv.waitKey(1)

                    # if key == 27:
                    #     break
                    # cameraClient.close()

                except Exception as e:
                    pass
                    

            # cv.destroyAllWindows()
    def recvall(self, sock, count):
        try:
            buf = b''
            newbuf=None
            while count:
                newbuf = sock.recv(count)
                if not newbuf: return None
                buf += newbuf
                count -= len(newbuf)   
            return buf
        
        except Exception as e:
            pass
    def connect_to_server(self):
        """서버에 연결을 시도하는 함수"""
        print("try to connect serber~~")
        
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((SERVER_HOST, CLIENT_PORT))
            print("Connected to server.")
            self.connected = True

        except socket.error as err:
            print(f"Connection error: {err}")
            self.client_socket.close()
        # else:
        #     self.disconnect_from_server()

    def disconnect_from_server(self):
        """서버 연결을 해제하는 함수"""
        if self.connected:
            self.client_socket.close()
            print("Disconnected from server.")
            self.connected = False
    
    def run_mp(self, input_stream0, input_stream1, input_stream2, P0, P1_L, P1_R, P2):
        mp_pose = mp.solutions.pose
        modlist = ["실시간 제어", "동작1", "동작2", "동작3"]
        # mp_drawing = mp.solutions.drawing_utils
        # mp_drawing_styles = mp.solutions.drawing_styles
        # frame_shape = [720, 1280]


        

        # cam0 = cv.VideoCapture(input_stream0)
        # cam1 = cv.VideoCapture(input_stream1)
        # cam2 = cv.VideoCapture(input_stream2)
        cam0 = cv.VideoCapture(0)
        cam1 = cam0
        cam2 = cam0
        cams = [cam0, cam1, cam2]

        action1_0 = cv.VideoCapture('recode/1/cut2x2.mp4')
        action1_1 = cv.VideoCapture('recode/1/cut3x2.mp4')
        action1_2 = cv.VideoCapture('recode/1/cut1x2.mp4')

        # action1_0 = cv.VideoCapture('recode/front/recorded_video2.avi')
        # action1_1 = cv.VideoCapture('recode/front/recorded_video3.avi')
        # action1_2 = cv.VideoCapture('recode/front/recorded_video1.avi')
        action1 = [action1_0, action1_1, action1_2]

        action2_0 = cv.VideoCapture('recode/2/cut2x2.mp4')
        action2_1 = cv.VideoCapture('recode/2/cut3x2.mp4')
        action2_2 = cv.VideoCapture('recode/2/cut1x2.mp4')
        action2 = [action2_0, action2_1, action2_2]

        action3_0 = cv.VideoCapture('recode/3/cut2x2.mp4')
        action3_1 = cv.VideoCapture('recode/3/cut3x2.mp4')
        action3_2 = cv.VideoCapture('recode/3/cut1x2.mp4')
        action3 = [action3_0, action3_1, action3_2]

        caps = cams + action1 + action2 + action3

        # cap0.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
        # cap0.set(cv.CAP_PROP_FRAME_HEIGHT, 720)

        # cap1.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
        # cap1.set(cv.CAP_PROP_FRAME_HEIGHT, 720)

        # for cap in caps:
        #     cap.set(3, frame_shape[1])
        #     cap.set(4, frame_shape[0])

        pose0 = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        pose1 = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        pose2 = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

        # 여기에 인덱스 큐 읽는거 추가

        seq = []
        action_seq = [] 
        fps = 1/60
        prev_time = 0 
        while True:
            if time.time() - prev_time >= fps:
                prev_time = time.time()

                if self.sendQ3.qsize()>0:
                    print("MOD CHANGED")
                    self.mod = self.sendQ3.get()
                    if self.mod == 0:
                        cap0 = cam0
                        cap1 = cam1
                        cap2 = cam2
                    elif self.mod == 1:
                        cap0 = action1_0
                        cap1 = action1_1
                        cap2 = action1_2
                    elif self.mod == 2:
                        cap0 = action2_0
                        cap1 = action2_1
                        cap2 = action2_2
                    elif self.mod == 3:
                        cap0 = action3_0
                        cap1 = action3_1
                        cap2 = action3_2
                    
                    '''안되면 말기'''
                    #  try :
                    #     cap0.set(cv.CAP_PROP_POS_FRAMES, 0)                    
                    #     cap1.set(cv.CAP_PROP_POS_FRAMES, 0)                    
                    #     cap2.set(cv.CAP_PROP_POS_FRAMES, 0)
                    # except:
                    #     pass
                    
                    '''무한시도'''
                    # while True:
                    #     if cap0.set(cv.CAP_PROP_POS_FRAMES, 0) and cap1.set(cv.CAP_PROP_POS_FRAMES, 0) and cap2.set(cv.CAP_PROP_POS_FRAMES, 0):
                    #         break

                    '''적당히 시도'''
                    # for i in range(3):
                    #     if cap0.set(cv.CAP_PROP_POS_FRAMES, 0):
                    #         break
                    # for i in range(3):
                    #     if cap1.set(cv.CAP_PROP_POS_FRAMES, 0):
                    #         break
                    # for i in range(3):
                    #     if cap2.set(cv.CAP_PROP_POS_FRAMES, 0):
                    #         break
                    
                    while True:
                        if cap0.set(cv.CAP_PROP_POS_FRAMES, 0) and cap1.set(cv.CAP_PROP_POS_FRAMES, 0) and cap2.set(cv.CAP_PROP_POS_FRAMES, 0):
                            break
                    continue
                    

                ret0, frame0 = cap0.read()
                ret1, frame1 = cap1.read()
                ret2, frame2 = cap2.read()
                if not ret0 or not ret1 or not ret2:
                    print("카메라 에러")
                    while True:
                        if cap0.set(cv.CAP_PROP_POS_FRAMES, 0) and cap1.set(cv.CAP_PROP_POS_FRAMES, 0) and cap2.set(cv.CAP_PROP_POS_FRAMES, 0):
                            break
                    continue

                # if frame0.shape[1] != 720:
                #     frame0 = frame0[:, frame_shape[1] // 2 - frame_shape[0] // 2:frame_shape[1] // 2 + frame_shape[0] // 2]
                #     frame1 = frame1[:, frame_shape[1] // 2 - frame_shape[0] // 2:frame_shape[1] // 2 + frame_shape[0] // 2]

                frame0 = cv.cvtColor(frame0, cv.COLOR_BGR2RGB)
                frame1 = cv.cvtColor(frame1, cv.COLOR_BGR2RGB)
                frame2 = cv.cvtColor(frame2, cv.COLOR_BGR2RGB)

                frame0.flags.writeable = False
                frame1.flags.writeable = False
                frame2.flags.writeable = False
                results0 = pose0.process(frame0)
                results1 = pose1.process(frame1)
                results2 = pose2.process(frame2)


                frame0.flags.writeable = True
                frame1.flags.writeable = True
                frame2.flags.writeable = True
                frame0 = cv.cvtColor(frame0, cv.COLOR_RGB2BGR)
                frame1 = cv.cvtColor(frame1, cv.COLOR_RGB2BGR)
                frame2 = cv.cvtColor(frame2, cv.COLOR_RGB2BGR)

                '''프로그램 속도 상승을 위한 프레임 스킵 기능'''
                # frame+=1
                # if frame%2 == 0:
                #     pass
                
                #캠1
                frame0_keypoints = []
                if results0.pose_landmarks:
                    for i, landmark in enumerate(results0.pose_landmarks.landmark):
                        if i not in pose_keypoints:
                            continue
                        pxl_x = landmark.x * frame0.shape[1]
                        pxl_y = landmark.y * frame0.shape[0]
                        pxl_x = int(round(pxl_x))
                        pxl_y = int(round(pxl_y))
                        cv.circle(frame0, (pxl_x, pxl_y), 3, (0, 0, 255), -1)
                        kpts = [pxl_x, pxl_y]
                        frame0_keypoints.append(kpts)
                else:
                    frame0_keypoints = [[-1, -1]] * len(pose_keypoints)

                #캠2
                frame1_keypoints = []
                if results1.pose_landmarks:
                    for i, landmark in enumerate(results1.pose_landmarks.landmark):
                        if i not in pose_keypoints:
                            continue
                        pxl_x = landmark.x * frame1.shape[1]
                        pxl_y = landmark.y * frame1.shape[0]
                        pxl_x = int(round(pxl_x))
                        pxl_y = int(round(pxl_y))
                        cv.circle(frame1, (pxl_x, pxl_y), 3, (0, 0, 255), -1)
                        kpts = [pxl_x, pxl_y]
                        frame1_keypoints.append(kpts)
                else:
                    frame1_keypoints = [[-1, -1]] * len(pose_keypoints)

                #캠3
                frame2_keypoints = []
                if results2.pose_landmarks:
                    for i, landmark in enumerate(results2.pose_landmarks.landmark):
                        if i not in pose_keypoints:
                            continue
                        pxl_x = landmark.x * frame1.shape[1]
                        pxl_y = landmark.y * frame1.shape[0]
                        pxl_x = int(round(pxl_x))
                        pxl_y = int(round(pxl_y))
                        cv.circle(frame2, (pxl_x, pxl_y), 3, (0, 0, 255), -1)
                        kpts = [pxl_x, pxl_y]
                        frame2_keypoints.append(kpts)
                else:
                    frame2_keypoints = [[-1, -1]] * len(pose_keypoints)


                frame_p3ds_12 = []
                for uv1, uv2 in zip(frame1_keypoints, frame2_keypoints):
                    if uv1[0] == -1 or uv2[0] == -1:
                        _p3d = [-1, -1, -1]
                    else:
                        _p3d = DLT(P1_R, P2, uv1, uv2)
                    frame_p3ds_12.append(_p3d)

                frame_p3ds_12 = np.array(frame_p3ds_12).reshape((14, 3))


                frame_p3ds_10 = []
                for uv1, uv2 in zip(frame1_keypoints, frame0_keypoints):
                    if uv1[0] == -1 or uv2[0] == -1:
                        _p3d = [-1, -1, -1]
                    else:
                        _p3d = DLT(P1_L, P0, uv1, uv2)
                    frame_p3ds_10.append(_p3d)

                frame_p3ds_10 = np.array(frame_p3ds_10).reshape((14, 3))
                

                # 오른쪽 각도 계산 시도
                try:
                    arm_angle12 = calculate_3d(frame_p3ds_12)
                    arm_angle10 = calculate_3d(frame_p3ds_10)
                    arm_angle = arm_angle12[:4] + arm_angle10[4:]
                    # print(arm_angle)
                    if any(math.isnan(i) for i in arm_angle):
                        arm_angle = self.pre_arm_angle
                    else:
                        self.pre_arm_angle = arm_angle
                    self.pre_arm_angle = arm_angle
                except Exception as e:
                    print(e)
                    arm_angle = self.pre_arm_angle

                # sendValue ={0x31:arm_angle[0],0x32:arm_angle[1],0x33:arm_angle[2],0x34:arm_angle[3],0x35:0,0x36:0,0x37:arm_angle[4],0x38:arm_angle[5],0x39:arm_angle[6],0x3A:arm_angle[7],0x3B:0,0x3C:0}
                # sendValue ={1:arm_angle[0],2:arm_angle[1],3:arm_angle[2],4:arm_angle[3],5:0,6:0,7:arm_angle[4],8:arm_angle[5],9:arm_angle[6],10:arm_angle[7],11:0,12:0}
                # Draw angles on frame
                nameTag = ['R_shoulder','R_shoulder','R_elbow','R_wrist','L_shoulder','L_shoulder','L_elbow','L_wrist']
                # Draw angles on frame
                # for i, (name, angle) in enumerate(zip(nameTag,arm_angle)):
                #     text = f'Angle {name}: {angle:.2f}'
                #     cv.putText(frame0, text, (10, 30 + i * 30), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv.LINE_AA)
                self._sendtime = time.time()   

                sendValue = dict()
                sendValue[1] = self.vcf[1].filter(arm_angle[0])
                sendValue[2] = self.vcf[2].filter(arm_angle[1])
                sendValue[3] = self.vcf[3].filter(arm_angle[2])
                sendValue[4] = self.vcf[4].filter(arm_angle[3])

                sendValue[7] = self.vcf[7].filter(arm_angle[4])
                sendValue[8] = self.vcf[8].filter(arm_angle[5])
                sendValue[9] = self.vcf[9].filter(arm_angle[6])
                sendValue[10] = self.vcf[10].filter(arm_angle[7])

                # send_value[13] = self._sendtime % 10

                self._data = dict(zip(sendValue.keys(),sendValue.values()))


                for i, (name, angle) in enumerate(zip(nameTag,self._data.values())):
                    text = f'Angle {name}: {angle:.2f}'
                    cv.putText(frame0, text, (10, 30 + i * 30), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv.LINE_AA)


                # 연결 상태 표시
                # status_text = "Connected" if self.connected else "Disconnected"
                # cv.putText(frame1, status_text, (10, 30), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                self.sendQ1.put([frame0, frame1,frame2])
                
                if self.sendQ2.qsize()>0:
                    print("SERVER CONNECT BTN PRESSED")
                    state = self.sendQ2.get()
                    if state:
                        self.server_flag= 0
                        if self.once:
                            self.once=0
                            self.connect_to_server()
                        
                    else:
                        self.server_flag=1
                        #self.disconnect_from_server()

                if self.connected :
                    try:
                        BUFF_SIZE = 1024
                        LIMIT_TIME = 10
                        # send_value = self.SMART.contorol_motor([0x31,0x32,0x33,0x34,0x35,0x36,0x37,0x38,0x39,0x3A,0x3B,0x3C,0x3D],[value,value,value,value,value,value,value,value,value,value,value,value,value])
                        self._data[0xfe]=self.server_flag
                        send_value =(str(self._data))
                        # send_value = self.SMART.contorol_motor([0x31],[1])
                        # data = pickle.dumps(send_value, protocol=pickle.HIGHEST_PROTOCOL)

                        if len(send_value) <92:
                            for i in range(0, 92-len(send_value)):
                                send_value+=' '

                        # print(bytes(send_value,'utf-8'))
                        self.client_socket.sendall(bytes(send_value,'utf-8'))
                        # time.sleep(0.1)
                        # print(send_value, len((send_value)))

                    except socket.timeout as err:
                        print(f'Timeout Error : {err}')
                        
                        # 추가적인 예외처리 로직 구성...
                        self.connected = False
                        self.client_socket.close()

                    except socket.error as err:
                        print(f'Something Error : {err}')
                        self.connected = False
                        self.client_socket.close()

                    # time.sleep(1)


            # # 화면에 표시
            # cv.imshow('cam1', frame1)
            # cv.imshow('cam0', frame0)

            # key = cv.waitKey(1) & 0xFF
            # if key == 27:  # ESC 키
            #     break
            # elif key == 32:  # Space 키를 눌러 연결/해제 전환
            #     self.connect_to_server()

        for cap in caps:
            cap.release()


if __name__ == "__main__":
    client = SocketServer(CLIENT_PORT)
    camera = SocketServer(CAMERA_PORT)

    while True:
        time.sleep(0.1)