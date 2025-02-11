# Database Layer
from ..config import DB_PATH, HISTORY_CONTEXT
import sqlite3

class ChatDatabase:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self._create_table()

    def _create_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                user_message TEXT,
                bot_response TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def save_chat(self, session_id: str, user_message: str, bot_response: str):
        self.conn.execute("""
            INSERT INTO chat_history (session_id, user_message, bot_response)
            VALUES (?, ?, ?)
        """, (session_id, user_message, bot_response))
        self.conn.commit()

    def get_chat_history(self, session_id: str, limit: int = HISTORY_CONTEXT) -> List[tuple]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT user_message, bot_response FROM chat_history
            WHERE session_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (session_id, limit))
        return cursor.fetchall()[::-1]