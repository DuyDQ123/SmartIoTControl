import pickle
import cv2
import mediapipe as mp
import numpy as np
import paho.mqtt.client as mqtt
import time

# MQTT Setup
mqtt_broker = "192.168.137.71"  # Raspberry Pi IP
mqtt_port = 1883
mqtt_topic = "gesture/control"

# Connect to MQTT broker
client = mqtt.Client()
print("Connecting to MQTT broker...")
try:
    client.connect(mqtt_broker, mqtt_port, 60)
    client.loop_start()
    print("Successfully connected!")
except Exception as e:
    print(f"MQTT connection error: {e}")
    exit(1)

# Load gesture recognition model
try:
    model_dict = pickle.load(open('./model.p', 'rb'))
    model = model_dict['model']
    print("Gesture recognition model loaded")
except Exception as e:
    print(f"Error loading model: {e}")
    exit(1)

# Camera setup
cap = None
for i in range(20, 36):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"Camera opened at index {i}")
        break
else:
    print("No camera found in range 20-35. Exiting.")
    exit(1)


# MediaPipe setup
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)
c
# Gesture to command mapping - simplified
labels_dict = {0: '0', 1: '1', 2: '2', 3: '3', 4: '4', 5: '5'}
command_names = {
    '0': 'TURN ON LIGHT',
    '1': 'TURN OFF LIGHT',
    '2': 'TURN ON FAN',
    '3': 'TURN OFF FAN',
    '4': 'TURN ON BUZZER',
    '5': 'TURN OFF BUZZER'
}

# Finger counting
FINGER_TIPS = [4, 8, 12, 16, 20]

# Variables
last_command_time = 0
command_cooldown = 2  # Seconds between commands
gesture_start_time = 0
gesture_confirm_time = 1.5  # Seconds to hold gesture
current_gesture = None

print("Ready for gesture detection!")

def count_fingers(hand_landmarks):
    fingers = []
    # Thumb
    if hand_landmarks.landmark[FINGER_TIPS[0]].x < hand_landmarks.landmark[FINGER_TIPS[0] - 1].x:
        fingers.append(1)
    else:
        fingers.append(0)
    # Other fingers
    for id in range(1, 5):
        if hand_landmarks.landmark[FINGER_TIPS[id]].y < hand_landmarks.landmark[FINGER_TIPS[id] - 2].y:
            fingers.append(1)
        else:
            fingers.append(0)
    return fingers.count(1)

def draw_progress_bar(frame, start_time, required_time):
    current_time = time.time()
    progress = min((current_time - start_time) / required_time, 1.0)
    
    bar_width = 200
    bar_height = 30
    filled_width = int(bar_width * progress)
    
    x = (frame.shape[1] - bar_width) // 2
    y = frame.shape[0] - 50
    
    cv2.rectangle(frame, (x, y), (x + bar_width, y + bar_height), (0, 0, 0), -1)
    cv2.rectangle(frame, (x, y), (x + filled_width, y + bar_height), (0, 255, 0), -1)
    cv2.rectangle(frame, (x, y), (x + bar_width, y + bar_height), (255, 255, 255), 2)
    
    cv2.putText(frame, f"Confirming: {int(progress * 100)}%", (x, y - 10), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    return progress >= 1.0

try:
    while True:
        # Read frame
        ret, frame = cap.read()
        if not ret:
            print("Cannot read frame")
            break
            
        # Process image
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)
        
        # Show connection status
        cv2.putText(frame, "MQTT Connected", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        if results.multi_hand_landmarks:
            data_aux = []
            x_ = []
            y_ = []
            
            # Draw hand landmarks
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                # Count fingers (use first hand only)
                finger_count = count_fingers(hand_landmarks)
                cv2.putText(frame, f"Fingers: {finger_count}", (10, 60), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                # Collect keypoints for gesture recognition
                for i in range(len(hand_landmarks.landmark)):
                    x = hand_landmarks.landmark[i].x
                    y = hand_landmarks.landmark[i].y
                    x_.append(x)
                    y_.append(y)
                
                for i in range(len(hand_landmarks.landmark)):
                    x = hand_landmarks.landmark[i].x
                    y = hand_landmarks.landmark[i].y
                    data_aux.append(x - min(x_))
                    data_aux.append(y - min(y_))
                
                break  # Process only first hand
            
            # Draw bounding box
            if x_ and y_:
                H, W, _ = frame.shape
                x1 = int(min(x_) * W) - 10
                y1 = int(min(y_) * H) - 10
                x2 = int(max(x_) * W) + 10
                y2 = int(max(y_) * H) + 10
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # Use finger count as shortcut for buzzer control
                if finger_count == 4:
                    detected_gesture = '4'  # Turn ON buzzer
                    cv2.putText(frame, "BUZZER ON", (50, 120), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                elif finger_count == 5:
                    detected_gesture = '5'  # Turn OFF buzzer
                    cv2.putText(frame, "BUZZER OFF", (50, 120), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 200, 200), 2)
                else:
                    # Use trained model for other gestures
                    prediction = model.predict([np.asarray(data_aux)])
                    detected_gesture = labels_dict[int(prediction[0])]
                
                # Show detected gesture
                command_name = command_names.get(detected_gesture, "Unknown")
                cv2.putText(frame, f"Gesture: {detected_gesture} ({command_name})", 
                            (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                
                # Gesture confirmation system
                current_time = time.time()
                
                if current_gesture != detected_gesture:
                    current_gesture = detected_gesture
                    gesture_start_time = current_time
                
                # If holding the same gesture
                if current_time - last_command_time > command_cooldown:
                    is_confirmed = draw_progress_bar(frame, gesture_start_time, gesture_confirm_time)
                    
                    if is_confirmed:
                        print(f"Sending command: {detected_gesture} - {command_name}")
                        client.publish(mqtt_topic, detected_gesture)
                        
                        # Show confirmation
                        cv2.putText(frame, f"Sent: {command_name}", (50, 90), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                        last_command_time = current_time
                        current_gesture = None  # Reset confirmation
        else:
            current_gesture = None
        
        # Display frame
        cv2.imshow('Gesture Control', frame)
        
        # Add small delay to reduce CPU usage
        time.sleep(0.03)
        
        # Check for exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Program stopped by user")
except Exception as e:
    print(f"Error: {e}")
finally:
    cap.release()
    cv2.destroyAllWindows()
    client.loop_stop()
    client.disconnect()
    print("Disconnected from MQTT broker")