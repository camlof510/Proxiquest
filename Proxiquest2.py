# -------------------------------------------------------
#   PROXIQUEST — 3 Button Version (Non-Blocking)
# -------------------------------------------------------

from gpiozero import LED, Button
import RPi.GPIO as GPIO
import threading
import time
import random

# -------------------------------------------------------
#   ULTRASONIC SENSOR
# -------------------------------------------------------
TRIG = 23
ECHO = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# -------------------------------------------------------
#   LEDs (use 3 LEDs to match 3 buttons)
# -------------------------------------------------------
leds = [LED(2), LED(26), LED(13)]   # pick any 3

# -------------------------------------------------------
#   Buttons (only 3 now)
#   Buttons wired to GND → use pull_up=True
# -------------------------------------------------------
button_pins = [4, 7, 27]    # BUTTONS 2,3,4
buttons = [Button(pin, pull_up=True) for pin in button_pins]

# -------------------------------------------------------
#   Game State
# -------------------------------------------------------
score = 0
target_button = None
target_range = (10, 30)
latest_distance = 999  # updated in background thread

# -------------------------------------------------------
#   Ultrasonic Sensor (safer timeouts)
# -------------------------------------------------------
def get_distance():
    GPIO.output(TRIG, False)
    time.sleep(0.002)

    # trigger pulse
    GPIO.out
