# ============================================
# NOVA - Voice Input (voice_input.py)
# ============================================
# This is Nova's ears — it listens to you
# and converts your speech to text
# 
# What you'll learn:
# - How microphones work in Python
# - Speech recognition
# - Background listening (always on)
# - Error handling for real world use
# ============================================

import speech_recognition as sr
import threading
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class NovaEars:
    def __init__(self):
        # ---- Setup the recognizer ----
        # This is the engine that converts speech to text
        self.recognizer = sr.Recognizer()
        
        # ---- Microphone ----
        self.microphone = sr.Microphone()
        
        # ---- Settings ----
        # How long Nova waits for you to start speaking
        self.listen_timeout = 5
        
        # How long Nova listens after you start speaking
        self.phrase_timeout = 10
        
        # Is Nova currently listening?
        self.is_listening = False
        
        # Callback function — what to do when Nova hears something
        # This gets set by nova_ui.py later
        self.on_speech_detected = None
        
        # ---- Calibrate microphone ----
        # This adjusts for background noise in your room
        print("🎙️ Calibrating microphone for background noise...")
        with self.microphone as source:
            # Listens for 1 second to measure background noise
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        print("✅ Microphone ready!")

    # ============================================
    # LISTEN ONCE
    # Listen for one thing you say and return it
    # Good for: push to talk, single commands
    # ============================================
    def listen_once(self):
        with self.microphone as source:
            print("🎙️ Listening...")
            try:
                # Wait for you to speak
                audio = self.recognizer.listen(
                    source,
                    timeout=self.listen_timeout,
                    phrase_time_limit=self.phrase_timeout
                )
                
                print("🧠 Processing speech...")
                
                # Convert speech to text using Google (free!)
                text = self.recognizer.recognize_google(audio)
                print(f"✅ You said: {text}")
                return text.lower()
                
            except sr.WaitTimeoutError:
                # You didn't say anything
                return None
                
            except sr.UnknownValueError:
                # Nova heard something but couldn't understand
                print("❓ Could not understand audio")
                return None
                
            except sr.RequestError as e:
                # Internet connection issue
                print(f"❌ Speech service error: {e}")
                return None

    # ============================================
    # LISTEN FOR WAKE WORD
    # Nova waits until you say "Hey Nova"
    # Then starts listening for your command
    # ============================================
    def listen_for_wake_word(self, wake_word=None):
        if wake_word is None:
            wake_word = f"hey {config.NOVA_NAME.lower()}"
            
        print(f"💤 Waiting for wake word: '{wake_word}'")
        
        while self.is_listening:
            text = self.listen_once()
            
            if text and wake_word in text:
                print(f"🔱 Wake word detected!")
                return True
                
        return False

    # ============================================
    # CONTINUOUS LISTENING
    # Nova listens in background all the time
    # When wake word detected, captures command
    # ============================================
    def start_continuous_listening(self, callback=None):
        self.is_listening = True
        self.on_speech_detected = callback
        
        # Run in background thread so UI stays responsive
        self.listen_thread = threading.Thread(
            target=self._continuous_listen_loop,
            daemon=True
        )
        self.listen_thread.start()
        print(f"✅ Nova is now always listening for 'Hey {config.NOVA_NAME}'!")

    def _continuous_listen_loop(self):
        wake_word = f"hey {config.NOVA_NAME.lower()}"
        
        while self.is_listening:
            try:
                # Wait for wake word
                text = self.listen_once()
                
                if text is None:
                    continue
                
                # Check for wake word
                if wake_word in text:
                    print("🔱 Wake word detected! Listening for command...")
                    
                    # Now listen for the actual command
                    command = self.listen_once()
                    
                    if command and self.on_speech_detected:
                        # Send command to UI/brain
                        self.on_speech_detected(command)
                        
            except Exception as e:
                print(f"❌ Listening error: {e}")
                continue

    # ============================================
    # STOP LISTENING
    # ============================================
    def stop_listening(self):
        self.is_listening = False
        print("🛑 Nova stopped listening!")


# ============================================
# TEST NOVA'S EARS
# Run: python senses/voice_input.py
# ============================================
if __name__ == "__main__":
    print("🔱 Testing Nova's Ears...")
    ears = NovaEars()
    
    print("\n--- Test 1: Single Listen ---")
    print("Say something in 5 seconds!")
    result = ears.listen_once()
    
    if result:
        print(f"✅ Nova heard: '{result}'")
    else:
        print("❌ Nothing heard")
        
    print("\n--- Test 2: Wake Word ---")
    print(f"Say 'Hey {config.NOVA_NAME}' to wake Nova up!")
    ears.is_listening = True
    detected = ears.listen_for_wake_word()
    
    if detected:
        print("🔱 Nova is awake and ready!")