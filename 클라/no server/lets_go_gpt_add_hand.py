import cv2 as cv
import mediapipe as mp
import numpy as np
import sys
from utils import DLT, get_projection_matrix

# hand
max_num_hands = 1
gesture = {
    0:'fist', 1:'one', 2:'two', 3:'three', 4:'four', 5:'five',
    6:'six', 7:'rock', 8:'spiderman', 9:'yeah', 10:'ok',
}
grab = {0:'fist', 6:'six'}
mp_hands = mp.solutions.hands


mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

frame_shape = [720, 1280]

# add here if you need more keypoints
pose_keypoints = [20, 16, 14, 12, 11, 13, 15, 24, 23, 25, 26, 27, 28]


GRAP_VAL = 100
DROP_VAL = 10

# Function to project a point onto a plane
def project_point_onto_plane(point, plane_point, normal):
    vector = point - plane_point
    distance = np.dot(vector, normal) / np.linalg.norm(normal)
    projected_point = point - distance * normal / np.linalg.norm(normal)
    return projected_point

# calculate angle between ab and bc project a point onto the plane1
def calculate_angle0(A, B, C):
    # Calculate B0 based on B
    B0 = np.array([B[0]-1, B[1], B[2]])
    
    # Calculate normal vector of the plane
    AB = B - A
    AB0 = B0 - A
    normal_vector = np.cross(AB, AB0)

    # Project point C onto the plane
    C_proj = project_point_onto_plane(C, A, normal_vector)

    # Calculate vectors
    BC_proj_vector = C_proj - B
    BB0_vector = B0 - B

    # Calculate the angle between BC_proj_vector and BB0_vector
    dot_product = np.dot(BC_proj_vector, BB0_vector)
    norms_product = np.linalg.norm(BC_proj_vector) * np.linalg.norm(BB0_vector)
    cos_theta = dot_product / norms_product
    theta = np.arccos(cos_theta)

    # Convert radians to degrees
    theta_degrees = np.degrees(theta)
    return theta_degrees

# calculate angle between ab and bc project a point onto the plane2
def calculate_angle1(A, B, C):
    # Calculate B0 based on B (with x coordinate -10)
    B0 = np.array([B[0], B[1]-1, B[2]])
    
    # Calculate normal vector of plane 1
    AB = B - A
    AB0 = B0 - A
    normal_vector_1 = np.cross(AB, AB0)
    
    # yz 평면의 법선 벡터
    yz_normal_vector = np.array([0, 1, 0])
    
    # 평면 2의 법선 벡터는 평면 1의 법선 벡터와 yz 평면의 법선 벡터의 외적
    normal_vector_2 = np.cross(normal_vector_1, yz_normal_vector)

    # Project point C onto plane 2
    C_proj_to_plane2 = project_point_onto_plane(C, B, normal_vector_2)

    # Calculate vectors
    BB0_vector = B0 - B
    BC_proj_to_plane2_vector = C_proj_to_plane2 - B

    # Calculate the angle between BB0_vector and BC_proj_to_plane2_vector
    dot_product = np.dot(BB0_vector, BC_proj_to_plane2_vector)
    norms_product = np.linalg.norm(BB0_vector) * np.linalg.norm(BC_proj_to_plane2_vector)
    cos_theta = dot_product / norms_product
    theta = np.arccos(cos_theta)

    # Convert radians to degrees
    theta_degrees = np.degrees(theta)
    return theta_degrees


# calculate angle between ab and bc
def calculate_angle2(A, B, C):
    # Calculate vectors
    AB_vector = B - A
    BC_vector = C - B

    # Calculate the angle between AB_vector and BC_vector
    dot_product = np.dot(AB_vector, BC_vector)
    norms_product = np.linalg.norm(AB_vector) * np.linalg.norm(BC_vector)
    cos_theta = dot_product / norms_product
    theta = np.arccos(cos_theta)

    # Convert radians to degrees
    theta_degrees = np.degrees(theta)
    return theta_degrees

