from core.retriever import DocumentRetriever
from core.models import ResponseGenerator
from core.database import ChatDatabase
import uuid

class Chatbot:
    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.db = ChatDatabase()
        self.retriever = DocumentRetriever()  # Auto-loads processed docs
        self.generator = ResponseGenerator()

    def chat(self, user_input):
        # Retrieve relevant documents
        docs = self.retriever.retrieve_documents(user_input)

        # Generate response using retrieved content
        response = self.generator.generate_response(user_input, docs)
        response_text = response.content
        
        # Save chat history
        self.db.save_chat(self.session_id, user_input, response_text)

        return response, docs

    def get_history(self):
        return self.db.get_chat_history(self.session_id)
