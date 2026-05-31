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
        
        print("🖥️ Loading UI...")
        self.ui = NovaUI()
        
        # Connect UI to Nova's processor
        self.ui.brain = self.brain
        self.ui._process_input = self._on_text_command
        
        print("=" * 50)
        print(f"✅ Nova is fully online!")
        print(f"💬 Say 'Hey Nova' or type in the window!")
        print("=" * 50)

    # ============================================
    # ON VOICE COMMAND
    # Called when Nova hears your voice
    # ============================================
    def _on_voice_command(self, text):
        print(f"🎙️ Voice command: {text}")
        
        # Show in UI
        self.ui.root.after(0,
            self.ui.add_message,
            config.OWNER_NAME,
            f"🎙️ {text}",
            "user"
        )
        
        # Process command
        self._process_command(text)

    # ============================================
    # ON TEXT COMMAND
    # Called when you type in the UI
    # ============================================
    def _on_text_command(self, text):
        print(f"⌨️ Text command: {text}")
        threading.Thread(
            target=self._process_command,
            args=(text,),
            daemon=True
        ).start()

    # ============================================
    # PROCESS COMMAND
    # Sends to brain and responds
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

        # Send to AI
        response = self.brain.think(text)
        self._respond(response)

    # ============================================
    # RESPOND
    # Shows in UI and speaks
    # ============================================
    def _respond(self, response):
        # Show in UI
        self.ui.root.after(0,
            self.ui.add_message,
            config.NOVA_NAME,
            response,
            "nova"
        )
        
        # Update status
        self.ui.root.after(0,
            self.ui.update_status,
            "🔊 Speaking...",
            "#00aaff"
        )
        
        # Speak (blocking — waits until done)
        self.mouth.speak(response)
        
        # Reset status
        self.ui.root.after(0,
            self.ui.update_status,
            "💤 Idle — Say 'Hey Nova' or type below",
            "#555555"
        )

    # ============================================
    # SHUTDOWN
    # ============================================
    def _shutdown(self):
        print("👋 Nova shutting down...")
        self.mouth.speak("Goodbye! Shutting down now.")
        self.ears.stop_listening()
        time.sleep(2)
        self.ui.root.destroy()
        sys.exit(0)

    # ============================================
    # RUN
    # ============================================
    def run(self):
        greeting = f"Hello {config.OWNER_NAME}! Nova is online and ready. How can I help you today?"
        
        # Show greeting in UI
        self.ui.add_message(config.NOVA_NAME, greeting, "nova")
        
        # Speak greeting in background
        threading.Thread(
            target=self.mouth.speak,
            args=(greeting,),
            daemon=True
        ).start()
        
        # Start voice listening
        threading.Thread(
            target=self.ears.start_continuous_listening,
            args=(self._on_voice_command,),
            daemon=True
        ).start()
        
        # Start UI
        self.ui.run()


if __name__ == "__main__":
    nova = Nova()
    nova.run()