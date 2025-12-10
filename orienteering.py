from line_follow import lineFollower
from sensor import LineReader
import neopixel
import machine
import time


BLACK_THRESH     = 1500      # big black line
DARK_GRAY_LOW    = 835       # dark gray line range
DARK_GRAY_HIGH   = 870
LIGHT_GRAY_LOW   = 815       # light gray center range
LIGHT_GRAY_HIGH  = 835

STATION_CONF_THRESHOLD = 0.25

# Speeds
BLACK_FWD_SPEED   = 20
GRAY_FWD_SPEED    = 10

# Spin speeds / times
TURN_SPEED_180    = 3.0
TURN_TIME_180     = 1.35
TURN_SPEED_90     = 3.0
TURN_TIME_90      = 0.55

MAX_BLACK_STEPS   = 4000
MAX_GRAY_STEPS    = 4000

CENTER_PUSH_TIME  = 0.7

# NeoPixel station colors
STATION_COLORS = {
    1: (255,   0,   0),   # Red
    2: (0,     0, 255),   # Blue
    3: (0,   255,   0),   # Green
    4: (255, 255,   0),   # Yellow
}


def classify_zone(darkness):
    if darkness is None:
        return "unknown"
    if darkness > BLACK_THRESH:
        return "black"
    if DARK_GRAY_LOW <= darkness <= DARK_GRAY_HIGH:
        return "dark_gray"
    if LIGHT_GRAY_LOW <= darkness <= LIGHT_GRAY_HIGH:
        return "light_gray"
    return "other"


