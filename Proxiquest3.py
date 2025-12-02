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
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    # wait for echo start
    start_limit = time.time() + 0.02
    while GPIO.input(ECHO) == 0:
        if time.time() > start_limit:
            return 999
    pulse_start = time.time()

    # wait for echo end
    end_limit = time.time() + 0.02
    while GPIO.input(ECHO) == 1:
        if time.time() > end_limit:
            return 999
    pulse_end = time.time()

    duration = pulse_end - pulse_start
    return round(duration * 17150, 1)

# -------------------------------------------------------
#   Background Distance Thread
# -------------------------------------------------------
def ultrasonic_worker():
    global latest_distance
    while True:
        latest_distance = get_distance()
        time.sleep(0.05)

# -------------------------------------------------------
#   Start New Round
# -------------------------------------------------------
def new_round():
    global target_button, target_range

    target_button = random.randint(0, 2)  # only 3 buttons now
    target_range = (random.randint(10, 20), random.randint(25, 40))

    # LED indication
    for i, led in enumerate(leds):
        led.on() if i == target_button else led.off()

    print("\n-------------------------------------")
    print("🎯 New Round:")
    print(f"👉 Press Button {target_button + 1}")
    print(f"📏 Stay within {target_range[0]}–{target_range[1]} cm")
    print("-------------------------------------")

# -------------------------------------------------------
#   Handle Button Press
# -------------------------------------------------------
def handle_press(i):
    global score

    dist = latest_distance
    print(f"\nButton {i+1} pressed | Distance: {dist} cm")

    if dist == 999:
        print("⚠️ Distance not detected — try again.")
        return

    right_button = (i == target_button)
    right_distance = (target_range[0] <= dist <= target_range[1])

    if right_button and right_distance:
        print("✅ Perfect! Correct button + correct distance!")
        score += 15
    elif right_button:
        print("➕ Correct button, wrong distance.")
        score += 5
    elif right_distance:
        print("➕ Correct distance, wrong button.")
        score += 5
    else:
        print("❌ Wrong button AND wrong distance!")
        score -= 5

    print(f"🏆 Score: {score}")
    new_round()

# -------------------------------------------------------
#   Attach Events
# -------------------------------------------------------
for i, b in enumerate(buttons):
    b.when_pressed = (lambda idx=i: handle_press(idx))

# -------------------------------------------------------
#   Start Game
# -------------------------------------------------------
print("🎮 Starting ProxiQuest — 3 Button Edition!")
time.sleep(0.2)  # ultrasonic warm-up
threading.Thread(target=ultrasonic_worker, daemon=True).start()
new_round()

try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    GPIO.cleanup()
    print("\nGame Over. Final Score:", score)
