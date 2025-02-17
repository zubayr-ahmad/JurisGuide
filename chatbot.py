from typing import Dict
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

    def chat(self, user_message: str, session_id: str = None):
        session_id = session_id or str(uuid.uuid4())
        history = self.db.get_chat_history(session_id, limit=HISTORY_CONTEXT)
        initial_state = {
            "session_id": session_id,
            "user_message": user_message,
            "reference_docs": [],
            "response": "",
            "history": [
                {"user_message": h['user_message'], "response": h["response"], "reference_docs": h['reference_docs']}
                for h in history
            ]
        }
        full_response = ""
        print("Generator ", self.workflow.stream(initial_state))
        print("Type", type(self.workflow.stream(initial_state)))
        # This is your generator streaming updates
        for update in self.workflow.stream(initial_state):
            # Check if a response chunk is available
            if "generate" in update:
                chunk = update["generate"].get("response", "")
                full_response += chunk
                # Yield the chunk for streaming
                yield {"chunk": chunk, "full_response": full_response}
            # You can also yield final payloads or metadata as needed.
        # Optionally yield a final payload with metadata at the end.
        yield {"final": True, "session_id": session_id, "response": full_response, "reference_docs": []}
    