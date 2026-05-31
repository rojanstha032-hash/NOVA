# ============================================
# NOVA - Hand Gesture Control (gesture.py)
# ============================================
# Pure OpenCV - no MediaPipe conflicts!
# Uses skin color detection + finger counting
# ============================================

import cv2
import numpy as np
import threading
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class NovaGestures:
    def __init__(self):
        self.is_running = False
        self.last_gesture = None
        self.last_gesture_time = 0
        self.gesture_cooldown = 2.0
        self.on_gesture_detected = None
        self.show_camera = False
        
        # ---- Gesture actions ----
        self.gesture_actions = {
            "zero":  "mute",
            "one":   "open youtube",
            "two":   "take a screenshot",
            "three": "volume up",
            "four":  "volume down",
            "five":  "open camera",
        }
        
        print("✅ Gesture control ready!")

    # ============================================
    # COUNT FINGERS
    # Uses convex hull to count fingers
    # ============================================
    def _count_fingers(self, frame):
        # Convert to HSV for skin detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Skin color range
        lower = np.array([0, 20, 70], dtype=np.uint8)
        upper = np.array([20, 255, 255], dtype=np.uint8)
        mask = cv2.inRange(hsv, lower, upper)
        
        # Clean up mask
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.dilate(mask, kernel, iterations=4)
        mask = cv2.GaussianBlur(mask, (5, 5), 100)
        
        # Find contours
        contours, _ = cv2.findContours(
            mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
        )
        
        if not contours:
            return 0, frame
        
        # Get largest contour (hand)
        contour = max(contours, key=cv2.contourArea)
        
        if cv2.contourArea(contour) < 3000:
            return 0, frame
        
        # Draw contour
        if self.show_camera:
            cv2.drawContours(frame, [contour], -1, (0, 255, 0), 2)
        
        # Convex hull
        hull = cv2.convexHull(contour, returnPoints=False)
        
        if len(hull) < 3:
            return 0, frame
        
        # Find defects (gaps between fingers)
        defects = cv2.convexityDefects(contour, hull)
        
        if defects is None:
            return 0, frame
        
        finger_count = 0
        
        for i in range(defects.shape[0]):
            s, e, f, d = defects[i, 0]
            start = tuple(contour[s][0])
            end = tuple(contour[e][0])
            far = tuple(contour[f][0])
            
            # Calculate angle
            a = np.sqrt((end[0]-start[0])**2 + (end[1]-start[1])**2)
            b = np.sqrt((far[0]-start[0])**2 + (far[1]-start[1])**2)
            c = np.sqrt((end[0]-far[0])**2 + (end[1]-far[1])**2)
            
            if c == 0:
                continue
                
            angle = np.arccos((b**2 + c**2 - a**2) / (2*b*c))
            
            # Count as finger gap if angle < 90 degrees
            if angle <= np.pi / 2:
                finger_count += 1
                if self.show_camera:
                    cv2.circle(frame, far, 5, (0, 0, 255), -1)
        
        # Add 1 because defects = gaps between fingers
        finger_count = min(finger_count + 1, 5)
        
        return finger_count, frame

    # ============================================
    # FINGERS TO GESTURE NAME
    # ============================================
    def _fingers_to_gesture(self, count):
        mapping = {
            0: "zero",
            1: "one",
            2: "two",
            3: "three",
            4: "four",
            5: "five"
        }
        return mapping.get(count)

    # ============================================
    # START DETECTING
    # ============================================
    def start_detecting(self, callback=None, show_camera=False):
        self.on_gesture_detected = callback
        self.is_running = True
        self.show_camera = show_camera
        
        thread = threading.Thread(
            target=self._detection_loop,
            daemon=True
        )
        thread.start()
        print("✋ Gesture detection started!")

    # ============================================
    # DETECTION LOOP
    # ============================================
    def _detection_loop(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Could not open camera!")
            return
        
        # Collect samples for stability
        finger_samples = []
        sample_size = 5
        
        while self.is_running:
            ret, frame = cap.read()
            if not ret:
                continue
            
            frame = cv2.flip(frame, 1)
            
            # Only detect in bottom right region
            # (where hand usually is)
            h, w = frame.shape[:2]
            roi = frame[h//2:h, w//2:w]
            
            count, roi = self._count_fingers(roi)
            frame[h//2:h, w//2:w] = roi
            
            # Collect samples
            finger_samples.append(count)
            if len(finger_samples) > sample_size:
                finger_samples.pop(0)
            
            # Use most common count
            if len(finger_samples) == sample_size:
                stable_count = max(set(finger_samples), key=finger_samples.count)
                gesture = self._fingers_to_gesture(stable_count)
                
                if self.show_camera:
                    cv2.putText(frame, f"Fingers: {stable_count}",
                               (10, 50), cv2.FONT_HERSHEY_SIMPLEX,
                               1, (0, 255, 0), 2)
                    action = self.gesture_actions.get(gesture, "")
                    cv2.putText(frame, f"Action: {action}",
                               (10, 90), cv2.FONT_HERSHEY_SIMPLEX,
                               0.7, (0, 255, 255), 2)
                    
                    # Draw ROI box
                    cv2.rectangle(frame, (w//2, h//2), (w, h), (255, 0, 0), 2)
                    cv2.putText(frame, "Show hand here",
                               (w//2 + 10, h//2 + 30),
                               cv2.FONT_HERSHEY_SIMPLEX,
                               0.6, (255, 0, 0), 2)
                
                # Trigger gesture
                if gesture:
                    current_time = time.time()
                    if (gesture != self.last_gesture or
                        current_time - self.last_gesture_time > self.gesture_cooldown):
                        
                        self.last_gesture = gesture
                        self.last_gesture_time = current_time
                        
                        print(f"✋ {stable_count} fingers → {gesture}")
                        
                        action = self.gesture_actions.get(gesture)
                        if action and self.on_gesture_detected:
                            self.on_gesture_detected(gesture, action)
            
            if self.show_camera:
                cv2.imshow("Nova Gesture Control", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            time.sleep(0.05)
        
        cap.release()
        if self.show_camera:
            cv2.destroyAllWindows()

    def add_gesture_action(self, gesture, action):
        self.gesture_actions[gesture] = action
        print(f"✅ Gesture added: {gesture} → {action}")

    def stop_detecting(self):
        self.is_running = False
        print("🛑 Gesture detection stopped!")


# ============================================
# TEST
# ============================================
if __name__ == "__main__":
    print("🔱 Testing Nova Gesture Control...")
    print("Show your hand in the BLUE BOX!")
    print()
    print("Gestures:")
    print("  ✊ 0 fingers → Mute")
    print("  ☝️ 1 finger  → Open YouTube")
    print("  ✌️ 2 fingers → Screenshot")
    print("  🖖 3 fingers → Volume up")
    print("  🖐 4 fingers → Volume down")
    print("  ✋ 5 fingers → Open camera")
    print()
    print("Press Q to quit\n")
    
    gestures = NovaGestures()
    
    def on_gesture(gesture, action):
        print(f"✋ {gesture} → executing: {action}")
    
    gestures.start_detecting(
        callback=on_gesture,
        show_camera=True
    )
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        gestures.stop_detecting()
        print("👋 Done!")