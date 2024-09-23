import socket, time, os
import threading 
import sys
import random
import json
import struct
import pickle
import numpy as np
from collections import deque
import heapq
from protocol import *
from tensorflow.keras.models import load_model

import cv2 as cv
import mediapipe as mp
from utils import DLT, get_projection_matrix, calculate_3d
from LowPassFilterTest import LowPassFilter

#사용할 키포인트
pose_keypoints = [19, 20, 16, 14, 12, 11, 13, 15, 24, 23, 25, 26, 27, 28]

#그리퍼 값
GRAP_VAL = 70
DROP_VAL = 20
data = {1:0, 2:0, 3:0, 4:0, 6:DROP_VAL}
#인식 전 초기값
data = {1:125, 2:0, 3:0, 4:125, 5:0, 6:10}

lpf = dict()
lpf[1] = LowPassFilter(cut_off_freqency= 1., ts= 0.1, limit_low=105, limit_high=165)
lpf[2] = LowPassFilter(cut_off_freqency= 1., ts= 0.1, limit_low=0, limit_high=45)
lpf[3] = LowPassFilter(cut_off_freqency= 1., ts= 0.1, limit_low=0, limit_high=70)
lpf[4] = LowPassFilter(cut_off_freqency= 1., ts= 0.1, limit_low=125, limit_high=170)
lpf[6] = LowPassFilter(cut_off_freqency= 0.5, ts= 0.1)
        
lpf[7] = LowPassFilter(cut_off_freqency= 1., ts= 0.1, limit_low=105, limit_high=165)
lpf[8] = LowPassFilter(cut_off_freqency= 1., ts= 0.1, limit_low=0, limit_high=45)
lpf[9] = LowPassFilter(cut_off_freqency= 1., ts= 0.1, limit_low=0, limit_high=70)
lpf[10] = LowPassFilter(cut_off_freqency= 1., ts= 0.1, limit_low=125, limit_high=170)
lpf[12] = LowPassFilter(cut_off_freqency= 0.5, ts= 0.1)

pre_arm_angle = []
prevSendTime = time.time()

lock = threading.Lock()

def run_mp(input_stream1, input_stream2, P0, P1):
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

        
        # frame0_keypoints = []
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
            pre_arm_angle = arm_angle
            
            pot = armR_angle + armL_angle
        except Exception as e:
            print(e)
            arm_angle = pre_arm_angle
            pot = []
            armR_angle = []
            armL_angle = []

        sendValue = dict(zip([1,2,3,4,6,7,8,9,10,12],pot))
        print(sendValue)
        # print(sendValue)

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
            # self._sendtime = time.time()
            print(armR_angle)
            print(armL_angle)

            sendValue[1] = round(lpf[1].filter(125+90+45-armR_angle[0]))
            sendValue[2] = round(lpf[2].filter(armR_angle[1]/3))
            sendValue[3] = round(lpf[3].filter(armR_angle[2]/2))
            sendValue[4] = round(lpf[4].filter(125-armR_angle[3]))
            sendValue[6] = round(lpf[6].filter(armR_angle[4]))

            sendValue[7] = round(lpf[7].filter(125+90+45-armL_angle[0]))
            sendValue[8] = round(lpf[8].filter(armL_angle[1]/3))
            sendValue[9] = round(lpf[9].filter(armL_angle[2]/2))
            sendValue[10] = round(lpf[10].filter(125-armL_angle[3]))
            sendValue[12] = round(lpf[12].filter(armL_angle[4]))

                    
            processed_keys = [key + 48 for key in list(sendValue.keys())]


        data = dict(zip(processed_keys,sendValue.values()))

        prevSendTime = time.time()

        cv.imshow('cam1', frame1)
        cv.imshow('cam0', frame0)

        k = cv.waitKey(1)
        if k & 0xFF == 27:
            break

    cv.destroyAllWindows()
    for cap in caps:
        cap.release()

if __name__ == '__main__':
    input_stream1 = 0#'media/cam0_test.mp4'
    input_stream2 = 1#'media/cam1_test.mp4'

    if len(sys.argv) == 3:
        input_stream1 = int(sys.argv[1])
        input_stream2 = int(sys.argv[2])

    P0 = get_projection_matrix(0)
    P1 = get_projection_matrix(1)

    run_mp(input_stream1, input_stream2, P0, P1)
