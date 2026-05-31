# ============================================
# NOVA - AI Brain (ai_core.py)
# ============================================
# Supports multiple AI providers!
# Switch between Groq and Gemini in config.py
# ============================================

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class NovaBrain:
    def __init__(self):
        self.conversation_history = []
        
        self.system_prompt = f"""
        You are {config.NOVA_NAME}, a powerful personal AI assistant.
        You are smart, helpful, and loyal ONLY to {config.OWNER_NAME}.
        You are running on their personal Windows computer.
        
        Your personality:
        - Speak naturally and conversationally
        - Be concise — no long unnecessary answers
        - Be proactive — suggest things when relevant
        - Remember you can control the computer, send emails, manage files
        - If asked to do something on the computer, confirm before doing it
        
        Always respond in plain text — no markdown, no bullet points.
        Keep responses short unless asked for detail.
        """
        
        # ---- Load the right AI provider ----
        if config.AI_PROVIDER == "gemini":
            self._init_gemini()
        else:
            self._init_groq()
            
        print(f"✅ {config.NOVA_NAME}'s brain is online!")
        print(f"🧠 Using: {config.AI_PROVIDER.upper()}")

    # ============================================
    # INIT GROQ
    # ============================================
    def _init_groq(self):
        from groq import Groq
        self.client = Groq(api_key=config.GROQ_API_KEY)
        self.provider = "groq"
        
    # ============================================
    # INIT GEMINI
    # ============================================
    def _init_gemini(self):
        import google.generativeai as genai
        genai.configure(api_key=config.GEMINI_API_KEY)
        self.gemini_model = genai.GenerativeModel(
            model_name="gllama-3.3-70b-versatile",
            system_instruction=self.system_prompt
        )
        self.gemini_chat = self.gemini_model.start_chat(history=[])
        self.provider = "gemini"

    # ============================================
    # THINK
    # ============================================
    def think(self, user_input, memory_context=""):
        full_input = user_input
        if memory_context:
            full_input = f"[Memory Context: {memory_context}]\n\nUser says: {user_input}"

        try:
            if self.provider == "gemini":
                return self._think_gemini(full_input)
            else:
                return self._think_groq(full_input)
        except Exception as e:
            return f"Sorry, I had a brain glitch: {str(e)}"

    # ============================================
    # THINK WITH GROQ
    # ============================================
    def _think_groq(self, user_input):
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        if len(self.conversation_history) > config.MAX_MEMORY_CONTEXT:
            self.conversation_history = self.conversation_history[-config.MAX_MEMORY_CONTEXT:]
        
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": self.system_prompt},
                *self.conversation_history
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        nova_response = response.choices[0].message.content
        
        self.conversation_history.append({
            "role": "assistant",
            "content": nova_response
        })
        
        return nova_response

    # ============================================
    # THINK WITH GEMINI
    # ============================================
    def _think_gemini(self, user_input):
        response = self.gemini_chat.send_message(user_input)
        return response.text

    # ============================================
    # CLEAR MEMORY
    # ============================================
    def clear_memory(self):
        self.conversation_history = []
        if self.provider == "gemini":
            self.gemini_chat = self.gemini_model.start_chat(history=[])
        print("🧹 Memory cleared!")

    # ============================================
    # SWITCH PROVIDER
    # Switch between Groq and Gemini on the fly!
    # ============================================
    def switch_provider(self, provider):
        if provider == "gemini":
            self._init_gemini()
        else:
            self._init_groq()
        print(f"🔄 Switched to {provider.upper()}!")


# ============================================
# TEST
# ============================================
if __name__ == "__main__":
    print("🔱 Testing Nova's Brain...")
    brain = NovaBrain()
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        response = brain.think(user_input)
        print(f"Nova: {response}")