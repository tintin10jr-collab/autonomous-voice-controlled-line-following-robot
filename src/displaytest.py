import serial
import time

ESP32_PORT = "/dev/ttyUSB0"
BAUD_RATE = 115200

esp32 = serial.Serial(
    ESP32_PORT,
    BAUD_RATE,
    timeout=1
)

# Give ESP32 time to reset after USB connection
time.sleep(2)

print("ESP32 connected!")
print("Type a command:")

try:
    while True:
        print()
        print("1 = IDLE")
        print("2 = LISTEN")
        print("3 = TALK")
        print("4 = THINK")
        print("5 = HAPPY")
        print("6 = EXCITED")
        print("7 = SAD")
        print("8 = CONFUSED")
        print("9 = FOCUS")
        print("10 = ALERT")
        print("q = Quit")

        choice = input("Command: ").strip()

        commands = {
            "1": "IDLE",
            "2": "LISTEN",
            "3": "TALK",
            "4": "THINK",
            "5": "HAPPY",
            "6": "EXCITED",
            "7": "SAD",
            "8": "CONFUSED",
            "9": "FOCUS",
            "10": "ALERT"
        }

        if choice.lower() == "q":
            break

        if choice in commands:
            command = commands[choice]

            esp32.write((command + "\n").encode())

            print("Sent:", command)

        else:
            print("Invalid command")

except KeyboardInterrupt:
    print("\nStopping...")

finally:
    esp32.close()
    print("ESP32 disconnected.")