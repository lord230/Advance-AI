import cv2
import mediapipe as mp
import math
import time
import pyautogui



mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

pyautogui.FAILSAFE = False

prev_time = 0
fps = 0

screen_width, screen_height = pyautogui.size()  
Iamspeed = 2.5

cap = cv2.VideoCapture(2)

# initial pos
current_mouse_x, current_mouse_y = pyautogui.position()

def smooth_move(x, y, speed=0.1):
    global current_mouse_x, current_mouse_y
    
    distance_x = x - current_mouse_x
    distance_y = y - current_mouse_y

    
    steps = int(max(abs(distance_x), abs(distance_y)) / speed)

    
    for i in range(steps):
        intermediate_x = current_mouse_x + (distance_x / steps) * i
        intermediate_y = current_mouse_y + (distance_y / steps) * i
        pyautogui.moveTo(intermediate_x, intermediate_y)
    
   
    pyautogui.moveTo(x, y)
    
    current_mouse_x, current_mouse_y = x, y

with mp_hands.Hands(
    model_complexity=0,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:

    while cap.isOpened():
        success, image = cap.read()

        # image = cv2.resize(image, (320, 240))
        if not success:
            print("Ignoring empty camera frame.")
            continue

        # FPS display
        current_time = time.time()
        fps = 1 / (current_time - prev_time)
        prev_time = current_time
        cv2.putText(image, f"FPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_h, image_w, _ = image.shape
        results = hands.process(image)

        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())

                idx_x = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * image_w
                idx_y = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * image_h

                
                screen_x = int(idx_x / image_w * screen_width * Iamspeed)
                screen_y = int(idx_y / image_h * screen_height * Iamspeed)

         
                smooth_move(screen_x, screen_y)

        cv2.imshow('MediaPipe Hands', image)
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break
        

cap.release()
cv2.destroyAllWindows()
