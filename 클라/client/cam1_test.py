import os
os.add_dll_directory('C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v11.8/bin')
os.add_dll_directory('C:/opencv/build/install/x64/vc16/bin')
os.add_dll_directory('C:/opencv/build/bin')
import cv2

# 일반적으로 웹캠 불러오기
# cap = cv2.VideoCapture(0)
# ret, frame = cap.read()

# 기존 방식으로 연결이 안될 경우
# 여기서 숫자 0은 웹캠의 채널 인덱스

cap = cv2.VideoCapture(0)
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# print(actual_width,actual_height)

while True:
    ret, frame = cap.read()

    if not ret:
        print("카메라 에러")
        break

    print(frame.shape)

    cv2.imshow('test',frame)

    if cv2.waitKey(5) & 0xFF == 27:
        break
cap.release()