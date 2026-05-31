# ============================================
# NOVA - AI Brain (ai_core.py)
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
        - You have a long term memory — use it to personalize responses
        - If you learn something about {config.OWNER_NAME}, remember it
        - Always respond in plain text — no markdown, no bullet points
        - Keep responses short unless asked for detail
        """
        
        # ---- Load AI provider ----
        if config.AI_PROVIDER == "gemini":
            self._init_gemini()
        else:
            self._init_groq()
            
        # ---- Load memory ----
        from memory.long_term import LongTermMemory
        from memory.short_term import ShortTermMemory
        self.long_memory = LongTermMemory()
        self.short_memory = ShortTermMemory()
        self.long_memory.start_session()
            
        print(f"✅ {config.NOVA_NAME}'s brain is online!")
        print(f"🧠 Using: {config.AI_PROVIDER.upper()}")

    def _init_groq(self):
        from groq import Groq
        self.client = Groq(api_key=config.GROQ_API_KEY)
        self.provider = "groq"
        
    def _init_gemini(self):
        import google.generativeai as genai
        genai.configure(api_key=config.GEMINI_API_KEY)
        self.gemini_model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=self.system_prompt
        )
        self.gemini_chat = self.gemini_model.start_chat(history=[])
        self.provider = "gemini"

    # ============================================
    # THINK
    # Now uses memory context!
    # ============================================
    def think(self, user_input):
        # ---- Get memory context ----
        long_memory_context = self.long_memory.get_memory_context()
        short_memory_context = self.short_memory.get_context()
        
        # ---- Build full context ----
        memory_context = ""
        if long_memory_context:
            memory_context += f"Long term memory:\n{long_memory_context}\n\n"
        if short_memory_context:
            memory_context += f"Current conversation:\n{short_memory_context}"

        # ---- Save user message to memory ----
        self.long_memory.save_conversation(config.OWNER_NAME, user_input)
        self.short_memory.add(config.OWNER_NAME, user_input)

        try:
            if self.provider == "gemini":
                response = self._think_gemini(user_input, memory_context)
            else:
                response = self._think_groq(user_input, memory_context)
                
            # ---- Save Nova's response to memory ----
            self.long_memory.save_conversation(config.NOVA_NAME, response)
            self.short_memory.add(config.NOVA_NAME, response)
            
            return response
            
        except Exception as e:
            return f"Sorry, I had a brain glitch: {str(e)}"

    def _think_groq(self, user_input, memory_context=""):
        full_input = user_input
        if memory_context:
            full_input = f"[Memory Context:\n{memory_context}]\n\nUser: {user_input}"
            
        self.conversation_history.append({
            "role": "user",
            "content": full_input
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

    def _think_gemini(self, user_input, memory_context=""):
        full_input = user_input
        if memory_context:
            full_input = f"[Memory Context:\n{memory_context}]\n\nUser: {user_input}"
        response = self.gemini_chat.send_message(full_input)
        return response.text

    def clear_memory(self):
        self.conversation_history = []
        self.short_memory.clear()
        if self.provider == "gemini":
            self.gemini_chat = self.gemini_model.start_chat(history=[])
        print("🧹 Memory cleared!")

    def switch_provider(self, provider):
        if provider == "gemini":
            self._init_gemini()
        else:
            self._init_groq()
        print(f"🔄 Switched to {provider.upper()}!")


if __name__ == "__main__":
    print("🔱 Testing Nova's Brain with Memory...")
    brain = NovaBrain()
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        response = brain.think(user_input)
        print(f"Nova: {response}")