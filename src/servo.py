import pigpio
import time

SERVO_GPIO = 18

# Your calibrated positions
LEFT = 500
CENTER = 800
RIGHT = 1100

# Smaller = faster
STEP_DELAY = 0.015

pi = pigpio.pi()

if not pi.connected:
    print("ERROR: pigpio daemon is not running.")
    print("Run:")
    print("sudo systemctl start pigpiod")
    exit()


def set_servo(pulse):
    pi.set_servo_pulsewidth(
        SERVO_GPIO,
        pulse
    )


try:

    print("================================")
    print("      SERVO SWEEP TEST")
    print("================================")
    print()
    print("Left   : 500 us")
    print("Center : 800 us")
    print("Right  : 1100 us")
    print()

    while True:

        # ==============================================
        # LEFT → RIGHT
        # ==============================================

        print("Moving LEFT → RIGHT")

        for pulse in range(LEFT, RIGHT + 1, 2):

            set_servo(pulse)

            time.sleep(STEP_DELAY)


        # ==============================================
        # RIGHT → LEFT
        # ==============================================

        print("Moving RIGHT → LEFT")

        for pulse in range(RIGHT, LEFT - 1, -2):

            set_servo(pulse)

            time.sleep(STEP_DELAY)


except KeyboardInterrupt:

    print()
    print("Stopping servo...")


finally:

    # Return to calibrated center
    set_servo(CENTER)

    time.sleep(0.5)

    # Stop servo pulses
    pi.set_servo_pulsewidth(
        SERVO_GPIO,
        0
    )

    pi.stop()

    print("Servo stopped at center.")
