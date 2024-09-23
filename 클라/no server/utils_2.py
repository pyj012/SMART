import numpy as np

def calculate_angle1(A, B, C):
    # Define points as numpy arrays
    A = np.array(A)
    B = np.array(B)
    C = np.array(C)
    
    # Define B0 (Assuming B0 as the point given by B with z coordinate 2)
    B0 = np.array([B[0], B[1], 2])
    
    # Calculate vectors AB and AB0
    AB = B - A
    AB0 = B0 - A
    
    # Calculate the normal vector to plane P1
    normal_vector = np.cross(AB, AB0)
    
    # Calculate vector BC
    BC = C - B
    
    # Projection of BC onto the normal vector
    projection_length = np.dot(BC, normal_vector) / np.linalg.norm(normal_vector)
    projection_vector = projection_length * normal_vector / np.linalg.norm(normal_vector)
    
    # Calculate Cp1
    Cp1 = C - projection_vector
    
    # Calculate D (new point 4 units away from B0 along the normal vector)
    normalized_normal = normal_vector / np.linalg.norm(normal_vector)
    D = B0 + 4 * normalized_normal
    
    # Calculate vectors B0B and B0D
    B0B = B - B0
    B0D = D - B0
    
    # Calculate normal vector to the plane P2
    normal_vector_p2 = np.cross(B0B, B0D)
    
    # Calculate projection of BC onto the normal vector of P2
    projection_length_p2 = np.dot(BC, normal_vector_p2) / np.linalg.norm(normal_vector_p2)
    projection_vector_p2 = projection_length_p2 * normal_vector_p2 / np.linalg.norm(normal_vector_p2)
    
    # Calculate Cp2
    Cp2 = C - projection_vector_p2
    
    # Calculate vectors B0B and BCp2
    B0B_vector = B0 - B
    BCp2_vector = Cp2 - B
    
    # Calculate the dot product of the vectors
    dot_product = np.dot(B0B_vector, BCp2_vector)
    
    # Calculate the magnitudes of the vectors
    magnitude_B0B = np.linalg.norm(B0B_vector)
    magnitude_BCp2 = np.linalg.norm(BCp2_vector)
    
    # Calculate the angle in radians
    angle_radians = np.arccos(dot_product / (magnitude_B0B * magnitude_BCp2))
    
    # Convert the angle to degrees
    angle_degrees = np.degrees(angle_radians)
    
    return angle_degrees

def calculate_angle2(A, B, C):
    # Define the points
    A = np.array(A)
    B = np.array(B)
    C = np.array(C)
    
    # Define B0 (Assuming B0 as the point given by B with z coordinate 2)
    B0 = np.array([B[0], B[1], 2])
    
    # Calculate vectors
    AB = B - A
    AB0 = B0 - A
    
    # Normal vector to plane P1
    normal_vector = np.cross(AB, AB0)
    
    # Vector BC
    BC = C - B
    
    # Projection of BC onto the normal vector
    projection_length = np.dot(BC, normal_vector) / np.linalg.norm(normal_vector)
    projection_vector = projection_length * normal_vector / np.linalg.norm(normal_vector)
    
    # Calculate Cp1
    Cp1 = C - projection_vector
    
    # Vectors B0B and BCp1
    B0B_vector = B0 - B
    BCp1_vector = Cp1 - B
    
    # Calculate the angle between B0B and BCp1
    dot_product = np.dot(B0B_vector, BCp1_vector)
    magnitude_B0B = np.linalg.norm(B0B_vector)
    magnitude_BCp1 = np.linalg.norm(BCp1_vector)
    
    # Calculate the angle in radians
    angle_radians = np.arccos(dot_product / (magnitude_B0B * magnitude_BCp1))
    
    # Convert the angle to degrees
    angle_degrees = np.degrees(angle_radians)
    
    return angle_degrees

def calculate_angle3(A, B, C):
    # Define points as numpy arrays
    A = np.array(A)
    B = np.array(B)
    C = np.array(C)
    
    # Calculate vectors B-A and B-C
    BA = A - B
    BC = C - B
    
    # Calculate the dot product of the vectors
    dot_product = np.dot(BA, BC)
    
    # Calculate the magnitudes of the vectors
    magnitude_BA = np.linalg.norm(BA)
    magnitude_BC = np.linalg.norm(BC)
    
    # Calculate the angle in radians
    angle_radians = np.arccos(dot_product / (magnitude_BA * magnitude_BC))
    
    # Convert the angle to degrees
    angle_degrees = np.degrees(angle_radians)
    
    return angle_degrees

def calculate_3d(kpts3d):
    target = [kpts3d[0], kpts3d[1], kpts3d[2], kpts3d[3], kpts3d[4],kpts3d[5], kpts3d[6],kpts3d[7], kpts3d[8]]
    
    for i in target:
        # print(n," ",i)
        # print(i,end="")
        i = np.array([i[1], i[2], i[0]])
        # print(i)

    angles = []
    angles.append(calculate_angle1(target[0], target[1], target[3]))
    angles.append(calculate_angle2(target[0], target[1], target[3]))
    angles.append(calculate_angle3(target[1], target[3], target[5]))
    angles.append(calculate_angle3(target[3], target[5], target[7]))

    angles.append(calculate_angle1(target[1], target[0], target[2]))
    angles.append(calculate_angle2(target[1], target[0], target[2]))
    angles.append(calculate_angle3(target[0], target[2], target[4]))
    angles.append(calculate_angle3(target[2], target[4], target[6]))
    
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

if __name__ == '__main__':

    P2 = get_projection_matrix(0)
    P1 = get_projection_matrix(1)
