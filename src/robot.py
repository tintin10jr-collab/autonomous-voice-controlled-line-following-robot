import RPi.GPIO as GPIO
import time
import json
import os
import subprocess
import serial
import pigpio
import threading
import pyaudio
from vosk import Model, KaldiRecognizer


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "vosk-model-small-en-us-0.15"
)

CANTEEN_AUDIO = os.path.join(
    BASE_DIR,
    "canteen.mp3"
)

GATE_AUDIO = os.path.join(
    BASE_DIR,
    "gate.mp3"
)
GUIDE_AUDIO = os.path.join(
    BASE_DIR,
    "guide.mp3"
)

CANTEEN_START_AUDIO = os.path.join(
    BASE_DIR,
    "canteen_start.mp3"
)

GATE_START_AUDIO = os.path.join(
    BASE_DIR,
    "canteen_start.mp3"
)

# ============================================================
# ESP32 OLED
# ============================================================

ESP32_PORT = "/dev/ttyUSB0"
ESP32_BAUD = 115200

try:
    esp32 = serial.Serial(
        ESP32_PORT,
        ESP32_BAUD,
        timeout=1
    )

    # ESP32 may reset when serial connection opens
    time.sleep(2)

    print("ESP32 OLED connected.")

except Exception as e:
    print("WARNING: ESP32 OLED not connected.")
    print(e)
    esp32 = None


def set_face(face):
    """
    Send a face command to the ESP32.
    Supported:
    IDLE, LISTEN, TALK, THINK, HAPPY,
    EXCITED, SAD, CONFUSED, FOCUS, ALERT
    """

    if esp32 is None:
        return

    try:
        esp32.write((face + "\n").encode())
        esp32.flush()

        print("ESP32 face:", face)

    except Exception as e:
        print("ESP32 communication error:", e)
# ============================================================
# MOTOR GPIO
# ============================================================

# FRONT L298N

FRONT_ENA = 5
FRONT_IN1 = 6
FRONT_IN2 = 13

FRONT_ENB = 19
FRONT_IN3 = 26
FRONT_IN4 = 16


# REAR L298N

REAR_ENA = 20
REAR_IN1 = 21
REAR_IN2 = 12

REAR_ENB = 25
REAR_IN3 = 24
REAR_IN4 = 23


# ============================================================
# GPIO INITIALIZATION
# ============================================================

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


PINS = [
    FRONT_ENA,
    FRONT_IN1,
    FRONT_IN2,
    FRONT_ENB,
    FRONT_IN3,
    FRONT_IN4,

    REAR_ENA,
    REAR_IN1,
    REAR_IN2,
    REAR_ENB,
    REAR_IN3,
    REAR_IN4
]


for pin in PINS:
    GPIO.setup(pin, GPIO.OUT)


# ============================================================
# PWM
# ============================================================

PWM_FREQUENCY = 1000

front_left_pwm = GPIO.PWM(
    FRONT_ENA,
    PWM_FREQUENCY
)

front_right_pwm = GPIO.PWM(
    FRONT_ENB,
    PWM_FREQUENCY
)

rear_left_pwm = GPIO.PWM(
    REAR_ENA,
    PWM_FREQUENCY
)

rear_right_pwm = GPIO.PWM(
    REAR_ENB,
    PWM_FREQUENCY
)


front_left_pwm.start(0)
front_right_pwm.start(0)
rear_left_pwm.start(0)
rear_right_pwm.start(0)

set_face("IDLE")
# ============================================================
# ROBOT SETTINGS
# ============================================================

MOTOR_SPEED = 70

CANTEEN_TIME = 5.0
GATE_TIME = 8.0

# Calibrate this later
TURN_TIME = 1.5

# ============================================================
# SERVO SETTINGS
# ============================================================

SERVO_GPIO = 18

SERVO_LEFT = 500
SERVO_CENTER = 800
SERVO_RIGHT = 1100

SERVO_STEP = 2
SERVO_STEP_DELAY = 0.015

servo_pi = pigpio.pi()

if not servo_pi.connected:
    print("ERROR: pigpio daemon is not running.")
    print("Run:")
    print("sudo systemctl start pigpiod")
    GPIO.cleanup()
    exit()

servo_running = False
servo_thread = None
# ============================================================
# SERVO FUNCTIONS
# ============================================================

def set_servo(pulse):
    servo_pi.set_servo_pulsewidth(
        SERVO_GPIO,
        pulse
    )


def servo_sweep():

    global servo_running

    print("Servo scanning...")

    while servo_running:

        # LEFT → RIGHT
        for pulse in range(
            SERVO_LEFT,
            SERVO_RIGHT + 1,
            SERVO_STEP
        ):

            if not servo_running:
                break

            set_servo(pulse)
            time.sleep(SERVO_STEP_DELAY)

        # RIGHT → LEFT
        for pulse in range(
            SERVO_RIGHT,
            SERVO_LEFT - 1,
            -SERVO_STEP
        ):

            if not servo_running:
                break

            set_servo(pulse)
            time.sleep(SERVO_STEP_DELAY)


