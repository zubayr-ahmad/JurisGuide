from core.retriever import DocumentRetriever
from core.models import ResponseGenerator
from core.database import ChatDatabase
import uuid

class Chatbot:
    def __init__(self, session_id=None):
        self.db = ChatDatabase()
        self.retriever = DocumentRetriever()  # Auto-loads processed docs
        self.generator = ResponseGenerator()
        
        # Maintain session ID
        if session_id is None:
            self.session_id = str(uuid.uuid4())
        else:
            self.session_id = session_id

    def chat(self, user_input):
        """Handles a single chat interaction."""
        # Retrieve relevant documents
        docs = self.retriever.retrieve_documents(user_input)

        # Generate response using retrieved content
        response = self.generator.generate_response(user_input, docs)
        response_text = response.content
        
        # Save chat history
        self.db.save_chat(self.session_id, user_input, response_text)

        return response_text, docs

    def get_history(self):
        """Fetches the entire chat history for the current session."""
        return self.db.get_chat_history(self.session_id)

    def get_all_sessions(self):
        """Retrieves all previous sessions."""
        return self.db.get_all_sessions()