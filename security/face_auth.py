# ============================================
# NOVA - Face Authentication (face_auth.py)
# ============================================

import cv2
import os
import sys
import pickle
import threading
import time
import numpy as np
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class FaceAuth:
    def __init__(self):
        self.is_running = False
        self.owner_verified = False
        self.owner_photos = []
        self.stranger_detected = False
        self.on_stranger_detected = None
        self.on_owner_detected = None
        self.stranger_count = 0
        self.owner_count = 0
        self.deepface = None
        
        self._load_owner_faces()
        self._preload_deepface()
        
        print("✅ Face authentication ready!")

    def _preload_deepface(self):
        print("🧠 Loading face recognition model...")
        try:
            from deepface import DeepFace
            self.deepface = DeepFace
            # Warm up the model
            DeepFace.build_model("VGG-Face")
            print("✅ Face model loaded!")
        except Exception as e:
            print(f"❌ Model load error: {e}")

    def _load_owner_faces(self):
        face_data_path = "data/owner_face.pkl"
        if os.path.exists(face_data_path):
            with open(face_data_path, "rb") as f:
                face_data = pickle.load(f)
            self.owner_photos = face_data.get("photos", [])
            print(f"✅ Loaded {len(self.owner_photos)} owner face photos!")
        else:
            print("⚠️ No face data found! Run face_setup.py first!")

    def verify_face(self, frame):
        if not self.deepface:
            return False, 0
            
        try:
            temp_path = "data/temp_face.jpg"
            cv2.imwrite(temp_path, frame)
            
            owner_votes = 0
            stranger_votes = 0
            photos_to_check = min(5, len(self.owner_photos))
            
            for owner_photo in self.owner_photos[:photos_to_check]:
                try:
                    result = self.deepface.verify(
                        img1_path=temp_path,
                        img2_path=owner_photo,
                        model_name="VGG-Face",
                        detector_backend="opencv",
                        enforce_detection=False,
                        distance_metric="cosine"
                    )
                    
                    if result["verified"]:
                        owner_votes += 1
                    else:
                        stranger_votes += 1
                        
                except Exception:
                    continue
            
            return owner_votes > stranger_votes, owner_votes
                
        except Exception as e:
            print(f"❌ Verification error: {e}")
            return False, 0

    def start_watching(self, on_stranger=None, on_owner=None):
        self.on_stranger_detected = on_stranger
        self.on_owner_detected = on_owner
        self.is_running = True
        
        thread = threading.Thread(
            target=self._watch_loop,
            daemon=True
        )
        thread.start()
        print("👁️ Face authentication is watching...")

    def _watch_loop(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Could not open camera!")
            return
        
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        last_check = time.time()
        check_interval = 5
        
        print("🎥 Camera watching started!")
        
        while self.is_running:
            ret, frame = cap.read()
            if not ret:
                continue
            
            if time.time() - last_check > check_interval:
                last_check = time.time()
                
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                
                print(f"👁️ Checking... faces found: {len(faces)}")
                
                if len(faces) > 0:
                    print("🔍 Face found! Verifying identity...")
                    is_owner, votes = self.verify_face(frame)
                    
                    if is_owner:
                        self.owner_count += 1
                        self.stranger_count = 0
                        print(f"✅ Owner vote: {self.owner_count}/2")
                        
                        if self.owner_count >= 2 and not self.owner_verified:
                            print(f"✅ Owner confirmed! ({config.OWNER_NAME})")
                            self.owner_verified = True
                            self.stranger_detected = False
                            self.owner_count = 0
                            if self.on_owner_detected:
                                self.on_owner_detected()
                    else:
                        self.stranger_count += 1
                        self.owner_count = 0
                        print(f"⚠️ Stranger vote: {self.stranger_count}/3")
                        
                        if self.stranger_count >= 3 and not self.stranger_detected:
                            print("🚨 STRANGER CONFIRMED!")
                            self.stranger_detected = True
                            self.owner_verified = False
                            self.stranger_count = 0
                            self._save_stranger_photo(frame)
                            if self.on_stranger_detected:
                                self.on_stranger_detected(frame)
                else:
                    self.owner_count = max(0, self.owner_count - 1)
                    self.stranger_count = max(0, self.stranger_count - 1)
            
            time.sleep(0.1)
        
        cap.release()

    def _save_stranger_photo(self, frame):
        strangers_dir = "data/recordings"
        os.makedirs(strangers_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        photo_path = f"{strangers_dir}/stranger_{timestamp}.jpg"
        cv2.imwrite(photo_path, frame)
        print(f"📸 Stranger photo saved: {photo_path}")
        return photo_path

    def stop_watching(self):
        self.is_running = False
        print("🛑 Face authentication stopped!")


if __name__ == "__main__":
    print("🔱 Testing Face Authentication...")
    
    auth = FaceAuth()
    
    def on_stranger(frame):
        print("🚨 STRANGER ALERT!")
    
    def on_owner():
        print(f"✅ Welcome back {config.OWNER_NAME}!")
    
    auth.start_watching(
        on_stranger=on_stranger,
        on_owner=on_owner
    )
    
    print("\n👁️ Watching for 120 seconds...")
    print("Look at camera!")
    
    for i in range(120):
        time.sleep(1)
        if auth.owner_verified:
            print("🎉 Owner verified! Test successful!")
            break
    
    auth.stop_watching()