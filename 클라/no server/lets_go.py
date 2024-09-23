#초기 작업 틀

import cv2 as cv
import mediapipe as mp
import numpy as np
import sys
from utils import DLT, get_projection_matrix

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

frame_shape = [720, 1280]

# add here if you need more keypoints
pose_keypoints = [20, 16, 14, 12, 11, 13, 15, 24, 23, 25, 26, 27, 28]

import numpy as np

import numpy as np

# Function to 
def project_point_onto_plane(point, plane_point, normal):
    vector = point - plane_point
    distance = np.dot(vector, normal) / np.linalg.norm(normal)
    projected_point = point - distance * normal / np.linalg.norm(normal)
    return projected_point

# calculate angle between ab and bc project a point onto the plane1
def calculate_angle0(A, B, C):
    # Calculate B0 based on B
    B0 = np.array([B[0], B[1], B[2] - 10])
    
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
    # Calculate B0 based on B
    B0 = np.array([B[0], B[1], B[2] - 10])
    
    # Calculate normal vector of plane 1
    AB = B - A
    AB0 = B0 - A
    normal_vector_1 = np.cross(AB, AB0)

    # Calculate normal vector of plane 2
    normal_vector_2 = np.cross(normal_vector_1, [0, 0, 1])

    # Project point C onto Plane 2
    C_proj_on_plane_2 = project_point_onto_plane(C, B, normal_vector_2)

    # Calculate vectors
    BC_proj_on_plane_2_vector = C_proj_on_plane_2 - B
    BB0_vector = B0 - B

    # Calculate the angle between BC_proj_on_plane_2_vector and BB0_vector
    dot_product = np.dot(BC_proj_on_plane_2_vector, BB0_vector)
    norms_product = np.linalg.norm(BC_proj_on_plane_2_vector) * np.linalg.norm(BB0_vector)
    cos_theta = dot_product / norms_product
    theta = np.arccos(cos_theta)

    # Convert radians to degrees
    theta_degrees = np.degrees(theta)
    return theta_degrees

# calculateangle between ab and bc
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

    """Now visualize in 3D"""
    torso = [[0, 1] , [1, 8], [8, 7], [7, 0]]
    armr = [[1, 3], [3, 5], [5, 6]]
    arml = [[0, 2], [2, 4]]
    legr = [[8, 10], [10, 12]]
    legl = [[7, 9], [9, 11]]

    #현재는 오른팔을 타겟으로 잡음
    target = [0,1,3,5,6]
    body = [target]

    #지금은 필요없음
    colors = ['red', 'blue', 'green', 'black', 'orange']
    for bodypart in body:
        for _c in bodypart:
            #좌표 적용 예시
            a = _c[0]
            b = _c[1]
            c = _c[2]
            d = _c[3]
            e = _c[4]
            #여기 부터 추가로 구현해야 하는 곳
            angle = []
            angle.append(calculate_angle0(a,b,c))
            angle.append(calculate_angle1(a,b,c))
            angle.append(calculate_angle2(b,c,d))
            angle.append(calculate_angle2(c,d,e))



