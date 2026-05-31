# ============================================
# NOVA - Face Setup (face_setup.py)
# ============================================

import cv2
import os
import sys
import pickle
import numpy as np
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def register_face():
    print("🔱 Nova Face Registration")
    print("=" * 50)
    print(f"📸 Registering face for: {config.OWNER_NAME}")
    print("=" * 50)
    
    faces_dir = "data/faces"
    os.makedirs(faces_dir, exist_ok=True)
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Could not open camera!")
        return
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    print("\n📸 Camera is open!")
    print("Press SPACE to take photo | Q to quit\n")
    
    photos_taken = 0
    saved_photos = []
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        display = frame.copy()
        cv2.putText(display, f"Photos: {photos_taken}/10",
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(display, "SPACE=Photo | Q=Done",
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        cv2.imshow("Nova Face Registration", display)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord(' '):
            photo_path = f"{faces_dir}/owner_{photos_taken + 1}.jpg"
            cv2.imwrite(photo_path, frame)
            saved_photos.append(photo_path)
            photos_taken += 1
            print(f"✅ Photo {photos_taken} saved!")
            
            white = np.ones_like(frame) * 255
            cv2.imshow("Nova Face Registration", white)
            cv2.waitKey(200)
        
        if key == ord('q') or photos_taken >= 20:
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    if saved_photos:
        print(f"\n✅ {photos_taken} photos taken!")
        print("🧠 Processing faces with DeepFace...")
        
        try:
            from deepface import DeepFace
            
            valid_photos = []
            for photo_path in saved_photos:
                try:
                    # Test if face detected in photo
                    result = DeepFace.extract_faces(
                        img_path=photo_path,
                        detector_backend='opencv'
                    )
                    if result:
                        valid_photos.append(photo_path)
                        print(f"✅ Face found in photo {saved_photos.index(photo_path) + 1}")
                except Exception as e:
                    print(f"⚠️ No face in photo {saved_photos.index(photo_path) + 1}")
            
            if valid_photos:
                # Save list of valid face photos
                face_data = {
                    "name": config.OWNER_NAME,
                    "photos": valid_photos,
                    "model": "DeepFace"
                }
                
                with open("data/owner_face.pkl", "wb") as f:
                    pickle.dump(face_data, f)
                
                print(f"\n✅ {len(valid_photos)} face photos registered!")
                print(f"🔐 Nova will now recognize you!")
            else:
                print("❌ No faces detected! Make sure your face is visible and well lit!")
                
        except ImportError:
            print("❌ DeepFace not installed!")
            print("Run: py -3.11 -m pip install deepface")
    else:
        print("❌ No photos taken!")


if __name__ == "__main__":
    register_face()