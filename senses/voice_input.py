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
        
        # ---- Stop Nova cutting you off ----
        self.recognizer.pause_threshold = 2.0
        self.recognizer.phrase_threshold = 0.3
        self.recognizer.non_speaking_duration = 1.5
        
        # ---- Separate recognizer for interruptions ----
        self.interrupt_recognizer = sr.Recognizer()
        self.interrupt_recognizer.pause_threshold = 0.5
        self.interrupt_recognizer.non_speaking_duration = 0.3
        
        # ---- Settings ----
        self.listen_timeout = 8
        self.phrase_timeout = 20
        self.is_listening = False
        self.is_processing = False
        self.interrupted = False
        self.on_speech_detected = None
        
        print("🎙️ Calibrating microphone for background noise...")
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        print("✅ Microphone ready!")

    # ============================================
    # LISTEN ONCE
    # ============================================
    def listen_once(self):
        with sr.Microphone() as source:
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
            except Exception as e:
                print(f"❌ Listen error: {e}")
                return None

    # ============================================
    # LISTEN WHILE SPEAKING
    # ============================================
    def listen_while_speaking(self, mouth):
        def _interrupt_loop():
            while mouth.is_speaking:
                try:
                    with sr.Microphone() as source:
                        audio = self.interrupt_recognizer.listen(
                            source,
                            timeout=2,
                            phrase_time_limit=5
                        )
                        text = self.interrupt_recognizer.recognize_google(audio)
                        
                        if text and len(text.split()) >= 1:
                            print(f"🛑 Interrupted! You said: {text}")
                            self.interrupted = True
                            mouth.stop()
                            time.sleep(0.5)
                            if self.on_speech_detected:
                                self.on_speech_detected(text.lower())
                            break
                            
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    continue
                except Exception:
                    time.sleep(0.1)
                    continue
        
        thread = threading.Thread(target=_interrupt_loop, daemon=True)
        thread.start()

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
                # Wait if Nova is processing or speaking
                if self.is_processing:
                    time.sleep(0.5)
                    continue
                
                text = self.listen_once()
                
                if text is None:
                    continue

                # ---- CONVERSATION MODE ----
                if config.CONVERSATION_MODE:
                    if len(text.split()) < 2:
                        continue
                    
                    # ---- Ignore if Nova is speaking ----
                    if self.is_processing:
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
                print(f"❌ Loop error: {e}")
                time.sleep(0.5)
                continue

    # ============================================
    # HANDLE COMMAND
    # ============================================
    def _handle_command(self, command):
        self.is_processing = True
        self.interrupted = False
        
        if self.on_speech_detected:
            self.on_speech_detected(command)
        
        time.sleep(1)
        self.is_processing = False
        print("🎙️ Ready for next command!")

    # ============================================
    # STOP LISTENING
    # ============================================
    def stop_listening(self):
        self.is_listening = False
        print("🛑 Nova stopped listening!")


if __name__ == "__main__":
    print("🔱 Testing Nova's Ears...")
    ears = NovaEars()
    print("\nSay something!")
    result = ears.listen_once()
    if result:
        print(f"✅ Nova heard: '{result}'")
    else:
        print("❌ Nothing heard")