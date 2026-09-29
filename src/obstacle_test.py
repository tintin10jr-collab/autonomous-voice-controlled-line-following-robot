import time
import serial
import RPi.GPIO as GPIO


# ============================================================
# CONFIGURATION
# ============================================================

UART_PORT = "/dev/serial0"
UART_BAUDRATE = 115200

SERVO_GPIO = 18

LEFT_ANGLE = 45
CENTER_ANGLE = 90
RIGHT_ANGLE = 135


# ============================================================
# GPIO SETUP
# ============================================================

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(SERVO_GPIO, GPIO.OUT)

servo = GPIO.PWM(SERVO_GPIO, 50)
servo.start(0)


# ============================================================
# SERVO CONTROL
# ============================================================

def servo_angle(angle):

    # SG90 approximate PWM conversion
    duty = 2.5 + (angle / 18.0)

    servo.ChangeDutyCycle(duty)

    # Give servo time to move
    time.sleep(0.5)

    # Reduce jitter
    servo.ChangeDutyCycle(0)


# ============================================================
# TF02-PRO UART
# ============================================================

print()
print("========================================")
print("       TF02-PRO + SERVO TEST")
print("========================================")
print()

print("Opening UART:", UART_PORT)

try:

    lidar = serial.Serial(
        port=UART_PORT,
        baudrate=UART_BAUDRATE,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=0.2
    )

except Exception as e:

    print()
    print("ERROR opening UART:")
    print(e)

    servo.stop()
    GPIO.cleanup()

    exit()


print("UART opened successfully.")
print("Baud rate:", UART_BAUDRATE)


# ============================================================
# TF02-PRO DATA READER
# ============================================================

def read_distance():

    # Read bytes until we find the TF02-Pro header
    while lidar.in_waiting > 0:

        first = lidar.read(1)

        if len(first) != 1:
            return None

        if first[0] != 0x59:
            continue

        second = lidar.read(1)

        if len(second) != 1:
            return None

        if second[0] != 0x59:
            continue

        # Remaining 7 bytes
        remaining = lidar.read(7)

        if len(remaining) != 7:
            return None

        frame = bytes(
            [0x59, 0x59]
        ) + remaining

        # ----------------------------------------------------
        # CHECKSUM
        # ----------------------------------------------------

        checksum = sum(frame[0:8]) & 0xFF

        if checksum != frame[8]:
            continue

        # ----------------------------------------------------
        # DISTANCE
        #
        # TF02-Pro standard frame:
        # Byte 2 = distance low
        # Byte 3 = distance high
        #
        # Distance is cm
        # ----------------------------------------------------

        distance_cm = (
            frame[2]
            |
            (frame[3] << 8)
        )

        return distance_cm

    return None


# ============================================================
# GET MULTIPLE READINGS
# ============================================================

def get_distance():

    readings = []

    start_time = time.time()

    while time.time() - start_time < 0.5:

        distance = read_distance()

        if distance is not None:

            readings.append(distance)

        time.sleep(0.01)

    if len(readings) == 0:

        return None

    # Median gives us a more stable reading
    readings.sort()

    middle = len(readings) // 2

    return readings[middle]


# ============================================================
# START
# ============================================================

try:

    print()
    print("Centering servo...")

    servo_angle(CENTER_ANGLE)

    time.sleep(1)

    # Clear any old UART data
    lidar.reset_input_buffer()

    print()
    print("========================================")
    print("              READY")
    print("========================================")
    print()
    print("Scanning:")
    print("LEFT   = 45 degrees")
    print("CENTER = 90 degrees")
    print("RIGHT  = 135 degrees")
    print()
    print("Press CTRL+C to stop.")
    print()


    while True:

        # ====================================================
        # LEFT
        # ====================================================

        servo_angle(LEFT_ANGLE)

        distance_left = get_distance()

        if distance_left is not None:

            print(
                "LEFT   | Servo: 45°  | Distance:",
                distance_left,
                "cm"
            )

        else:

            print(
                "LEFT   | Servo: 45°  | No reading"
            )


        # ====================================================
        # CENTER
        # ====================================================

        servo_angle(CENTER_ANGLE)

        distance_center = get_distance()

        if distance_center is not None:

            print(
                "CENTER | Servo: 90°  | Distance:",
                distance_center,
                "cm"
            )

        else:

            print(
                "CENTER | Servo: 90°  | No reading"
            )


        # ====================================================
        # RIGHT
        # ====================================================

        servo_angle(RIGHT_ANGLE)

        distance_right = get_distance()

        if distance_right is not None:

            print(
                "RIGHT  | Servo: 135° | Distance:",
                distance_right,
                "cm"
            )

        else:

            print(
                "RIGHT  | Servo: 135° | No reading"
            )


        # ====================================================
        # SIMPLE DECISION
        # ====================================================

        if (
            distance_left is not None
            and
            distance_right is not None
        ):

            if distance_left > distance_right:

                print(
                    ">>> More space on LEFT"
                )

            elif distance_right > distance_left:

                print(
                    ">>> More space on RIGHT"
                )

            else:

                print(
                    ">>> LEFT and RIGHT are equal"
                )


        print("----------------------------------------")

        time.sleep(0.5)


# ============================================================
# STOP
# ============================================================

except KeyboardInterrupt:

    print()
    print("Stopping obstacle test...")


finally:

    # Return servo to center
    try:
        servo_angle(CENTER_ANGLE)
    except:
        pass

    servo.stop()

    lidar.close()

    GPIO.cleanup()

    print()
    print("Obstacle test stopped safely.")