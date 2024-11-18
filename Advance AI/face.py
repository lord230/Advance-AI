import cv2
import numpy as np

# Load Haar cascades for face and eye detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")

# Thresholds and counters for blink detection
EAR_THRESHOLD = 0.2
BLINK_FRAMES = 3
left_blink_count = 0
right_blink_count = 0
left_eye_closed = False
right_eye_closed = False

# Eye aspect ratio function
def calculate_ear(eye):
    # h, w = eye.shape[:2]
    _, threshold = cv2.threshold(eye, 50, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
         area = cv2.contourArea(contour)
         if 100 < area < 1000:  # Filter noise
            x, y, w, h = cv2.boundingRect(contour)
            return h / w if w > 0 else 0
    return 0

# Start video feed
cap = cv2.VideoCapture(1)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        roi_gray = gray[y:y + h, x:x + w]
        roi_color = frame[y:y + h, x:x + w]

        eyes = eye_cascade.detectMultiScale(roi_gray)
        for (ex, ey, ew, eh) in eyes:
            eye_roi = roi_gray[max(0, ey-10):ey+eh+10, max(0, ex-10):ex+ew+10]

            ear = calculate_ear(eye_roi)

            if ex + ew / 2 < w / 2:  # Left eye
                if ear < EAR_THRESHOLD:
                    left_eye_closed = True
                else:
                    if left_eye_closed:
                        left_blink_count += 1
                        print("Left Blink Detected")
                    left_eye_closed = False

            else:  # Right eye
                if ear < EAR_THRESHOLD:
                    right_eye_closed = True
                else:
                    if right_eye_closed:
                        right_blink_count += 1
                        print("Right Blink Detected")
                    right_eye_closed = False

            cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)

    # Display blink count
    cv2.putText(frame, f"Left Blinks: {left_blink_count}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
    cv2.putText(frame, f"Right Blinks: {right_blink_count}", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

    cv2.imshow("Blink Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
