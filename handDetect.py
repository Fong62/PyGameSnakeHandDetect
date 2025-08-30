import cv2
import mediapipe as mp
from directkeys import PressKey, ReleaseKey, up_arrow_pressed, down_arrow_pressed, left_arrow_pressed, right_arrow_pressed
import threading
import time

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)

# Set to keep track of currently pressed keys
current_key_pressed = set()

# Give some time to set up the camera
time.sleep(2.0)

# Start video capture
video = cv2.VideoCapture(0)

# Define movement thresholds
move_threshold = 100  # Ngưỡng di chuyển
upper_threshold = 150  # Tăng ngưỡng nhảy
lower_threshold = 325 # Giữ nguyên ngưỡng cúi

width, height = 640, 480
video.set(3, width)
video.set(4, height)

hand_movement = 'neutral'  # Giá trị mặc định ban đầu

def detect_hand_movement():
    global hand_movement  # Sử dụng biến toàn cục
    while True:
        ret, frame = video.read()
    
        # Resize the frame
        frame = cv2.resize(frame, (width, height))

        # Draw division lines
        cv2.line(frame, (0, upper_threshold), (width, upper_threshold), (0, 255, 0), 2)  # Jump line
        cv2.line(frame, (0, lower_threshold), (width, lower_threshold), (0, 255, 0), 2)  # Crouch line
        cv2.line(frame, (width // 2, 0), (width // 2, height), (255, 0, 0), 2)  # Center line

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp.solutions.drawing_utils.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                wrist_x = int(hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].x * 640)
                wrist_y = int(hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].y * 480)

                if wrist_y < upper_threshold:
                    cv2.putText(frame, 'Moving Up', (420, 460), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)
                    hand_movement = 'up'
                elif wrist_y > lower_threshold:
                    cv2.putText(frame, 'Moving Down', (420, 460), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)
                    hand_movement = 'down'
                elif wrist_x > 320 + move_threshold:
                    cv2.putText(frame, 'Moving Left', (420, 460), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)
                    hand_movement = 'left'
                elif wrist_x < 320 - move_threshold:
                    cv2.putText(frame, 'Moving Right', (420, 460), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)
                    hand_movement = 'right'
                else:
                    cv2.putText(frame, 'Neutral', (420, 460), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)
                    hand_movement = 'neutral'

        # Hiển thị cửa sổ video của OpenCV (nếu muốn)
        cv2.imshow("Hand Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):  # Đóng cửa sổ OpenCV khi nhấn 'q'
            break

# Khởi động thread cho nhận diện cử động tay
hand_detection_thread = threading.Thread(target=detect_hand_movement)
hand_detection_thread.daemon = True  # Đảm bảo thread sẽ kết thúc khi chương trình chính kết thúc
hand_detection_thread.start()

# Trả về cử động tay hiện tại
def get_hand_movement():
    global hand_movement  # Đảm bảo lấy giá trị cập nhật từ thread
    return hand_movement
