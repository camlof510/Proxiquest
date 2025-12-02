# Import libraries for GPIO control and timing
from gpiozero import LED, Button
import RPi.GPIO as GPIO
import time
import random

# -------------------------------------------------------
#   ULTRASONIC SENSOR (HC-SR04) — GPIO PINS
# -------------------------------------------------------
TRIG = 23
ECHO = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# -------------------------------------------------------
#   LEDs — CONNECTED TO GPIO PINS 2, 26, 13, 11
# -------------------------------------------------------
leds = [LED(2), LED(26), LED(13), LED(11)]

# -------------------------------------------------------
#   BUTTONS — CONNECTED TO GPIO PINS 9, 4, 7, 27
#   (Buttons wired to GND, using internal pull-ups)
# -------------------------------------------------------
buttons = [Button(9), Button(4), Button(7), Button(27)]

# -------------------------------------------------------
#   GAME STATE
# -------------------------------------------------------
score = 0
target_button = None
target_range = (10, 30)

# -------------------------------------------------------
#   ULTRASONIC MEASUREMENT (NON-BLOCKING, SAFE)
# -------------------------------------------------------
def get_distance():
    GPIO.output(TRIG, False)
    time.sleep(0.002)

    # Trigger pulse
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    # Wait for echo start with timeout
    start_timeout = time.time() + 0.02
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
        if time.time() > start_timeout:
            return 999  # No echo

    # Wait for echo end with timeout
    end_timeout = time.time() + 0.02
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
        if time.time() > end_timeout:
            return 999

    # Calculate distance
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    return round(distance, 2)

# -------------------------------------------------------
#   START A NEW ROUND
# -------------------------------------------------------
def new_round():
    global target_button, target_range

    target_button = random.randint(0, 3)
    target_range = (
        random.randint(10, 20),
        random.randint(25, 40)
    )

    print("\n-------------------------------------")
    print(f"🎯 New Round:")
    print(f"➡ Press Button {target_button+1}")
    print(f"➡ Stay within {target_range[0]}–{target_range[1]} cm")
    print("-------------------------------------")

# -------------------------------------------------------
#   HANDLE BUTTON PRESS
# -------------------------------------------------------
def check_input(index):
    global score

    dist = get_distance()
    print(f"\nButton {index+1} pressed | Distance: {dist} cm")

    if dist == 999:
        print("⚠️ Distance not detected, ignoring...")
        return

    # Scoring logic
    correct_button = index == target_button
    correct_distance = target_range[0] <= dist <= target_range[1]

    if correct_button and correct_distance:
        print("✅ Correct button AND distance!")
        score += 15
    elif correct_button:
        print("⚠️ Correct button, wrong distance.")
        score += 5
    elif correct_distance:
        print("⚠️ Correct distance, wrong button.")
        score += 5
    else:
        print("❌ Wrong button AND wrong distance.")
        score -= 5

    print(f"🏆 Score: {score}")
    new_round()

# -------------------------------------------------------
#   ATTACH BUTTON EVENTS
# -------------------------------------------------------
for i, button in enumerate(buttons):
    button.when_pressed = lambda i=i: check_input(i)

# -------------------------------------------------------
#   START GAME
# -------------------------------------------------------
print("🎮 Starting ProxiQuest!")
new_round()

try:
    while True:
        time.sleep(0.1)

except KeyboardInterrupt:
    GPIO.cleanup()
    print("\nGame Over. Final Score:", score)

        
   
        


        
