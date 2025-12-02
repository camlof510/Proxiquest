# -------------------------------------------------------
#   PROXIQUEST — Non-Blocking, Threaded Ultrasonic Game
# -------------------------------------------------------

from gpiozero import LED, Button
import RPi.GPIO as GPIO
import threading
import time
import random

# -------------------------------------------------------
#   ULTRASONIC SENSOR — GPIO pins
# -------------------------------------------------------
TRIG = 23
ECHO = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# -------------------------------------------------------
#   LEDs + Buttons
# -------------------------------------------------------
leds = [LED(2), LED(26), LED(13), LED(11)]

# Buttons wired to GND -> need pull_up=True
buttons = [
    Button(9, pull_up=True),
    Button(4, pull_up=True),
    Button(7, pull_up=True),
    Button(27, pull_up=True)
]

# -------------------------------------------------------
#   Game State
# -------------------------------------------------------
score = 0
target_button = None
target_range_


        
   
        


        
