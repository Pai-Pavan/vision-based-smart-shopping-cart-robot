# Vision-Based Smart Shopping Cart Robot

An autonomous smart shopping cart robot capable of real-time human following and QR-based item identification using computer vision and wireless robotic control.

## Overview

This project combines:
- Human tracking using MediaPipe pose estimation
- QR code recognition using Pyzbar
- Wireless robot control via Wi-Fi HTTP communication
- ESP-based motor control with L298N driver

The robot follows a person automatically and stops to scan/display QR-coded items when presented to the camera.

---

## Features

### Human Following
The robot tracks a person using shoulder landmarks detected from live video feed.

Movement logic:
- Person centered → Move Forward
- Person left → Turn Left
- Person right → Turn Right
- No person detected → Stop

### QR Item Detection
When a QR code is shown:
- Robot halts movement
- QR code is decoded instantly
- Item data is transmitted to onboard controller

### Wireless Communication
Laptop sends movement and QR commands to ESP over Wi-Fi using HTTP requests.

---

## System Architecture

Laptop Camera → Python Vision Engine → Wi-Fi HTTP Commands → ESP Controller → L298N Motor Driver → Robot Motion

---

## Hardware Used

- Laptop/Webcam
- ESP8266 / ESP32
- L298N Motor Driver
- BO Motors
- Robot Chassis
- Battery Pack

---

## Software Stack

### Python Side:
- OpenCV
- MediaPipe
- Pyzbar
- Requests
- NumPy

### Embedded Side:
- Arduino IDE
- ESP WiFi Library

---

## Python Dependencies

Install required packages:

```bash
pip install opencv-python mediapipe pyzbar requests numpy
