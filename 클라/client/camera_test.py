import cv2

cam1 = cv2.VideoCapture(0)
cam2 = cv2.VideoCapture(1)
cam3 = cv2.VideoCapture(2)
cam1.set(cv2.CAP_PROP_FRAME_HEIGHT, 640)
cam1.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
cam2.set(cv2.CAP_PROP_FRAME_HEIGHT, 640)
cam2.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
cam3.set(cv2.CAP_PROP_FRAME_HEIGHT, 640)
cam3.set(cv2.CAP_PROP_FRAME_WIDTH, 480)

while cv2.waitKey(33)<0:
    ret,frame1 = cam1.read()
    ret,frame2 = cam2.read()
    ret,frame3 = cam3.read()
    cv2.imshow("cam1", frame1)   
    cv2.imshow("cam2", frame2)
    cv2.imshow("cam3", frame3)

cam1.release()
cam2.release()
cam3.release()
cv2.destroyAllWindows()
