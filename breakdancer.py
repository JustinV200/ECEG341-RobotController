import machine
import time
import random
import neopixel
from breakdancemotor import driver


# ---------------- MOTOR SETUP ----------------
M1A = machine.PWM(machine.Pin(8))   # right motor forward
M1B = machine.PWM(machine.Pin(9))   # right motor reverse
M2A = machine.PWM(machine.Pin(10))  # left motor forward
M2B = machine.PWM(machine.Pin(11))  # left motor reverse

for m in [M1A, M1B, M2A, M2B]:
    m.freq(8000)

Gbot = driver(M1A, M1B, M2A, M2B)


# ---------------- RGB NEOPIXEL SETUP (Pin 18) ----------------
np = neopixel.NeoPixel(machine.Pin(18), 2)
np.fill((0, 0, 0))
np.write()


# ---------------- BUZZER SETUP ----------------
buzzer = machine.PWM(machine.Pin(22))


# ---------------- BEAT SETUP ----------------
BPM = 140
BEAT_INTERVAL = 60 / BPM

# Melody notes
GUITAR_NOTES = [
    659, 831, 659, 831,
    659, 831, 659, 831,
    659, 880, 659, 880,
    659, 988, 659, 988
]

# All notes = half-beat
NOTE_LENGTHS_BEATS = [
    0.5, 0.5, 0.5, 0.5,
    0.5, 0.5, 0.5, 0.5,
    0.5, 0.5, 0.5, 0.5,
    0.5, 0.5
]


# ---------------- RGB LIGHTS ----------------
def random_rgb():
    return (
        random.randint(40, 255),
        random.randint(40, 255),
        random.randint(40, 255)
    )

def lights_on_beat():
    color = random_rgb()
    np.fill(color)
    np.write()


# ---------------- SOUND ----------------
def play_beat_sound(frequency=600, duration=BEAT_INTERVAL * 0.9):
    buzzer.freq(int(frequency))
    buzzer.duty_u16(32768)
    t = machine.Timer(-1)
    t.init(
        period=int(duration * 1000),
        mode=machine.Timer.ONE_SHOT,
        callback=lambda t: buzzer.duty_u16(0)
    )


# ---------------- MOVEMENT ----------------
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

def full_circle_spin(speed=0.6, t=3.0):
    Gbot.drive(0, speed)
    time.sleep(t)
    Gbot.stop()


# ---------------- MAIN JIT -------------------
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
        forward, spin_left, spin_right, reverse,
        spin_right, reverse, forward, spin_left,
        forward, spin_left, spin_right, reverse,
        spin_right, reverse, forward, spin_left,
        forward, spin_left, spin_right, reverse,
        spin_right, reverse, forward, spin_left,
        forward, spin_left, spin_right, reverse
    ]

    TOTAL_DURATION_MS = 30000   # total show time
    SPIN_TIME_SEC = 3.0         # reserved final spin time
    SPIN_TIME_MS = int(SPIN_TIME_SEC * 1000)

    start = time.ticks_ms()
    note_index = 0

    while True:

        now = time.ticks_ms()
        elapsed = time.ticks_diff(now, start)
        remaining = TOTAL_DURATION_MS - elapsed

        if remaining <= SPIN_TIME_MS:
            break

        for move in moves:

            now = time.ticks_ms()
            elapsed = time.ticks_diff(now, start)
            remaining = TOTAL_DURATION_MS - elapsed

            if remaining <= SPIN_TIME_MS:
                break

            # Melody
            freq = GUITAR_NOTES[note_index % len(GUITAR_NOTES)]
            length_beats = NOTE_LENGTHS_BEATS[note_index % len(NOTE_LENGTHS_BEATS)]
            note_duration = length_beats * BEAT_INTERVAL
            move_time_ms = int(note_duration * 1000)

            if remaining - move_time_ms <= SPIN_TIME_MS:
                break

            lights_on_beat()
            play_beat_sound(freq, duration=note_duration * 0.9)
            move(t=note_duration)

            note_index += 1
        else:
            continue
        break

    freq = GUITAR_NOTES[note_index % len(GUITAR_NOTES)]
    lights_on_beat()
    play_beat_sound(freq, duration=SPIN_TIME_SEC * 0.9)
    full_circle_spin(t=SPIN_TIME_SEC)

    np.fill((0, 0, 0))
    np.write()


jit_dance_with_lights()