import numpy as np
import matplotlib.pyplot as plt
import random
import math

class ValueControlFilter(object):
    def __init__(self, prev_data = 0, dev = 0, dev_Limit = None, limit_low = None, limit_high = None):
        if limit_low is not None and limit_high is not None:
            self.limit_low = limit_low
            self.limit_high = limit_high
            self.limit_mode = True
        else:
            self.limit_mode = False

        self.prev_data = prev_data
        self.dev = dev
        self.dev_Limit = dev_Limit

    def set_limit(self, L, H, value):
        if value<L:
            value = L
        if value>H:
            value = H
        return value

    def filter(self, data):
        if self.dev_Limit is not None:
            data = data if ((self.prev_data + self.dev_Limit > data) and (self.prev_data - self.dev_Limit < data)) else self.prev_data
        
        val = round(data if ((self.prev_data + self.dev < data) or (self.prev_data - self.dev > data)) else self.prev_data)
        # val = (data if ((self.prev_data + self.dev < data) or (self.prev_data - self.dev > data)) else self.prev_data)
        
        if self.limit_mode:
            val = self.set_limit(self.limit_low,self.limit_high,val)
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
        return math.sin(self.i) #+ self.noise()


if __name__ == "__main__":

    xs = []
    sensors = []
    filters = []

    lpf = ValueControlFilter(0, 0.1,limit_low=-0.6,limit_high=0.6)
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