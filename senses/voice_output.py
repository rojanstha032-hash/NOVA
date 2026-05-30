# ============================================
# NOVA - Voice Output (voice_output.py)
# ============================================
# This is Nova's mouth — it speaks back to you
# Converts text to speech
#
# What you'll learn:
# - Text to speech in Python
# - Voice customization
# - Threading for non-blocking speech
# ============================================

import pyttsx3
import threading
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class NovaMouth:
    def __init__(self):
        # ---- Setup the speech engine ----
        self.engine = pyttsx3.init()
        
        # ---- Voice Settings ----
        self.engine.setProperty('rate', config.NOVA_VOICE_RATE)
        self.engine.setProperty('volume', config.NOVA_VOICE_VOLUME)
        
        # ---- Choose a voice ----
        # Get all available voices on your PC
        voices = self.engine.getProperty('voices')
        
        # Try to find a female voice for Nova
        # (sounds more like a real assistant)
        for voice in voices:
            if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
        
        # ---- Is Nova currently speaking? ----
        self.is_speaking = False
        
        print("✅ Nova's voice is ready!")
        
    # ============================================
    # SPEAK
    # Nova says something out loud
    # ============================================
    def speak(self, text):
        if not text:
            return
            
        self.is_speaking = True
        print(f"🔊 Nova: {text}")
        
        self.engine.say(text)
        self.engine.runAndWait()
        
        self.is_speaking = False

    # ============================================
    # SPEAK IN BACKGROUND
    # Speaks without freezing the UI
    # ============================================
    def speak_async(self, text):
        thread = threading.Thread(
            target=self.speak,
            args=(text,),
            daemon=True
        )
        thread.start()

    # ============================================
    # STOP SPEAKING
    # ============================================
    def stop(self):
        self.engine.stop()
        self.is_speaking = False


# ============================================
# TEST NOVA'S VOICE
# Run: python senses/voice_output.py
# ============================================
if __name__ == "__main__":
    print("🔱 Testing Nova's Voice...")
    mouth = NovaMouth()
    
    print("Nova will now speak!")
    mouth.speak(f"Hello! I am {config.NOVA_NAME}, your personal AI assistant. I am online and ready to help you!")
    
    print("✅ Voice test complete!")