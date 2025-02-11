import os

# Database and Vector Store paths
DB_PATH = os.getenv("DB_PATH", "data/chat_history.db")
VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH", "data/chroma_db")
PROCESSED_FOLDER = "data/processed"
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL")
HISTORY_CONTEXT = 5
RETRIEVE_DOCS = 3