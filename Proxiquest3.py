# -------------------------------------------------------
#   PROXIQUEST — 3 Button Version (Safe Test Mode)
# -------------------------------------------------------

from gpiozero import LED, Button
import time
import random

# -------------------------------------------------------
#   LEDs (3 LEDs for 3 buttons)
# -------------------------------------------------------
leds = [LED(2), LED(26), LED(13)]   # adjust pins to your setup

# -------------------------------------------------------
#   Buttons (only 3 now)
# -------------------------------------------------------
button_pins = [4, 7, 27]    # Buttons 2,3,4
buttons = [Button(pin, pull_up=True) for pin in button_pins]

# -------------------------------------------------------
#   Game State
# -------------------------------------------------------
score = 0
target_button = None
target_range = (10, 30)
latest_distance = 999  # will simulate distances

# -------------------------------------------------------
#   Simulate Distance Reading
# -------------------------------------------------------
def get_simulated_distance():
    # Random distance between 5 and 50 cm
    return round(random.uniform(5, 50), 1)

# -------------------------------------------------------
#   Start a new round
# -------------------------------------------------------
def new_round():
    global target_button, target_range, latest_distance

    target_button = random.randint(0, 2)  # only 3 buttons
    target_range = (random.randint(10, 20), random.randint(25, 40))
    latest_distance = get_simulated_distance()  # new simulated distance

    # LED indication
    for i, led in enumerate(leds):
        led.on() if i == target_button else led.off()

    print("\n-------------------------------------")
    print("🎯 New Round:")
    print(f"👉 Press Button {target_button + 1}")
    print(f"📏 Stay within {target_range[0]}–{target_range[1]} cm")
    print(f"(Simulated distance: {latest_distance} cm)")
    print("-------------------------------------")

# -------------------------------------------------------
#   Handle Button Press
# -------------------------------------------------------
def handle_press(i):
    global score, latest_distance

    # Update simulated distance on every press
    latest_distance = get_simulated_distance()
    dist = latest_distance
    print(f"\nButton {i+1} pressed | Distance: {dist} cm")

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
#   Attach button events
# -------------------------------------------------------
for i, b in enumerate(buttons):
    b.when_pressed = (lambda idx=i: handle_press(idx))

# -------------------------------------------------------
#   Start the game
# -------------------------------------------------------
print("🎮 Starting ProxiQuest — 3 Button Edition (Simulated Distance)")
new_round()  # show the first round immediately

try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nGame Over. Final Score:", score)
