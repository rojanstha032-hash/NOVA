# ============================================
# NOVA - Voice Output (voice_output.py)
# ============================================

import subprocess
import os
import sys
import threading
import asyncio
import edge_tts
import tempfile

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class NovaMouth:
    def __init__(self):
        self.is_speaking = False
        self._lock = threading.Lock()
        self._current_process = None
        print("✅ Nova's voice is ready!")

    # ============================================
    # SPEAK
    # Uses Aria - natural neural voice!
    # ============================================
    def speak(self, text):
        if not text:
            return

        with self._lock:
            self.is_speaking = True
            print(f"🔊 Nova: {text}")
            try:
                # Generate speech file
                asyncio.run(self._generate_speech(text))
                
                # Play it
                audio_path = os.path.abspath("data/nova_speech.mp3")
                self._current_process = subprocess.Popen([
                    'powershell', '-c',
                    f'Add-Type -AssemblyName presentationCore; '
                    f'$player = New-Object system.windows.media.mediaplayer; '
                    f'$player.open([uri]"{audio_path}"); '
                    f'$player.play(); '
                    f'$duration = 0; '
                    f'while ($player.NaturalDuration.HasTimeSpan -eq $false) {{ Start-Sleep -Milliseconds 100; $duration++; if ($duration -gt 20) {{ break }} }}; '
                    f'if ($player.NaturalDuration.HasTimeSpan) {{ Start-Sleep $player.NaturalDuration.TimeSpan.TotalSeconds }}; '
                    f'$player.Stop();'
                ])
                self._current_process.wait()
                
            except Exception as e:
                print(f"❌ Speech error: {e}")
                # Fallback to Zira if Aria fails
                try:
                    clean_text = text.replace("'", "").replace('"', "")
                    subprocess.run([
                        'powershell', '-Command',
                        f"Add-Type -AssemblyName System.Speech; "
                        f"$speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                        f"$speak.SelectVoice('Microsoft Zira Desktop'); "
                        f"$speak.Rate = 0; "
                        f"$speak.Speak('{clean_text}');"
                    ])
                except:
                    pass
            
            self.is_speaking = False
            self._current_process = None

    # ============================================
    # GENERATE SPEECH
    # Creates mp3 file using Edge TTS
    # ============================================
    async def _generate_speech(self, text):
        os.makedirs("data", exist_ok=True)
        tts = edge_tts.Communicate(text, config.NOVA_VOICE)
        await tts.save("data/nova_speech.mp3")

    # ============================================
    # SPEAK ASYNC
    # ============================================
    def speak_async(self, text):
        thread = threading.Thread(
            target=self.speak,
            args=(text,),
            daemon=True
        )
        thread.start()

    # ============================================
    # STOP
    # ============================================
    def stop(self):
        self.is_speaking = False
        try:
            if self._current_process:
                self._current_process.kill()
                self._current_process = None
            os.system("taskkill /f /im powershell.exe /t >nul 2>&1")
        except:
            pass
        print("🛑 Speech stopped!")


# ============================================
# TEST
# ============================================
if __name__ == "__main__":
    print("🔱 Testing Nova's Voice...")
    mouth = NovaMouth()
    mouth.speak("Hello Rojan! I am Nova, your personal AI assistant. How can I help you today?")
    print("✅ Voice test complete!")