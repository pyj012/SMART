import os
os.add_dll_directory('C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v11.8/bin')
os.add_dll_directory('C:/opencv/build/install/x64/vc16/bin')
os.add_dll_directory('C:/opencv/build/bin')
import cv2 as cv
import mediapipe as mp
import numpy as np
import sys
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from utils import DLT, get_projection_matrix

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

frame_shape = [720, 1280]
pose_keypoints = [20, 19, 16, 14, 12, 11, 13, 15, 24, 23, 25, 26, 27, 28]

def visualize_3d(ax, kpts3d):
    ax.clear()
    torso = [[0, 1], [1, 9], [9, 8], [8, 0]]
    armr = [[1, 3], [3, 5], [5, 7]]
    arml = [[0, 2], [2, 4], [4, 6]]
    legr = [[9, 11], [11, 13]]
    legl = [[8, 10], [10, 12]]
    body = [torso, arml, armr, legl, legr]
    colors = ['red', 'blue', 'green', 'black', 'orange']

    for bodypart, part_color in zip(body, colors):
        for _c in bodypart:
            ax.plot(xs=[kpts3d[_c[0],0], kpts3d[_c[1],0]],
                    ys=[kpts3d[_c[0],1], kpts3d[_c[1],1]],
                    zs=[kpts3d[_c[0],2], kpts3d[_c[1],2]],
                    linewidth=4, c=part_color)

    ax.set_xlim3d(-50, 50)
    ax.set_ylim3d(-50, 50)
    ax.set_zlim3d(0, 100)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')

def run_mp(input_stream1, input_stream2, P0, P1):
    cap0 = cv.VideoCapture(input_stream1)
    cap1 = cv.VideoCapture(input_stream2)
    caps = [cap0, cap1]

    pose0 = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    pose1 = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    plt.ion()

    while True:
        ret0, frame0 = cap0.read()
        ret1, frame1 = cap1.read()

        if not ret0 or not ret1:
            break

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
        frame1_keypoints = []

        if results0.pose_landmarks and results1.pose_landmarks:
            for i, (landmark0, landmark1) in enumerate(zip(results0.pose_landmarks.landmark, results1.pose_landmarks.landmark)):
                if i not in pose_keypoints:
                    continue
                
                pxl_x0 = int(landmark0.x * frame0.shape[1])
                pxl_y0 = int(landmark0.y * frame0.shape[0])
                pxl_x1 = int(landmark1.x * frame1.shape[1])
                pxl_y1 = int(landmark1.y * frame1.shape[0])

                cv.circle(frame0, (pxl_x0, pxl_y0), 3, (0,0,255), -1)
                cv.circle(frame1, (pxl_x1, pxl_y1), 3, (0,0,255), -1)

                frame0_keypoints.append([pxl_x0, pxl_y0])
                frame1_keypoints.append([pxl_x1, pxl_y1])

            frame_p3ds = []
            for uv1, uv2 in zip(frame0_keypoints, frame1_keypoints):
                _p3d = DLT(P0, P1, uv1, uv2)
                frame_p3ds.append(_p3d)

            frame_p3ds = np.array(frame_p3ds).reshape((len(pose_keypoints), 3))
            visualize_3d(ax, frame_p3ds)
            plt.draw()
            plt.pause(0.001)

        cv.imshow('cam1', frame1)
        cv.imshow('cam0', frame0)

        if cv.waitKey(1) & 0xFF == 27:
            break

    cv.destroyAllWindows()
    for cap in caps:
        cap.release()
    plt.ioff()
    plt.close()

if __name__ == '__main__':
    input_stream1 = 0  # Default to first camera
    input_stream2 = 2  # Default to third camera

    if len(sys.argv) == 3:
        input_stream1 = int(sys.argv[1])
        input_stream2 = int(sys.argv[2])

    P0 = get_projection_matrix(0)
    P1 = get_projection_matrix(1)

    run_mp(input_stream1, input_stream2, P0, P1)