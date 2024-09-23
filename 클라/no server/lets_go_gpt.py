import os
os.add_dll_directory('C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v11.8/bin')
os.add_dll_directory('C:/opencv/build/install/x64/vc16/bin')
os.add_dll_directory('C:/opencv/build/bin')

import cv2 as cv
import mediapipe as mp
import numpy as np
import sys
from utils_1 import DLT, get_projection_matrix

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

frame_shape = [720, 1280]

# add here if you need more keypoints
# pose_keypoints = [20, 16, 14, 12, 11, 13, 15, 24, 23, 25, 26, 27, 28]
pose_keypoints = [19, 20, 16, 14, 12, 11, 13, 15, 24, 23, 25, 26, 27, 28]

import numpy as np

# Function to project a point onto a plane
def project_point_onto_plane(point, plane_point, plane_normal):
    point = np.array(point)
    plane_point = np.array(plane_point)
    plane_normal = np.array(plane_normal)
    
    vec = point - plane_point
    distance = np.dot(vec, plane_normal) / np.linalg.norm(plane_normal)**2
    projection = point - distance * plane_normal
    return projection

# calculate angle between ab and bc project a point onto the plane1
# Function to calculate the signed angle between b->b0 and b->c_proj2
def calculate_angle1(a, b, c):
    # Create b0 by moving b -10 along the x-axis
    b0 = [b[0] - 10, b[1], b[2]]

    # Define the vector a-b and b-b0
    AB = np.array(b) - np.array(a)
    BB0 = np.array(b0) - np.array(b)

    # To make b1 perpendicular to both AB and BB0, we compute the cross product of these vectors
    perpendicular_vector = np.cross(AB, BB0)
    perpendicular_vector = perpendicular_vector / np.linalg.norm(perpendicular_vector)

    # Scale to make the z-coordinate of b1 equal to b's z + 10
    t = 10 / perpendicular_vector[2]
    b1 = np.array(b) + t * perpendicular_vector

    # Calculate the normal vector of the plane p2 (using points b0, b1, b)
    plane_normal = np.cross(np.array(b1) - np.array(b), np.array(b0) - np.array(b))

    # Project point c onto the plane p2
    c_proj2 = project_point_onto_plane(c, b, plane_normal)

    # Vector from b to b0 and b to c_proj2
    v_b_b0 = np.array(b0) - np.array(b)
    v_b_cproj2 = np.array(c_proj2) - np.array(b)

    # Compute the dot product and magnitudes
    dot_product = np.dot(v_b_b0, v_b_cproj2)
    magnitude_v_b_b0 = np.linalg.norm(v_b_b0)
    magnitude_v_b_cproj2 = np.linalg.norm(v_b_cproj2)

    # Compute the angle in radians
    angle_radians = np.arccos(dot_product / (magnitude_v_b_b0 * magnitude_v_b_cproj2))

    # Use the cross product to determine the sign of the angle
    cross_product = np.cross(v_b_b0, v_b_cproj2)
    if cross_product[1] > 0:  # Adjusted to check Y component for distinguishing the direction
        angle_radians = -angle_radians

    # Convert the angle to degrees
    angle_degrees = np.degrees(angle_radians)

    return angle_degrees

# calculate angle between ab and bc project a point onto the plane2
def calculate_angle2(a, b, c):
    b0 = [b[0] - 10, b[1], b[2]]  # Define b0 as b moved by -10 along x-axis

    # Define plane normal (using vectors AB and AB0)
    AB = np.array(b) - np.array(a)
    AB0 = np.array(b0) - np.array(a)
    plane_normal = np.cross(AB, AB0)

    # Project point c onto the plane p1
    c_proj1 = project_point_onto_plane(c, a, plane_normal)

    # Vector from b to b0 and b to c_proj1
    v1 = np.array(b0) - np.array(b)
    v2 = np.array(c_proj1) - np.array(b)

    # Compute the dot product and magnitudes
    dot_product = np.dot(v1, v2)
    magnitude_v1 = np.linalg.norm(v1)
    magnitude_v2 = np.linalg.norm(v2)

    # Compute the angle in radians and then convert to degrees
    angle_radians = np.arccos(dot_product / (magnitude_v1 * magnitude_v2))
    angle_degrees = np.degrees(angle_radians)

    return angle_degrees

# calculate angle between ab and bc
def calculate_angle3(a, b, c):
    # Convert points to numpy arrays
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    
    # Create vectors
    ab = b - a
    bc = c - b
    
    # Compute dot product and magnitudes
    dot_product = np.dot(ab, bc)
    magnitude_ab = np.linalg.norm(ab)
    magnitude_bc = np.linalg.norm(bc)
    
    # Calculate the cosine of the angle
    cos_theta = dot_product / (magnitude_ab * magnitude_bc)
    
    # Ensure the value is in the range [-1, 1] to avoid numerical errors
    cos_theta = np.clip(cos_theta, -1.0, 1.0)
    
    # Calculate the angle in radians and convert to degrees
    angle_radians = np.arccos(cos_theta)
    angle_degrees = np.degrees(angle_radians)
    
    return angle_degrees

