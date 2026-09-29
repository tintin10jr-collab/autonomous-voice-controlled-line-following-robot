# Autonomous Voice-Controlled Line-Following Robot

A final-year ECE project focused on building a compact indoor robot that can receive a destination through voice commands, follow a predefined path, and detect obstacles during navigation.

The robot uses a **Raspberry Pi 4B**, **IR line sensors**, and a **TF02 Pro LiDAR**. It follows a taped path and uses LiDAR-based obstacle detection to stop, provide a voice alert, perform basic avoidance, and continue towards the destination.

## Key Features

* Voice-based destination selection
* IR sensor-based line following
* TF02 Pro LiDAR-based obstacle detection
* DC motor and motor-driver control
* Voice alerts during navigation
* Predefined indoor route navigation

## Hardware

* Raspberry Pi 4B
* TF02 Pro LiDAR
* 3 × IR line sensors
* L298N motor drivers
* 4 × DC geared motors
* Robot chassis

## Software

* Python
* Raspberry Pi OS
* Speech-to-Text
* Text-to-Speech

## System Flow

```text
Voice Command
      ↓
Select Destination
      ↓
Follow Line using IR Sensors
      ↓
Monitor Obstacles using LiDAR
      ↓
Obstacle Detected
      ↓
Stop → Voice Alert → Basic Avoidance
      ↓
Continue Following Path
      ↓
Reach Destination → Voice Alert
```

## My Contributions

* Developed Raspberry Pi-based robot control
* Integrated IR sensors for line following
* Integrated TF02 Pro LiDAR for obstacle detection
* Worked on motor and motor-driver control
* Implemented voice-based destination selection
* Integrated voice alerts with robot navigation
* Tested and integrated the different hardware and software modules

## Current Version

The current prototype operates on a **predefined indoor path**. The main focus is reliable integration of voice control, line following, obstacle detection, motor control, and basic navigation.

## Future Improvements

* Improve obstacle avoidance
* Support more flexible routes
* Improve voice recognition in noisy environments
* Add additional sensors for navigation
* Explore advanced autonomous navigation techniques

## Project Status

**Final Year Major Project | 2025–2026**

**Team:** D. Kavya · Donthi Sai Preethi · S. Nitin · D. Jonathan
