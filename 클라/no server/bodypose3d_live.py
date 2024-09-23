import cv2 as cv
import mediapipe as mp
import numpy as np
import matplotlib.pyplot as plt
from utils import DLT, get_projection_matrix
from mpl_toolkits.mplot3d import Axes3D
import timeit


mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

frame_shape = [720, 1280]
pose_keypoints = [16, 14, 12, 11, 13, 15, 24, 23, 25, 26, 27, 28]
# pose_keypoints = [11, 13, 15]

# Visualize 3D function
def visualize_3d(p3ds, ax):
    torso = [[0, 1], [1, 7], [7, 6], [6, 0]]
    armr = [[1, 3], [3, 5]]
    arml = [[0, 2], [2, 4]]
    legr = [[6, 8], [8, 10]]
    legl = [[7, 9], [9, 11]]
    body = [torso, arml, armr, legr, legl]
    colors = ['red', 'blue', 'green', 'black', 'orange']

    ax.cla()
    for bodypart, part_color in zip(body, colors):
        for _c in bodypart:
            ax.plot(xs=[p3ds[_c[0], 0], p3ds[_c[1], 0]], 
                    ys=[p3ds[_c[0], 1], p3ds[_c[1], 1]], 
                    zs=[p3ds[_c[0], 2], p3ds[_c[1], 2]], 
                    linewidth=4, c=part_color)
    ax.set_xlim3d(-10, 10)
    ax.set_ylim3d(-10, 10)
    ax.set_zlim3d(-10, 10)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])
    plt.pause(0.1)

def run_mp(input_stream1, input_stream2, P0, P1):
    b = 0
    
    cap0 = cv.VideoCapture(input_stream1)
    cap1 = cv.VideoCapture(input_stream2)
    caps = [cap0, cap1]
    
    for cap in caps:
        cap.set(3, frame_shape[1])
        cap.set(4, frame_shape[0])

    pose0 = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    pose1 = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    while True:

        start_t = timeit.default_timer()

        ret0, frame0 = cap0.read()
        ret1, frame1 = cap1.read()

        if not ret0 or not ret1:
            break

        if frame0.shape[1] != 720:
            frame0 = frame0[:, frame_shape[1]//2 - frame_shape[0]//2:frame_shape[1]//2 + frame_shape[0]//2]
            frame1 = frame1[:, frame_shape[1]//2 - frame_shape[0]//2:frame_shape[1]//2 + frame_shape[0]//2]

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

        frame_p3ds = np.array(frame_p3ds).reshape((12, 3))

        if b:
            visualize_3d(frame_p3ds, ax)
            b = 0
        else:
            b = 1
        cv.imshow('cam1', frame1)
        cv.imshow('cam0', frame0)

        if cv.waitKey(1) & 0xFF == 27:
            break

        terminate_t = timeit.default_timer()
        FPS = int(1./(terminate_t - start_t ))
        print(FPS)

    cv.destroyAllWindows()
    for cap in caps:
        cap.release()

if __name__ == '__main__':
    input_stream1 = 1
    input_stream2 = 2

    P0 = get_projection_matrix(1)
    P1 = get_projection_matrix(2)

    run_mp(input_stream1, input_stream2, P0, P1)
