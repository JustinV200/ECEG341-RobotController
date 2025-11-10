from machine import Pin
import time
import math

class LineReader():
    def __init__(self, pins = [0,1,2,3,4,5], positions = [-20, -12, -4, 4, 12, 20]):
        self.pins = pins
        self.positions = positions
        self.offset = 0
        self.darkness = 0
        self.confidence = 0
    def calculate_confidence(self, data_list):
        mean = sum(data_list) / len(data_list)
        squared_differences = [(x - mean) ** 2 for x in data_list]
        sum_squared_differences = sum(squared_differences)
        variance = sum_squared_differences / (len(data_list) - 1)
        exponent_value = -0.001 * (variance)
        self.confidence = 1 - math.exp(exponent_value)

    def reflectance_sample(self, pin, samples, delay_us):
        # charge capacitance
        pin.init(Pin.OUT, value=1)
        time.sleep_us(10)
        # change to input
        pin.init(Pin.IN, pull = None)
        count = 0
        for i in range(samples):
            # wait one sample period
            time.sleep_us(delay_us)
            # count the number of 1's
            count += pin.value()    
        # the pulse width is the number of 1's 
        # detected times the delay
        return (count * delay_us)
    
    def update(self):
        decayTimes = []
        for i in self.pins:
            decayTimes.append( self.reflectance_sample(pin = Pin(i), 
                samples = 40, delay_us = 15))
        print(f'decayTimes: {decayTimes}')
        m = min(decayTimes)
        self.darkness = sum(decayTimes)
        #print(m)
        subDecayTimes = []
        for obj in decayTimes:
            subDecayTimes.append(obj - m)
        self.calculate_confidence(subDecayTimes)

        normalizedDecayTimes=[]
        totalDecayTimes = sum(subDecayTimes)
        if(totalDecayTimes!= 0):
            for obj in subDecayTimes:
                normalizedDecayTimes.append(obj/totalDecayTimes)
        else:
            normalizedDecayTimes = subDecayTimes
        print(f'normalizedDecayTimes: {normalizedDecayTimes}')
        weightedPosition = 0
        iterator = 0

        for item in normalizedDecayTimes:
            weightedPosition += item * self.positions[iterator]
            iterator+=1
        self.offset = weightedPosition
    def get_offset(self):
        return self.offset
    def get_darkness(self):
        return self.darkness
    def get_confidence(self):
        return self.confidence

if __name__=="__main__":  
    positions = [-20, -12, -4, 4, 12, 20]
    pins = [0,1,2,3,4,5]
    l = LineReader(pins, positions)  
    while True:        
        #print(weightedPosition)
        #print(decayTimes)
        #print(subDecayTimes)
        l.update()
        print(f'Offset: {l.get_offset()}')
        print(f'Darkness: {l.get_darkness()}')
        print(f'Confidence: {l.get_confidence(): .2f}')
        time.sleep(0.5)