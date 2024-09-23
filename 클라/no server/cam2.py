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
    torso = [[0, 1] , [1, 7], [7, 6], [6, 0]]
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

def run_mp(input_stream1, input_stream2, P0, P1):
    # 입력 비디오 스트림
    cap0 = cv.VideoCapture(input_stream1)
    cap1 = cv.VideoCapture(input_stream2)
    caps = [cap0, cap1]

    # 웹캠을 사용할 경우 해상도를 1280x720으로 설정하십시오. 더 큰 해상도는 손 검출에 약간의 지연을 초래할 수 있습니다
    for cap in caps:
        cap.set(3, frame_shape[1])
        cap.set(4, frame_shape[0])

    # 바디 키포인트 검출 객체 생성
    pose0 = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5, model_complexity=2)
    pose1 = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5, model_complexity=2)

    # 각 카메라에 대해 검출된 키포인트를 저장할 컨테이너. 각 프레임마다 채워짐
    kpts_cam0 = []
    kpts_cam1 = []
    kpts_3d = []

    # 3D 시각화를 위한 Matplotlib 설정
    plt.ion()
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    while True:
        # 스트림에서 프레임을 읽음
        ret0, frame0 = cap0.read()
        ret1, frame1 = cap1.read()

        if not ret0 or not ret1:
            break

        # 720x720으로 자름
        # 주의: 카메라 보정 매개변수는 이 해상도에 맞춰져 있습니다. 이를 변경하면 카메라 내부 매개변수도 변경해야 합니다
        if frame0.shape[1] != 720:
            frame0 = frame0[:, frame_shape[1] // 2 - frame_shape[0] // 2:frame_shape[1] // 2 + frame_shape[0] // 2]
            frame1 = frame1[:, frame_shape[1] // 2 - frame_shape[0] // 2:frame_shape[1] // 2 + frame_shape[0] // 2]

        # BGR 이미지를 RGB로 변환
        frame0 = cv.cvtColor(frame0, cv.COLOR_BGR2RGB)
        frame1 = cv.cvtColor(frame1, cv.COLOR_BGR2RGB)

        # 성능을 향상시키기 위해, 이미지의 쓰기 가능 여부를 False로 설정하여 참조로 전달
        frame0.flags.writeable = False
        frame1.flags.writeable = False
        results0 = pose0.process(frame0)
        results1 = pose1.process(frame1)

        # 변경 사항을 되돌림
        frame0.flags.writeable = True
        frame1.flags.writeable = True
        frame0 = cv.cvtColor(frame0, cv.COLOR_RGB2BGR)
        frame1 = cv.cvtColor(frame1, cv.COLOR_RGB2BGR)

        # 키포인트 검출 확인
        frame0_keypoints = []
        if results0.pose_landmarks:
            for i, landmark in enumerate(results0.pose_landmarks.landmark):
                if i not in pose_keypoints:
                    continue  # 지정된 키포인트만 저장
                pxl_x = landmark.x * frame0.shape[1]
                pxl_y = landmark.y * frame0.shape[0]
                pxl_x = int(round(pxl_x))
                pxl_y = int(round(pxl_y))
                cv.circle(frame0, (pxl_x, pxl_y), 3, (0, 0, 255), -1)  # 검출된 키포인트를 그림에 추가
                kpts = [pxl_x, pxl_y]
                frame0_keypoints.append(kpts)
        else:
            # 키포인트를 찾지 못하면 각 키포인트에 대해 [-1, -1]로 프레임 데이터를 채움
            frame0_keypoints = [[-1, -1]] * len(pose_keypoints)

        # 이 프레임의 키포인트를 메모리에 유지
        kpts_cam0.append(frame0_keypoints)

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
            # 키포인트를 찾지 못하면 각 키포인트에 대해 [-1, -1]로 프레임 데이터를 채움
            frame1_keypoints = [[-1, -1]] * len(pose_keypoints)

        # 키포인트 컨테이너 업데이트
        kpts_cam1.append(frame1_keypoints)

        # 3D 위치 계산
        frame_p3ds = []
        for uv1, uv2 in zip(frame0_keypoints, frame1_keypoints):
            if uv1[0] == -1 or uv2[0] == -1:
                _p3d = [-1, -1, -1]
            else:
                _p3d = DLT(P0, P1, uv1, uv2)  # 키포인트의 3D 위치 계산
            frame_p3ds.append(_p3d)

        frame_p3ds = np.array(frame_p3ds).reshape((12, 3))
        kpts_3d.append(frame_p3ds)

        # 실시간 3D 시각화
        visualize_3d(ax, [frame_p3ds])

        cv.imshow('cam1', frame1)
        cv.imshow('cam0', frame0)

        k = cv.waitKey(1)
        if k & 0xFF == 27:
            break  # 27은 ESC 키입니다.

    cv.destroyAllWindows()
    for cap in caps:
        cap.release()

    return np.array(kpts_cam0), np.array(kpts_cam1), np.array(kpts_3d)

if __name__ == '__main__':
    # 카메라 ID가 주어지지 않은 경우 기본 웹캠 사용
    input_stream1 = 0
    input_stream2 = 1

    # 명령줄 인수로 카메라 ID 지정
    if len(sys.argv) == 3:
        input_stream1 = int(sys.argv[1])
        input_stream2 = int(sys.argv[2])

    # 투영 행렬 가져오기
    P0 = get_projection_matrix(input_stream1)
    P1 = get_projection_matrix(input_stream2)

    run_mp(input_stream1, input_stream2, P0, P1)
