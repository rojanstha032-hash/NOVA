# ============================================
# NOVA - Voice Input (voice_input.py)
# ============================================

import speech_recognition as sr
import threading
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class NovaEars:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.listen_timeout = 5
        self.phrase_timeout = 10
        self.is_listening = False
        self.is_processing = False
        self.on_speech_detected = None
        
        print("🎙️ Calibrating microphone for background noise...")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        print("✅ Microphone ready!")

    # ============================================
    # LISTEN ONCE
    # ============================================
    def listen_once(self):
        with self.microphone as source:
            print("🎙️ Listening...")
            try:
                audio = self.recognizer.listen(
                    source,
                    timeout=self.listen_timeout,
                    phrase_time_limit=self.phrase_timeout
                )
                print("🧠 Processing speech...")
                text = self.recognizer.recognize_google(audio)
                print(f"✅ You said: {text}")
                return text.lower()
            except sr.WaitTimeoutError:
                return None
            except sr.UnknownValueError:
                print("❓ Could not understand audio")
                return None
            except sr.RequestError as e:
                print(f"❌ Speech service error: {e}")
                return None

    # ============================================
    # START CONTINUOUS LISTENING
    # ============================================
    def start_continuous_listening(self, callback=None):
        self.is_listening = True
        self.on_speech_detected = callback
        self.listen_thread = threading.Thread(
            target=self._continuous_listen_loop,
            daemon=True
        )
        self.listen_thread.start()
        print(f"✅ Nova is now listening!")

    # ============================================
    # CONTINUOUS LISTEN LOOP
    # ============================================
    def _continuous_listen_loop(self):
        wake_word = f"hey {config.NOVA_NAME.lower()}"
        
        while self.is_listening:
            try:
                # Wait if Nova is processing
                if self.is_processing:
                    time.sleep(0.5)
                    continue
                
                text = self.listen_once()
                
                if text is None:
                    continue

                # ---- CONVERSATION MODE ----
                if config.CONVERSATION_MODE:
                    # Ignore very short words (noise)
                    if len(text.split()) < 2:
                        continue
                    print(f"✅ Command: {text}")
                    self._handle_command(text)
                    
                # ---- WAKE WORD MODE ----
                else:
                    if wake_word in text:
                        print("🔱 Wake word detected!")
                        command = text.replace(wake_word, "").strip()
                        
                        if command:
                            self._handle_command(command)
                        else:
                            command = self.listen_once()
                            if command:
                                self._handle_command(command)
                                
            except Exception as e:
                print(f"❌ Listening error: {e}")
                continue

    # ============================================
    # HANDLE COMMAND
    # ============================================
    def _handle_command(self, command):
        self.is_processing = True
        
        if self.on_speech_detected:
            self.on_speech_detected(command)
        
        # Wait for Nova to finish speaking
        time.sleep(1)
        self.is_processing = False
        print("🎙️ Ready for next command!")

    # ============================================
    # STOP LISTENING
    # ============================================
    def stop_listening(self):
        self.is_listening = False
        print("🛑 Nova stopped listening!")


# ============================================
# TEST
# ============================================
if __name__ == "__main__":
    print("🔱 Testing Nova's Ears...")
    ears = NovaEars()
    
    print("\nSay something!")
    result = ears.listen_once()
    if result:
        print(f"✅ Nova heard: '{result}'")
    else:
        print("❌ Nothing heard")