#각도 확을을 위한 촬영 추가(작동 안함)

import cv2 as cv
import mediapipe as mp
import numpy as np
import sys
from utils import DLT, get_projection_matrix

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

frame_shape = [720, 1280]

# add here if you need more keypoints
pose_keypoints = [16, 14, 12, 11, 13, 15, 24, 23, 25, 26, 27, 28]

def calculate_3d(kpts3d):
    """ 주어진 3D 키포인트로부터 각 관절의 회전 각도를 계산합니다. """
    
    shoulder = kpts3d[0]  # 어깨의 3D 좌표
    elbow = kpts3d[1]     # 팔꿈치의 3D 좌표
    wrist = kpts3d[2]     # 손목의 3D 좌표
    hand = kpts3d[3]      # 손의 3D 좌표 (그리퍼의 위치)

    # 기저부 관절 각도 계산
    base_angle = np.arctan2(shoulder[1], shoulder[0]) * 180 / np.pi

    # 어깨 각도 계산 (기저부 관절)
    shoulder_elbow_vector = elbow - shoulder
    shoulder_angle = np.arctan2(shoulder_elbow_vector[2], shoulder_elbow_vector[0]) * 180 / np.pi

    # 팔꿈치 각도 계산
    elbow_wrist_vector = wrist - elbow
    elbow_angle = np.arctan2(elbow_wrist_vector[1], elbow_wrist_vector[0]) * 180 / np.pi

    # 손목 각도 계산
    wrist_hand_vector = hand - wrist
    wrist_angle = np.arctan2(wrist_hand_vector[1], wrist_hand_vector[2]) * 180 / np.pi

    return base_angle, shoulder_angle, elbow_angle, wrist_angle

def run_mp(input_stream1, input_stream2, P0, P1, output_video='output.avi'):
    # input video stream
    cap0 = cv.VideoCapture(input_stream1)
    cap1 = cv.VideoCapture(input_stream2)
    caps = [cap0, cap1]

    # VideoWriter 객체를 초기화합니다.
    fourcc = cv.VideoWriter_fourcc(*'XVID')
    out = cv.VideoWriter(output_video, fourcc, 20.0, (frame_shape[1], frame_shape[0]))

    # set camera resolution if using webcam to 1280x720. Any bigger will cause some lag for hand detection
    for cap in caps:
        cap.set(3, frame_shape[1])
        cap.set(4, frame_shape[0])

    # create body keypoints detector objects.
    pose0 = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    pose1 = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    while True:
        # read frames from stream
        ret0, frame0 = cap0.read()
        ret1, frame1 = cap1.read()

        if not ret0 or not ret1: break

        # crop to 720x720.
        if frame0.shape[1] != 720:
            frame0 = frame0[:, frame_shape[1] // 2 - frame_shape[0] // 2:frame_shape[1] // 2 + frame_shape[0] // 2]
            frame1 = frame1[:, frame_shape[1] // 2 - frame_shape[0] // 2:frame_shape[1] // 2 + frame_shape[0] // 2]

        # the BGR image to RGB.
        frame0 = cv.cvtColor(frame0, cv.COLOR_BGR2RGB)
        frame1 = cv.cvtColor(frame1, cv.COLOR_BGR2RGB)

        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        frame0.flags.writeable = False
        frame1.flags.writeable = False
        results0 = pose0.process(frame0)
        results1 = pose1.process(frame1)

        # reverse changes
        frame0.flags.writeable = True
        frame1.flags.writeable = True
        frame0 = cv.cvtColor(frame0, cv.COLOR_RGB2BGR)
        frame1 = cv.cvtColor(frame1, cv.COLOR_RGB2BGR)

        # check for keypoints detection
        frame0_keypoints = []
        if results0.pose_landmarks:
            for i, landmark in enumerate(results0.pose_landmarks.landmark):
                if i not in pose_keypoints: continue  # only save keypoints that are indicated in pose_keypoints
                pxl_x = landmark.x * frame0.shape[1]
                pxl_y = landmark.y * frame0.shape[0]
                pxl_x = int(round(pxl_x))
                pxl_y = int(round(pxl_y))
                cv.circle(frame0, (pxl_x, pxl_y), 3, (0, 0, 255), -1)  # add keypoint detection points into figure
                kpts = [pxl_x, pxl_y]
                frame0_keypoints.append(kpts)
        else:
            # if no keypoints are found, simply fill the frame data with [-1,-1] for each kpt
            frame0_keypoints = [[-1, -1]] * len(pose_keypoints)

        frame1_keypoints = []
        if results1.pose_landmarks:
            for i, landmark in enumerate(results1.pose_landmarks.landmark):
                if i not in pose_keypoints: continue
                pxl_x = landmark.x * frame1.shape[1]
                pxl_y = landmark.y * frame1.shape[0]
                pxl_x = int(round(pxl_x))
                pxl_y = int(round(pxl_y))
                cv.circle(frame1, (pxl_x, pxl_y), 3, (0, 0, 255), -1)
                kpts = [pxl_x, pxl_y]
                frame1_keypoints.append(kpts)
        else:
            # if no keypoints are found, simply fill the frame data with [-1,-1] for each kpt
            frame1_keypoints = [[-1, -1]] * len(pose_keypoints)

        # calculate 3d position
        frame_p3ds = []
        for uv1, uv2 in zip(frame0_keypoints, frame1_keypoints):
            if uv1[0] == -1 or uv2[0] == -1:
                _p3d = [-1, -1, -1]
            else:
                _p3d = DLT(P0, P1, uv1, uv2)  # calculate 3d position of keypoint
            frame_p3ds.append(_p3d)

        # This contains the 3d position of each keypoint in current frame.
        # For real time application, this is what you want.
        frame_p3ds = np.array(frame_p3ds).reshape((12, 3))

        # 어깨, 팔꿈치, 손목 각도 계산
        base_angle, shoulder_angle, elbow_angle, wrist_angle = calculate_3d(frame_p3ds)

        # 각도 정보를 프레임에 표시
        cv.putText(frame0, f"Base angle: {base_angle:.2f}", (10, 30), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv.putText(frame0, f"Shoulder angle: {shoulder_angle:.2f}", (10, 60), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv.putText(frame0, f"Elbow angle: {elbow_angle:.2f}", (10, 90), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv.putText(frame0, f"Wrist angle: {wrist_angle:.2f}", (10, 120), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # 3D 키포인트와 각도를 출력
        print("3D Keypoints:", frame_p3ds)
        print(f"Base angle: {base_angle}, Shoulder angle: {shoulder_angle}, Elbow angle: {elbow_angle}, Wrist angle: {wrist_angle}")

        # 프레임 표시
        cv.imshow('cam0', frame0)
        cv.imshow('cam1', frame1)

        # 비디오 파일에 프레임 저장
        out.write(frame0)

        k = cv.waitKey(1)
        if k & 0xFF == 27: break  # 27 is ESC key.

    cv.destroyAllWindows()
    for cap in caps:
        cap.release()
    out.release()

if __name__ == '__main__':
    # this will load the sample videos if no camera ID is given
    input_stream1 = 'media/cam0_test.mp4'
    input_stream2 = 'media/cam1_test.mp4'

    # put camera id as command line arguments
    if len(sys.argv) == 3:
        input_stream1 = int(sys.argv[1])
        input_stream2 = int(sys.argv[2])

    # get projection matrices
    P0 = get_projection_matrix(0)
    P1 = get_projection_matrix(1)

    run_mp(input_stream1, input_stream2, P0, P1)
