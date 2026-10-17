
# Hardware Pinout and Connections

## 1. Main Controller

- Controller: Raspberry Pi 4 Model B
- Operating system: Raspberry Pi OS
- Programming language: Python

## 2. Hardware Components

| Component | Quantity | Function |
|---|---:|---|
| Raspberry Pi 4B | 1 | Main controller |
| TCRT5000 IR sensors | 3 | Line detection |
| TF02 Pro LiDAR | 1 | Distance measurement and obstacle detection |
| L298N motor driver | As installed | DC motor control |
| DC geared motors | 4 | Robot movement |
| Robot chassis | 1 | Mechanical platform |

## 3. GPIO Connections

GPIO assignments must be verified against the actual wiring.

| Component | Signal | Raspberry Pi GPIO |
|---|---|---|
| Left IR sensor | Digital output | TBD |
| Centre IR sensor | Digital output | TBD |
| Right IR sensor | Digital output | TBD |
| L298N | Motor control inputs | TBD |
| TF02 Pro LiDAR | UART TX/RX | Verify actual interface |
| Audio output | USB / audio device | Verify actual device |

**Important:** Use BCM GPIO numbering when documenting Raspberry Pi GPIO pins. Confirm voltage compatibility before connecting sensors or UART signals.

## 4. Power and Safety

- Use an appropriate power supply for the Raspberry Pi and motors.
- Do not power the motors directly from Raspberry Pi GPIO pins.
- Verify common ground and driver wiring.
- Check the TF02 Pro LiDAR supply voltage and interface pinout against its manufacturer documentation before powering it.

## 5. Verification Status

This document is a preliminary hardware reference. Replace TBD entries with the verified connections from the working robot before treating this pinout as final.

