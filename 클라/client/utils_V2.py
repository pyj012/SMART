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
