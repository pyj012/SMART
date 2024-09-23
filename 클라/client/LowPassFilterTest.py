import numpy as np
import matplotlib.pyplot as plt
import random
import math

class LowPassFilter(object):
    def __init__(self, cut_off_freqency, ts, limit_low = None, limit_high = None):
    	# cut_off_freqency: 차단 주파수
        # ts: 주기
        
        self.ts = ts
        self.cut_off_freqency = cut_off_freqency
        self.tau = self.get_tau()

        if limit_low is not None and limit_high is not None:
            self.limit_low = limit_low
            self.limit_high = limit_high
            self.limit_mode = True
        else:
            self.limit_mode = False

        self.prev_data = 0.
        
    def get_tau(self):
        return 1 / (2 * np.pi * self.cut_off_freqency)

    def filter(self, data):
        val = (self.ts * data + self.tau * self.prev_data) / (self.tau + self.ts)
        if self.limit_mode:
            if val > self.limit_high:
                val = self.limit_high
            if val < self.limit_low:
                val = self.limit_low
        
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

    lpf = LowPassFilter(3., 0.1)
    sensor = Sensor()

    for i in range(200):
        z = sensor.sense()
        f = lpf.filter(z)

        xs.append(i)
        sensors.append(z)
        filters.append(f)

    plt.plot(xs, filters)
    plt.scatter(xs, sensors, c="r", s=1)

    plt.show()

    print(0x31)