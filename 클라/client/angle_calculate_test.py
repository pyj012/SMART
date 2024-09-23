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

if __name__ == '__main__':
    A = [10, 10, 10]
    B = [15, 15, 12]
    C = [16, 20, 4]

    #yzx=xyz
    angle1 = calculate_angle1(A, B, C)
    angle2 = calculate_angle2(A, B, C)
    angle3 = calculate_angle3(A, B, C)
    print(f"The angle between B0B and BCp2 is {angle1:.2f} degrees")
    print(f"The angle between B0B and BCp1 is {angle2:.2f} degrees")
    print(f"The angle between B-A and B--C is {angle3:.2f} degrees")

