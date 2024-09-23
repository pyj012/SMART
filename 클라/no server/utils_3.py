import numpy as np

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
def calculate_angle1(a, b, c):
    # Define points A, B, C
    A = np.array(a)
    B = np.array(b)
    C = np.array(c)
    
    # Define point B0 by shifting B's x-coordinate by -10
    B0 = np.array([B[0] - 10, B[1], B[2]])
    
    # Calculate the normal vector to the plane p1 (based on A, B, B0)
    AB_vector = B - A
    AB0_vector = B0 - A
    normal_vector = np.cross(AB_vector, AB0_vector)
    
    # Project point C onto the plane p1
    AC_vector = C - A
    dot_product = np.dot(AC_vector, normal_vector)
    normal_magnitude = np.linalg.norm(normal_vector)
    distance_to_plane = dot_product / normal_magnitude
    C_proj1 = C - (distance_to_plane * (normal_vector / normal_magnitude))
    
    # Define vectors B -> B0 and B -> C_proj1
    B0_vector = B0 - B
    BC_proj1_vector = C_proj1 - B
    
    # Calculate the dot product and magnitudes of the vectors
    dot_product = np.dot(B0_vector, BC_proj1_vector)
    B0_magnitude = np.linalg.norm(B0_vector)
    BC_proj1_magnitude = np.linalg.norm(BC_proj1_vector)
    
    # Calculate the angle in radians and convert to degrees
    cos_theta = dot_product / (B0_magnitude * BC_proj1_magnitude)
    theta_radians = np.arccos(cos_theta)
    theta_degrees = np.degrees(theta_radians)
    
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
    target = [kpts3d[0], kpts3d[1], kpts3d[2], kpts3d[3], kpts3d[4],kpts3d[5], kpts3d[6],kpts3d[7]]
    angles = list()
    # for key , val in enumerate(target,start=1):
    angles.append(0)#round(calculate_angle0(target[0], target[1], target[3])))
    angles.append(round(calculate_angle1(kpts3d[0], kpts3d[1], kpts3d[3])))
    print("a : ",kpts3d[0]," b : ",kpts3d[1]," c : ",kpts3d[3],"deg : ",calculate_angle1(kpts3d[0], kpts3d[1], kpts3d[3]))
    angles.append(0)#round(calculate_angle2(target[1], target[3], target[5])))
    angles.append(0)#round(calculate_angle2(target[3], target[5], target[7])))

    angles.append(0)#round(calculate_angle1(target[1], target[0], target[2])))
    angles.append(0)#round(calculate_angle0(target[1], target[0], target[2])))
    angles.append(0)#round(calculate_angle2(target[0], target[2], target[4])))
    angles.append(0)#round(calculate_angle2(target[2], target[4], target[6])))
    
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

if __name__ == '__main__':

    P2 = get_projection_matrix(0)
    P1 = get_projection_matrix(1)
