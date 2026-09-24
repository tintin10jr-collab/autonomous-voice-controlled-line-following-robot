# Autonomous Voice-Controlled Line-Following Robot

A final-year ECE project built using **Raspberry Pi 4B** to develop a simple indoor navigation robot.

The robot takes a voice command for a destination and follows a predefined path using **IR sensors**. A **TF02 Pro LiDAR** is used to detect obstacles in front of the robot. When an obstacle is detected, the robot stops, gives a voice alert, and performs basic obstacle avoidance before continuing.

### What I worked on

* Raspberry Pi 4B based robot control
* IR sensor based line following
* TF02 Pro LiDAR integration for obstacle detection
* DC motor and motor-driver control
* Voice-based destination selection
* Voice alerts during navigation
* Testing and integration of the complete system

### Hardware

* Raspberry Pi 4B
* TF02 Pro LiDAR
* 3 × IR line sensors
* L298N motor drivers
* 4 × DC geared motors
* Robot chassis

### Software

* Python
* Raspberry Pi OS
* Speech-to-Text
* Text-to-Speech

### How the robot works

```text
Voice Command
      ↓
Select Destination
      ↓
Follow Line using IR Sensors
      ↓
Check Obstacles using LiDAR
      ↓
Obstacle Detected → Stop → Alert → Avoid
      ↓
Continue Following Path
      ↓
Reach Destination → Voice Alert
```

### Current Version

The current prototype works on a **predefined indoor path**. The focus of this version is on getting the basic voice control, line following, obstacle detection, and motor control working together reliably.

### Future Improvements

* Improve obstacle avoidance
* Make navigation more flexible
* Improve voice recognition in noisy environments
* Add more sensors for better navigation
* Explore advanced autonomous navigation techniques

### Project Status

**Final Year Major Project | 2025–2026**

**Team:** D. Kavya · Donthi Sai Preethi · S. Nitin · D. Jonathan