def calculate_3d(kpts3d):
    # target = [kpts3d[0], kpts3d[1], kpts3d[3], kpts3d[5], kpts3d[7]]
    target = [kpts3d[0], kpts3d[1], kpts3d[2], kpts3d[3], kpts3d[4],kpts3d[5], kpts3d[6],kpts3d[7]]

    # a = list([round(kpts3d[0,0]),round(kpts3d[0,1]),round(kpts3d[0,2])])
    # b = list([round(kpts3d[1,0]),round(kpts3d[1,1]),round(kpts3d[1,2])])
    # c = list([round(kpts3d[3,0]),round(kpts3d[3,1]),round(kpts3d[3,2])])
    # d = list([round(kpts3d[2,0]),round(kpts3d[2,1]),round(kpts3d[2,2])])
    # print('a = ',a,'b = ',b,'c = ',c,'d = ',d)
    # print('[',a,',',b,',',c,',',d,'],')
    
    angles = list()

    angles.append(calculate_angle1(target[0], target[1], target[3]))
    angles.append(calculate_angle2(target[0], target[1], target[3]))
    angles.append(calculate_angle3(target[1], target[3], target[5]))
    angles.append(calculate_angle3(target[3], target[5], target[7]))

    angles.append(calculate_angle1(target[1], target[0], target[2]))
    angles.append(calculate_angle2(target[1], target[0], target[2]))
    angles.append(calculate_angle3(target[0], target[2], target[4]))
    angles.append(calculate_angle3(target[2], target[4], target[6]))

    
    return angles

def run_mp(input_stream1, input_stream2, P0, P1):
    cap0 = cv.VideoCapture(input_stream1)
    cap1 = cv.VideoCapture(input_stream2)
    caps = [cap0, cap1]

    # for cap in caps:
    #     cap.set(3, frame_shape[1])
    #     cap.set(4, frame_shape[0])

    pose0 = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    pose1 = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    kpts_cam0 = []
    kpts_cam1 = []
    kpts_3d = []

    while True:
        ret0, frame0 = cap0.read()
        ret1, frame1 = cap1.read()

        if not ret0 or not ret1:
            break

        # if frame0.shape[1] != 720:
        #     frame0 = frame0[:, frame_shape[1] // 2 - frame_shape[0] // 2:frame_shape[1] // 2 + frame_shape[0] // 2]
        #     frame1 = frame1[:, frame_shape[1] // 2 - frame_shape[0] // 2:frame_shape[1] // 2 + frame_shape[0] // 2]

        frame0 = cv.cvtColor(frame0, cv.COLOR_BGR2RGB)
        frame1 = cv.cvtColor(frame1, cv.COLOR_BGR2RGB)

        frame0.flags.writeable = False
        frame1.flags.writeable = False
        results0 = pose0.process(frame0)
        results1 = pose1.process(frame1)

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

        kpts_cam1.append(frame1_keypoints)

        frame_p3ds = []
        for uv1, uv2 in zip(frame0_keypoints, frame1_keypoints):
            if uv1[0] == -1 or uv2[0] == -1:
                _p3d = [-1, -1, -1]
            else:
                _p3d = DLT(P0, P1, uv1, uv2)
            frame_p3ds.append(_p3d)

        frame_p3ds = np.array(frame_p3ds).reshape((len(pose_keypoints), 3))

        # print('[',frame_p3ds[0],frame_p3ds[1],frame_p3ds[3],'],')
        '''여기까진 정상!!!'''
        print(frame_p3ds)

        _angle = calculate_3d(frame_p3ds)
        if _angle[0] < 0: _angle[0] = 0
        if _angle[4] < 0: _angle[4] = 0
        nameTag = ['R_shoulder','R_shoulder','R_elbow','R_wrist','L_shoulder','L_shoulder','L_elbow','L_wrist']
        # Draw angles on frame
        for i, (name, angle) in enumerate(zip(nameTag,_angle)):
            text = f'Angle {name}: {angle:.2f}'
            cv.putText(frame0, text, (10, 30 + i * 30), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv.LINE_AA)


        # cv.imshow('cam1', frame1)
        # cv.imshow('cam0', frame0)

        frame0_resized = cv.resize(frame0, (1280, 720))
        frame1_resized = cv.resize(frame1, (1280, 720))

        # 리사이즈된 프레임을 imshow로 출력
        cv.imshow('Camera 2 - 720p', frame1_resized)
        cv.imshow('Camera 1 - 720p', frame0_resized)

        k = cv.waitKey(1)
        if k & 0xFF == 27:
            break

    cv.destroyAllWindows()
    for cap in caps:
        cap.release()

if __name__ == '__main__':
    input_stream1 = 0#'media/cam0_test.mp4'
    input_stream2 = 2#'media/cam1_test.mp4'

    if len(sys.argv) == 3:
        input_stream1 = int(sys.argv[1])
        input_stream2 = int(sys.argv[2])

    P0 = get_projection_matrix(0)
    P1 = get_projection_matrix(1)

    run_mp(input_stream1, input_stream2, P0, P1)
