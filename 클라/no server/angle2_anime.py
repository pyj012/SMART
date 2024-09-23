import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

# Function to project point onto a plane
def project_point_onto_plane(point, plane_point, plane_normal):
    point = np.array(point)
    plane_point = np.array(plane_point)
    plane_normal = np.array(plane_normal)
    
    vec = point - plane_point
    distance = np.dot(vec, plane_normal) / np.linalg.norm(plane_normal)**2
    projection = point - distance * plane_normal
    return projection

# Define a function to create the plot for each set of coordinates with added points and angle calculation
def plot_coordinates_animation_with_angle(coordinate_sets, pause_time=0.5):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    for coords in coordinate_sets:
        a, b, c, d = coords
        b0 = [b[0] - 10, b[1], b[2]]

        # Clear the plot
        ax.cla()

        # Define plane normal (using a, b, b0)
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

        # Compute the angle in degrees
        angle_radians = np.arccos(dot_product / (magnitude_v1 * magnitude_v2))
        angle_degrees = np.degrees(angle_radians)

        # Plot points
        ax.scatter(a[0], a[1], a[2], color='r', label='Point A')
        ax.scatter(b[0], b[1], b[2], color='g', label='Point B')
        ax.scatter(b0[0], b0[1], b0[2], color='c', label='Point B0')
        ax.scatter(c[0], c[1], c[2], color='b', label='Point C')
        ax.scatter(c_proj1[0], c_proj1[1], c_proj1[2], color='m', label='Point C_proj1')

        # Annotate points with their names
        ax.text(a[0], a[1], a[2], 'A', color='red')
        ax.text(b[0], b[1], b[2], 'B', color='green')
        ax.text(b0[0], b0[1], b0[2], 'B0', color='cyan')
        ax.text(c[0], c[1], c[2], 'C', color='blue')
        ax.text(c_proj1[0], c_proj1[1], c_proj1[2], 'C_proj1', color='magenta')

        # Plot the connections
        ax.plot([a[0], b[0]], [a[1], b[1]], [a[2], b[2]], color='gray')  # Connect A and B
        ax.plot([b[0], c[0]], [b[1], c[1]], [b[2], c[2]], color='gray')  # Connect B and C
        ax.plot([a[0], d[0]], [a[1], d[1]], [a[2], d[2]], color='gray')  # Connect A and D
        ax.plot([b[0], b0[0]], [b[1], b0[1]], [b[2], b0[2]], color='cyan')  # Connect B and B0
        ax.plot([c_proj1[0], b[0]], [c_proj1[1], b[1]], [c_proj1[2], b[2]], color='magenta')  # Connect C_proj1 and B

        # Set labels
        ax.set_xlabel('X axis')
        ax.set_ylabel('Y axis')
        ax.set_zlabel('Z axis')

        # Update the title with the current angle
        ax.set_title(f'3D Plot with Angle: {angle_degrees:.2f} degrees')

        ax.set_xlim3d(-10, 10)
        ax.set_ylim3d(-10, 10)
        ax.set_zlim3d(-10, 10)

        # Add legend
        ax.legend()

        plt.draw()
        plt.pause(pause_time)  # Pause for the given interval

    plt.show()

