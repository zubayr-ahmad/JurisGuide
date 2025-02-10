import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DB_PATH", "data/chat_history.db")

class ChatDatabase:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        """Creates the chat history table if it does not exist."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                user_message TEXT,
                bot_response TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def save_chat(self, session_id, user_message, bot_response):
        """Saves a chat message to the database."""
        self.cursor.execute("""
            INSERT INTO chat_history (session_id, user_message, bot_response)
            VALUES (?, ?, ?)
        """, (session_id, user_message, bot_response))
        self.conn.commit()

    def get_chat_history(self, session_id):
        """Retrieves all messages from a session."""
        self.cursor.execute("""
            SELECT user_message, bot_response FROM chat_history
            WHERE session_id = ?
            ORDER BY timestamp ASC
        """, (session_id,))
        return self.cursor.fetchall()

    def get_all_sessions(self):
        """Retrieve all unique session IDs."""
        self.cursor.execute("""
            SELECT DISTINCT session_id FROM chat_history ORDER BY timestamp DESC
        """)
        return [row[0] for row in self.cursor.fetchall()]