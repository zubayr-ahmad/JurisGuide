from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
import os

load_dotenv()
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "default-llm")

class ResponseGenerator:
    def __init__(self):
        self.llm = ChatGroq(api_key=LLM_API_KEY, model=LLM_MODEL)

    def generate_response(self, query, retrieved_docs):
        context = "\n\n".join([doc.page_content for doc in retrieved_docs])
        messages = [
            SystemMessage(content="You are an AI assistant trained to provide accurate answers based on context."),
            HumanMessage(content=f"Context:\n{context}\n\nQuestion: {query}\nAnswer:")
        ]

        return self.llm(messages)
