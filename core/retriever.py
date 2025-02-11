import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Any
from ..config import PROCESSED_FOLDER, VECTOR_STORE_PATH, RETRIEVE_DOCS
# Document Retrieval Layer
class DocumentRetriever:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings()
        self.db = self._initialize_vectorstore()

    def _initialize_vectorstore(self):
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
            return Chroma.from_documents(texts, self.embeddings, persist_directory=VECTOR_STORE_PATH)
        
        return Chroma(persist_directory=VECTOR_STORE_PATH, embedding_function=self.embeddings)

    def retrieve_documents(self, query: str, k=RETRIEVE_DOCS) -> List[Any]:
        return self.db.similarity_search(query, k)
