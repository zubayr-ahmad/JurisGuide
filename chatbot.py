from typing import Dict
from core.database import ChatDatabase
from core.models import create_workflow
from core.config import HISTORY_CONTEXT
import uuid



# Chat Interface
class LangGraphChat:
    def __init__(self):
        self.workflow = create_workflow()
        self.db = ChatDatabase()

    def chat(self, user_message: str, session_id: str = None) -> Dict:
        session_id = session_id or str(uuid.uuid4())
        history = self.db.get_chat_history(session_id, limit=HISTORY_CONTEXT)
        print("History >>>>>>>>>>>>>>>", history)
        print("Session id >>>>>>>>>>>>>>>>>>>>>>>", session_id)
        initial_state = {
            "session_id": session_id,
            "user_message": user_message,
            "reference_docs": [],
            "response": "",
            "history": [{"user_message": h['user_message'], "response": h["response"], "reference_docs":h['reference_docs']} for h in history]
        }

        result = self.workflow.invoke(initial_state)
        return {
            "session_id": session_id,
            "response": result["response"],
            "reference_docs": [{
                "content": doc.page_content,
                "metadata": doc.metadata
            } for doc in result["reference_docs"]]
        }
    