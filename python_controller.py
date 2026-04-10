import cv2
import numpy as np
from pyzbar.pyzbar import decode
import mediapipe as mp
import requests
import time
import urllib.parse

# ESP device IP address (robot controller)
ESP_IP = "http://192.168.4.1"

# -------------------------------
# Communication Helpers
# -------------------------------
def safe_request(path):
    """
    Send a GET request to the ESP device with a short timeout.
    Prints the ESP response or an error if communication fails.
    """
    try:
        r = requests.get(ESP_IP + path, timeout=0.5)
        print("ESP:", r.text)
    except Exception as e:
        print("ESP Error:", e)

# Motor control commands
def move_forward(): safe_request("/forward")
def move_backward(): safe_request("/backward")
def turn_left(): safe_request("/left")
def turn_right(): safe_request("/right")
def stop_motors(): safe_request("/stop")

def send_qr(qr_text):
    """
    Encode QR text safely for URL transmission and send to ESP.
    """
    encoded = urllib.parse.quote(qr_text)
    safe_request(f"/qr?data={encoded}")

# -------------------------------
# Camera & Pose Setup
# -------------------------------

# Open webcam (0 = default camera)
cap = cv2.VideoCapture(0)

# Initialize Mediapipe Pose model
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

print("Running combined QR + Pose + WiFi control... Press 'q' to quit.")

# -------------------------------
# Control Variables
# -------------------------------
last_sent = 0          # Timestamp of last command sent
send_interval = 0.2    # Minimum delay between commands (seconds)
qr_active = False      # Flag indicating if a QR code is detected

# -------------------------------
# Main Loop
# -------------------------------
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    h, w, _ = frame.shape
    # -------------------------------
    # QR Code Detection
    # -------------------------------
    qr_codes = decode(frame)
    qr_data = None
    if qr_codes:
        qr = qr_codes[0]
        qr_data = qr.data.decode('utf-8')
        qr_active = True
        print("QR Code Detected:", qr_data)

        # Draw bounding polygon around QR code
        pts = qr.polygon
        if len(pts) > 4:
            hull = cv2.convexHull(np.array([pt for pt in pts], dtype=np.float32))
            hull = list(map(tuple, np.squeeze(hull)))
        else:
            hull = pts
        for j in range(len(hull)):
            cv2.line(frame, hull[j], hull[(j + 1) % len(hull)], (0, 255, 0), 3)

        # Display decoded QR text above QR code
        x, y, w_qr, h_qr = qr.rect
        cv2.putText(frame, qr_data, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
    else:
        qr_active = False

    # -------------------------------
    # Pose Detection
    # -------------------------------
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_frame)

    # Define central “control zone” rectangle
    center_left = int(w * 1/3)
    center_right = int(w * 2/3)
    center_top = int(h * 0.2)
    center_bottom = int(h * 0.8)
    cv2.rectangle(frame, (center_left, center_top),
                  (center_right, center_bottom), (255, 255, 0), 2)

    # Default direction = Stop
    direction = "S"

    if results.pose_landmarks:
        # Extract shoulder landmarks
        landmarks = results.pose_landmarks.landmark
        left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]

        # Midpoint between shoulders
        mid_x = int(((left_shoulder.x + right_shoulder.x) / 2) * w)
        mid_y = int(((left_shoulder.y + right_shoulder.y) / 2) * h)

        # Draw circle at midpoint
        cv2.circle(frame, (mid_x, mid_y), 10, (0, 255, 0), -1)

        # Decide direction based on shoulder position
        if center_left < mid_x < center_right:
            direction = "F"   # Forward
        elif mid_x <= center_left:
            direction = "L"   # Left
        elif mid_x >= center_right:
            direction = "R"   # Right
    else:
        direction = "S"       # Stop if no pose detected

    # -------------------------------
    # Command Sending
    # -------------------------------
    now = time.time()
    if now - last_sent >= send_interval:
        if qr_active and qr_data:
            # Priority: send QR data if detected
            send_qr(qr_data)
            print(f"Sent QR to ESP: {qr_data}")
        else:
            # Otherwise send movement command
            if direction == "F":
                move_forward()
            elif direction == "L":
                turn_left()
            elif direction == "R":
                turn_right()
            else:
                stop_motors()
            print("Direction:", direction)
        last_sent = now

    # -------------------------------
    # Display Info
    # -------------------------------
    if qr_active:
        cv2.putText(frame, f"QR: {qr_data}", (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.putText(frame, f"Direction: {direction}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    # Show live video feed with overlays
    cv2.imshow("QR + Pose + ESP", frame)

    # Exit condition: press 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# -------------------------------
# Cleanup
# -------------------------------
cap.release()
cv2.destroyAllWindows()
stop_motors()
