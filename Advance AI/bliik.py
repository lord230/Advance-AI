import cv2
import mediapipe as mp
import pyautogui
import time

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.7, min_tracking_confidence=0.7)



# Eye landmarks (based on the Mediapipe face mesh model)
LEFT_EYE_LANDMARKS = [33, 160, 158, 133, 153, 144]
RIGHT_EYE_LANDMARKS = [362, 385, 387, 263, 373, 380]


# Helper function to calculate eye aspect ratio (EAR)
def calculate_ear(eye_landmarks, landmarks):
    # Get coordinates of eye landmarks
    a = ((landmarks[eye_landmarks[1]].x - landmarks[eye_landmarks[5]].x) ** 2 +
         (landmarks[eye_landmarks[1]].y - landmarks[eye_landmarks[5]].y) ** 2) ** 0.5
    b = ((landmarks[eye_landmarks[2]].x - landmarks[eye_landmarks[4]].x) ** 2 +
         (landmarks[eye_landmarks[2]].y - landmarks[eye_landmarks[4]].y) ** 2) ** 0.5
    c = ((landmarks[eye_landmarks[0]].x - landmarks[eye_landmarks[3]].x) ** 2 +
         (landmarks[eye_landmarks[0]].y - landmarks[eye_landmarks[3]].y) ** 2) ** 0.5
    # Calculate EAR
    return (a + b) / (2.0 * c)


def map_coordinates(x, y, frame_width, frame_height, screen_width, screen_height):
    return int(x / frame_width * screen_width), int(y / frame_height * screen_height)

# Initialize MediaPipe Face Detection
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils
face_detection = mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.7)
screen_width, screen_height = pyautogui.size()


# Initialize webcam
cap = cv2.VideoCapture(0)

blink_detected = False
blink_start_time = None

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_height , frame_width,_ = frame.shape
    face_rest = face_detection.process(rgb_frame)
    result = face_mesh.process(rgb_frame)


    if face_rest.detections:
        for detection in face_rest.detections:
            # Draw bounding box
            mp_drawing.draw_detection(frame, detection)
            nose = detection.location_data.relative_keypoints[2]
            nose_x = int(nose.x*frame_height)
            nose_y = int(nose.y*frame_width)
            cv2.circle(frame, (nose_x, nose_y),5, (0, 255, 0), -1)
    
    screen_x, screen_y = map_coordinates(nose_x,nose_y,frame_height,frame_height,screen_width,screen_height)
    pyautogui.moveTo(screen_x, screen_y)


    if result.multi_face_landmarks:
        for face_landmarks in result.multi_face_landmarks:
            # Calculate EAR for both eyes
            left_ear = calculate_ear(LEFT_EYE_LANDMARKS, face_landmarks.landmark)
            right_ear = calculate_ear(RIGHT_EYE_LANDMARKS, face_landmarks.landmark)

            # Average EAR
            ear = (left_ear + right_ear) / 2.0

            # Blink detection: EAR below threshold (adjust 0.25 based on your webcam/environment)
            if ear < 0.25:
                if not blink_detected:
                    blink_detected = True
                    blink_start_time = time.time()
            else:
                if blink_detected:
                    # Check blink duration
                    blink_duration = time.time() - blink_start_time
                    if blink_duration < 0.4:  # Adjust blink duration as needed
                        print("Blink detected! Triggering mouse click.")
                        pyautogui.click()
                    blink_detected = False

    # Display the frame
    cv2.imshow("Blink to Click", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()