import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DB_PATH", "data/chat_history.db")

class ChatDatabase:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                user_input TEXT,
                bot_response TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def save_chat(self, session_id, user_input, bot_response):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO chat_history (session_id, user_input, bot_response) VALUES (?, ?, ?)", 
                       (session_id, user_input, bot_response))
        self.conn.commit()

    def get_chat_history(self, session_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT user_input, bot_response FROM chat_history WHERE session_id = ?", (session_id,))
        return cursor.fetchall()
