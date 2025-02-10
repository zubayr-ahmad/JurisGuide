import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()
VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH", "data/chroma_db")
PROCESSED_FOLDER = "data/processed"

class DocumentRetriever:
    def __init__(self):
        self.db = None
        self.embeddings = HuggingFaceEmbeddings()
        self.load_database()

    def load_database(self):
        """Automatically loads processed documents and builds vector store."""
        if not os.path.exists(PROCESSED_FOLDER):
            os.makedirs(PROCESSED_FOLDER)
        
        docs = []
        for file in os.listdir(PROCESSED_FOLDER):
            if file.endswith(".pdf"):
                loader = PyPDFLoader(os.path.join(PROCESSED_FOLDER, file))
                docs.extend(loader.load())

        if docs:
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
            texts = text_splitter.split_documents(docs)

            if not os.path.exists(VECTOR_STORE_PATH):
                os.makedirs(VECTOR_STORE_PATH)
            
            self.db = Chroma.from_documents(texts, self.embeddings, persist_directory=VECTOR_STORE_PATH)
        else:
            self.db = Chroma(persist_directory=VECTOR_STORE_PATH, embedding_function=self.embeddings)

    def retrieve_documents(self, query):
        return self.db.similarity_search(query, k=3)