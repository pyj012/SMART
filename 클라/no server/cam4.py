import cv2 as cv
import mediapipe as mp
import numpy as np
import sys
from utils import DLT, get_projection_matrix, write_keypoints_to_disk
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

frame_shape = [720, 1280]

pose_keypoints = [16, 14, 12, 11, 13, 15, 24, 23, 25, 26, 27, 28]

def visualize_3d(ax, p3ds):
    """Now visualize in 3D"""
    torso = [[0, 1], [1, 7], [7, 6], [6, 0]]
    armr = [[1, 3], [3, 5]]
    arml = [[0, 2], [2, 4]]
    legr = [[6, 8], [8, 10]]
    legl = [[7, 9], [9, 11]]
    body = [torso, arml, armr, legr, legl]
    colors = ['red', 'blue', 'green', 'black', 'orange']

    ax.cla()

    for kpts3d in p3ds:
        for bodypart, part_color in zip(body, colors):
            for _c in bodypart:
                ax.plot(xs=[kpts3d[_c[0], 0], kpts3d[_c[1], 0]],
                        ys=[kpts3d[_c[0], 1], kpts3d[_c[1], 1]],
                        zs=[kpts3d[_c[0], 2], kpts3d[_c[1], 2]],
                        linewidth=4, c=part_color)

    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])

    ax.set_xlim3d(-10, 10)
    ax.set_xlabel('x')
    ax.set_ylim3d(-10, 10)
    ax.set_ylabel('y')
    ax.set_zlim3d(-10, 10)
    ax.set_zlabel('z')

    plt.draw()
    plt.pause(0.001)

def run_mp(input_streams, Ps):
    caps = [cv.VideoCapture(stream) for stream in input_streams]

    for cap in caps:
        cap.set(3, frame_shape[1])
        cap.set(4, frame_shape[0])

    poses = [mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) for _ in input_streams]

    kpts_cams = [[] for _ in input_streams]
    kpts_3d = []

    plt.ion()
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    while True:
        frames = [cap.read()[1] for cap in caps]

        if any([frame is None for frame in frames]):
            break

        frames = [cv.cvtColor(frame[:, frame_shape[1] // 2 - frame_shape[0] // 2:frame_shape[1] // 2 + frame_shape[0] // 2], cv.COLOR_BGR2RGB) for frame in frames]

        results = [pose.process(frame) for pose, frame in zip(poses, frames)]

        frames = [cv.cvtColor(frame, cv.COLOR_RGB2BGR) for frame in frames]

        frame_keypoints = [[] for _ in input_streams]

        for idx, result in enumerate(results):
            if result.pose_landmarks:
                for i, landmark in enumerate(result.pose_landmarks.landmark):
                    if i not in pose_keypoints:
                        continue
                    pxl_x = landmark.x * frames[idx].shape[1]
                    pxl_y = landmark.y * frames[idx].shape[0]
                    pxl_x = int(round(pxl_x))
                    pxl_y = int(round(pxl_y))
                    cv.circle(frames[idx], (pxl_x, pxl_y), 3, (0, 0, 255), -1)
                    kpts = [pxl_x, pxl_y]
                    frame_keypoints[idx].append(kpts)
            else:
                frame_keypoints[idx] = [[-1, -1]] * len(pose_keypoints)

            kpts_cams[idx].append(frame_keypoints[idx])

        frame_p3ds = []
        for keypoints in zip(*frame_keypoints):
            if any([kp[0] == -1 for kp in keypoints]):
                frame_p3ds.append([-1, -1, -1])
            else:
                A = []
                for kp, P in zip(keypoints, Ps):
                    A.append(kp[1] * P[2, :] - P[1, :])
                    A.append(P[0, :] - kp[0] * P[2, :])
                A = np.array(A).reshape((2 * len(input_streams), 4))
                _, _, Vh = np.linalg.svd(A)
                frame_p3ds.append(Vh[3, 0:3] / Vh[3, 3])

        frame_p3ds = np.array(frame_p3ds).reshape((12, 3))
        kpts_3d.append(frame_p3ds)

        visualize_3d(ax, [frame_p3ds])

        for idx, frame in enumerate(frames):
            cv.imshow(f'cam{idx}', frame)

        k = cv.waitKey(1)
        if k & 0xFF == 27:
            break

    cv.destroyAllWindows()
    for cap in caps:
        cap.release()

    return [np.array(kpts_cam) for kpts_cam in kpts_cams], np.array(kpts_3d)

if __name__ == '__main__':
    input_streams = [0, 1, 2, 3]

    if len(sys.argv) == 5:
        input_streams = [int(arg) for arg in sys.argv[1:5]]

    Ps = [get_projection_matrix(stream) for stream in input_streams]

    run_mp(input_streams, Ps)
