import numpy as np

# Function to project a point onto a plane
def project_point_onto_plane(point, plane_point, plane_normal):
    point_vector = np.array(point) - np.array(plane_point)
    distance = np.dot(point_vector, plane_normal) / np.linalg.norm(plane_normal)
    projection = np.array(point) - distance * (plane_normal / np.linalg.norm(plane_normal))
    return projection

def calculate_angle_with_direction(v1, v2, normal_vector):
    # Calculate the angle using dot product
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    angle_radians = np.arccos(dot_product / (norm_v1 * norm_v2))

    # Use cross product to determine the direction (sign of the angle)
    cross_product = np.cross(v1, v2)
    if np.dot(cross_product, normal_vector) < 0:
        angle_radians = -angle_radians  # Clockwise direction, negative angle

    angle_degrees = np.degrees(angle_radians)  # Convert to degrees
    return angle_degrees

def calculate_b1(a, b, b0):
    # Calculate the normal vector (n) perpendicular to both a-b and b-b0
    ab = np.array(b) - np.array(a)
    b_b0 = np.array(b0) - np.array(b)
    normal_vector = np.cross(ab, b_b0)
    
    # Unit direction vector for the normal line
    normal_unit_vector = normal_vector / np.linalg.norm(normal_vector)
    
    # Define z = b[2] + 20 and solve for t using the z-component of the line equation
    delta_z = 20  # The difference in z-coordinate (b1's z value is b's z + 20)
    t = delta_z / normal_unit_vector[2]  # Solve for t using the z-component

    # Calculate the coordinates of b1
    b1 = np.array(b) + t * normal_unit_vector
    return b1

def calculate_angle1(a, b, c):
    # b0 point is created by adding 20 to the y-coordinate of b
    b0 = [b[0], b[1] + 20, b[2]]

    # Calculate b1 (the point where the line is perpendicular to both a-b and b-b0)
    b1 = calculate_b1(a, b, b0)

    # Define the normal of the plane using b, b0, b1 to create plane p2
    b_b0 = np.array(b0) - np.array(b)
    b_b1 = np.array(b1) - np.array(b)
    normal_p2 = np.cross(b_b0, b_b1)

    # Project point c onto the plane p2 (defined by b, b0, b1)
    c_proj2 = project_point_onto_plane(c, b, normal_p2)

    # Calculate the angle between b -> b0 and b -> c_proj2
    b_to_c_proj2 = np.array(c_proj2) - np.array(b)
    b_to_b0 = np.array(b0) - np.array(b)
    
    # Calculate angle1 with directionality
    angle1 = calculate_angle_with_direction(b_to_b0, b_to_c_proj2, normal_p2)
    
    return -angle1

def calculate_angle2(a, b, c):
    # b0 point is created by adding 20 to the y-coordinate of b
    b0 = [b[0], b[1] + 20, b[2]]

    # Define the normal of the plane using vectors from a to b and a to b0
    ab = np.array(b) - np.array(a)
    ab0 = np.array(b0) - np.array(a)
    normal = np.cross(ab, ab0)  # Compute the normal of the plane

    # Project point c onto the plane defined by a, b, and b0
    c_proj1 = project_point_onto_plane(c, a, normal)

    # Calculate the angle between b -> c_proj1 and b -> b0
    b_to_c_proj1 = np.array(c_proj1) - np.array(b)
    b_to_b0 = np.array(b0) - np.array(b)
    
    # Calculate angle2 with directionality
    angle2 = calculate_angle_with_direction(b_to_c_proj1, b_to_b0, normal)
    
    return angle2

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
    # target = kpts3d[:8]
    target = [kpts3d[0], kpts3d[1], kpts3d[2], kpts3d[3], kpts3d[4],kpts3d[5], kpts3d[6],kpts3d[7]]

    angles = list()
    # for key , val in enumerate(target,start=1):
    angles.append(round(calculate_angle1(target[0], target[1], target[3])))
    angles.append(round(calculate_angle2(target[0], target[1], target[3])))
    angles.append(round(calculate_angle3(target[1], target[3], target[5])))
    angles.append(round(calculate_angle3(target[3], target[5], target[7])))

    angles.append(round(calculate_angle1(target[1], target[0], target[2])))
    angles.append(round(calculate_angle2(target[1], target[0], target[2])))
    angles.append(round(calculate_angle3(target[0], target[2], target[4])))
    angles.append(round(calculate_angle3(target[2], target[4], target[6])))
    
    #소수점 제거
    # for i in range(len(angles)):
    #     angles[i] = round(angles[i])

    return angles

