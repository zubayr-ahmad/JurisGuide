
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_groq import ChatGroq
from typing import List, Any, Dict, TypedDict, Annotated, Optional
from langgraph.graph import StateGraph, END
from .database import ChatDatabase
from .retriever import DocumentRetriever

from .config import LLM_API_KEY, LLM_MODEL, HISTORY_CONTEXT

# LLM Response Generation
# State Definition
class ChatState(TypedDict):
    session_id: str
    user_message: str
    reference_docs: Optional[List[Any]]
    response: Optional[str]
    requires_retrieval: bool
    history: List[Dict[str, Any]]

# LLM Response Generation
class ResponseGenerator:
    def __init__(self):
        self.llm = ChatGroq(api_key=LLM_API_KEY, 
                          model=LLM_MODEL)

    def generate_response(self, context: str, history: str, query: str) -> str:
        messages = [
            SystemMessage(content="""
            You are an AI assistant with expertise in various topics, including legal definitions, documentation, and general knowledge.
            
            - If the user's query is related to **legal matters** (e.g., laws, regulations, contracts, legal definitions, compliance), respond in a **professional and informative** manner.
            - Use the **provided context** if available to generate an **accurate and relevant** response.
            - If the **context is missing**, use your general knowledge to answer.
            - Use **conversation history** if relevant to maintain continuity.
            - If the query is **ambiguous**, ask for clarification instead of assuming.

            Always ensure that responses are **clear, concise, and factually correct**.
            """),
            HumanMessage(content=f"Context:\n{context}\n\nConversation History:\n{history}\n\nUser Query:\n{query}\n\nResponse:")
        ]

        return self.llm(messages).content

    
    def custom_call(self, user_prompt, system_prompt=None):
        messages = [HumanMessage(content=user_prompt)]
        if system_prompt:
            messages.insert(0, SystemMessage(system_prompt))
        return self.llm(messages).content

# Chat Nodes Class
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
    
    def decide_retrieval(self, state: ChatState):
        """Uses the LLM to decide whether retrieval is needed."""
        prompt = f"""
        You are an AI assistant that determines whether a user's query requires retrieving external knowledge.

        Rules:
        1. If the query is a greeting or a general conversational question (e.g., "How are you?", "What's up?"), respond `False`.
        2. If the query is related to legal issues, definitions, or specific knowledge (e.g., "What is the definition of negligence?", "Explain copyright law"), respond `True`.
        3. If the query is ambiguous or lacks sufficient information, respond `True` to ensure accurate retrieval.
        4. For all other cases, respond `True` if the query requires factual or specific knowledge, otherwise `False`.

        Query: "{state['user_message']}"
        Answer with 'True' if retrieval is needed, otherwise 'False'. It should be either of them in all cases.
        """

        response = self.generator.custom_call(prompt)  
        state['requires_retrieval'] = "true" in response.lower().strip() 
        return state

# LangGraph Workflow Setup with LLM Classification
def create_workflow():
    nodes = ChatNodes()
    workflow = StateGraph(ChatState)

    workflow.add_node("decide_retrieval", nodes.decide_retrieval)  # LLM decides if retrieval is needed
    workflow.add_node("retrieve", nodes.retrieve_documents)
    workflow.add_node("generate", nodes.generate_response)
    workflow.add_node("save", nodes.save_conversation)

    workflow.set_entry_point("decide_retrieval")

    # Conditional transition based on LLM decision
    workflow.add_conditional_edges(
        "decide_retrieval",
        lambda state: "retrieve" if state['requires_retrieval'] else "generate",
        {"retrieve": "retrieve", "generate": "generate"},
    )

    workflow.add_edge("retrieve", "generate")
    workflow.add_edge("generate", "save")
    workflow.add_edge("save", END)

    return workflow.compile()