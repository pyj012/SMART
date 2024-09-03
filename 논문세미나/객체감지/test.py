import cv2
import os
import time
from PIL import Image
import numpy as np
# Set YOLOv8 to quiet mode
def map(x,input_min,input_max,output_min,output_max):
    return (x-input_min)*(output_max-output_min)/(input_max-input_min)+output_min #map()함수 정의.

os.environ['YOLO_VERBOSE'] = 'False'

from ultralytics import YOLO, solutions
model = YOLO("yolov8n.pt", verbose=False)
names = model.model.names
model.info(verbose=False)
model.predict(source="0", show=False, stream=True, classes=0)  # [0, 3, 5] for multiple classes

cap = cv2.VideoCapture(0)
assert cap.isOpened(), "Error reading video file"
w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))



distance50 = 1700

distance100 = 910

# Process results list

while cap.isOpened():
    success, im0 = cap.read()
    resultes= model(im0) 

    for result in resultes:
        boxes = result.boxes  # Boxes object for bbox outputs
        masks = result.masks  # Masks object for segmentation masks outputs
        keypoints = result.keypoints  # Keypoints object for pose outputs
        probs = result.probs  # Class probabilities for classification outputs
        bgr_array = result.plot()
        rgb_array = bgr_array[..., ::-1]
        output_image = Image.fromarray(rgb_array)
        # pil_image = Image.open(output_image).convert('RGB')
        open_cv_image = np.array(output_image)
        # Convert RGB to BGR
        open_cv_image = open_cv_image[:, :, ::-1].copy()
        # result_img = cv2.imread(img_path)



        for box in boxes:
            xyxylist = (box.xyxy[0]).tolist()
            x1 = round(xyxylist[0])
            y1 = round(xyxylist[1])

            if y1 <=5:
                y1 = y1 + 100
            else :
                y1 =y1+60
            # print(x1,y1)
            data = (box.xywh[0]).tolist()
            templist = []
            for value in data:
                templist.append(round(value,1))

            distance = round(map(templist[2], distance50, distance100, 50, 100),2)
            blue = (255, 0, 0)
            green= (0, 255, 0)
            red= (0, 0, 255)
            white= (255, 255, 255) 
            # 폰트 지정
            font =  cv2.FONT_HERSHEY_PLAIN
            
            # 이미지에 글자 합성하기
            open_cv_image = cv2.putText(open_cv_image, str(distance)+"cm", (x1, y1), font, 4, red, 5, cv2.LINE_AA)     
            cv2.imshow('test',open_cv_image)

        if cv2.waitKey(25) == ord('q'):
            print("동영상 종료")
            break


cv2.waitKey(0)
cap.release()
cv2.destroyAllWindows()