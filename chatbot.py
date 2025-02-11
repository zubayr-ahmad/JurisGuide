from typing import Dict
from core.database import ChatDatabase
from core.models import create_workflow
from config import HISTORY_CONTEXT
import uuid



# Chat Interface
class LangGraphChat:
    def __init__(self):
        self.workflow = create_workflow()
        self.db = ChatDatabase()

    def chat(self, user_input: str, session_id: str = None) -> Dict:
        session_id = session_id or str(uuid.uuid4())
        history = self.db.get_chat_history(session_id, limit=HISTORY_CONTEXT)
        
        initial_state = {
            "session_id": session_id,
            "user_input": user_input,
            "retrieved_docs": [],
            "response": "",
            "history": [{"user": h[0], "bot": h[1]} for h in history]
        }

        result = self.workflow.invoke(initial_state)
        return {
            "session_id": session_id,
            "response": result["response"],
            "references": [{
                "content": doc.page_content,
                "metadata": doc.metadata
            } for doc in result["retrieved_docs"]]
        }
    