# chatbot.py
from typing import Dict, Generator
from core.database import ChatDatabase
from core.models import create_workflow
from core.config import HISTORY_CONTEXT
import types
import uuid

# Chat Interface
class LangGraphChat:
    def __init__(self):
        self.workflow = create_workflow()
        self.db = ChatDatabase()
        from core.models import ResponseGenerator
        self.generator = ResponseGenerator()

    def chat(self, user_message: str, session_id: str = None) -> Generator:
        """
        Process the chat through LangGraph and then stream the response 
        for Streamlit to display.
        """
        session_id = session_id or str(uuid.uuid4())
        history = self.db.get_chat_history(session_id, limit=HISTORY_CONTEXT)
        
        # Prepare initial state
        initial_state = {
            "session_id": session_id,
            "user_message": user_message,
            "reference_docs": [],
            "response": "",
            "context": "",
            "chat_history": "",
            "history": [
                {"user_message": h['user_message'], "response": h["response"], "reference_docs": h['reference_docs']}
                for h in history
            ]
        }
        
        # Run workflow to get context and prepare for streaming
        final_state = self.workflow.invoke(initial_state)
        
        # Get reference documents for later use
        reference_docs = final_state.get("reference_docs", [])
        
        # Now get the stream from the LLM
        stream = self.generator.get_stream(
            context=final_state.get("context", ""),
            history=final_state.get("chat_history", ""),
            query=user_message
        )
        
        # Stream the response to Streamlit
        full_response = ""
        for chunk in stream:
            if hasattr(chunk, 'content'):
                content = chunk.content
            elif hasattr(chunk, 'delta') and hasattr(chunk.delta, 'content'):
                content = chunk.delta.content
            else:
                content = str(chunk)
                
            if content:
                full_response += content
                # Yield the chunk for streaming in Streamlit
                yield {"chunk": content, "full_response": full_response}
        
        # Save the completed response to the database
        self.db.save_chat(
            session_id,
            user_message,
            full_response,
            reference_docs=reference_docs
        )
        
        # Final yield with metadata and reference docs
        yield {
            "final": True, 
            "session_id": session_id, 
            "response": full_response, 
            "reference_docs": [
                {"page_content": doc.page_content, "metadata": doc.metadata}
                for doc in reference_docs
            ]
        }