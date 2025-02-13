
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_groq import ChatGroq
from typing import List, Any, Dict, TypedDict, Annotated
from langgraph.graph import StateGraph, END
from .database import ChatDatabase
from .retriever import DocumentRetriever

from .config import LLM_API_KEY, LLM_MODEL, HISTORY_CONTEXT

# LLM Response Generation
class ResponseGenerator:
    def __init__(self):
        self.llm = ChatGroq(api_key=LLM_API_KEY, 
                          model=LLM_MODEL)

    def generate_response(self, context: str, history: str, query: str) -> str:
        messages = [
            SystemMessage(content="You are an AI assistant. Use the provided context to generate accurate answers. If the context is insufficient, state that you are unsure rather than guessing."),
            HumanMessage(content=f"Context:\n{context}\n\nConversation History:\n{history}\n\nUser Query:\n{query}\n\nResponse:")
        ]

        return self.llm(messages).content
    
# LangGraph State Definition
class ChatState(TypedDict):
    session_id: str
    user_message: str
    reference_docs: List[Any]
    response: str
    history: Annotated[List[Dict[str, str]], lambda x, y: x + y]

# LangGraph Nodes
class ChatNodes:
    def __init__(self):
        self.db = ChatDatabase()
        self.retriever = DocumentRetriever()
        self.generator = ResponseGenerator()

    def retrieve_documents(self, state: ChatState) -> Dict:
        docs = self.retriever.retrieve_documents(state["user_message"])
        return {"reference_docs": docs}

    def generate_response(self, state: ChatState) -> Dict:
        context = "\n\n".join([doc.page_content for doc in state["reference_docs"]])
        history = "\n".join([f"User: {msg['user_message']}\nBot: {msg['response']}" 
                           for msg in state.get("history", [])[-HISTORY_CONTEXT:]])
        print("Context >>>>>>>>>>>>>>>>>>>>>>>>", context)
        print("History >>>>>>>>>>>>>>>>>>>>>>>>", history)
        response = self.generator.generate_response(
            context=context,
            history=history,
            query=state["user_message"]
        )
        return {"response": response}

    def save_conversation(self, state: ChatState) -> Dict:
        self.db.save_chat(
            state["session_id"],
            state["user_message"],
            state["response"],
            reference_docs=state["reference_docs"]
        )
        return {
            "history": [{
                "user_message": state["user_message"],
                "response": state["response"],
                "reference_docs": state["reference_docs"]
            }]
        }

# LangGraph Workflow Setup
def create_workflow():
    nodes = ChatNodes()
    workflow = StateGraph(ChatState)

    workflow.add_node("retrieve", nodes.retrieve_documents)
    workflow.add_node("generate", nodes.generate_response)
    workflow.add_node("save", nodes.save_conversation)

    workflow.set_entry_point("retrieve")
    workflow.add_edge("retrieve", "generate")
    workflow.add_edge("generate", "save")
    workflow.add_edge("save", END)

    return workflow.compile()
