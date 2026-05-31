# ============================================
# NOVA - Main Entry Point (nova.py)
# ============================================

import threading
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from brain.ai_core import NovaBrain
from senses.voice_input import NovaEars
from senses.voice_output import NovaMouth
from actions.desktop import DesktopController
from actions.nova_email import NovaEmail
from security.face_auth import FaceAuth
from remote.server import start_server
from nova_ui import NovaUI
import config

class Nova:
    def __init__(self):
        print("🔱 Initializing Nova...")
        print("=" * 50)
        
        print("🧠 Loading brain...")
        self.brain = NovaBrain()
        
        print("🎙️ Loading ears...")
        self.ears = NovaEars()
        
        print("🔊 Loading voice...")
        self.mouth = NovaMouth()
        
        print("🖥️ Loading desktop controller...")
        self.desktop = DesktopController()
        
        print("📧 Loading email system...")
        self.email_system = NovaEmail()
        
        print("👤 Loading face authentication...")
        self.face_auth = FaceAuth()
        
        print("🖥️ Loading UI...")
        self.ui = NovaUI()
        
        # Connect UI
        self.ui.brain = self.brain
        self.ui._process_input = self._on_text_command
        
        # Security state
        self.is_locked = False
        
        print("=" * 50)
        print(f"✅ Nova is fully online!")
        print(f"💬 Say 'Hey Nova' or type in the window!")
        print(f"📱 Remote: http://{config.TAILSCALE_IP}:{config.REMOTE_PORT}")
        print("=" * 50)

    # ============================================
    # ON VOICE COMMAND
    # ============================================
    def _on_voice_command(self, text):
        if self.is_locked:
            print("🔒 Nova is locked!")
            return
            
        print(f"🎙️ Voice command: {text}")
        
        self.ui.root.after(0,
            self.ui.add_message,
            config.OWNER_NAME,
            f"🎙️ {text}",
            "user"
        )
        
        threading.Thread(
            target=self._process_command,
            args=(text,),
            daemon=True
        ).start()

    # ============================================
    # ON TEXT COMMAND
    # ============================================
    def _on_text_command(self, text):
        if self.is_locked:
            return
        threading.Thread(
            target=self._process_command,
            args=(text,),
            daemon=True
        ).start()

    # ============================================
    # PROCESS COMMAND
    # ============================================
    def _process_command(self, text):
        self.ui.root.after(0,
            self.ui.update_status,
            "🧠 Thinking...",
            "#ffaa00"
        )
        
        text_lower = text.lower()
        
        # Special commands
        if any(word in text_lower for word in ["exit nova", "shutdown nova", "goodbye nova"]):
            self._shutdown()
            return
            
        if "clear memory" in text_lower:
            self.brain.clear_memory()
            self._respond("Memory cleared! Starting fresh.")
            return

        # Email commands
        email_result = self.email_system.process_command(text)
        if email_result:
            self._respond(email_result)
            return

        # Desktop commands
        desktop_result = self.desktop.process_command(text)
        if desktop_result:
            self._respond(desktop_result)
            return

        # AI brain
        response = self.brain.think(text)
        self._respond(response)

    # ============================================
    # RESPOND
    # ============================================
    def _respond(self, response):
        self.ui.root.after(0,
            self.ui.add_message,
            config.NOVA_NAME,
            response,
            "nova"
        )
        
        self.ui.root.after(0,
            self.ui.update_status,
            "🔊 Speaking... (talk to interrupt!)",
            "#00aaff"
        )
        
        # Pause listening while speaking
        self.ears.is_processing = True
        
        self.ears.listen_while_speaking(self.mouth)
        self.mouth.speak(response)
        
        # Resume listening
        self.ears.is_processing = False
        self.ears.interrupted = False
        
        self.ui.root.after(0,
            self.ui.update_status,
            "💤 Idle — Say 'Hey Nova' or type below",
            "#555555"
        )

    # ============================================
    # ON OWNER DETECTED
    # ============================================
    def _on_owner_detected(self):
        print(f"👤 Owner detected!")
        self.is_locked = False
        
        self.ui.root.after(0,
            self.ui.update_status,
            f"👤 {config.OWNER_NAME} verified!",
            "#00ff88"
        )
        
        threading.Thread(
            target=self.mouth.speak,
            args=(f"Welcome back {config.OWNER_NAME}!",),
            daemon=True
        ).start()

    # ============================================
    # ON STRANGER DETECTED
    # ============================================
    def _on_stranger_detected(self, frame):
        print("🚨 STRANGER DETECTED!")
        self.is_locked = True
        
        self.ui.root.after(0,
            self.ui.update_status,
            "🚨 INTRUDER DETECTED! Nova locked!",
            "#ff0000"
        )
        
        threading.Thread(
            target=self.mouth.speak,
            args=("Warning! Unauthorized access detected! This incident has been recorded!",),
            daemon=True
        ).start()
        
        self.ui.root.after(0,
            self.ui.add_message,
            "⚠️ SECURITY",
            "🚨 Stranger detected! Nova is locked. Photo saved to recordings folder!",
            "nova"
        )

    # ============================================
    # SHUTDOWN
    # ============================================
    def _shutdown(self):
        print("👋 Nova shutting down...")
        self.mouth.speak("Goodbye! Shutting down now.")
        self.ears.stop_listening()
        self.face_auth.stop_watching()
        self.brain.long_memory.end_session()
        time.sleep(2)
        self.ui.root.destroy()
        sys.exit(0)

    # ============================================
    # RUN
    # ============================================
    def run(self):
        greeting = f"Hello {config.OWNER_NAME}! Nova is online and ready. How can I help you today?"
        
        self.ui.add_message(config.NOVA_NAME, greeting, "nova")
        
        threading.Thread(
            target=self.mouth.speak,
            args=(greeting,),
            daemon=True
        ).start()
        
        threading.Thread(
            target=self.ears.start_continuous_listening,
            args=(self._on_voice_command,),
            daemon=True
        ).start()
        
        threading.Thread(
            target=self.face_auth.start_watching,
            args=(self._on_stranger_detected, self._on_owner_detected),
            daemon=True
        ).start()
        
        # Start remote access server
        threading.Thread(
            target=start_server,
            args=(self,),
            daemon=True
        ).start()
        
        # Start UI
        self.ui.run()


if __name__ == "__main__":
    nova = Nova()
    nova.run()