class DecayOrienteering:
    def __init__(self):
        self.bot = lineFollower()
        self.lr = self.bot.lr

        self.pixels = neopixel.NeoPixel(machine.Pin(18), 2)
        self.pixels.fill((0, 0, 0))
        self.pixels.write()

        self.bot.setStats(-0.3, -0.5, 25, 10, 0.4)

    def stop(self):
        self.bot.stop()

    def read_darkness_zone(self):
        d = self.lr.get_darkness()
        return d, classify_zone(d)

    def at_station(self):
        off = self.lr.get_offset()
        conf = self.lr.get_confidence()
        return (off is None) and (conf is not None) and (conf < STATION_CONF_THRESHOLD)

    def light_station(self, station_number):
        color = STATION_COLORS.get(station_number, (255, 255, 255))
        self.pixels.fill(color)
        self.pixels.write()

    def turn_around(self):
        """Approx 180° turn in place."""
        self.bot.drive(0, TURN_SPEED_180)
        time.sleep(TURN_TIME_180)
        self.stop()

    def turn_right_90(self):
        """Approx 90° turn to the right (clockwise)."""
        self.bot.drive(0, -TURN_SPEED_90)
        time.sleep(TURN_TIME_90)
        self.stop()


    def follow_black_to_station(self, station_number):
        print("Leg to BLACK station", station_number)
        steps = 0
        while steps < MAX_BLACK_STEPS:
            self.bot.follow()
            if self.at_station():
                self.stop()
                print("Station", station_number, "reached on black.")
                self.light_station(station_number)
                return True
            steps += 1
        self.stop()
        print("WARNING: did not reach station", station_number, "on black.")
        return False

    def return_along_black_to_center(self):
        """
        From station heading back:
          - Follow black with PID until we leave 'black' zone,
          - Then push forward into center for CENTER_PUSH_TIME.
        """
        print("Returning on BLACK toward center...")
        steps = 0
        while steps < MAX_BLACK_STEPS:
            self.bot.follow()
            d, zone = self.read_darkness_zone()
            if zone != "black":
                print("Left black zone ->", zone, "dark=", d)
                break
            steps += 1

        self.bot.drive(BLACK_FWD_SPEED, 0)
        time.sleep(CENTER_PUSH_TIME)
        self.stop()

        time.sleep_ms(200)
        self.lr.update()
        d, zone = self.read_darkness_zone()
        print("After center push, zone:", zone, "dark=", d)
        return zone

    def drive_forward_until_zone(self, target_zone, speed, max_steps=1000):
        print("Driving forward to find zone:", target_zone)
        steps = 0
        while steps < max_steps:
            self.bot.drive(speed, 0)
            self.lr.update()
            d, zone = self.read_darkness_zone()
            if zone == target_zone:
                time.sleep_ms(150)
                self.lr.update()
                d2, zone2 = self.read_darkness_zone()
                print("Found", target_zone, "zone:", zone2, "dark=", d2)
                self.stop()
                return True
            steps += 1
            time.sleep_ms(10)

        self.stop()
        print("WARNING: drive_forward_until_zone failed for", target_zone)
        return False

    def follow_dark_gray_to_station(self, station_number):
        """
        From center, moving forward after a right turn:
          - First, get onto dark_gray spoke,
          - Then follow dark_gray until station signature.
        """
        print("Leg to DARK GRAY station", station_number)

        ok = self.drive_forward_until_zone("dark_gray", GRAY_FWD_SPEED, max_steps=1500)
        if not ok:
            print("Could not find dark_gray spoke for station", station_number)
            return False

        steps = 0
        while steps < MAX_GRAY_STEPS:
            self.lr.update()
            if self.at_station():
                self.stop()
                print("Station", station_number, "reached on dark_gray.")
                self.light_station(station_number)
                return True

            d, zone = self.read_darkness_zone()

            if zone == "dark_gray":
                self.bot.drive(GRAY_FWD_SPEED, 0)
            elif zone == "light_gray":
                self.bot.drive(0, -1.0)
            else:
                self.bot.drive(0, 1.0)

            steps += 1
            time.sleep_ms(10)

        self.stop()
        print("did not reach station", station_number, "on dark_gray.")
        return False

    def return_along_dark_gray_to_center(self):
        print("Returning on DARK GRAY toward center...")
        steps = 0
        while steps < MAX_GRAY_STEPS:
            self.lr.update()
            d, zone = self.read_darkness_zone()

            if zone == "light_gray":
                print("Reached LIGHT GRAY center, dark=", d)
                break

            if zone == "dark_gray":
                self.bot.drive(GRAY_FWD_SPEED, 0)
            else:
                if d is not None and d < DARK_GRAY_LOW:
                    self.bot.drive(0, -1.0)
                else:
                    self.bot.drive(0, 1.0)

            steps += 1
            time.sleep_ms(10)

        self.bot.drive(GRAY_FWD_SPEED, 0)
        time.sleep(CENTER_PUSH_TIME / 2)
        self.stop()

        time.sleep_ms(200)
        self.lr.update()
        d2, zone2 = self.read_darkness_zone()
        print("After gray center push, zone:", zone2, "dark=", d2)
        return zone2


    def run(self):

        if not self.follow_black_to_station(1):
            print("Abort after S1 forward")
            return

        self.turn_around()
        time.sleep(0.1)
        center_zone_1 = self.return_along_black_to_center()
        print("After S1, center zone:", center_zone_1)

        self.turn_right_90()
        time.sleep(0.1)

        if not self.follow_dark_gray_to_station(2):
            print("Abort after S2 forward")
            return

        self.turn_around()
        time.sleep(0.1)
        center_zone_2 = self.return_along_dark_gray_to_center()
        print("After S2, center zone:", center_zone_2)

        self.turn_right_90()
        time.sleep(0.1)

        if not self.drive_forward_until_zone("black", BLACK_FWD_SPEED, max_steps=1500):
            print("Abort: could not find black for S3")
            return

        if not self.follow_black_to_station(3):
            print("Abort after S3 forward")
            return

        self.turn_around()
        time.sleep(0.1)
        center_zone_3 = self.return_along_black_to_center()
        print("After S3, center zone:", center_zone_3)

        self.turn_right_90()
        time.sleep(0.1)

        if not self.follow_dark_gray_to_station(4):
            print("Abort after S4 forward")
            return

        self.turn_around()
        time.sleep(0.1)
        center_zone_4 = self.return_along_dark_gray_to_center()
        print("After S4, center zone:", center_zone_4)

        print("COURSE COMPLETE")
        self.stop()



if __name__ == "__main__":
    robot = DecayOrienteering()
    time.sleep(1)
    robot.run()
