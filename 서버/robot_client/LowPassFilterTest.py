import numpy as np
import matplotlib.pyplot as plt
import random
import math
import time
class LowPassFilter(object):
    def __init__(self, cut_off_freqency, ts):
    	# cut_off_freqency: 차단 주파수
        # ts: 주기
        
        self.ts = ts
        self.cut_off_freqency = cut_off_freqency
        self.tau = self.get_tau()

        self.prev_data = 0.
        
    def get_tau(self):
        return 1 / (2 * np.pi * self.cut_off_freqency)

    def filter(self, data):
        val = (self.ts * data + self.tau * self.prev_data) / (self.tau + self.ts)
        self.prev_data = val
        return val
    
class Sensor(object):
    def __init__(self):
        self.value = 10
        self.i = 0

    def noise(self):
        return random.randint(-10, 10) * 0.01

    def sense(self):
        self.i += 0.05
        return math.sin(self.i) + self.noise()


if __name__ == "__main__":

    xs = []
    sensors = []
    filters = []

    lpf = LowPassFilter(0.02,0.1)

    for i in range(200):
        f = lpf.filter(100)
        filters.append(f)

    for i in range(200):
        f = lpf.filter(200)
        filters.append(f)



    plt.plot(filters)

    plt.show()