def _make_homogeneous_rep_matrix(R, t):
    P = np.zeros((4,4))
    P[:3,:3] = R
    P[:3, 3] = t.reshape(3)
    P[3,3] = 1
    return P

#direct linear transform
def DLT(P1, P2, point1, point2):

    A = [point1[1]*P1[2,:] - P1[1,:],
         P1[0,:] - point1[0]*P1[2,:],
         point2[1]*P2[2,:] - P2[1,:],
         P2[0,:] - point2[0]*P2[2,:]
        ]
    A = np.array(A).reshape((4,4))
    #print('A: ')
    #print(A)

    B = A.transpose() @ A
    from scipy import linalg
    U, s, Vh = linalg.svd(B, full_matrices = False)

    #print('Triangulated point: ')
    #print(Vh[3,0:3]/Vh[3,3])
    return Vh[3,0:3]/Vh[3,3]

def read_camera_parameters(camera_id):

    inf = open('camera_parameters/c' + str(camera_id) + '.dat', 'r')

    cmtx = []
    dist = []

    line = inf.readline()
    for _ in range(3):
        line = inf.readline().split()
        line = [float(en) for en in line]
        cmtx.append(line)

    line = inf.readline()
    line = inf.readline().split()
    line = [float(en) for en in line]
    dist.append(line)

    return np.array(cmtx), np.array(dist)

def read_rotation_translation(camera_id, savefolder = 'camera_parameters/'):

    inf = open(savefolder + 'rot_trans_c'+ str(camera_id) + '.dat', 'r')

    inf.readline()
    rot = []
    trans = []
    for _ in range(3):
        line = inf.readline().split()
        line = [float(en) for en in line]
        rot.append(line)

    inf.readline()
    for _ in range(3):
        line = inf.readline().split()
        line = [float(en) for en in line]
        trans.append(line)

    inf.close()
    return np.array(rot), np.array(trans)

def _convert_to_homogeneous(pts):
    pts = np.array(pts)
    if len(pts.shape) > 1:
        w = np.ones((pts.shape[0], 1))
        return np.concatenate([pts, w], axis = 1)
    else:
        return np.concatenate([pts, [1]], axis = 0)

def get_projection_matrix(camera_id):

    #read camera parameters
    cmtx, dist = read_camera_parameters(camera_id)
    rvec, tvec = read_rotation_translation(camera_id)

    #calculate projection matrix
    P = cmtx @ _make_homogeneous_rep_matrix(rvec, tvec)[:3,:]
    return P

def write_keypoints_to_disk(filename, kpts):
    fout = open(filename, 'w')

    for frame_kpts in kpts:
        for kpt in frame_kpts:
            if len(kpt) == 2:
                fout.write(str(kpt[0]) + ' ' + str(kpt[1]) + ' ')
            else:
                fout.write(str(kpt[0]) + ' ' + str(kpt[1]) + ' ' + str(kpt[2]) + ' ')

        fout.write('\n')
    fout.close()

# def set_limit(L, H, value):
#     if value<L:
#         value = L
#     if value>H:
#         value = H
#     return round(value)

if __name__ == '__main__':

    P2 = get_projection_matrix(0)
    P1 = get_projection_matrix(1)
