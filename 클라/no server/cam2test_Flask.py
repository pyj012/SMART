import os
os.add_dll_directory('C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v11.8/bin')
os.add_dll_directory('C:/opencv/build/install/x64/vc16/bin')
os.add_dll_directory('C:/opencv/build/bin')

import cv2
import threading

def capture_camera(cap, window_name):
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow(window_name, frame)
        if cv2.waitKey(1) & 0xFF == 27:  # ESC 키를 누르면 종료
            break
    cap.release()
    cv2.destroyWindow(window_name)

print("where1")

# 첫 번째 카메라 스트림을 받아오기 위한 VideoCapture 객체 생성
cap0 = cv2.VideoCapture("http://localhost:5000/video_feed1")

# 두 번째 카메라 스트림을 받아오기 위한 VideoCapture 객체 생성
cap1 = cv2.VideoCapture("http://localhost:5000/video_feed2")

print("where2")

# 각각의 카메라를 독립적인 스레드에서 처리
thread0 = threading.Thread(target=capture_camera, args=(cap0, 'frame0'))
thread1 = threading.Thread(target=capture_camera, args=(cap1, 'frame1'))

# 스레드 시작
thread0.start()
thread1.start()

# 스레드가 종료될 때까지 대기
thread0.join()
thread1.join()

# 모든 창 닫기
cv2.destroyAllWindows()