def start_servo_sweep():

    global servo_running
    global servo_thread

    if servo_running:
        return

    servo_running = True

    servo_thread = threading.Thread(
        target=servo_sweep,
        daemon=True
    )

    servo_thread.start()


def stop_servo_sweep():

    global servo_running

    servo_running = False

    if servo_thread is not None:
        servo_thread.join(timeout=1)

    # Return to physical center
    set_servo(SERVO_CENTER)

    time.sleep(0.3)

    # Stop servo pulses
    servo_pi.set_servo_pulsewidth(
        SERVO_GPIO,
        0
    )

    print("Servo centered.")
# ============================================================
# MOTOR FUNCTIONS
# ============================================================

def motor_forward(in1, in2, pwm, speed=MOTOR_SPEED):

    GPIO.output(in1, GPIO.HIGH)
    GPIO.output(in2, GPIO.LOW)

    pwm.ChangeDutyCycle(speed)


def motor_backward(in1, in2, pwm, speed=MOTOR_SPEED):

    GPIO.output(in1, GPIO.LOW)
    GPIO.output(in2, GPIO.HIGH)

    pwm.ChangeDutyCycle(speed)


def motor_stop(in1, in2, pwm):

    GPIO.output(in1, GPIO.LOW)
    GPIO.output(in2, GPIO.LOW)

    pwm.ChangeDutyCycle(0)


# ============================================================
# STOP ROBOT
# ============================================================

def stop_robot():

    motor_stop(
        FRONT_IN1,
        FRONT_IN2,
        front_left_pwm
    )

    motor_stop(
        FRONT_IN3,
        FRONT_IN4,
        front_right_pwm
    )

    motor_stop(
        REAR_IN1,
        REAR_IN2,
        rear_left_pwm
    )

    motor_stop(
        REAR_IN3,
        REAR_IN4,
        rear_right_pwm
    )


# ============================================================
# MOVE FORWARD
# ============================================================

def move_forward(duration):

    print()
    print("================================")
    print("ROBOT MOVING FORWARD")
    print("================================")

    # OLED → ALERT
    set_face("ALERT")

    # Start servo scanning
    start_servo_sweep()

    # ----------------------------------------
    # START ALL FOUR MOTORS
    # ----------------------------------------

    motor_forward(
        FRONT_IN1,
        FRONT_IN2,
        front_left_pwm
    )

    motor_forward(
        FRONT_IN3,
        FRONT_IN4,
        front_right_pwm
    )

    motor_forward(
        REAR_IN1,
        REAR_IN2,
        rear_left_pwm
    )

    motor_forward(
        REAR_IN3,
        REAR_IN4,
        rear_right_pwm
    )

    # Robot moves for specified time
    time.sleep(duration)

    # ----------------------------------------
    # STOP MOTORS
    # ----------------------------------------

    stop_robot()

    # Stop servo scanning
    stop_servo_sweep()



    print("Movement completed.")
# ============================================================
# 180 DEGREE TURN
# ============================================================

def turn_180():

    print()
    print("================================")
    print("TURNING 180 DEGREES")
    print("================================")

    # Stop servo scanning
    stop_servo_sweep()

    # OLED → ALERT
    set_face("ALERT")

    # LEFT SIDE BACKWARD

    motor_backward(
        FRONT_IN1,
        FRONT_IN2,
        front_left_pwm
    )

    motor_backward(
        REAR_IN1,
        REAR_IN2,
        rear_left_pwm
    )

    # RIGHT SIDE FORWARD

    motor_forward(
        FRONT_IN3,
        FRONT_IN4,
        front_right_pwm
    )

    motor_forward(
        REAR_IN3,
        REAR_IN4,
        rear_right_pwm
    )

    time.sleep(TURN_TIME)

    stop_robot()

    # Servo stays centered
    set_servo(SERVO_CENTER)



    print("180 degree turn completed.")


# ============================================================
# PLAY AUDIO
# ============================================================

def play_audio(filename):

    if not os.path.exists(filename):

        print()
        print("ERROR: Audio file not found:")
        print(filename)

        return


    print()
    print("================================")
    print("PLAYING AUDIO")
    print("================================")

    print(filename)

    # Robot is talking
    set_face("TALK")

    subprocess.run(
        [
            "mpg123",
            "-q",
            filename
        ],
        check=False
    )

    print("Audio finished.")


# ============================================================
# CANTEEN ROUTINE
# ============================================================

def go_to_canteen():

    print()
    print("################################")
    print("      CANTEEN ROUTINE")
    print("################################")

    play_audio(CANTEEN_START_AUDIO)

    time.sleep(0.5)
    # MOVE

    move_forward(
        CANTEEN_TIME
    )


    time.sleep(0.5)


    # TURN

    turn_180()


    time.sleep(0.5)


    # PLAY SOUND

    play_audio(
        CANTEEN_AUDIO
    )


    print()
    print("CANTEEN ROUTINE COMPLETE")
    print()


