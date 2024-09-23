import numpy as np
import matplotlib.pyplot as plt
from utils import DLT
plt.style.use('seaborn-v0_8')


pose_keypoints = np.array([20, 16, 14, 12, 11, 13, 15, 24, 23, 25, 26, 27, 28])
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

        # print(len(line))
        # print()
        #print([row[0] for row in line])

        kpts.append(line)

    kpts = np.array(kpts)
    print(kpts)
    return kpts


def visualize_3d(p3ds):

    """Now visualize in 3D"""
    torso = [[0, 1] , [1, 8], [8, 7], [7, 0]]
    armr = [[1, 3], [3, 5], [5, 6]]
    arml = [[0, 2], [2, 4]]
    legr = [[8, 10], [10, 12]]
    legl = [[7, 9], [9, 11]]
    body = [torso, arml, armr, legl, legr]
    colors = ['red', 'blue', 'green', 'black', 'orange']

    from mpl_toolkits.mplot3d import Axes3D

    fig = plt.figure()
    ## 1 by 1 공간 만들어서 그래프 1개 생성
    ax = fig.add_subplot(111, projection='3d')

    #프레임마다 저장한 LandMark 별 좌표값 매겨서 저장
    for framenum, kpts3d in enumerate(p3ds):
        #절반은 스킵
        if framenum%2 == 0: continue #skip every 2nd frame
        #색 입히기: 굳이 필요 없음
        for bodypart, part_color in zip(body, colors):
            for _c in bodypart:
                #좌표 적용
                ax.plot(xs = [kpts3d[_c[0],0], kpts3d[_c[1],0]], ys = [kpts3d[_c[0],1], kpts3d[_c[1],1]], zs = [kpts3d[_c[0],2], kpts3d[_c[1],2]], linewidth = 4, c = part_color)
                xs = [kpts3d[_c[0],0], kpts3d[_c[1],0]]
                ys = [kpts3d[_c[0],1], kpts3d[_c[1],1]]
                zs = [kpts3d[_c[0],2], kpts3d[_c[1],2]]
                # print(xs, ys, zs)
                



        #자체 넘버링 매겨주는 코드
        #uncomment these if you want scatter plot of keypoints and their indices.
        for i in range(13):
            ax.text(kpts3d[i,0], kpts3d[i,1], kpts3d[i,2], str(round(kpts3d[i,0],3)))
            ax.scatter(xs = kpts3d[i:i+1,0], ys = kpts3d[i:i+1,1], zs = kpts3d[i:i+1,2])
        ax.set_axis_off()
        #자체 넘버링 매겨주는 코드 = 여기 까지


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

    p3ds = read_keypoints('kpts_3d_AddDot.dat')
    #print(p3ds)
    visualize_3d(p3ds)
