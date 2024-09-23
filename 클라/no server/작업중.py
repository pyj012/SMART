import os
os.add_dll_directory('C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v11.8/bin')
os.add_dll_directory('C:/opencv/build/install/x64/vc16/bin')
os.add_dll_directory('C:/opencv/build/bin')

import cv2 as cv
import mediapipe as mp
import numpy as np
import sys, math
from utils_3 import DLT, get_projection_matrix, calculate_3d

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

frame_shape = [720, 1280]

# add here if you need more keypoints
pose_keypoints = [19, 20, 16, 14, 12, 11, 13, 15, 24, 23, 25, 26, 27, 28]

import numpy as np

# Function to project a point onto a plane


def run_mp(input_stream1, input_stream2, P0, P1):
    print("where1")
    cap0 = cv.VideoCapture(input_stream1)
    cap1 = cv.VideoCapture(input_stream2)
    caps = [cap0, cap1]
    print("where2")
    # cap0.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
    # cap0.set(cv.CAP_PROP_FRAME_HEIGHT, 720)

    # cap1.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
    # cap1.set(cv.CAP_PROP_FRAME_HEIGHT, 720)
    print("where3")
    frame_width = int(cap0.get(cv.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap0.get(cv.CAP_PROP_FRAME_HEIGHT))

    print(f"카메라 해상도: {frame_width}x{frame_height}")

    # for cap in caps:
    #     cap.set(3, frame_shape[1])
    #     cap.set(4, frame_shape[0])

    pose0 = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    pose1 = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    while True:
        ret0, frame0 = cap0.read()
        ret1, frame1 = cap1.read()

        if not ret0 or not ret1:
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

        frame_p3ds = []
        for uv1, uv2 in zip(frame0_keypoints, frame1_keypoints):
            if uv1[0] == -1 or uv2[0] == -1:
                _p3d = [-1, -1, -1]
            else:
                _p3d = DLT(P0, P1, uv1, uv2)
            frame_p3ds.append(_p3d)

        frame_p3ds = np.array(frame_p3ds).reshape((len(pose_keypoints), 3))

        try:
            _angle = calculate_3d(frame_p3ds)
            # print(arm_angle)
            # if any(math.isnan(i) for i in arm_angle):
            #     arm_angle = self.pre_arm_angle
            # else:
            #     self.pre_arm_angle = arm_angle
        except Exception as e:
            print(e)
        # Draw angles on frame
        for i, angle in enumerate(_angle):
            text = f'Angle {i+1}: {angle:.2f}'
            cv.putText(frame0, text, (10, 30 + i * 30), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv.LINE_AA)

        cv.imshow('cam1', frame1)
        cv.imshow('cam0', frame0)

        k = cv.waitKey(1)
        if k & 0xFF == 27:
            break

    cv.destroyAllWindows()
    for cap in caps:
        cap.release()

if __name__ == '__main__':
    input_stream1 = 'media/cam0_test_half_speed.mp4'
    input_stream2 = 'media/cam1_test_half_speed.mp4'

    if len(sys.argv) == 3:
        input_stream1 = int(sys.argv[0])
        input_stream2 = int(sys.argv[2])

    P0 = get_projection_matrix(0)
    P1 = get_projection_matrix(2)

    run_mp(input_stream1, input_stream2, P0, P1)