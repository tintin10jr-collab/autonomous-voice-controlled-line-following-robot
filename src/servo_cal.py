import pigpio
import time

SERVO_GPIO = 18

pi = pigpio.pi()

if not pi.connected:
    print("ERROR: pigpio daemon is not running.")
    print("Run: sudo systemctl start pigpiod")
    exit()


def move_servo(pulse):
    print(f"Pulse width: {pulse} us")
    pi.set_servo_pulsewidth(SERVO_GPIO, pulse)
    time.sleep(1)


try:

    print("================================")
    print("       SG90 CALIBRATION")
    print("================================")
    print()
    print("Look at the servo/TF02 mounting.")
    print("We want to find the pulse that points")
    print("STRAIGHT FORWARD.")
    print()

    # Start at center
    
    move_servo(500)

    input("Press ENTER to test 800 us...")
    
    move_servo(1100)

    input("Press ENTER to test 800 us...")

    move_servo(1200)

    input("Press ENTER to test 00 us...")

    move_servo(1300)

    input("Press ENTER to test 800 us...")

    move_servo(1400)

    input("Press ENTER to test 900 us...")

    move_servo(900)

    input("Press ENTER to test 1000 us...")

    move_servo(1000)

    print()
    print("Now tell me which pulse width")
    print("points STRAIGHT FORWARD.")


except KeyboardInterrupt:

    print("\nCalibration stopped.")


finally:

    pi.set_servo_pulsewidth(SERVO_GPIO, 0)
    pi.stop()
