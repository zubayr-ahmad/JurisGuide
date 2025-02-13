# Database Layer
import sqlite3
from typing import List
from .config import DB_PATH, HISTORY_CONTEXT
import json

class ChatDatabase:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self._create_table()

    def _create_table(self):
        # print("Creating tables >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                user_message TEXT,
                response TEXT,
                reference_docs TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                name TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def save_chat(self, session_id: str, user_message: str, response: str, reference_docs=None):
        """Save a chat message with references stored as JSON"""
        cursor = self.conn.cursor()
        
        # Convert list of Documents to list of dictionaries
        references = json.dumps([
            {"page_content": doc.page_content, "metadata": doc.metadata}
            for doc in (reference_docs or [])
        ])
        
        cursor.execute("""
            INSERT INTO chats (session_id, user_message, response, reference_docs)
            VALUES (?, ?, ?, ?)
        """, (session_id, user_message, response, references))
        
        self.conn.commit()
    def create_session(self, session_id: str, metadata: dict):
        """Create a new session with metadata"""
        # Add this method to save session metadata (name, created_at) to your database
        # Implementation depends on your database structure
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO sessions (session_id, name, created_at)
            VALUES (?, ?, ?)
        """, (session_id, metadata['name'], metadata['created_at']))
        self.conn.commit()

    def get_all_sessions(self):
        """Retrieve all sessions with their metadata"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT session_id, name, created_at
            FROM sessions
        """)
        sessions = {}
        for row in cursor.fetchall():
            sessions[row[0]] = {
                'name': row[1],
                'created_at': row[2]
            }
        return sessions

    def get_chat_history(self, session_id: str, limit=HISTORY_CONTEXT):
        """Retrieve chat history for a session with reference docs as list of dicts"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT user_message, response, reference_docs
            FROM chats
            WHERE session_id = ?
            ORDER BY timestamp DESC LIMIT ?
        """, (session_id, limit))
        
        history = []
        for row in cursor.fetchall():
            user_message, response, reference_docs_json = row
            reference_docs = json.loads(reference_docs_json) if reference_docs_json else []
            
            history.append({
                'user_message': user_message,
                'response': response,
                'reference_docs': reference_docs
            })
        
        return history