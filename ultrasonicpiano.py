from machine import Pin, PWM
import neopixel

import time



class Ultrasound():

    def __init__(self, trigger, echo, timeout=30000):  # timeout in microseconds

        self.t = trigger

        self.e = echo

        self.timeout = timeout


    def measure(self):

        # create trigger pulse

        self.t.low()

        time.sleep_us(2)

        self.t.high()

        time.sleep_us(15)

        self.t.low()


        start = time.ticks_us()

        # wait for start of echo

        while self.e.value() == 0:

            if time.ticks_diff(time.ticks_us(), start) > self.timeout:

                return -1

        signaloff = time.ticks_us()


        while self.e.value() == 1:

            if time.ticks_diff(time.ticks_us(), signaloff) > self.timeout:

                return -2  

        signalon = time.ticks_us()


        timepassed = signalon - signaloff

        return timepassed / 1000 * 19.0 + 0.192


if __name__ == "__main__":


    simple_tune = [
    (261.63, 250),  # C4 (Quarter Note)
    (392.00, 250),  # G4 (Quarter Note)
    (329.63, 500),  # E4 (Half Note)
    (0, 100),       # Rest (Eighth Note)
    (261.63, 250)   # C4 (Quarter Note)
]
    
    songIterator = 0;


    pixels = neopixel.NeoPixel(Pin(18), 2)

    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    OFF = (0, 0, 0)


    ultrasound = Ultrasound(trigger=Pin(28, Pin.OUT), echo=Pin(7, Pin.IN))
    buzzer = PWM(Pin(22))

    while True:

        dist = ultrasound.measure()

        if dist < 0:

            print("Sensor timeout or disconnected!")

        else:

            print(f"Distance = {dist:.2f} cm")
            #freq, duration = simple_tune[songIterator]
            freq = dist*10
            duration = 5
            buzzer.freq(int(freq))
            buzzer.duty_u16(0x7fff)


            if dist < 30:
                pixels.fill(RED)
            elif dist < 60:
                pixels.fill(BLUE)
            elif dist < 90:
                pixels.fill(GREEN)
            else:
                pixels.fill(OFF)
                buzzer.duty_u16(0)
            pixels.write()

            time.sleep_ms(int(duration))


        time.sleep(0.5)