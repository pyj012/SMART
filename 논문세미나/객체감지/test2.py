
rom ultralytics import YOLO
import cv2
# Load a model
model = YOLO('yolov8n.pt')  # pretrained YOLOv8n model
model.predict(source="0", show=True, stream=True, classes=0)  # [0, 3, 5] for multiple classes

# Define image file path
image_folder = 'C:\\aabb\\serch\\yolotest\\'

# Define image file names
image_file_1 = 'im1.jpg'
image_file_2 = 'im2.jpg'

# Construct full image file paths
image_path_1 = image_folder + image_file_1
image_path_2 = image_folder + image_file_2

# Run batched inference on a list of images
results = model([image_path_1, image_path_2])  # return a list of Results objects

# Process results list
for result in results:
    boxes = result.boxes  # Boxes object for bbox outputs
    masks = result.masks  # Masks object for segmentation masks outputs
    keypoints = result.keypoints  # Keypoints object for pose outputs
    probs = result.probs  # Class probabilities for classification outputs
    
    # Print box coordinates
    print("Box coordinates:")
    for box in boxes:
        print(box)

    # Display result with boxes
    result.plot()
    cv2.waitKey(0)
    cv2.destroyAllWindows()