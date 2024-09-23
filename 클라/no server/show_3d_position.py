import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

pose_keypoints = np.array([16, 14, 12, 11, 13, 15, 24, 23, 25, 26, 27, 28])
print(pose_keypoints)

def read_keypoints(filename):
    fin = open(filename, 'r')

    kpts = []
    while(True):
        line = fin.readline()
        if line == '': break

        line = line.split()
        line = [float(s) for s in line]

        # 여기서 line은 12개의 xyz 좌표가 일렬로 놓여져있는 상태 총 36개
        line = np.reshape(line, (len(pose_keypoints), -1))

        # 여기서 line은 12개의 xyz 좌표가 묶음으로 놓여져있는 상태 총 12*3 상태
        kpts.append(line)

    kpts = np.array(kpts)
    print(kpts)
    return kpts


def visualize_3d(p3ds):

    """Now visualize in 3D"""
    torso = [[0, 1] , [1, 7], [7, 6], [6, 0]]
    armr = [[1, 3], [3, 5]]
    arml = [[0, 2], [2, 4]]
    legr = [[7, 9], [9, 11]]
    legl = [[6, 8], [8, 10]]
    body = [torso, arml, armr, legl, legr]
    colors = ['red', 'blue', 'green', 'black', 'orange']

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    for framenum, kpts3d in enumerate(p3ds):
        if framenum % 2 == 0: continue  # Skip every 2nd frame
        for bodypart, part_color in zip(body, colors):
            for _c in bodypart:
                ax.plot(xs=[kpts3d[_c[0], 0], kpts3d[_c[1], 0]],
                        ys=[kpts3d[_c[0], 1], kpts3d[_c[1], 1]],
                        zs=[kpts3d[_c[0], 2], kpts3d[_c[1], 2]],
                        linewidth=4, c=part_color)

        # 좌표 표시
        # for i in range(13):
        #     ax.text(kpts3d[i, 0], kpts3d[i, 1], kpts3d[i, 2], f'{i}: ({kpts3d[i, 0]:.2f}, {kpts3d[i, 1]:.2f}, {kpts3d[i, 2]:.2f})', fontsize=8)
        #     ax.scatter(xs=kpts3d[i:i+1, 0], ys=kpts3d[i:i+1, 1], zs=kpts3d[i:i+1, 2])

        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_zticks([])

        ax.set_xlim3d(-10, 10)
        ax.set_xlabel('x')
        ax.set_ylim3d(-10, 10)
        ax.set_ylabel('y')
        ax.set_zlim3d(-10, 10)
        ax.set_zlabel('z')
        plt.pause(0.1)
        ax.cla()


if __name__ == '__main__':
    p3ds = read_keypoints('kpts_3d.dat')
    visualize_3d(p3ds)
