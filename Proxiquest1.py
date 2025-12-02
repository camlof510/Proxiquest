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
target_range = (10, 30)
latest_distance = 999  # updated in background thread

# -------------------------------------------------------
#   Ultrasonic Sensor (safe, timeout-protected)
# -------------------------------------------------------
def get_distance():
    GPIO.output(TRIG, False)
    time.sleep(0.002)

    # Trigger pulse
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    # Wait for echo start (timeout)
    start_time = time.time()
    while GPIO.input(ECHO) == 0:
        if time.time() - start_time > 0.005:
            return 999
    pulse_start = time.time()

    # Wait for echo end (timeout)
    start_time = time.time()
    while GPIO.input(ECHO) == 1:
        if time.time() - start_time > 0.005:
            return 999
    pulse_end = time.time()

    # Calculate distance in cm
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    return round(distance, 1)

# -------------------------------------------------------
#   Ultrasonic Worker Thread (non-blocking)
# -------------------------------------------------------
def ultrasonic_worker():
    global latest_distance
    while True:
        latest_distance = get_distance()
        time.sleep(0.05)  # 20 readings per sec

# -------------------------------------------------------
#   Start a new round
# -------------------------------------------------------
def new_round():
    global target_button, target_range

    target_button = random.randint(0, 3)
    target_range = (
        random.randint(10, 20),
        random.randint(25, 40)
    )

    # Light only the target LED
    for i, led in enumerate(leds):
        led.on() if i == target_button else led.off()

    print("\n-------------------------------------")
    print("🎯 New Round:")
    print(f"➡ Press Button {target_button + 1}")
    print(f"➡ Stay within {target_range[0]}–{target_range[1]} cm")
    print("-------------------------------------")

# -------------------------------------------------------
#   Handle Button Press
# -------------------------------------------------------
def handle_press(i):
    global score

    dist = latest_distance
    print(f"\nButton {i+1} pressed | Distance: {dist} cm")

    if dist == 999:
        print("⚠️ Distance not detected (timeout). Try again.")
        return

    correct_button = (i == target_button)
    correct_distance = (target_range[0] <= dist <= target_range[1])

    if correct_button and correct_distance:
        print("✅ Correct button AND correct distance!")
        score += 15
    elif correct_button:
        print("➡ Correct button, BUT wrong distance.")
        score += 5
    elif correct_distance:
        print("➡ Correct distance, BUT wrong button.")
        score += 5
    else:
        print("❌ Wrong button AND wrong distance.")
        score -= 5

    print(f"🏆 Score: {score}")
    new_round()

# -------------------------------------------------------
#   Attach button events (correct lambda capture)
# -------------------------------------------------------
for i, b in enumerate(buttons):
    b.when_pressed = (lambda idx=i: handle_press(idx))

# -------------------------------------------------------
#   Start the game
# -------------------------------------------------------
print("🎮 Starting ProxiQuest!")
threading.Thread(target=ultrasonic_worker, daemon=True).start()
new_round()

try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    GPIO.cleanup()
    print("\nGame Over. Final Score:", score)
