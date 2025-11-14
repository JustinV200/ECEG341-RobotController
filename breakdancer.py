import machine
import time
import random
from Motor import driver

# Motor setup
M1A = machine.PWM(machine.Pin(8))  # right motor forward
M1B = machine.PWM(machine.Pin(9))  # right motor reverse
M2A = machine.PWM(machine.Pin(10)) # left motor forward
M2B = machine.PWM(machine.Pin(11)) # left motor reverse

for m in [M1A, M1B, M2A, M2B]:
    m.freq(8000)

Gbot = driver(M1A, M1B, M2A, M2B)

# LED setup
led_pins = [0,1,2,3,4,5,6,7,16,17,26,27,28]
leds = [machine.Pin(pin, machine.Pin.OUT) for pin in led_pins]

# Buzzer setup (GP22)
buzzer = machine.PWM(machine.Pin(22))

# Beat configuration
BPM = 125
BEAT_INTERVAL = 60 / BPM

# LED helper function
def lights_on_beat():
    pattern_type = random.randint(0, 3)
    for i, led in enumerate(leds):
        if pattern_type == 0:
            led.value(1 if i % 2 == 0 else 0)
        elif pattern_type == 1:
            led.value(1 if i % 2 == 1 else 0)
        elif pattern_type == 2:
            led.value(1 if i % 3 == 0 else 0)
        else:
            led.value(random.choice([0,1]))

# Buzzer helper (non-blocking)
def play_beat_sound(frequency=600, duration=BEAT_INTERVAL*0.9):
    buzzer.freq(frequency)
    buzzer.duty_u16(32768) 
    t = machine.Timer(-1)
    t.init(period=int(duration*1000), mode=machine.Timer.ONE_SHOT,
           callback=lambda t: buzzer.duty_u16(0))

# Movement functions
def forward(speed=0.5, t=BEAT_INTERVAL):
    Gbot.drive(speed, 0)
    time.sleep(t)
    Gbot.stop()

def reverse(speed=0.5, t=BEAT_INTERVAL):
    Gbot.drive(-speed, 0)
    time.sleep(t)
    Gbot.stop()

def spin_left(speed=1.0, t=BEAT_INTERVAL):
    Gbot.drive(0, speed)
    time.sleep(t)
    Gbot.stop()

def spin_right(speed=1.0, t=BEAT_INTERVAL):
    Gbot.drive(0, -speed)
    time.sleep(t)
    Gbot.stop()

def full_circle_spin(speed=0.6):
    Gbot.drive(0, speed)
    time.sleep(3.0)
    Gbot.stop()

# Dance routine
def jit_dance_with_lights():
    moves = [
        forward, spin_left, reverse, spin_right,
        spin_right, forward, spin_left, reverse,
        spin_left, reverse, forward, spin_right,
        reverse, spin_left, forward, spin_right,
        forward, reverse, spin_right, spin_left,
        spin_right, forward, reverse, spin_left,
        forward, spin_right, spin_left, reverse,
        spin_left, forward, spin_right, reverse,
        reverse, spin_right, forward, spin_left,
        forward, spin_left, reverse, spin_right,
        spin_left, forward, spin_right, reverse,
        forward, spin_right, spin_left, reverse,
        spin_right, reverse, forward, spin_left,
        forward, spin_left, spin_right, reverse

    ]
   
    for move in moves:
        lights_on_beat()                        
        play_beat_sound(random.randint(400, 1000))
        move()

    lights_on_beat()
    play_beat_sound(random.randint(400, 1000))
    full_circle_spin()

    for led in leds:
        led.value(0)

jit_dance_with_lights()


