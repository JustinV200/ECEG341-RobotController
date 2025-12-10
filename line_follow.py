# line_follow.py
from sensor import LineReader
from Motor import driver
import machine
import time

class lineFollower():

    def __init__(self, kp = -0.3, kd = -0.5, MAX_VELOCITY = 5, MIN_VELOCITY = 5, velAdjustor = 0.5, ki = 0.0):
        #slalom
        #kp = -0.6

        #1 Meter Dash
        #velocity = max(15, 30 - abs(error) * 0.5)
        # Slalom
        #velocity = max(5, 15 - abs(error) * 0.3)

        # ----- CONFIG ------
        self.M1A = machine.PWM(machine.Pin(8))
        self.M1B = machine.PWM(machine.Pin(9))
        self.M2A = machine.PWM(machine.Pin(10))
        self.M2B = machine.PWM(machine.Pin(11))

        self.M1A.freq(8_000)
        self.M1B.freq(8_000)
        self.M2A.freq(8_000)
        self.M2B.freq(8_000)

        self.M1A.duty_u16(0)
        self.M1B.duty_u16(0)
        self.M2A.duty_u16(0)
        self.M2B.duty_u16(0)

        #kp, proportional turns, how much should we correct when an error is noticed?
        self.kp = kp
        # kd. derivative of prev error - current error, 
        # readjust based on how intense we correct, reduce oscillation and allow for smoother
        #driving
        self.kd = kd
        positions = [-20, -12, -4, 4, 12, 20]
        pins = [0,1,2,3,4,5]
        self.lr = LineReader(pins, positions) 
        self.m = driver(self.M1A, self.M1B, self.M2A, self.M2B)


        self.MAX_VELOCITY = MAX_VELOCITY
        self.MIN_VELOCITY = MIN_VELOCITY
        #default is off, can be adjusted accordingly
        #integral of total error, can be adjusted for small tweaks/adjustments as needed
        self.velocity = MIN_VELOCITY
        self.ki = ki
        #how much do we adjust the speed based on error?
        self.velAdjustor = velAdjustor

        #set preverror and integral for tracking
        self.previous_error = 0
        self.integral = 0

    def follow(self, darkness="black", erroradjustor=0):
        self.lr.mode = darkness
        self.lr.update()
        error = self.lr.get_offset()

        if error is None:
            # Line lost: skip PID update but keep last velocity
            self.m.drive(self.velocity, 0)  # maintain forward speed, no angular change
            return

        error += erroradjustor

        # Velocity based on error
        self.velocity = max(self.MIN_VELOCITY, self.MAX_VELOCITY - abs(error) * self.velAdjustor)

        # PID calculation
        self.integral += error
        derivative = error - self.previous_error
        angular_velocity = self.kp * error + self.ki * self.integral + self.kd * derivative
        self.previous_error = error

        self.m.drive(self.velocity, angular_velocity)
        time.sleep_ms(1)


    def stop(self):
        self.m.stop()

    def setStats(self, kp, kd, MAX_VELOCITY, MIN_VELOCITY, velAdjustor):
        self.MAX_VELOCITY = MAX_VELOCITY
        self.MIN_VELOCITY = MIN_VELOCITY
        #kp, proportional turns, how much should we correct when an error is noticed?
        self.kp = kp
        # kd. derivative of prev error - current error, 
        # readjust based on how intense we correct, reduce oscillation and allow for smoother
        #driving
        self.kd = kd
        self.velAdjustor = velAdjustor
    
    def drive(self, vel, aVel):
        self.m.drive(vel, aVel)

    def straighten(self):
        tolerance = 0.05
        straight = -0.46
        max_turn = 5
        min_turn = 0.5
        timeout = 4000
        start_time = time.ticks_ms()

        while True:
            self.lr.update()
            error = self.lr.get_offset()
            if error is None:
                self.m.drive(0, 1)
                time.sleep_ms(50)
                continue

            delta = error - straight

            if abs(delta) <= tolerance:
                print("Line straightened!")
                break

            # Correct sign for your motor system
            angular_velocity = -self.kp * delta

            # clamp max turn
            angular_velocity = max(-max_turn, min(max_turn, angular_velocity))

            # enforce minimum turn
            if 0 < abs(angular_velocity) < min_turn:
                angular_velocity = min_turn * (1 if angular_velocity > 0 else -1)

            self.m.drive(0, angular_velocity)
            time.sleep_ms(10)

            if time.ticks_diff(time.ticks_ms(), start_time) > timeout:
                print("Straighten timeout reached!")
                break

        self.m.stop()






#def __init__(self, kp = -0.3, kd = -0.5, MAX_VELOCITY = 30, MIN_VELOCITY = 15, velAdjustor = 0.3, ki = 0.0):
#slalom
#x = lineFollower(-0.3, -0.5, 30,5, 0.7)
#x = lineFollower()