def run_mp(input_stream1, input_stream2, P0, P1):
    # input video stream
    cap0 = cv.VideoCapture(input_stream1)
    cap1 = cv.VideoCapture(input_stream2)
    caps = [cap0, cap1]

    # set camera resolution if using webcam to 1280x720. Any bigger will cause some lag for hand detection
    for cap in caps:
        cap.set(3, frame_shape[1])
        cap.set(4, frame_shape[0])

    # create body keypoints detector objects.
    pose0 = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    pose1 = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    while True:
        # read frames from stream
        ret0, frame0 = cap0.read()
        ret1, frame1 = cap1.read()

        if not ret0 or not ret1: break

        # crop to 720x720.
        # Note: camera calibration parameters are set to this resolution. If you change this, make sure to also change camera intrinsic parameters
        if frame0.shape[1] != 720:
            frame0 = frame0[:, frame_shape[1] // 2 - frame_shape[0] // 2:frame_shape[1] // 2 + frame_shape[0] // 2]
            frame1 = frame1[:, frame_shape[1] // 2 - frame_shape[0] // 2:frame_shape[1] // 2 + frame_shape[0] // 2]

        # the BGR image to RGB.
        frame0 = cv.cvtColor(frame0, cv.COLOR_BGR2RGB)
        frame1 = cv.cvtColor(frame1, cv.COLOR_BGR2RGB)

        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        frame0.flags.writeable = False
        frame1.flags.writeable = False
        results0 = pose0.process(frame0)
        results1 = pose1.process(frame1)

        # reverse changes
        frame0.flags.writeable = True
        frame1.flags.writeable = True
        frame0 = cv.cvtColor(frame0, cv.COLOR_RGB2BGR)
        frame1 = cv.cvtColor(frame1, cv.COLOR_RGB2BGR)

        # check for keypoints detection
        frame0_keypoints = []
        if results0.pose_landmarks:
            for i, landmark in enumerate(results0.pose_landmarks.landmark):
                if i not in pose_keypoints: continue  # only save keypoints that are indicated in pose_keypoints
                pxl_x = landmark.x * frame0.shape[1]
                pxl_y = landmark.y * frame0.shape[0]
                pxl_x = int(round(pxl_x))
                pxl_y = int(round(pxl_y))
                cv.circle(frame0, (pxl_x, pxl_y), 3, (0, 0, 255), -1)  # add keypoint detection points into figure
                kpts = [pxl_x, pxl_y]
                frame0_keypoints.append(kpts)
        else:
            # if no keypoints are found, simply fill the frame data with [-1,-1] for each kpt
            frame0_keypoints = [[-1, -1]] * len(pose_keypoints)

        frame1_keypoints = []
        if results1.pose_landmarks:
            for i, landmark in enumerate(results1.pose_landmarks.landmark):
                if i not in pose_keypoints: continue
                pxl_x = landmark.x * frame1.shape[1]
                pxl_y = landmark.y * frame1.shape[0]
                pxl_x = int(round(pxl_x))
                pxl_y = int(round(pxl_y))
                cv.circle(frame1, (pxl_x, pxl_y), 3, (0, 0, 255), -1)
                kpts = [pxl_x, pxl_y]
                frame1_keypoints.append(kpts)
        else:
            # if no keypoints are found, simply fill the frame data with [-1,-1] for each kpt
            frame1_keypoints = [[-1, -1]] * len(pose_keypoints)

        # calculate 3d position
        frame_p3ds = []
        for uv1, uv2 in zip(frame0_keypoints, frame1_keypoints):
            if uv1[0] == -1 or uv2[0] == -1:
                _p3d = [-1, -1, -1]
            else:
                _p3d = DLT(P0, P1, uv1, uv2)  # calculate 3d position of keypoint
            frame_p3ds.append(_p3d)

        # This contains the 3d position of each keypoint in current frame.
        # For real time application, this is what you want.
        frame_p3ds = np.array(frame_p3ds).reshape((13, 3))

        # uncomment these if you want to see the full keypoints detections
        # mp_drawing.draw_landmarks(frame0, results0.pose_landmarks, mp_pose.POSE_CONNECTIONS,
        #                           landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
        #
        # mp_drawing.draw_landmarks(frame1, results1.pose_landmarks, mp_pose.POSE_CONNECTIONS,
        #                           landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())

        cv.imshow('cam1', frame1)
        cv.imshow('cam0', frame0)

        # 3D 키포인트만 출력
        # print("3D Keypoints:", frame_p3ds)


        # _angle = list(calculate_3d(frame_p3ds))


        k = cv.waitKey(1)
        if k & 0xFF == 27: break  # 27 is ESC key.

    cv.destroyAllWindows()
    for cap in caps:
        cap.release()

if __name__ == '__main__':
    # this will load the sample videos if no camera ID is given
    input_stream1 = 'media/cam0_test.mp4'
    input_stream2 = 'media/cam1_test.mp4'

    # put camera id as command line arguments
    if len(sys.argv) == 3:
        input_stream1 = int(sys.argv[1])
        input_stream2 = int(sys.argv[2])

    # get projection matrices
    P0 = get_projection_matrix(0)
    P1 = get_projection_matrix(1)

    run_mp(input_stream1, input_stream2, P0, P1)
