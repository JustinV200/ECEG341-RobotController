import machine
import time
import math
'''
M1A.freq(8_000)
M1B.freq(8_000)
M2A.freq(8_000)
M2B.freq(8_000)

M1A.duty_u16(0)
M1B.duty_u16(0)
M2A.duty_u16(0)
M2B.duty_u16(0)
'''


class driver():
    def __init__(self, rMotor_f, rMotor_r, lMotor_f, lMotor_r):

        self.rMotor_f = rMotor_f
        self.rMotor_r = rMotor_r
        self.lMotor_f = lMotor_f
        self.lMotor_r = lMotor_r

    def drive_angle(self, v, w):
        L = 13
        V_right = v + (w * L / 2)
        V_left  = v - (w * L / 2)
        return (V_left, V_right)


    def drive(self, v, w):
        bias = .01
        DUTY_CYCLE = int(0xffff)
        # split bias to left/right motors
        left_bias = 1.0 - bias/2
        right_bias = 1.0 + bias/2 
        lV, rV = self.drive_angle(v, w)
        print(f'left velocity {lV} right velocity {rV}')

        # Right motor
        if rV >= 0:
            self.rMotor_f.duty_u16(int((rV * 1541) * right_bias))
            self.rMotor_r.duty_u16(0)
        else:
            self.rMotor_f.duty_u16(0)
            self.rMotor_r.duty_u16(int(abs(rV * 1541) * right_bias))

        # Left motor
        if lV >= 0:
            self.lMotor_f.duty_u16(int((lV * 1541) * left_bias))
            self.lMotor_r.duty_u16(0)
        else:
            self.lMotor_f.duty_u16(0)
            self.lMotor_r.duty_u16(int(abs(lV * 1541) * left_bias))
            
    def stop(self):
        self.rMotor_f.duty_u16(0)
        self.rMotor_r.duty_u16(0)
        self.lMotor_f.duty_u16(0)
        self.lMotor_r.duty_u16(0)