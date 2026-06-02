import cv2
import sys

try:
    import mediapipe as mp
    # Manually forcing the import of solutions
    from mediapipe.python.solutions import hands as mp_hands
    from mediapipe.python.solutions import drawing_utils as mp_drawing
    print("✅ MediaPipe loaded successfully!")
except ImportError as e:
    print(f"❌ Error: {e}")
    sys.exit()

# Initialize Hand Tracking
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    gesture = "IDLE"

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Simple Logic: Check index finger tip vs knuckle
            lm = hand_landmarks.landmark
            if lm[8].y < lm[6].y:  # Index finger is up
                gesture = "READY TO SHOOT"
            else:
                gesture = "WAITING"

    cv2.putText(frame, gesture, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow('Hand Tracker Test', frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()