import os
os.environ["OPENcv2_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
import cv2
import timeit
import numpy as np
import mediapipe as mp

cap0 = cv2.VideoCapture(0,cv2.CAP_DSHOW)
cap1 = cv2.VideoCapture(1,cv2.CAP_DSHOW)
caps = [cap0, cap1]


cap0.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap0.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

cap1.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap1.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# frame_shape = [1080, 1920]
frame_shape = [720, 1280]
# frame_shape = [480, 640]

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

pose0 = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
pose1 = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

while True:
    ret0, frame0 = cap0.read()
    ret1, frame1 = cap1.read()
    
    if not ret0 or not ret1:
        print("카메라 에러")
        break

    if frame0.shape[1] != 1080:
        frame0 = frame0[:, frame_shape[1] // 2 - frame_shape[0] // 2:frame_shape[1] // 2 + frame_shape[0] // 2]
        frame1 = frame1[:, frame_shape[1] // 2 - frame_shape[0] // 2:frame_shape[1] // 2 + frame_shape[0] // 2]
    print(frame0.shape,frame1.shape)

    frame0 = cv2.cvtColor(frame0, cv2.COLOR_BGR2RGB)
    frame1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
        
    frame0.flags.writeable = False
    frame1.flags.writeable = False
    results0 = pose0.process(frame0)
    results1 = pose1.process(frame1)
        
    frame0.flags.writeable = True
    frame1.flags.writeable = True
    frame0 = cv2.cvtColor(frame0, cv2.COLOR_RGB2BGR)
    frame1 = cv2.cvtColor(frame1, cv2.COLOR_RGB2BGR)

    mp_drawing.draw_landmarks(
        frame0,
        results0.pose_landmarks,
        mp_pose.POSE_CONNECTIONS,
        landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
    
    mp_drawing.draw_landmarks(
        frame1,
        results1.pose_landmarks,
        mp_pose.POSE_CONNECTIONS,
        landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
    
    cv2.imshow('MediaPipe Pose0', frame0)
    cv2.imshow('MediaPipe Pose1', frame1)
    
    
    if cv2.waitKey(5) & 0xFF == 27:
        break
cap0.release()