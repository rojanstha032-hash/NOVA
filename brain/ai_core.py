# ============================================
# NOVA - AI Brain (ai_core.py)
# ============================================
# This is Nova's brain — it connects to Groq
# and makes Nova understand and respond to you
# ============================================

from groq import Groq
import sys
import os

# This lets us import config.py from the parent folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# ============================================
# WHAT IS A CLASS?
# Think of a class like a blueprint
# NovaBrain is the blueprint for Nova's brain
# ============================================

class NovaBrain:
    def __init__(self):
        # ---- Connect to Groq (Nova's free AI) ----
        self.client = Groq(api_key=config.GROQ_API_KEY)
        
        # ---- Nova's personality ----
        # This tells the AI how to behave
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
        
        # ---- Conversation memory ----
        # This stores the conversation so Nova remembers context
        self.conversation_history = []
        
        print(f"✅ {config.NOVA_NAME}'s brain is online!")

    # ============================================
    # THINK METHOD
    # This is how Nova processes what you say
    # and generates a response
    # ============================================
    def think(self, user_input, memory_context=""):
        
        # Add memory context if available
        full_input = user_input
        if memory_context:
            full_input = f"[Memory Context: {memory_context}]\n\nUser says: {user_input}"
        
        # Add your message to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": full_input
        })
        
        # Keep only last N messages to save memory
        if len(self.conversation_history) > config.MAX_MEMORY_CONTEXT:
            self.conversation_history = self.conversation_history[-config.MAX_MEMORY_CONTEXT:]
        
        try:
            # ---- Send to Groq AI and get response ----
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",  # Free and powerful model
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    *self.conversation_history
                ],
                temperature=0.7,   # 0 = robotic, 1 = creative
                max_tokens=500     # Max length of response
            )
            
            # Extract Nova's response text
            nova_response = response.choices[0].message.content
            
            # Add Nova's response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": nova_response
            })
            
            return nova_response
            
        except Exception as e:
            return f"Sorry, I had a brain glitch: {str(e)}"
    
    # ============================================
    # CLEAR MEMORY METHOD
    # Clears short term conversation memory
    # ============================================
    def clear_memory(self):
        self.conversation_history = []
        print("🧹 Short term memory cleared!")


# ============================================
# TEST NOVA'S BRAIN
# Run this file directly to test:
# python brain/ai_core.py
# ============================================
if __name__ == "__main__":
    print("🔱 Testing Nova's Brain...")
    brain = NovaBrain()
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Nova: Goodbye!")
            break
            
        response = brain.think(user_input)
        print(f"Nova: {response}")