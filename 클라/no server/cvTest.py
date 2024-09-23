import cv2

def main():
    # 카메라 열기 (기본 카메라를 열거나, 카메라 번호를 지정할 수 있음)
    cap = cv2.VideoCapture(1)  # 0은 기본 카메라를 의미, 만약 다른 카메라를 사용하려면 카메라 번호를 변경하세요.

    if not cap.isOpened():
        print("카메라를 열 수 없습니다.")
        return

    while True:
        # 카메라에서 프레임 읽기
        ret, frame = cap.read()

        if not ret:
            print("프레임을 읽을 수 없습니다.")
            break

        # 프레임 화면에 표시
        cv2.imshow('Camera', frame)

        # 'q' 키를 누르면 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 종료 후 해제
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
