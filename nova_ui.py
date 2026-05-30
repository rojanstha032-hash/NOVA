# ============================================
# NOVA - Beautiful UI (nova_ui.py)
# ============================================
# This is Nova's face — the window you see
# Built with customtkinter for modern look
# Background can be changed anytime in config
# ============================================

import customtkinter as ctk
import threading
import time
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config

# ============================================
# UI SETTINGS
# Change these anytime to customize Nova's look
# ============================================
ctk.set_appearance_mode("dark")        # "dark" or "light"
ctk.set_default_color_theme("blue")    # "blue", "green", "dark-blue"


class NovaUI:
    def __init__(self):
        # ---- Main Window ----
        self.root = ctk.CTk()
        self.root.title(f"{config.NOVA_NAME} - AI Assistant")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # ---- Background color (we'll add image later) ----
        # TODO: Replace with cool background image
        # self.root.configure(bg_image=...)
        self.root.configure(fg_color="#0a0a0a")  # Near black for now
        
        # ---- State ----
        self.is_listening = False
        self.is_thinking = False
        
        # ---- Build the UI ----
        self._build_header()
        self._build_chat_area()
        self._build_status_bar()
        self._build_input_area()
        self._build_plugin_sidebar()
        
        # ---- Welcome Message ----
        self.add_message("Nova", f"🔱 Online and ready, {config.OWNER_NAME}. How can I help?", "nova")
        
        print("✅ Nova UI is ready!")

    # ============================================
    # HEADER — Top of window
    # Shows Nova's name, time, status
    # ============================================
    def _build_header(self):
        self.header = ctk.CTkFrame(
            self.root,
            fg_color="#111111",
            height=70,
            corner_radius=0
        )
        self.header.pack(fill="x", padx=0, pady=0)
        self.header.pack_propagate(False)
        
        # Nova name
        self.title_label = ctk.CTkLabel(
            self.header,
            text=f"🔱 {config.NOVA_NAME.upper()}",
            font=ctk.CTkFont(family="Arial", size=28, weight="bold"),
            text_color="#00aaff"
        )
        self.title_label.pack(side="left", padx=20, pady=10)
        
        # Version
        self.version_label = ctk.CTkLabel(
            self.header,
            text=f"v{config.PROJECT_VERSION}",
            font=ctk.CTkFont(size=12),
            text_color="#444444"
        )
        self.version_label.pack(side="left", padx=0, pady=10)
        
        # Clock (right side)
        self.clock_label = ctk.CTkLabel(
            self.header,
            text="",
            font=ctk.CTkFont(size=14),
            text_color="#666666"
        )
        self.clock_label.pack(side="right", padx=20)
        self._update_clock()
        
        # Status indicator
        self.status_indicator = ctk.CTkLabel(
            self.header,
            text="● ONLINE",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#00ff88"
        )
        self.status_indicator.pack(side="right", padx=20)

    # ============================================
    # CHAT AREA — Middle of window
    # Shows conversation between you and Nova
    # ============================================
    def _build_chat_area(self):
        # Main container
        self.chat_container = ctk.CTkFrame(
            self.root,
            fg_color="#0d0d0d",
            corner_radius=0
        )
        self.chat_container.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Scrollable chat box
        self.chat_box = ctk.CTkScrollableFrame(
            self.chat_container,
            fg_color="#0d0d0d",
            corner_radius=10
        )
        self.chat_box.pack(fill="both", expand=True, padx=15, pady=15)

    # ============================================
    # STATUS BAR — Shows what Nova is doing
    # "Listening...", "Thinking...", "Speaking..."
    # ============================================
    def _build_status_bar(self):
        self.status_frame = ctk.CTkFrame(
            self.root,
            fg_color="#111111",
            height=40,
            corner_radius=0
        )
        self.status_frame.pack(fill="x")
        self.status_frame.pack_propagate(False)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="💤 Idle — Say something or type below",
            font=ctk.CTkFont(size=12),
            text_color="#555555"
        )
        self.status_label.pack(side="left", padx=15)
        
        # Memory indicator
        self.memory_label = ctk.CTkLabel(
            self.status_frame,
            text="🧠 Memory: Active",
            font=ctk.CTkFont(size=12),
            text_color="#555555"
        )
        self.memory_label.pack(side="right", padx=15)

    # ============================================
    # INPUT AREA — Bottom of window
    # Type or click mic button to talk
    # ============================================
    def _build_input_area(self):
        self.input_frame = ctk.CTkFrame(
            self.root,
            fg_color="#111111",
            height=70,
            corner_radius=0
        )
        self.input_frame.pack(fill="x", padx=0, pady=0)
        self.input_frame.pack_propagate(False)
        
        # Mic button
        self.mic_button = ctk.CTkButton(
            self.input_frame,
            text="🎙️",
            width=50,
            height=45,
            font=ctk.CTkFont(size=20),
            fg_color="#1a1a2e",
            hover_color="#00aaff",
            corner_radius=10,
            command=self._toggle_listening
        )
        self.mic_button.pack(side="left", padx=10, pady=10)
        
        # Text input
        self.text_input = ctk.CTkEntry(
            self.input_frame,
            placeholder_text=f"Talk to {config.NOVA_NAME} or type here...",
            height=45,
            font=ctk.CTkFont(size=14),
            fg_color="#1a1a1a",
            border_color="#333333",
            text_color="#ffffff",
            corner_radius=10
        )
        self.text_input.pack(side="left", fill="x", expand=True, padx=5, pady=10)
        self.text_input.bind("<Return>", self._on_text_submit)
        
        # Send button
        self.send_button = ctk.CTkButton(
            self.input_frame,
            text="Send ➤",
            width=80,
            height=45,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#00aaff",
            hover_color="#0088cc",
            corner_radius=10,
            command=self._on_text_submit
        )
        self.send_button.pack(side="right", padx=10, pady=10)

    # ============================================
    # PLUGIN SIDEBAR
    # Quick access buttons for features
    # Add new plugins here later!
    # ============================================
    def _build_plugin_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self.root,
            fg_color="#111111",
            width=60,
            corner_radius=0
        )
        # Hidden for now — will show when plugins added
        # self.sidebar.pack(side="right", fill="y")
        
        # ---- PLUGIN BUTTONS GO HERE ----
        # Example of how to add a plugin button:
        # ctk.CTkButton(self.sidebar, text="📧", ...).pack(pady=5)
        # Just uncomment and add your plugin!

    # ============================================
    # ADD MESSAGE TO CHAT
    # Call this to show messages in the chat area
    # ============================================
    def add_message(self, sender, message, msg_type="user"):
        # Timestamp
        timestamp = datetime.now().strftime("%H:%M")
        
        # Message frame
        msg_frame = ctk.CTkFrame(
            self.chat_box,
            fg_color="#1a1a2e" if msg_type == "nova" else "#1a2e1a",
            corner_radius=10
        )
        msg_frame.pack(
            fill="x",
            padx=5,
            pady=5,
            anchor="w" if msg_type == "nova" else "e"
        )
        
        # Sender label
        sender_label = ctk.CTkLabel(
            msg_frame,
            text=f"{'🔱 ' + sender if msg_type == 'nova' else '👤 ' + sender} • {timestamp}",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#00aaff" if msg_type == "nova" else "#00ff88"
        )
        sender_label.pack(anchor="w", padx=10, pady=(8, 2))
        
        # Message text
        msg_label = ctk.CTkLabel(
            msg_frame,
            text=message,
            font=ctk.CTkFont(size=13),
            text_color="#dddddd",
            wraplength=600,
            justify="left"
        )
        msg_label.pack(anchor="w", padx=10, pady=(0, 8))

    # ============================================
    # UPDATE STATUS
    # Call this to update the status bar
    # ============================================
    def update_status(self, text, color="#555555"):
        self.status_label.configure(text=text, text_color=color)

    # ============================================
    # TOGGLE LISTENING
    # Called when mic button is clicked
    # ============================================
    def _toggle_listening(self):
        if not self.is_listening:
            self.is_listening = True
            self.mic_button.configure(fg_color="#ff0044")
            self.update_status("🎙️ Listening...", "#ff0044")
            # TODO: Connect to voice input module
        else:
            self.is_listening = False
            self.mic_button.configure(fg_color="#1a1a2e")
            self.update_status("💤 Idle", "#555555")

    # ============================================
    # TEXT SUBMIT
    # Called when Enter pressed or Send clicked
    # ============================================
    def _on_text_submit(self, event=None):
        text = self.text_input.get().strip()
        if not text:
            return
        
        # Show user message
        self.add_message(config.OWNER_NAME, text, "user")
        self.text_input.delete(0, "end")
        self.update_status("🧠 Thinking...", "#ffaa00")
        
        # Process in background thread so UI doesn't freeze
        threading.Thread(
            target=self._process_input,
            args=(text,),
            daemon=True
        ).start()

    # ============================================
    # PROCESS INPUT
    # Sends text to Nova's brain and shows response
    # ============================================
    def _process_input(self, text):
        # Import brain here to avoid circular imports
        from brain.ai_core import NovaBrain
        
        if not hasattr(self, 'brain'):
            self.brain = NovaBrain()
        
        response = self.brain.think(text)
        
        # Update UI from main thread
        self.root.after(0, self.add_message, "Nova", response, "nova")
        self.root.after(0, self.update_status, "💤 Idle", "#555555")

    # ============================================
    # CLOCK UPDATER
    # Updates clock every second
    # ============================================
    def _update_clock(self):
        now = datetime.now().strftime("%A, %B %d  •  %I:%M:%S %p")
        self.clock_label.configure(text=now)
        self.root.after(1000, self._update_clock)

    # ============================================
    # START NOVA UI
    # ============================================
    def run(self):
        self.root.mainloop()


# ============================================
# RUN NOVA
# ============================================
if __name__ == "__main__":
    print("🔱 Starting Nova UI...")
    app = NovaUI()
    app.run()