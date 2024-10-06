import os
os.add_dll_directory('C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v11.8/bin')
os.add_dll_directory('C:/opencv/build/install/x64/vc16/bin')
os.add_dll_directory('C:/opencv/build/bin')

import socket, time, json, math
import threading 
import sys
import random
import struct
import pickle
import numpy as np
from collections import deque
import heapq
from protocol import *
# from tensorflow.keras.models import load_model

import cv2 as cv
import mediapipe as mp
from utils_V3 import DLT, get_projection_matrix, calculate_3d
from ValueControlFilter import ValueControlFilter



#사용할 키포인트
pose_keypoints = [19, 20, 16, 14, 12, 11, 13, 15, 24, 23, 25, 26, 27, 28]

#그리퍼 값
GRAP_VAL = 70
DROP_VAL = 20

#인식 전 초기값
data = {0x31:0, 0x32:0, 0x33:0, 0x34:0, 0x36:DROP_VAL}


prevSendTime = time.time()

lock = threading.Lock()
# SERVER_HOST = "192.168.20.2"
SERVER_HOST = "192.168.0.213"
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5051


class SocketServer():
    def __init__(self):
        # 서버 구동에 필요한 정보 세팅
        self._host = SERVER_HOST
        self._port = SERVER_PORT
        self.connected = False  # 초기 연결 상태
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._data = data
        self._angle = angle
        self._prestate = data
        self._sendtime = ""
        self.pre_arm_angle = [0,0,0,0,0,0,0,0]
        
        # 필터 : 일단 개별 각도의 변동이 작은경우, 큰 경우 무시하는걸로 만들었는데 끝점 좌표가 많이 변하면 제한하는 방식이 나을지도?
        self.vcf = dict()
        self.vcf[1] = ValueControlFilter(prev_data = 0, dev = 10, dev_Limit= 50, limit_low = 0, limit_high = 160)
        self.vcf[2] = ValueControlFilter(prev_data = 0, dev = 10, dev_Limit= 50, limit_low = 0, limit_high = 120)
        self.vcf[3] = ValueControlFilter(prev_data = 0, dev = 10, limit_low = 0, limit_high = 120)
        self.vcf[4] = ValueControlFilter(prev_data = 0, dev = 10, limit_low = 0, limit_high = 110)
        # self.lpf[6] = LowPassFilter(cut_off_freqency= 0.5, ts= 0.1)
        
        self.vcf[7] = ValueControlFilter(prev_data = 0, dev = 10, dev_Limit= 50, limit_low = 0, limit_high = 160)
        self.vcf[8] = ValueControlFilter(prev_data = 0, dev = 10, dev_Limit= 50, limit_low = 0, limit_high = 120)
        self.vcf[9] = ValueControlFilter(prev_data = 0, dev = 10, limit_low = 0, limit_high = 120)
        self.vcf[10] = ValueControlFilter(prev_data = 0, dev = 10, limit_low = 0, limit_high = 110)
        # self.lpf[12] = LowPassFilter(cut_off_freqency= 0.5, ts= 0.1)

        #미디어파이프 카메라 초기 세팅
        input_stream1 = 0#'media/cam0_test_half_speed.mp4'
        input_stream2 = 2#'media/cam1_test_half_speed.mp4'
        P0 = get_projection_matrix(0)
        P1 = get_projection_matrix(1)

        self.cv_thread = threading.Thread(target=self.run_mp, args=(input_stream1, input_stream2, P0, P1))
        self.cv_thread.daemon = True
        self.cv_thread.start()

        self.receive_thread = threading.Thread(target=self._handle_client)
        self.receive_thread.daemon = True
        self.receive_thread.start()


    def connect_to_server(self):
        """서버에 연결을 시도하는 함수"""
        if not self.connected:
            try:
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect((SERVER_HOST, SERVER_PORT))
                print("Connected to server.")
                self.connected = True
            except socket.error as err:
                print(f"Connection error: {err}")
                self.client_socket.close()
        else:
            self.disconnect_from_server()

    def disconnect_from_server(self):
        """서버 연결을 해제하는 함수"""
        if self.connected:
            self.client_socket.close()
            print("Disconnected from server.")
            self.connected = False
    
    def run_mp(self, input_stream1, input_stream2, P0, P1):

        mp_pose = mp.solutions.pose
        mp_drawing = mp.solutions.drawing_utils
        mp_drawing_styles = mp.solutions.drawing_styles
        frame_shape = [720, 1280]

        cap0 = cv.VideoCapture(input_stream1)
        cap1 = cv.VideoCapture(input_stream2)
        caps = [cap0, cap1]
        # cap0.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
        # cap0.set(cv.CAP_PROP_FRAME_HEIGHT, 720)

        # cap1.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
        # cap1.set(cv.CAP_PROP_FRAME_HEIGHT, 720)


        # for cap in caps:
        #     cap.set(3, frame_shape[1])
        #     cap.set(4, frame_shape[0])

        pose0 = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        pose1 = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

        seq = []
        action_seq = []

        while True:
            ret0, frame0 = cap0.read()
            ret1, frame1 = cap1.read()

            if not ret0 or not ret1:
                print("카메라 에러")
                break

            # if frame0.shape[1] != 720:
            #     frame0 = frame0[:, frame_shape[1] // 2 - frame_shape[0] // 2:frame_shape[1] // 2 + frame_shape[0] // 2]
            #     frame1 = frame1[:, frame_shape[1] // 2 - frame_shape[0] // 2:frame_shape[1] // 2 + frame_shape[0] // 2]

            frame0 = cv.cvtColor(frame0, cv.COLOR_BGR2RGB)
            frame1 = cv.cvtColor(frame1, cv.COLOR_BGR2RGB)

            frame0.flags.writeable = False
            frame1.flags.writeable = False
            results0 = pose0.process(frame0)
            results1 = pose1.process(frame1)


            frame0.flags.writeable = True
            frame1.flags.writeable = True
            frame0 = cv.cvtColor(frame0, cv.COLOR_RGB2BGR)
            frame1 = cv.cvtColor(frame1, cv.COLOR_RGB2BGR)

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


            frame_p3ds = []
            for uv1, uv2 in zip(frame0_keypoints, frame1_keypoints):
                if uv1[0] == -1 or uv2[0] == -1:
                    _p3d = [-1, -1, -1]
                else:
                    _p3d = DLT(P0, P1, uv1, uv2)
                frame_p3ds.append(_p3d)

            frame_p3ds = np.array(frame_p3ds).reshape((14, 3))
            
            try:
                arm_angle = calculate_3d(frame_p3ds)
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

            global prevSendTime
            if time.time()-prevSendTime>=0.05:
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

                '''
                sendValue[1] = set_limit(0,160,arm_angle[0]//10*10)
                if sendValue[1] < 90:
                    sendValue[2] = set_limit(0,120,arm_angle[1]//10*10)
                else:
                    sendValue[2] = set_limit(0,120,180 - arm_angle[1]//10*10)
                sendValue[3] = set_limit(0,120,arm_angle[2]//10*10)
                sendValue[4] = set_limit(0,110,arm_angle[3]*1)

                sendValue[7] = 0#set_limit(0,180,arm_angle[4])
                sendValue[8] = 0#set_limit(0,120,arm_angle[5])
                sendValue[9] = 0#set_limit(0,120,arm_angle[6])
                sendValue[10] = 0#set_limit(0,110,arm_angle[7]*1)
                '''

                # processed_keys = list(np.array(list(sendValue.keys()))+48)
                # processed_keys = [key + 48 for key in list(sendValue.keys())]
            self._data = dict(zip(sendValue.keys(),sendValue.values()))

            for i, (name, angle) in enumerate(zip(nameTag,self._data.values())):
                text = f'Angle {name}: {angle:.2f}'
                cv.putText(frame0, text, (10, 30 + i * 30), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv.LINE_AA)


            # print(self._data)
            # print()

            prevSendTime = time.time()

            # 연결 상태 표시
            status_text = "Connected" if self.connected else "Disconnected"
            cv.putText(frame1, status_text, (10, 30), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # 화면에 표시
            cv.imshow('cam1', frame1)
            cv.imshow('cam0', frame0)

            key = cv.waitKey(1) & 0xFF
            if key == 27:  # ESC 키
                break
            elif key == 32:  # Space 키를 눌러 연결/해제 전환
                self.connect_to_server()

        cv.destroyAllWindows()
        for cap in caps:
            cap.release()

    def _handle_client(self):
        step = 0
        flag=True
        value = 0
        while True:
            if self.connected:
                try:
                    BUFF_SIZE = 1024
                    LIMIT_TIME = 10
                    # send_value = self.SMART.contorol_motor([0x31,0x32,0x33,0x34,0x35,0x36,0x37,0x38,0x39,0x3A,0x3B,0x3C,0x3D],[value,value,value,value,value,value,value,value,value,value,value,value,value])
                    send_value =(str(self._data))
                    # send_value = self.SMART.contorol_motor([0x31],[1])
                    # data = pickle.dumps(send_value, protocol=pickle.HIGHEST_PROTOCOL)

                    if len(send_value) <90:
                        for i in range(0, 90-len(send_value)):
                            send_value+=' '

                    print(bytes(send_value,'utf-8'))
                    self.client_socket.sendall(bytes(send_value,'utf-8'))
                    time.sleep(0.1)
                    # print(send_value, len((send_value)))

                except socket.timeout as err:
                    print(f'Timeout Error : {err}')
                    
                    # 추가적인 예외처리 로직 구성...
                    self.connected = False
                    self.client_socket.close()
                    break
                except socket.error as err:
                    print(f'Something Error : {err}')
                    self.connected = False
                    self.client_socket.close()
                    break
            else:
                time.sleep(1)

if __name__ == "__main__":
    server = SocketServer()
    while True:
        time.sleep(0.1)