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
Iamspeed = 1.5

cap = cv2.VideoCapture(1)

current_mouse_x, current_mouse_y = pyautogui.position()

# def smooth_move(x, y, speed=0.1):
#     global current_mouse_x, current_mouse_y
    
#     distance_x = x - current_mouse_x
#     distance_y = y - current_mouse_y

    
#     steps = int(max(abs(distance_x), abs(distance_y)) / speed)

    
#     for i in range(steps):
#         intermediate_x = current_mouse_x + (distance_x / steps) * i
#         intermediate_y = current_mouse_y + (distance_y / steps) * i
#         pyautogui.moveTo(intermediate_x, intermediate_y)
    
   
#     pyautogui.moveTo(x, y)
    
#     current_mouse_x, current_mouse_y = x, y

def register_click(l_x, l_y, idx_x, idx_y, r_x, r_y, w_x, w_y):
    # Calculate distances from each finger landmark to the wrist
    distance_thumb = math.sqrt((l_x - w_x) ** 2 + (l_y - w_y) ** 2)  # Thumb
    distance_index = math.sqrt((idx_x - w_x) ** 2 + (idx_y - w_y) ** 2)  # Index Finger
    distance_ring = math.sqrt((r_x - w_x) ** 2 + (r_y - w_y) ** 2)  # Ring Finger


    print("Distances:", distance_thumb, distance_index, distance_ring)

   
    thumb_min, thumb_max = 10, 25  # Example values for the thumb
    index_min, index_max = 10, 30  # Example values for the index finger
    ring_min, ring_max = 15, 28  # Example values for the ring finger

    # Check if each distance is within its respective range
    thumb_closed = thumb_min <= distance_thumb <= thumb_max
    index_closed = index_min <= distance_index <= index_max
    ring_closed = ring_min <= distance_ring <= ring_max

    # If all fingers are closed (distances are within the ranges), register a click
    if thumb_closed and ring_closed:
        print("Click registered!")
        # pyautogui.click()  # Perform the click action


pyautogui.moveTo(screen_width//2, screen_height//2)


with mp_hands.Hands(
    model_complexity=0,
    max_num_hands = 1,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.7) as hands:

  while cap.isOpened():


    success, image = cap.read()

    image = cv2.resize(image, (320 , 240 ))
    if not success:
      print("Ignoring empty camera frame.")
      continue

    # FPS YAHA HAI
    current_time = time.time()
    fps = 1 / (current_time - prev_time)
    prev_time = current_time
    cv2.putText(image, f"FPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    # image yaha hai
    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_w, image_h, _ = image.shape
    # print(image_h,image_w)
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


        tmb_x = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x * image_w
        tmb_y = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].y * image_h

        l_x = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].x * image_w
        l_y = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y * image_h 

        r_x = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].x * image_w
        r_y = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].y * image_h 


        w_x = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x * image_w
        w_y = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].y * image_h 

      
        # distance1 = math.sqrt((l_x - w_x) ** 2 + (l_y - w_y) ** 2)
        # distance2 = math.sqrt((idx_x - w_x) ** 2 + (idx_y - w_y) ** 2)
        # distance3 = math.sqrt((r_x - w_x) ** 2 + (r_y - w_y) ** 2)

        # threshold_min = 0
        # threshold_max = 15
        # print(distance1,distance2,distance3)


        register_click(l_x, l_y, idx_x, idx_y, r_x, r_y, w_x, w_y)

      
        # if threshold_min <= distance <= threshold_max:
        #     # print("Click")
        #     pyautogui.click()

        
        screen_x = int(( idx_x / image_w * screen_height * Iamspeed))
        screen_y = int(idx_y / image_h * screen_height * Iamspeed* 2) 
        
      
        pyautogui.moveTo(screen_x, screen_y)
        print(screen_x,screen_y)
    
  
    cv2.imshow('MediaPipe Hands', image)
    if cv2.waitKey(5) & 0xFF == ord('q'):
      break

cap.release()


