import cv2
import mediapipe as mp
import math
import time
import pyautogui

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

prev_time = 0
fps = 0


LEFT_EYE_LANDMARKS = [33, 160, 158, 133, 153, 144]
RIGHT_EYE_LANDMARKS = [362, 385, 387, 263, 373, 380]



cap = cv2.VideoCapture(2)
with mp_hands.Hands(
    model_complexity=0,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:
  while cap.isOpened():
    success, image = cap.read()
    if not success:
      print("Ignoring empty camera frame.")
      continue


    current_time = time.time()
    fps = 1 / (current_time - prev_time)
    prev_time = current_time

   
    cv2.putText(image, f"FPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_w, image_h,_ = image.shape
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
        
        idx_x = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x*image_w
        idx_y = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y*image_h

        tmb_x = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x*image_w
        tmb_y = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].y*image_h

        # print(idx_x,idx_y,tmb_x,tmb_y)




        distance = math.sqrt((idx_x - tmb_x) ** 2 + (idx_y - tmb_y) ** 2)
        # print(distance)
        threshold_min = 20
        threshold_max = 35

        if threshold_min <= distance <= threshold_max:
            # print(idx_x, idx_y, tmb_x, tmb_y)
            pyautogui.click()
    
      pyautogui.moveTo(idx_x, idx_y)
    cv2.imshow('MediaPipe Hands', image)
    if cv2.waitKey(5) & 0xFF == ord('q'):
      break
cap.release()