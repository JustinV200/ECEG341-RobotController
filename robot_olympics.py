from line_follow import lineFollower
from sensor import LineReader
from Motor import driver
import machine
import time
from ultrasonicpiano import Ultrasound
from machine import Pin, PWM
import neopixel
import math

# def __init__(self, kp = -0.3, kd = -0.5, MAX_VELOCITY = 30, MIN_VELOCITY = 15, velAdjustor = 0.3, ki = 0.0):
class robot_olympics:
    def __init__(self):
        self.Gbot = lineFollower()
        self.err_hist = [0, 0, 0]
    def reset(self):
        self.Gbot = lineFollower()

    '''
    def slalom(self):
        self.Gbot.setStats(-0.3, -0.5, 30,15, 0.7)
        #for i in range(800):
        for i in range(3000):
            self.Gbot.follow()
        self.Gbot.stop()
    
    '''
    def slalom(self):
        base_kp = -0.3
        base_kd = -0.7
        max0 = 30
        min0 = 15
        adjust = 0.7

        for i in range(300):
            progress = i / 300

            VELscale = 0.5 + 0.5 * math.exp(-0.7 * progress)

            # gentle KP ramp (your 0.6 ramp was too aggressive)
            KPscale = 1 + 0.35 * progress

            curr_max = max0 * VELscale
            curr_min = min0 * VELscale
            
            if curr_min < 12:
                curr_min = 12

            # final gains
            kp_scaled = base_kp * KPscale

            # KD should NOT get stronger late (that caused overshoot)
            kd_scaled = base_kd

            self.Gbot.setStats(kp_scaled, kd_scaled, curr_max, curr_min, adjust)
            self.Gbot.follow()

        self.Gbot.stop()





    def luge(self):
        self.Gbot.setStats(-0.45, -0.95, 30,5, 0.5)
        #for i in range(800):
        for i in range(3000):
            self.Gbot.follow()
        self.Gbot.stop()

    def straightLine(self):
        self.Gbot.setStats(-0.15, -0.7, 60, 60, 0)
        ultrasound = Ultrasound(trigger=Pin(28, Pin.OUT), echo=Pin(7, Pin.IN))
        x = 0
        while x != -1:
            dist = ultrasound.measure()
            if (dist > 15):
                for i in range(800):
                    self.Gbot.follow()
                    dist = ultrasound.measure()
                    if (dist < 15):
                        self.Gbot.stop()
                    x = -1
            else:
                self.Gbot.stop()

    def bullseye(self):
            self.Gbot.setStats(-0.2, -0.7, 10, 5, 0.5)
            for _ in range(630):
                self.Gbot.follow()

            self.Gbot.stop()
            time.sleep(2)

            self.Gbot.drive(20, 0)
            time.sleep_ms(3050)

            np = neopixel.NeoPixel(machine.Pin(18), 2)   # 2 RGB LEDs
            np.fill((0, 0, 255))
            np.write()
            time.sleep_ms(1500)

            self.Gbot.stop()



    def marathon(self):

            self.Gbot.setStats(-0.3, -0.5, 25,15, 0.7)
            firstOne = 0 #unused
            ultrasound = Ultrasound(trigger=Pin(28, Pin.OUT), echo=Pin(7, Pin.IN))
            def mDodge(direction):

                self.Gbot.stop()

                #time.sleep(0.5)  # short pause before starting dodge

                time.sleep_ms(50)

                self.Gbot.drive(-10, 0)

                time.sleep_ms(800)  # move back a bit





                # ---- STEP 1: Turn right to avoid object ----

                self.Gbot.drive(1, 90*direction)   # slow right turn

                time.sleep_ms(175)

                self.Gbot.stop()

                #time.sleep(0.2)

                time.sleep_ms(50)





                # ---- STEP 2: Move forward to clear object ----

                self.Gbot.drive(10, 0)

                if(direction == -1):

                    time.sleep_ms(2500)  # adjust for obstacle size

                else:

                    time.sleep_ms(1900)

                self.Gbot.stop()

                #time.sleep(0.2)

                time.sleep_ms(50)





                # ---- STEP 3: Turn left to head back toward line ----

                if (direction == 1):

                    self.Gbot.drive(1, -90*direction)

                    time.sleep_ms(135)

                    self.Gbot.drive(10, 0)

                    time.sleep_ms(2300)

                    self.Gbot.stop()

                    time.sleep(0.2)

                else:

                    self.Gbot.drive(1, -90*direction)

                    time.sleep_ms(90)

                    self.Gbot.drive(10, 0)

                    time.sleep_ms(850)

                    self.Gbot.stop()

                    time.sleep(0.2)





                # ---- STEP 4: Check if obstacle still present ----

                d1 = ultrasound.measure()

                time.sleep_ms(10)

                d2 = ultrasound.measure()

                time.sleep_ms(10)

                d3 = ultrasound.measure()

                if all(0 < m < 5 for m in (d1, d2, d3)):

                    print("Obstacle still detected → dodge again")

                    return mDodge(direction)  # recursive dodge if multiple objects





                if (direction == 1):

                    self.Gbot.drive(1, -90)   # left turn

                    time.sleep_ms(120)

                    self.Gbot.drive(10, 0)

                    time.sleep_ms(3700)

                #     time.sleep_ms(4500)  # adjust for obstacle size

                # ---- STEP 5: Scan to find the line ----

                print("Scanning for line...")

                scan_start = time.ticks_ms()

                timeout_ms = 300000

                forward_speed = 8

                angular_speed = (-45* (1 * direction))




                

                while time.ticks_diff(time.ticks_ms(), scan_start) < timeout_ms:

                    self.Gbot.lr.update()

                    error = self.Gbot.lr.get_offset()

                    

                    if error is not None:

                        # Confirm using 5 rapid checks

                        confirm = 0

                        for _ in range(5):

                            self.Gbot.lr.update()

                            if self.Gbot.lr.get_offset() is not None:

                                confirm += 1

                            time.sleep_ms(5)


                        if confirm >= 4:

                            print("Line reacquired!")
                            self.Gbot.stop() 
                            time.sleep_ms(50)
                            return direction * -1
                    self.Gbot.drive(0, 15 * direction)

                    time.sleep_ms(100)

                    self.Gbot.drive(9,0)

                    time.sleep_ms(300)
                    # continuously move forward while slowly turning left

                    # if(x != 0):

                    #     self.Gbot.drive(0, angular_speed)

                    #     time.sleep_ms(2)

                    self.Gbot.drive(forward_speed, angular_speed)

                    time.sleep_ms(50)
                    self.Gbot.drive(forward_speed,0)

                    time.sleep_ms(50)  # frequent updates





                # if the loop exits, line was not found

                self.Gbot.stop()

                time.sleep(2)

                print("Line not found within scan period")

                

            





        def mFollow(counter):

            counter = -1

            last = [100, 100, 100, 100, 100, 100] #prev_dist checks 2 back to back measurements, as sometimes we get a weird accidental low value, so this allows us to ignore them

            for i in range(65000):

                dist = ultrasound.measure()

                last.pop(0)

                last.append(dist)

                self.Gbot.follow()

                print(dist)

                if all(d > 0 and d < 10 for d in last):

                    counter = mDodge(counter)

                    last = [100, 100, 100, 100, 100, 100]

                prev_dist = dist





        mFollow(counter=-1)



    def orienteering(self):
        self.Gbot.setStats(-0.3, -0.7, 20,5, 0.7)

        def station1():
            self.Gbot.setStats(-0.3, -0.7, 20,5, 0.7)
            for i in range(85):
                self.Gbot.follow()
            np = neopixel.NeoPixel(machine.Pin(18), 2)   # 2 RGB LEDs
            np.fill((255, 0, 255))
            np.write()
            self.Gbot.stop()
            time.sleep(1)
            self.Gbot.drive(-10, 0)
            time.sleep(1)
            self.Gbot.stop()
            time.sleep(1)
            self.Gbot.drive(0,-45)
            time.sleep_ms(200)
            flip(-1)
            np.fill((0, 0, 0))
            np.write()

            for i in range(40):
                self.Gbot.follow()
            self.Gbot.stop()
            time.sleep(1)

            self.Gbot.setStats(-0.15, -0.7, 4,3, 0.7)
            for i in range(50):
                self.Gbot.follow()
            self.Gbot.drive(10,0)
            time.sleep_ms(2000)

        def station2():
            np = neopixel.NeoPixel(machine.Pin(18), 2)   # 2 RGB LEDs

            self.Gbot.setStats(-0.3, -0.5, 10,10, 0.7)
            self.Gbot.drive(10,0)
            time.sleep_ms(4000)

            self.Gbot.stop()
            time.sleep(1)
            self.Gbot.drive(0,90)
            time.sleep_ms(190)
            self.Gbot.drive(10,0)
            time.sleep_ms(2200)

            #stop and lights
            self.Gbot.stop()
            np.fill((255, 0, 255))
            np.write()
            time.sleep(1)
            np.fill((0, 0, 0))
            np.write()

            #go back

            self.Gbot.drive(-10,0)
            time.sleep_ms(2400)
            #flip(-1)
            self.Gbot.stop()

            self.Gbot.drive(0,90)
            time.sleep_ms(225)

            self.Gbot.drive(10,0)
            time.sleep_ms(3700)
            self.Gbot.stop()
            time.sleep(1)

        def station3():
           #self.Gbot.setStats(-0.3, -0.7, 5,5, 0.7)
            #for i in range(30):
            #    self.Gbot.follow()



            
            self.Gbot.drive(10,0)
            time.sleep_ms(2700)

            self.Gbot.lr.update()
            error = self.Gbot.lr.get_offset()
            x = False
            while(x == False):
                self.Gbot.drive(10,0)
                time.sleep_ms(30)
                self.Gbot.drive(0,50)
                time.sleep_ms(10)    
                self.Gbot.stop()
                time.sleep_ms(1)
                self.Gbot.lr.update()
                error = self.Gbot.lr.get_offset()
                if error != None:
                    self.Gbot.drive(10,0)
                    time.sleep_ms(300)
                    flip(-1)
                    self.Gbot.setStats(-0.3, -0.7, 5,5, 0.7)
                    for i in range(30):
                        self.Gbot.follow()
                    x = True
         
            self.Gbot.setStats(-0.3, -0.7, 15,10, 0.7)
            self.Gbot.drive(10,0)
            time.sleep_ms(1000)
            self.Gbot.drive(0,45)
            time.sleep_ms(120)
            for i in range(60):
                self.Gbot.follow()
            np = neopixel.NeoPixel(machine.Pin(18), 2)   # 2 RGB LEDs
            np.fill((255, 0, 255))
            np.write()
            self.Gbot.stop()
            time.sleep(1)
            np.fill((0, 0, 0))
            np.write()

            self.Gbot.drive(-10,0)
            time.sleep_ms(2000)
            #flip(-1)
            self.Gbot.stop()
            time.sleep_ms(200)

            self.Gbot.drive(0,90)
            time.sleep_ms(220)
            self.Gbot.drive(10,0)
            time.sleep_ms(3000)


            self.Gbot.drive(10,0)
            time.sleep_ms(1000)
            self.Gbot.stop()
            time.sleep(1)
            for i in range(50):
                self.Gbot.follow()
            self.Gbot.stop()
            time.sleep(1)

        def station4():
            self.Gbot.drive(0,90)
            time.sleep_ms(120)
            self.Gbot.drive(10,0)
            time.sleep_ms(4000)
            self.Gbot.stop()
            time.sleep(1)

        def flip(direction):
            print("Scanning for line...")
            scan_start = time.ticks_ms()
            timeout_ms = 300000
            forward_speed = 8
            angular_speed = 45 * direction
            while time.ticks_diff(time.ticks_ms(), scan_start) < timeout_ms:
                self.Gbot.lr.update()
                error = self.Gbot.lr.get_offset()
                if error is not None:
                    self.Gbot.drive(10, 0)
                    time.sleep_ms(50)
                    print("Line reacquired!")
                    self.Gbot.follow()
                    return

                # continuously move forward while slowly turning left
                if(x != 0):
                    self.Gbot.drive(0, angular_speed)
                    time.sleep_ms(2)
        self.Gbot.drive(10,0)
        time.sleep(1)
        station1()

        self.Gbot.drive(10,0)
        time.sleep_ms(100)
        self.Gbot.drive(0,90)
        time.sleep_ms(215)
        self.Gbot.stop()
        time.sleep_ms(50)
        station2()
        self.Gbot.drive(0,90)
        time.sleep_ms(180)
        station3()
        time.sleep(1)
        station4()


    def followGray(self):
        self.Gbot.setStats(-0.7, -0.5, 10,10, 0.7)
        while True:
            self.Gbot.follow("gray")

x = robot_olympics()
x.orienteering()
            
            





