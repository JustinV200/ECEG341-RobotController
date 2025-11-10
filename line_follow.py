# line_follow.py
from sensor import LineReader
from Motor import driver
import machine
import time


M1A = machine.PWM(machine.Pin(8))
M1B = machine.PWM(machine.Pin(9))
M2A = machine.PWM(machine.Pin(10))
M2B = machine.PWM(machine.Pin(11))

M1A.freq(8_000)
M1B.freq(8_000)
M2A.freq(8_000)
M2B.freq(8_000)

M1A.duty_u16(0)
M1B.duty_u16(0)
M2A.duty_u16(0)
M2B.duty_u16(0)

positions = [-20, -12, -4, 4, 12, 20]
pins = [0,1,2,3,4,5]
# 1. --- Setup ---
# Instantiate your classes
lr = LineReader(pins, positions) # Assuming default pins/positions
m = driver(M1A, M1B, M2A, M2B)
 # you might have different constructor values

# Set a base speed. 30 is a good start.
velocity = 5
#proporotional gain
kp = -0.6
#derivative gain, how fast is the error changing? adjust accordingly
kd = -0.2
#integral error, small consistent offsets over time
#currently off, can be adjusted accordingly
ki = 0.0
previous_error = 0
integral = 0
# 2. --- Control Loop ---
try:
    for i in range(500): # run for 500 iterations then stop!
        # Get the latest sensor reading
        lr.update()
        error = lr.get_offset()
        #slow down with tighter lines
        velocity = max(5, 15 - abs(error) * 0.3)
        # 1. Calculate the total error
        integral += error
        #get derivative
        derivative = error - previous_error
        #adjusts turning strength based on how far off-center the line is and how fast that error is changing.        
        angular_velocity = kp * error + ki * integral + kd * derivative
        #save previous serror for future calculations
        previous_error = error
        # 2. Calculate the 'angular_velocity' based on the error
        print(f"Error: {error:.2f}, PID_AngVel: {angular_velocity:.2f}, Velocity: {velocity:.2f}")
        #angular_velocity = (kp-(error/100)) * error # given
        # --- END CONTROL LOGIC ---
        # Send the command to the motors
        # Note: We use -angular_velocity if your motor
        # class defines a positive angle as a left turn.
        # This depends on your motor.drive() implementation.
        # Let's start by assuming a positive value turns right.
        m.drive(velocity, angular_velocity)
        # A small delay is not needed if your loop
        # is fast, but 1ms can be okay. (try differnt values!)
        time.sleep_ms(1)

finally:
    m.stop() # Always stop the motors
