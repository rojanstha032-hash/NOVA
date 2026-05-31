# ============================================
# NOVA - Voice Output (voice_output.py)
# ============================================

import subprocess
import sys
import os
import threading

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class NovaMouth:
    def __init__(self):
        self.is_speaking = False
        self._lock = threading.Lock()
        print("✅ Nova's voice is ready!")

    def speak(self, text):
        if not text:
            return
        with self._lock:
            self.is_speaking = True
            print(f"🔊 Nova: {text}")
            try:
                clean_text = text.replace("'", "").replace('"', "")
                subprocess.run([
                    'powershell', '-Command',
                    f"Add-Type -AssemblyName System.Speech; "
                    f"$speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                    f"$speak.Rate = 1; "
                    f"$speak.Volume = 100; "
                    f"$speak.Speak('{clean_text}');"
                ], capture_output=True)
            except Exception as e:
                print(f"❌ Speech error: {e}")
            self.is_speaking = False

    def speak_async(self, text):
        thread = threading.Thread(
            target=self.speak,
            args=(text,),
            daemon=True
        )
        thread.start()

    def stop(self):
        self.is_speaking = False


if __name__ == "__main__":
    print("🔱 Testing Nova's Voice...")
    mouth = NovaMouth()
    mouth.speak(f"Hello! I am {config.NOVA_NAME}, your personal AI assistant!")
    print("✅ Voice test complete!")