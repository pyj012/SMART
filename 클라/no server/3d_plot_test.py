import numpy as np

# Function to project point onto a plane
def project_point_onto_plane(point, plane_point, plane_normal):
    point = np.array(point)
    plane_point = np.array(plane_point)
    plane_normal = np.array(plane_normal)

    # Vector from the plane point to the point
    vec = point - plane_point

    # Project vec onto the plane normal
    distance = np.dot(vec, plane_normal) / np.linalg.norm(plane_normal)**2

    # The projected point is the original point minus the projection along the normal
    projection = point - distance * plane_normal
    return projection

# Function to calculate the signed angle between b->b0 and b->c_proj2
def calculate_signed_angle_b0_cproj2_v2(a, b, c):
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
    if cross_product[1] >= 0:  # Adjusted to check Y component for distinguishing the direction
        angle_radians = -angle_radians

    # Convert the angle to degrees
    angle_degrees = np.degrees(angle_radians)

    return angle_degrees

# Example usage:
a = [6, 3, 16]
b = [6, -1, 16]
c1 = [3, -2, 18]
c2 = [3, -2, 14]

# Call the function to calculate the signed angles
angle_coords1_v2 = calculate_signed_angle_b0_cproj2_v2(a, b, c1)
angle_coords2_v2 = calculate_signed_angle_b0_cproj2_v2(a, b, c2)

print(f"Angle for coords1: {angle_coords1_v2:.2f} degrees")
print(f"Angle for coords2: {angle_coords2_v2:.2f} degrees")
