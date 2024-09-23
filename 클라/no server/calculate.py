import numpy as np

# Function to calculate the angle between B -> B0 and B -> C_proj1 vectors
def calculate_angle(a, b, c):
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

# Example usage:
a = (12, 15, 17)
b = (10, 10, 15)
c = (4, 9, 10)

# Call the function
angle = calculate_angle(a, b, c)
print(f"The angle between the vectors is {angle:.2f} degrees.")
