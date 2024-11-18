import cv2
import numpy as np
import pyautogui

# Function to map coordinates
def map_coordinates(x, y, frame_width, frame_height, screen_width, screen_height):
    return int(x / frame_width * screen_width), int(y / frame_height * screen_height)

# Initialize webcam
cap = cv2.VideoCapture(0)
screen_width, screen_height = pyautogui.size()

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.flip(frame, 1)
    frame_height, frame_width, _ = frame.shape
    
    # Convert to HSV for color segmentation
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_bound = np.array([0, 20, 70])  # Adjust for your hand's skin tone
    upper_bound = np.array([20, 255, 255])
    mask = cv2.inRange(hsv_frame, lower_bound, upper_bound)
    
    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        # Find the largest contour (assume it's the hand)
        max_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(max_contour)
        
        # Draw a rectangle around the hand
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        
        # Get center of the hand and map to screen coordinates
        hand_center_x = x + w // 2
        hand_center_y = y + h // 2
        screen_x, screen_y = map_coordinates(hand_center_x, hand_center_y, frame_width, frame_height, screen_width, screen_height)
        
        # Move mouse
        pyautogui.moveTo(screen_x, screen_y)
    
    # Display frame
    cv2.imshow("Gesture Control Mouse", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
