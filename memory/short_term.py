# ============================================
# NOVA - Short Term Memory (short_term.py)
# ============================================
# Remembers current conversation context
# Cleared when Nova restarts
# ============================================

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class ShortTermMemory:
    def __init__(self):
        # Current conversation messages
        self.messages = []
        self.max_messages = config.MAX_MEMORY_CONTEXT
        print("✅ Short term memory online!")

    def add(self, speaker, message):
        self.messages.append({
            "speaker": speaker,
            "message": message
        })
        # Keep only last N messages
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]

    def get_context(self):
        if not self.messages:
            return ""
        lines = []
        for msg in self.messages:
            lines.append(f"{msg['speaker']}: {msg['message']}")
        return "\n".join(lines)

    def clear(self):
        self.messages = []
        print("🧹 Short term memory cleared!")