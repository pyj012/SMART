import os
os.add_dll_directory('C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v11.8/bin')
os.add_dll_directory('C:/opencv/build/install/x64/vc16/bin')
os.add_dll_directory('C:/opencv/build/bin')

import cv2

print("where1")
# 첫 번째 카메라 스트림을 받아오기 위한 VideoCapture 객체 생성
cap0 = cv2.VideoCapture(0)

# 두 번째 카메라 스트림을 받아오기 위한 VideoCapture 객체 생성
cap1 = cv2.VideoCapture(2)
print("where2")

# cap0.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
# cap0.set(cv2.CAP_PROP_FRAME_HEIGHT,s 720)

# cap1.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
# cap1.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
while True:
    ret0, frame0 = cap0.read()
    ret1, frame1 = cap1.read()

    if not ret0 or not ret1:
        break

    # frame0 = cv2.cvtColor(frame0, cv2.COLOR_RGB2BGR)
    # frame1 = cv2.cvtColor(frame1, cv2.COLOR_RGB2BGR)

    cv2.imshow('frame0',frame0)
    cv2.imshow('frame1',frame1)

    k = cv2.waitKey(1)
    if k & 0xFF == 27:
        break

cap0.release()
cap1.release()