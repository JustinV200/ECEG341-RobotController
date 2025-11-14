from line_follow import lineFollower
from sensor import LineReader
from Motor import driver
import machine
import time
# def __init__(self, kp = -0.3, kd = -0.5, MAX_VELOCITY = 30, MIN_VELOCITY = 15, velAdjustor = 0.3, ki = 0.0):
class robot_olympics:
    def __init__(self):
        self.Gbot = lineFollower()
    def reset(self):
        self.Gbot = lineFollower()
    def slalom(self):
        self.Gbot.setStats(-0.3, -0.5, 30,5, 0.7)
        for i in range(500):
            self.Gbot.follow()
        self.Gbot.stop()
    def straightLine(self):
        for i in range(500):
            self.Gbot.follow()
        self.Gbot.stop()

    def bullseye(self):
        self.Gbot.setStats(-0.1, -0.7, 15,5, 0.5)
        for i in range(400):
            self.Gbot.follow()
        self.Gbot.straighten()
        self.Gbot.drive(20, 0)
        time.sleep(4.5)
        self.Gbot.stop()


x = robot_olympics()
x.bullseye()


