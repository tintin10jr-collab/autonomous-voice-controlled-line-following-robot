# Hardware Pinout and Connections

## 1. Main Controller

- **Controller:** Raspberry Pi 4 Model B
- **Operating System:** Raspberry Pi OS
- **Programming Language:** Python
- **Motor Drivers:** 2 × L298N motor drivers (front and rear)

## 2. Rear Motor Driver (L298N)

| Signal | Physical Pin | BCM GPIO |
|---|---:|---:|
| ENA | 22 | GPIO 25 |
| IN1 | 24 | GPIO 8 |
| IN2 | 26 | GPIO 7 |
| IN3 | 36 | GPIO 16 |
| IN4 | 38 | GPIO 20 |
| ENB | 40 | GPIO 21 |

### Power Connections
- Battery positive (+) → motor driver's battery supply terminal
- Battery negative (−) → motor driver's ground terminal

## 3. Front Motor Driver (L298N)

| Signal | Physical Pin | BCM GPIO |
|---|---:|---:|
| ENA | 19 | GPIO 10 |
| IN1 | 21 | GPIO 9 |
| IN2 | 23 | GPIO 11 |
| IN3 | 29 | GPIO 5 |
| IN4 | 31 | GPIO 6 |
| ENB | 33 | GPIO 13 |

### Power Connections
- Battery positive (+) → motor driver's battery supply terminal
- Battery negative (−) → motor driver's ground terminal

## 4. TF02 Pro LiDAR

| LiDAR Wire | Raspberry Pi Connection |
|---|---|
| Red | 5V |
| Black | GND |
| Green | Physical Pin 10 (BCM GPIO 15 / UART RXD) |
| White | Physical Pin 8 (BCM GPIO 14 / UART TXD) |

**Note:** Confirm the LiDAR's wire assignments and UART configuration against its manufacturer documentation and the working setup.

## 5. IR Line Sensors

| Sensor Signal | Raspberry Pi Connection |
|---|---|
| VCC | 3.3V |
| GND | GND |
| Left sensor DO | Physical Pin 11 (BCM GPIO 17) |
| Centre sensor DO | Physical Pin 13 (BCM GPIO 27) |
| Right sensor DO | Physical Pin 15 (BCM GPIO 22) |

The three IR sensors detect the black line on the predefined route.

## 6. Servo Motor

| Servo Wire | Raspberry Pi Connection |
|---|---|
| Brown | GND |
| Red | 5V |
| Orange / Yellow | Physical Pin 12 (BCM GPIO 18) |

The servo connection is documented from the supplied wiring information. Confirm its role in the final robot configuration before use.

## 7. Hardware Safety Notes

- Never connect motors directly to Raspberry Pi GPIO pins.
- Confirm the correct supply voltage and current requirements for each component.
- Ensure the Raspberry Pi and motor driver control signals share a suitable common ground.
- Check the L298N enable jumpers and PWM configuration before running motor-control software.
- Verify all connections with the power disconnected before making changes.
- Avoid powering motors from the Raspberry Pi's 5V pin unless the power arrangement has been specifically designed for it.

## 8. Verification Status

This pinout records the supplied physical pin and BCM GPIO assignments. Verify the connections against the assembled robot and its source code before using this document as a build guide.
