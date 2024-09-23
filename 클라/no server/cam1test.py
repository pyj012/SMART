import os
os.add_dll_directory('C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v11.8/bin')
os.add_dll_directory('C:/opencv/build/install/x64/vc16/bin')
os.add_dll_directory('C:/opencv/build/bin')

import cv2

print("where1")
cap0 = cv2.VideoCapture(0)
print("where2")

# get으로 caputure 객체의 속성을 얻을 수 있습니다
frame_width = cap0.get(cv2.CAP_PROP_FRAME_WIDTH)
frame_height = cap0.get(cv2.CAP_PROP_FRAME_HEIGHT)
fps = cap0.get(cv2.CAP_PROP_FPS)

# 얻은 속성 값 표시
print(f"CV_CAP_PROP_FRAME_WIDTH: {frame_width}")
print(f"CV_CAP_PROP_FRAME_HEIGHT: {frame_height}")
print(f"CAP_PROP_FPS: {fps}")

# cap0.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
# cap0.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# cap1.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
# cap1.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
while True:
    ret0, frame0 = cap0.read()

    if not ret0:
        break

    frame0 = cv2.cvtColor(frame0, cv2.COLOR_RGB2BGR)
    frame0 = cv2.cvtColor(frame0, cv2.COLOR_BGR2RGB)

    cv2.imshow('frame0',frame0)

    k = cv2.waitKey(1)
    if k & 0xFF == 27:
        break

cap0.release()