# Complete list of coordinate sets (example from previous data)
coordinate_sets = [
[ [6, 8, 9] , [7, 10, 13] , [4, 11, 14] , [3, 8, 9] ],
[ [7, 8, 10] , [8, 8, 16] , [4, 8, 17] , [4, 8, 10] ],
[ [7, 7, 11] , [8, 7, 16] , [4, 7, 16] , [4, 8, 11] ],
[ [7, 6, 13] , [7, 5, 17] , [4, 5, 17] , [3, 7, 12] ],
[ [7, 5, 13] , [7, 4, 17] , [4, 4, 17] , [3, 6, 13] ],
[ [7, 5, 14] , [7, 2, 17] , [4, 2, 18] , [4, 6, 14] ],
[ [7, 4, 15] , [7, 1, 16] , [4, 0, 18] , [3, 5, 15] ],

[ [6, 3, 16] , [6, -1, 16] , [3, -2, 18] , [3, 4, 17] ],
[ [5, 2, 16] , [5, -1, 16] , [2, -2, 17] , [2, 3, 18] ],
[ [4, 2, 16] , [3, -2, 16] , [1, -3, 17] , [1, 3, 18] ],
[ [3, 2, 17] , [3, -2, 16] , [0, -3, 17] , [0, 2, 19] ],
[ [2, 2, 17] , [2, -2, 16] , [-1, -3, 18] , [0, 2, 19] ],
[ [2, 2, 17] , [2, -1, 16] , [-1, -3, 18] , [-1, 2, 19] ],
[ [2, 2, 17] , [2, -1, 16] , [-1, -2, 18] , [0, 2, 19] ],
[ [2, 2, 17] , [2, -1, 16] , [-1, -2, 18] , [0, 3, 19] ],
[ [2, 3, 17] , [2, 0, 15] , [-1, -2, 18] , [0, 3, 19] ],
[ [3, 4, 16] , [2, 0, 16] , [-1, -1, 18] , [0, 4, 18] ],
[ [3, 4, 16] , [2, 1, 16] , [0, -1, 18] , [0, 5, 18] ],
[ [3, 4, 17] , [2, 1, 16] , [0, 0, 18] , [0, 5, 18] ],
[ [3, 4, 17] , [2, 1, 16] , [0, 0, 18] , [0, 5, 18] ],
[ [3, 4, 17] , [2, 1, 16] , [0, 0, 18] , [0, 5, 19] ],
[ [2, 4, 17] , [2, 1, 17] , [0, -1, 18] , [0, 5, 20] ],
[ [2, 4, 18] , [2, 0, 17] , [-1, -1, 19] , [0, 6, 20] ],
[ [2, 4, 19] , [1, 0, 18] , [-1, -2, 20] , [0, 6, 20] ],
[ [2, 4, 19] , [2, 0, 19] , [-1, -2, 21] , [0, 6, 21] ],
[ [2, 3, 20] , [1, -1, 20] , [-1, -2, 21] , [0, 5, 20] ],
[ [2, 3, 20] , [1, -1, 20] , [-1, -2, 22] , [0, 5, 21] ],
[ [2, 3, 20] , [1, -1, 19] , [-1, -3, 20] , [0, 5, 21] ],
[ [2, 3, 20] , [2, -1, 19] , [-1, -2, 20] , [0, 4, 21] ],
[ [2, 3, 20] , [2, -1, 19] , [0, -2, 19] , [-1, 4, 21] ],
[ [2, 3, 20] , [2, -1, 19] , [0, -2, 19] , [-1, 4, 21] ],
[ [2, 3, 19] , [2, -1, 18] , [0, -3, 18] , [-1, 4, 20] ],
[ [2, 3, 18] , [2, -1, 17] , [-1, -3, 18] , [-1, 4, 20] ],
[ [2, 3, 18] , [2, -1, 17] , [-1, -3, 17] , [-1, 4, 19] ],
[ [2, 2, 18] , [2, -2, 17] , [-1, -3, 17] , [-1, 3, 19] ],
[ [2, 2, 18] , [2, -2, 16] , [-1, -3, 16] , [-1, 3, 18] ],
[ [2, 2, 17] , [2, -2, 16] , [-1, -3, 16] , [-1, 3, 18] ],
[ [2, 2, 17] , [2, -2, 16] , [-1, -3, 16] , [-1, 3, 18] ],
[ [2, 2, 17] , [2, -2, 15] , [-1, -3, 16] , [-1, 3, 18] ],
[ [2, 2, 16] , [2, -2, 15] , [-1, -3, 15] , [-1, 3, 17] ],
[ [2, 2, 16] , [2, -1, 15] , [-1, -2, 15] , [-1, 4, 17] ],
[ [2, 3, 16] , [2, -1, 15] , [-1, -2, 15] , [-1, 4, 17] ],
[ [2, 3, 16] , [2, -1, 16] , [-1, -2, 16] , [-1, 4, 18] ],
[ [2, 3, 17] , [2, -1, 16] , [-1, -2, 17] , [-1, 4, 18] ],
[ [2, 3, 17] , [2, -1, 16] , [-1, -2, 17] , [-1, 5, 18] ],
[ [2, 3, 17] , [2, 0, 16] , [-1, -2, 17] , [0, 5, 18] ],
[ [2, 4, 17] , [2, 0, 16] , [0, -2, 17] , [0, 5, 18] ],
[ [2, 4, 17] , [2, 0, 16] , [0, -2, 16] , [0, 6, 17] ],
[ [2, 4, 16] , [2, 0, 15] , [0, -2, 15] , [0, 6, 16] ],
[ [2, 4, 15] , [2, 0, 14] , [0, -2, 15] , [0, 6, 16] ],
[ [3, 4, 14] , [3, 0, 13] , [0, -1, 14] , [0, 6, 15] ],
[ [4, 4, 14] , [4, 0, 13] , [1, -1, 14] , [2, 5, 14] ],
[ [6, 4, 14] , [6, 0, 13] , [3, -1, 13] , [3, 5, 15] ],
[ [7, 4, 14] , [7, 0, 13] , [4, -1, 13] , [5, 6, 15] ],
[ [7, 4, 14] , [7, 0, 13] , [5, -2, 13] , [5, 6, 15] ],
[ [7, 4, 14] , [7, 0, 13] , [6, -3, 13] , [6, 7, 14] ],
[ [7, 4, 14] , [7, 0, 13] , [6, -3, 13] , [7, 7, 15] ],
[ [7, 4, 14] , [7, 0, 13] , [6, -3, 13] , [7, 7, 14] ],
[ [7, 4, 14] , [7, 0, 13] , [6, -2, 12] , [7, 7, 14] ],
[ [7, 4, 14] , [7, 0, 13] , [6, -3, 12] , [7, 7, 14] ],
[ [7, 4, 14] , [7, 0, 13] , [6, -3, 13] , [7, 7, 14] ],
[ [7, 4, 14] , [7, 0, 13] , [6, -3, 13] , [7, 7, 14] ],
[ [7, 4, 14] , [7, 0, 13] , [6, -3, 13] , [7, 7, 14] ],
[ [7, 4, 14] , [7, 0, 13] , [6, -3, 13] , [7, 7, 14] ],
[ [7, 4, 14] , [7, 0, 13] , [6, -3, 13] , [6, 7, 14] ],
[ [6, 4, 13] , [6, 0, 13] , [4, -2, 13] , [4, 6, 14] ],
[ [5, 4, 13] , [5, 0, 13] , [2, -1, 13] , [2, 6, 14] ],
[ [4, 4, 13] , [4, 0, 13] , [1, -1, 14] , [1, 6, 14] ],
[ [3, 4, 14] , [2, 0, 13] , [0, -1, 14] , [0, 6, 15] ],
[ [2, 4, 14] , [2, 0, 14] , [0, -1, 14] , [0, 6, 15] ],
[ [2, 4, 15] , [2, 0, 14] , [-1, -2, 15] , [0, 6, 16] ],
[ [2, 4, 16] , [2, 0, 15] , [-1, -1, 16] , [0, 5, 17] ],
[ [2, 4, 17] , [2, 0, 16] , [-1, -1, 16] , [0, 5, 17] ],

[ [2, 4, 17] , [2, 0, 17] , [0, -2, 17] , [0, 5, 18] ],
[ [2, 4, 18] , [2, 0, 18] , [0, -2, 18] , [0, 5, 18] ],
[ [2, 4, 19] , [2, 0, 18] , [0, -2, 18] , [0, 5, 19] ],
[ [2, 4, 19] , [2, 0, 19] , [0, -2, 19] , [0, 5, 19] ],
[ [2, 4, 19] , [2, 0, 19] , [0, -1, 19] , [0, 5, 19] ],
[ [2, 4, 19] , [2, 0, 19] , [0, -1, 18] , [0, 5, 19] ],
[ [2, 4, 19] , [2, 0, 18] , [0, -2, 18] , [0, 5, 19] ],
[ [2, 4, 18] , [2, 0, 17] , [0, -2, 18] , [0, 6, 18] ],
[ [2, 4, 17] , [2, 0, 16] , [0, -2, 17] , [0, 6, 17] ],
[ [2, 4, 16] , [2, 0, 15] , [0, -2, 16] , [0, 6, 17] ],
[ [4, 4, 15] , [4, 0, 14] , [1, -2, 16] , [1, 5, 15] ],
[ [5, 3, 14] , [5, 0, 14] , [2, -1, 15] , [2, 4, 15] ],
[ [7, 3, 15] , [6, -1, 14] , [4, -1, 15] , [4, 4, 15] ],
[ [7, 3, 14] , [6, -1, 14] , [4, -2, 14] , [4, 4, 15] ],
[ [7, 3, 14] , [6, -1, 13] , [4, -2, 13] , [4, 4, 15] ],
[ [6, 4, 13] , [6, 0, 12] , [3, -1, 12] , [4, 4, 14] ],
[ [6, 4, 11] , [6, 0, 11] , [3, 0, 11] , [3, 5, 13] ],
[ [7, 5, 10] , [6, 2, 9] , [4, 1, 9] , [3, 6, 11] ],
[ [7, 6, 9] , [6, 2, 7] , [4, 1, 8] , [4, 7, 9] ],
[ [6, 7, 7] , [6, 3, 6] , [3, 2, 6] , [3, 8, 7] ]
]


# Call the function to animate with angle display
plot_coordinates_animation_with_angle(coordinate_sets, pause_time=0.1)