# ============================================================
# GATE ROUTINE
# ============================================================

def go_to_gate():

    print()
    print("################################")
    print("        GATE ROUTINE")
    print("################################")

    play_audio(GATE_START_AUDIO)

    time.sleep(0.5)
    # MOVE

    move_forward(
        GATE_TIME
    )


    time.sleep(0.5)


    # TURN

    turn_180()


    time.sleep(0.5)


    # PLAY SOUND

    play_audio(
        GATE_AUDIO
    )


    print()
    print("GATE ROUTINE COMPLETE")
    print()


# ============================================================
# CHECK VOSK MODEL
# ============================================================

print()
print("========================================")
print("     RASPBERRY PI VOICE ROBOT")
print("========================================")

print()
print("Checking Vosk model...")

if not os.path.exists(MODEL_PATH):

    print()
    print("ERROR!")
    print("Vosk model was not found.")
    print()
    print("Looking for:")
    print(MODEL_PATH)
    print()

    GPIO.cleanup()
    exit()


print("Vosk model found.")


# ============================================================
# LOAD VOSK
# ============================================================

print()
print("Loading Vosk model...")
print("Please wait...")

model = Model(
    MODEL_PATH
)

recognizer = KaldiRecognizer(
    model,
    16000
)

print("Vosk model loaded successfully.")


# ============================================================
# AUDIO FILE CHECK
# ============================================================

print()
print("Checking audio files...")

if os.path.exists(CANTEEN_AUDIO):

    print("canteen.mp3 : OK")

else:

    print("canteen.mp3 : NOT FOUND")


if os.path.exists(GATE_AUDIO):

    print("gate.mp3 : OK")

else:

    print("gate.mp3 : NOT FOUND")


# ============================================================
# MICROPHONE
# ============================================================

print()
print("Starting USB microphone...")

audio = pyaudio.PyAudio()


try:

    stream = audio.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=16000,
        input=True,
        frames_per_buffer=8000
    )


except Exception as e:

    print()
    print("ERROR opening microphone:")
    print(e)

    audio.terminate()
    GPIO.cleanup()

    exit()


stream.start_stream()


# ============================================================
# READY
# ============================================================

print()
print("========================================")
print("             READY")
print("========================================")
print()
print("Speak normally.")
print()
print('Example:')
print('    "Go to the canteen"')
print()
print('    "Go to the gate"')
print()
print("The recognized words will appear below.")
print()
print("========================================")
print()


# ============================================================
# MAIN LOOP
# ============================================================

try:

    while True:

        data = stream.read(
            4000,
            exception_on_overflow=False
        )


        # ====================================================
        # FINAL RECOGNITION
        # ====================================================

        if recognizer.AcceptWaveform(data):

            result = json.loads(
                recognizer.Result()
            )

            text = result.get(
                "text",
                ""
            ).lower().strip()


            if text:

                print()
                print("Recognized:", text)

                if "guide" in text or "robot" in text:
                    print()
                    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                    print("DETECTED: HI GUIDE ROBOT")
                    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                    print()
                    play_audio(GUIDE_AUDIO)
                    set_face("IDLE")
                # ============================================
                # CANTEEN DETECTION
                # ============================================

                elif "canteen" in text or "candy" in text:

                    print()
                    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                    print("DETECTED: CANTEEN")
                    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                    print()

                    go_to_canteen()
                    set_face("IDLE")


                # ============================================
                # GATE DETECTION
                # ============================================

                elif "gate" in text or "get" in text or "entrance" in text:

                    print()
                    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                    print("DETECTED: GATE")
                    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                    print()

                    go_to_gate()
                    set_face("IDLE")


        # ====================================================
        # PARTIAL RECOGNITION
        # ====================================================

        else:

            partial_result = json.loads(
                recognizer.PartialResult()
            )

            partial_text = partial_result.get(
                "partial",
                ""
            ).strip()


            if partial_text:

                print(
                    "Listening: " + partial_text,
                    end="\r"
                )


# ============================================================
# CTRL+C
# ============================================================

except KeyboardInterrupt:

    print()
    print()
    print("CTRL+C detected.")
    print("Stopping robot...")


# ============================================================
# CLEANUP
# ============================================================

finally:

    stop_robot()

    front_left_pwm.stop()
    front_right_pwm.stop()
    rear_left_pwm.stop()
    rear_right_pwm.stop()

    stream.stop_stream()
    stream.close()

    audio.terminate()

    # Return ESP32 display to idle
    set_face("IDLE")

    # Close ESP32 connection
    if esp32 is not None:
        esp32.close()

    GPIO.cleanup()

    print()
    print("========================================")
    print("Robot stopped safely.")
    print("GPIO cleaned up.")
    print("========================================")
