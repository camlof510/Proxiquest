# Import libraries for GPIO control and timing
from gpiozero import LED, Button
import RPi.GPIO as GPIO
import time
import random

# --- SETUP FOR ULTRASONIC SENSOR (HC-SR04) ---
TRIG = 23  # GPIO pin for trigger
ECHO = 24  # GPIO pin for echo

GPIO.setmode(GPIO.BCM)  # Use Broadcom pin numbering
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# --- SETUP FOR LEDs ---
# Connect LEDs to GPIO pins 5, 6, 13, 19
leds = [LED(5), LED(6), LED(13), LED(19)]

# --- SETUP FOR BUTTONS ---
# Connect buttons to GPIO pins 17, 27, 22, 10
buttons = [Button(17), Button(27), Button(22), Button(10)]

# --- GAME STATE VARIABLES ---
score = 0  # Player's score
target_button = None  # Which button is correct this round
target_range = (10, 30)  # Acceptable distance range in cm

# --- FUNCTION: Measure distance using HC-SR04 ---
def get_distance():
    GPIO.output(TRIG, False)
    time.sleep(0.05)  # Let sensor settle

    # Send 10µs pulse to trigger
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    # Wait for echo to start
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    # Wait for echo to end
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    # Calculate distance in cm
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    return round(distance, 2)

# --- FUNCTION: Start a new round with random target ---
def new_round():
    global target_button, target_range
    target_button = random.randint(0, 3)  # Pick a button index 0–3
    # Pick a random range between 10–20 and 25–40 cm
    target_range = (random.randint(10, 20), random.randint(25, 40))
    print(f"\n🎯 New Round: Press Button {target_button+1} and stay within {target_range[0]}–{target_range[1]} cm")

# --- FUNCTION: Handle button press ---
def check_input(index):
    global score
    dist = get_distance()
    print(f"Button {index+1} pressed | Distance: {dist} cm")

    # Scoring logic
    if index == target_button and target_range[0] <= dist <= target_range[1]:
        print("✅ Correct input!")
        score += 15
    elif index == target_button:
        print("⚠️ Correct button, wrong distance.")
        score += 5
    elif target_range[0] <= dist <= target_range[1]:
        print("⚠️ Correct distance, wrong button.")
        score += 5
    else:
        print("❌ Wrong input.")
        score -= 5

    print(f"🏆 Score: {score}")
    new_round()  # Start next round

# --- ASSIGN BUTTON HANDLERS ---
for i, button in enumerate(buttons):
    button.when_pressed = lambda i=i: check_input(i)

# --- START GAME ---
print("🎮 Starting ProxiQuest!")
new_round()

# --- MAIN LOOP ---
try:
    while True:
        time.sleep(0.1)  # Keep the program alive

except KeyboardInterrupt:
    GPIO.cleanup()  # Clean up GPIO on Ctrl+C
    print("\nGame Over. Final Score:", score)
