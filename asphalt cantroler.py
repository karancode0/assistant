import cv2
import mediapipe as mp
import pyautogui

# Initialize Mediapipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Get screen size
screen_width, screen_height = pyautogui.size()

# Open Webcam
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Flip and convert the frame to RGB
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process frame with Mediapipe Hands
    results = hands.process(rgb_frame)

    # Draw hand landmarks and control mouse
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get coordinates for finger tips and folded status
            folded_fingers = 0
            for finger_tip_id in [
                mp_hands.HandLandmark.THUMB_TIP,
                mp_hands.HandLandmark.INDEX_FINGER_TIP,
                mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
                mp_hands.HandLandmark.RING_FINGER_TIP,
                mp_hands.HandLandmark.PINKY_TIP,
            ]:
                tip_y = hand_landmarks.landmark[finger_tip_id].y
                base_y = hand_landmarks.landmark[finger_tip_id - 2].y  # Base of the finger

                # Check if the finger is folded
                if tip_y > base_y:
                    folded_fingers += 1

            # Detect Fist Gesture (All fingers folded)
            if folded_fingers == 5:
                pyautogui.hotkey("ctrl", "w")  # Close tab
                pyautogui.sleep(1)  # Add a delay to avoid repeated closures

            # Get index finger tip coordinates for cursor control
            index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            finger_x = int(index_finger_tip.x * screen_width)
            finger_y = int(index_finger_tip.y * screen_height)

            # Move the mouse cursor
            pyautogui.moveTo(finger_x, finger_y)

            # Get thumb tip coordinates
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]

            # Calculate distance between index finger tip and thumb tip
            distance = ((index_finger_tip.x - thumb_tip.x) ** 2 + (index_finger_tip.y - thumb_tip.y) ** 2) ** 0.5

            # Perform mouse click if the distance is small (e.g., pinch gesture)
            if distance < 0.05:
                pyautogui.click()

    # Display the frame
    cv2.imshow("Hand-Gesture Mouse with Fist Gesture", frame)

    # Break the loop with 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