def calculate_3d(kpts3d):
    target = [kpts3d[0], kpts3d[1], kpts3d[3], kpts3d[5], kpts3d[6]]
    
    angles = list()
    angles.append(round(calculate_angle1(target[0], target[1], target[2])))
    angles.append(round(calculate_angle0(target[0], target[1], target[2])))
    angles.append(round(calculate_angle2(target[1], target[2], target[3])))
    angles.append(round(calculate_angle2(target[2], target[3], target[4])))
    
    #소수점 제거
    # for i in range(len(angles)):
    #     angles[i] = round(angles[i])

    return angles

def run_mp(input_stream1, input_stream2, P0, P1):

    # Gesture recognition model
    file = np.genfromtxt('data/gesture_train.csv', delimiter=',')
    angle = file[:,:-1].astype(np.float32)
    label = file[:, -1].astype(np.float32)
    knn = cv.ml.KNearest_create()
    knn.train(angle, cv.ml.ROW_SAMPLE, label)


    cap0 = cv.VideoCapture(input_stream1)
    cap1 = cv.VideoCapture(input_stream2)
    caps = [cap0, cap1]

    for cap in caps:
        cap.set(3, frame_shape[1])
        cap.set(4, frame_shape[0])

    pose0 = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    pose1 = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    # hand
    hand = mp_hands.Hands(max_num_hands=max_num_hands,min_detection_confidence=0.5,min_tracking_confidence=0.5)


    while True:
        ret0, frame0 = cap0.read()
        ret1, frame1 = cap1.read()

        if not ret0 or not ret1:
            print("카메라 에러")
            break

        if frame0.shape[1] != 720:
            frame0 = frame0[:, frame_shape[1] // 2 - frame_shape[0] // 2:frame_shape[1] // 2 + frame_shape[0] // 2]
            frame1 = frame1[:, frame_shape[1] // 2 - frame_shape[0] // 2:frame_shape[1] // 2 + frame_shape[0] // 2]

        frame0 = cv.cvtColor(frame0, cv.COLOR_BGR2RGB)
        frame1 = cv.cvtColor(frame1, cv.COLOR_BGR2RGB)

        frame0.flags.writeable = False
        frame1.flags.writeable = False
        results0 = pose0.process(frame0)
        results1 = pose1.process(frame1)

        # hand
        results2 = hand.process(frame0)

        frame0.flags.writeable = True
        frame1.flags.writeable = True
        frame0 = cv.cvtColor(frame0, cv.COLOR_RGB2BGR)
        frame1 = cv.cvtColor(frame1, cv.COLOR_RGB2BGR)

        frame0_keypoints = []
        if results0.pose_landmarks:
            for i, landmark in enumerate(results0.pose_landmarks.landmark):
                if i not in pose_keypoints:
                    continue
                pxl_x = landmark.x * frame0.shape[1]
                pxl_y = landmark.y * frame0.shape[0]
                pxl_x = int(round(pxl_x))
                pxl_y = int(round(pxl_y))
                cv.circle(frame0, (pxl_x, pxl_y), 3, (0, 0, 255), -1)
                kpts = [pxl_x, pxl_y]
                frame0_keypoints.append(kpts)
        else:
            frame0_keypoints = [[-1, -1]] * len(pose_keypoints)

        frame1_keypoints = []
        if results1.pose_landmarks:
            for i, landmark in enumerate(results1.pose_landmarks.landmark):
                if i not in pose_keypoints:
                    continue
                pxl_x = landmark.x * frame1.shape[1]
                pxl_y = landmark.y * frame1.shape[0]
                pxl_x = int(round(pxl_x))
                pxl_y = int(round(pxl_y))
                cv.circle(frame1, (pxl_x, pxl_y), 3, (0, 0, 255), -1)
                kpts = [pxl_x, pxl_y]
                frame1_keypoints.append(kpts)
        else:
            frame1_keypoints = [[-1, -1]] * len(pose_keypoints)

        
        # frame0_keypoints = []
        gripper_val = DROP_VAL
        if results2.multi_hand_landmarks:
            for res, hand_handedness in zip(results2.multi_hand_landmarks, results2.multi_handedness):
                if True:#hand_handedness.classification[0].label == 'Left':
                    joint = np.zeros((21, 3))
                    for j, lm in enumerate(res.landmark):
                        joint[j] = [lm.x, lm.y, lm.z]

                    # Compute angles between joints
                    v1 = joint[[0,1,2,3,0,5,6,7,0,9,10,11,0,13,14,15,0,17,18,19],:] # Parent joint
                    v2 = joint[[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20],:] # Child joint
                    v = v2 - v1 # [20,3]
                    # Normalize v
                    v = v / np.linalg.norm(v, axis=1)[:, np.newaxis]

                    # Get angle using arcos of dot product
                    angle = np.arccos(np.einsum('nt,nt->n',
                        v[[0,1,2,4,5,6,8,9,10,12,13,14,16,17,18],:], 
                        v[[1,2,3,5,6,7,9,10,11,13,14,15,17,18,19],:])) # [15,]

                    angle = np.degrees(angle) # Convert radian to degree

                    # Inference gesture
                    data = np.array([angle], dtype=np.float32)
                    ret, results, neighbours, dist = knn.findNearest(data, 3)
                    idx = int(results[0][0])

                    # Other gestures
                    if idx in grab.keys():
                        cv.putText(frame0, text="GRAB", org=(int(res.landmark[0].x * frame0.shape[1]), int(res.landmark[0].y * frame0.shape[0] + 20)), fontFace=cv.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(255, 255, 255), thickness=2)
                        gripper_val = GRAP_VAL
                    else:
                        cv.putText(frame0, text="DROP", org=(int(res.landmark[0].x * frame0.shape[1]), int(res.landmark[0].y * frame0.shape[0] + 20)), fontFace=cv.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(255, 255, 255), thickness=2)
                        gripper_val = DROP_VAL

                    # mp_drawing.draw_landmarks(frame0, res, mp_hands.HAND_CONNECTIONS)




        frame_p3ds = []
        for uv1, uv2 in zip(frame0_keypoints, frame1_keypoints):
            if uv1[0] == -1 or uv2[0] == -1:
                _p3d = [-1, -1, -1]
            else:
                _p3d = DLT(P0, P1, uv1, uv2)
            frame_p3ds.append(_p3d)

        frame_p3ds = np.array(frame_p3ds).reshape((13, 3))

        armr_angle = calculate_3d(frame_p3ds)

        armr_angle[0] = round(125+90+45-armr_angle[0])
        armr_angle[1] = round(90-armr_angle[1])
        armr_angle[2] = round(armr_angle[2])
        armr_angle[3] = round(125-armr_angle[3])

        armr_angle.append(gripper_val)
        _angle = dict(zip([1,2,3,4,6],armr_angle))
        
        print(_angle)

        # Draw angles on frame
        for i, angle in enumerate(_angle.values()):
            text = f'Angle {i+1}: {angle:.2f}'
            cv.putText(frame0, text, (10, 30 + i * 30), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv.LINE_AA)

        cv.imshow('cam1', frame1)
        cv.imshow('cam0', frame0)

        k = cv.waitKey(1)
        if k & 0xFF == 27:
            break

    cv.destroyAllWindows()
    for cap in caps:
        cap.release()

if __name__ == '__main__':
    input_stream1 = 0#'media/cam0_test.mp4'
    input_stream2 = 1#'media/cam1_test.mp4'

    if len(sys.argv) == 3:
        input_stream1 = int(sys.argv[1])
        input_stream2 = int(sys.argv[2])

    P0 = get_projection_matrix(0)
    P1 = get_projection_matrix(1)

    run_mp(input_stream1, input_stream2, P0, P1)
