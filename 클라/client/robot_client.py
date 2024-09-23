import os
os.adddlldirectory('C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v11.8/bin')
os.add_dll_directory('C:/opencv/build/install/x64/vc16/bin')
os.add_dll_directory('C:/opencv/build/bin')

import socket, time, json
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
from utils import DLT, get_projection_matrix, calculate_3d
from LowPassFilterTest import LowPassFilter



#사용할 키포인트
pose_keypoints = [19, 20, 16, 14, 12, 11, 13, 15, 24, 23, 25, 26, 27, 28]

#그리퍼 값
GRAP_VAL = 70
DROP_VAL = 20

#인식 전 초기값
data = {1:0, 2:0, 3:0, 4:0, 6:DROP_VAL}


prevSendTime = time.time()

lock = threading.Lock()
SERVER_HOST = "192.168.20.6"
SERVER_PORT = 5051


class SocketServer():
    def __init__(self):
        # 서버 구동에 필요한 정보 세팅
        self._host = SERVER_HOST
        self._port = SERVER_PORT
        self._data = data
        self._angle = angle
        self._prestate = data
        self._sendtime = ""
        self.client_socket =socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY,1)
        self.client_socket.connect((SERVER_HOST, SERVER_PORT))
        self.pre_arm_angle = []
        
        self.lpf = dict()
        self.lpf[1] = LowPassFilter(cut_off_freqency= 1., ts= 0.1, limit_low=0, limit_high=90)
        self.lpf[2] = LowPassFilter(cut_off_freqency= 1., ts= 0.1, limit_low=0, limit_high=90)
        self.lpf[3] = LowPassFilter(cut_off_freqency= 1., ts= 0.1, limit_low=0, limit_high=90)
        self.lpf[4] = LowPassFilter(cut_off_freqency= 1., ts= 0.1, limit_low=0, limit_high=90)
        self.lpf[6] = LowPassFilter(cut_off_freqency= 0.5, ts= 0.1)
        
        self.lpf[7] = LowPassFilter(cut_off_freqency= 1., ts= 0.1, limit_low=105, limit_high=165)
        self.lpf[8] = LowPassFilter(cut_off_freqency= 1., ts= 0.1, limit_low=0, limit_high=45)
        self.lpf[9] = LowPassFilter(cut_off_freqency= 1., ts= 0.1, limit_low=0, limit_high=70)
        self.lpf[10] = LowPassFilter(cut_off_freqency= 1., ts= 0.1, limit_low=125, limit_high=170)
        self.lpf[12] = LowPassFilter(cut_off_freqency= 0.5, ts= 0.1)
        
        self.SMART = smartprotocol()
        self.client_socket =socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((SERVER_HOST, SERVER_PORT))
        
        serverthread = threading.Thread(target= self._handle_client, args=(self.client_socket,))
        serverthread.daemon = True
        serverthread.start()




        input_stream1 = 0#'media/cam0_test_half_speed.mp4'
        input_stream2 = 1#'media/cam1_test_half_speed.mp4'

        P0 = get_projection_matrix(0)
        P1 = get_projection_matrix(1)
        
        while(1):
            self.run_mp(input_stream1, input_stream2, P0, P1)
            pass
    
    

    def run_mp(self, input_stream1, input_stream2, P0, P1):
        actions = ['stop', 'grap', 'drop']
        seq_length = 30
        model = load_model('models/model.keras')

        max_num_hands = 1
        frame = 0

        mp_hands = mp.solutions.hands
        mp_pose = mp.solutions.pose
        mp_drawing = mp.solutions.drawing_utils
        mp_drawing_styles = mp.solutions.drawing_styles
        frame_shape = [720, 1280]

        cap0 = cv.VideoCapture(input_stream1)
        cap1 = cv.VideoCapture(input_stream2)
        caps = [cap0, cap1]
        cap0.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
        cap0.set(cv.CAP_PROP_FRAME_HEIGHT, 720)

        cap1.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
        cap1.set(cv.CAP_PROP_FRAME_HEIGHT, 720)

        for cap in caps:
            cap.set(3, frame_shape[1])
            cap.set(4, frame_shape[0])

        pose0 = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        pose1 = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

        # hand
        hand = mp_hands.Hands(max_num_hands=max_num_hands,min_detection_confidence=0.5,min_tracking_confidence=0.5)

        seq = []
        action_seq = []

        while True:
            ret0, frame0 = cap0.read()
            ret1, frame1 = cap1.read()

            if not ret0 or not ret1:
                print("카메라 에러")
                break

            if frame0.shape[1] != 720:
                frame0 = frame0[:, frame_shape[1] // 2 - frame_shape[0] // 2:frame_shape[1] // 2 + frame_shape[0] // 2]
                frame1 = frame1[:, frame_shape[1] // 2 - frame_shape[0] // 2:frame_shape[1] // 2 + frame_shape[0] // 2]

            frame0 = cv.cvtColor(frame0, cv.COLOR_BGR2RGB)
            frame1 = cv.cvtColor(frame1, cv.COLOR_BGR2RGB)

            frame0.flags.writeable = False
            frame1.flags.writeable = False
            results0 = pose0.process(frame0)
            results1 = pose1.process(frame1)

            # hand
            results2 = hand.process(frame0)

            frame0.flags.writeable = True
            frame1.flags.writeable = True
            frame0 = cv.cvtColor(frame0, cv.COLOR_RGB2BGR)
            frame1 = cv.cvtColor(frame1, cv.COLOR_RGB2BGR)

            #프로그램 속도 상승을 위한 프레임 스킵 기능
            frame+=1
            if frame%2 == 0:
                pass
            
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

            
            gripR_val = DROP_VAL
            gripL_val = DROP_VAL

            if results2.multi_hand_landmarks is not None:
                for res, handedness in zip(results2.multi_hand_landmarks, results2.multi_handedness):
                    # Process only left hand
                    if handedness.classification[0].label == 'Left':
                        joint = np.zeros((21, 4))
                        for j, lm in enumerate(res.landmark):
                            joint[j] = [lm.x, lm.y, lm.z, lm.visibility]

                        # Compute angles between joints
                        v1 = joint[[0,1,2,3,0,5,6,7,0,9,10,11,0,13,14,15,0,17,18,19], :3] # Parent joint
                        v2 = joint[[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20], :3] # Child joint
                        v = v2 - v1 # [20, 3]
                        # Normalize v
                        v = v / np.linalg.norm(v, axis=1)[:, np.newaxis]

                        # Get angle using arcos of dot product
                        angle = np.arccos(np.einsum('nt,nt->n',
                            v[[0,1,2,4,5,6,8,9,10,12,13,14,16,17,18],:], 
                            v[[1,2,3,5,6,7,9,10,11,13,14,15,17,18,19],:])) # [15,]

                        angle = np.degrees(angle) # Convert radian to degree

                        d = np.concatenate([joint.flatten(), angle])

                        seq.append(d)

                        mp_drawing.draw_landmarks(frame0, res, mp_hands.HAND_CONNECTIONS)

                        if len(seq) < seq_length:
                            continue

                        input_data = np.expand_dims(np.array(seq[-seq_length:], dtype=np.float32), axis=0)

                        y_pred = model.predict(input_data).squeeze()

                        i_pred = int(np.argmax(y_pred))
                        conf = y_pred[i_pred]

                        if conf < 0.9:
                            continue

                        action = actions[i_pred]
                        action_seq.append(action)

                        if len(action_seq) < 3:
                            continue

                        this_action = '?'
                        if action_seq[-1] == action_seq[-2] == action_seq[-3]:
                            this_action = action

                        cv.putText(frame0, f'{this_action.upper()}', org=(int(res.landmark[0].x * frame0.shape[1]), int(res.landmark[0].y * frame0.shape[0] + 20)), fontFace=cv.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(255, 255, 255), thickness=2)

                
                        if this_action == 'stop':
                            pass
                        
                        if this_action == 'grap':
                            gripR_val = GRAP_VAL
                        
                        if this_action == 'drop':
                            gripR_val = DROP_VAL


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
                armR_angle = arm_angle[:4]
                armR_angle.append(gripR_val)
                armL_angle = arm_angle[4:]
                armL_angle.append(gripL_val)
                self.pre_arm_angle = arm_angle
                
                pot = armR_angle + armL_angle
            except Exception as e:
                print(e)
                arm_angle = self.pre_arm_angle
                pot = []
                armR_angle = []
                armL_angle = []

            sendValue = dict(zip([1,2,3,4,6,7,8,9,10,12],pot))
            # print(dict(zip([1,2,3,4,6],armr_angle)))

            # Draw angles on frame
            for i, angle in enumerate(sendValue.values(),start=1):
                n = i
                if i >=6:
                    n+=1
                if i >=11:
                    n+=1
                text = f'Angle {n}: {angle:.2f}'
                cv.putText(frame0, text, (10, 30 + i * 30), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv.LINE_AA)
            
            global prevSendTime
            if time.time()-prevSendTime>=0.05:
                self._sendtime = time.time()

                sendValue[1] = round(self.lpf[1].filter(180-armR_angle[0]))
                sendValue[2] = round(self.lpf[2].filter(90-armR_angle[1]))
                sendValue[3] = round(self.lpf[3].filter(armR_angle[2]))
                sendValue[4] = round(self.lpf[4].filter(armR_angle[3]))
                sendValue[6] = round(self.lpf[6].filter(armR_angle[4]))

                sendValue[7] = round(self.lpf[7].filter(125+90+45-armL_angle[0]))
                sendValue[8] = round(self.lpf[8].filter(armL_angle[1]/3))
                sendValue[9] = round(self.lpf[9].filter(armL_angle[2]/2))
                sendValue[10] = round(self.lpf[10].filter(125-armL_angle[3]))
                sendValue[12] = round(self.lpf[12].filter(armL_angle[4]))


                del sendValue[7]
                del sendValue[8]
                del sendValue[9]
                del sendValue[10]
                del sendValue[12]

                # processed_keys = list(np.array(list(sendValue.keys()))+48)
                processed_keys = [key + 48 for key in list(sendValue.keys())]
            self._data = dict(zip(processed_keys,sendValue.values()))

                    
            # print(self._data)
            # print()

            prevSendTime = time.time()



            cv.imshow('cam1', frame1)
            cv.imshow('cam0', frame0)

            k = cv.waitKey(1)
            if k & 0xFF == 27:
                break

        cv.destroyAllWindows()
        for cap in caps:
            cap.release()


    def _handle_client(self, client_socket):
        step = 0
        flag=True
        value = 0
        while True:
            try:
                BUFF_SIZE = 1024
                LIMIT_TIME = 10
                # send_value = self.SMART.contorol_motor([0x31,0x32,0x33,0x34,0x35,0x36,0x37,0x38,0x39,0x3A,0x3B,0x3C,0x3D],[value,value,value,value,value,value,value,value,value,value,value,value,value])
                send_value =(str({0x31:value,0x32:value,0x33:value,0x34:value,0x36:value,0x37:value,0x38:value,0x39:value,0x3A:value,0x3C:value}))
                # send_value = self.SMART.contorol_motor([0x31],[1])
                # data = pickle.dumps(send_value, protocol=pickle.HIGHEST_PROTOCOL)

                if len(send_value) <90:
                    for i in range(0, 90-len(send_value)):
                        send_value+=' '
                client_socket.recv(1)

                client_socket.sendall(bytes(send_value,'utf-8'))
                time.sleep(1)
                # print(send_value, len((send_value)))

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

if __name__ == "__main__":
    server = SocketServer()