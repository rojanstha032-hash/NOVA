# ============================================
# NOVA - Long Term Memory (long_term.py)
# ============================================
# This is Nova's permanent memory
# Uses SQLite database — saves on your PC
# Nova will remember everything forever!
#
# What you'll learn:
# - Databases in Python
# - SQLite (file based database)
# - Storing and retrieving data
# - Building a memory system
# ============================================

import sqlite3
import json
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class LongTermMemory:
    def __init__(self):
        # ---- Database path ----
        self.db_path = config.MEMORY_DB_PATH
        
        # ---- Create data folder if not exists ----
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # ---- Connect to database ----
        self.conn = sqlite3.connect(
            self.db_path,
            check_same_thread=False
        )
        
        # ---- Create tables ----
        self._create_tables()
        
        print("✅ Long term memory online!")

    # ============================================
    # CREATE TABLES
    # Like creating folders to organize memories
    # ============================================
    def _create_tables(self):
        cursor = self.conn.cursor()
        
        # ---- Conversations table ----
        # Stores every conversation forever
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                speaker TEXT NOT NULL,
                message TEXT NOT NULL,
                date TEXT NOT NULL
            )
        ''')
        
        # ---- Facts table ----
        # Stores facts Nova learns about you
        # Example: "Rojan likes coffee"
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
        
        # ---- Preferences table ----
        # Stores your preferences
        # Example: "prefers short answers"
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
        
        # ---- Sessions table ----
        # Tracks each time Nova starts
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time TEXT NOT NULL,
                end_time TEXT,
                summary TEXT
            )
        ''')
        
        self.conn.commit()
        print("✅ Memory tables ready!")

    # ============================================
    # SAVE CONVERSATION
    # Saves every message to database
    # ============================================
    def save_conversation(self, speaker, message):
        cursor = self.conn.cursor()
        now = datetime.now()
        cursor.execute('''
            INSERT INTO conversations 
            (timestamp, speaker, message, date)
            VALUES (?, ?, ?, ?)
        ''', (
            now.isoformat(),
            speaker,
            message,
            now.strftime("%Y-%m-%d")
        ))
        self.conn.commit()

    # ============================================
    # GET RECENT CONVERSATIONS
    # Gets last N messages for context
    # ============================================
    def get_recent_conversations(self, limit=10):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT speaker, message, timestamp
            FROM conversations
            ORDER BY id DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        rows.reverse()  # Oldest first
        return rows

    # ============================================
    # SAVE FACT
    # Nova learns facts about you
    # Example: save_fact("personal", "favorite_food", "pizza")
    # ============================================
    def save_fact(self, category, key, value):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO facts (category, key, value, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (category, key, value, datetime.now().isoformat()))
        self.conn.commit()
        print(f"💾 Nova learned: {key} = {value}")

    # ============================================
    # GET FACTS
    # Gets all facts Nova knows about you
    # ============================================
    def get_facts(self, category=None):
        cursor = self.conn.cursor()
        if category:
            cursor.execute(
                'SELECT key, value FROM facts WHERE category = ?',
                (category,)
            )
        else:
            cursor.execute('SELECT category, key, value FROM facts')
        return cursor.fetchall()

    # ============================================
    # SAVE PREFERENCE
    # Saves your preferences
    # ============================================
    def save_preference(self, key, value):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO preferences (key, value, timestamp)
            VALUES (?, ?, ?)
        ''', (key, value, datetime.now().isoformat()))
        self.conn.commit()

    # ============================================
    # GET PREFERENCE
    # Gets a preference value
    # ============================================
    def get_preference(self, key, default=None):
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT value FROM preferences WHERE key = ?',
            (key,)
        )
        row = cursor.fetchone()
        return row[0] if row else default

    # ============================================
    # GET MEMORY CONTEXT
    # Builds a summary of what Nova knows
    # This gets sent to AI with every message!
    # ============================================
    def get_memory_context(self):
        context_parts = []
        
        # ---- Recent conversations ----
        recent = self.get_recent_conversations(5)
        if recent:
            context_parts.append("Recent conversation history:")
            for speaker, message, timestamp in recent:
                context_parts.append(f"  {speaker}: {message}")
        
        # ---- Known facts ----
        facts = self.get_facts()
        if facts:
            context_parts.append("\nWhat I know about you:")
            for category, key, value in facts:
                context_parts.append(f"  {key}: {value}")
        
        return "\n".join(context_parts)

    # ============================================
    # START SESSION
    # Called when Nova starts up
    # ============================================
    def start_session(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO sessions (start_time)
            VALUES (?)
        ''', (datetime.now().isoformat(),))
        self.conn.commit()
        self.current_session_id = cursor.lastrowid
        print(f"📅 Session {self.current_session_id} started!")

    # ============================================
    # END SESSION
    # Called when Nova shuts down
    # ============================================
    def end_session(self, summary=""):
        if hasattr(self, 'current_session_id'):
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE sessions
                SET end_time = ?, summary = ?
                WHERE id = ?
            ''', (
                datetime.now().isoformat(),
                summary,
                self.current_session_id
            ))
            self.conn.commit()

    # ============================================
    # GET LAST SESSION SUMMARY
    # What did we talk about last time?
    # ============================================
    def get_last_session(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT start_time, summary
            FROM sessions
            ORDER BY id DESC
            LIMIT 1
        ''')
        return cursor.fetchone()

    # ============================================
    # SEARCH MEMORY
    # Search for specific topics in memory
    # ============================================
    def search_memory(self, query):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT speaker, message, timestamp
            FROM conversations
            WHERE message LIKE ?
            ORDER BY id DESC
            LIMIT 5
        ''', (f'%{query}%',))
        return cursor.fetchall()

    # ============================================
    # CLOSE DATABASE
    # ============================================
    def close(self):
        self.conn.close()


# ============================================
# TEST
# Run: py -3.11 memory/long_term.py
# ============================================
if __name__ == "__main__":
    print("🔱 Testing Nova's Long Term Memory...")
    memory = LongTermMemory()
    
    # Test saving
    memory.start_session()
    memory.save_conversation("Rojan", "Hello Nova!")
    memory.save_conversation("Nova", "Hello Rojan! How can I help?")
    memory.save_fact("personal", "favorite_color", "blue")
    memory.save_preference("response_length", "short")
    
    # Test retrieving
    print("\n📚 Recent conversations:")
    for speaker, message, timestamp in memory.get_recent_conversations():
        print(f"  {speaker}: {message}")
    
    print("\n🧠 Memory context:")
    print(memory.get_memory_context())
    
    memory.close()
    print("\n✅ Memory test complete!")