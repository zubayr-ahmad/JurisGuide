import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Dict, Any
import json
from .config import PROCESSED_FOLDER, VECTOR_STORE_PATH, RETRIEVE_DOCS
# Document Retrieval Layer
class DocumentRetriever:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings()
        self.processed_files_path = os.path.join(VECTOR_STORE_PATH, "processed_files.json")
        self.processed_files = self._load_processed_files()
        self.db = self._initialize_vectorstore()

    def _load_processed_files(self) -> Dict[str, Dict]:
        """Load the list of processed files and their metadata."""
        if os.path.exists(self.processed_files_path):
            with open(self.processed_files_path, 'r') as f:
                return json.load(f)
        return {}

    def _save_processed_files(self):
        """Save the list of processed files and their metadata."""
        os.makedirs(VECTOR_STORE_PATH, exist_ok=True)
        with open(self.processed_files_path, 'w') as f:
            json.dump(self.processed_files, f, indent=2)

    def _get_file_metadata(self, filepath: str) -> Dict:
        """Get file metadata including modification time and size."""
        stat = os.stat(filepath)
        return {
            "mtime": stat.st_mtime,
            "size": stat.st_size
        }

    def _has_file_changed(self, filepath: str) -> bool:
        """Check if a file has been modified since last processing."""
        if not os.path.exists(filepath):
            return False

        current_metadata = self._get_file_metadata(filepath)
        filename = os.path.basename(filepath)

        if filename not in self.processed_files:
            return True

        stored_metadata = self.processed_files[filename]
        return (current_metadata["mtime"] != stored_metadata["mtime"] or
                current_metadata["size"] != stored_metadata["size"])

    def _initialize_vectorstore(self):
        """Initialize or update the vector store with new or modified documents."""
        if not os.path.exists(PROCESSED_FOLDER):
            os.makedirs(PROCESSED_FOLDER)

        # Get all PDF files in the processed folder
        pdf_files = [f for f in os.listdir(PROCESSED_FOLDER) if f.endswith(".pdf")]
        
        # Check for new or modified files
        new_docs = []
        for filename in pdf_files:
            filepath = os.path.join(PROCESSED_FOLDER, filename)
            
            if self._has_file_changed(filepath):
                print(f"Processing new/modified file: {filename}")
                loader = PyPDFLoader(filepath)
                new_docs.extend(loader.load())
                
                # Update processed files record
                self.processed_files[filename] = self._get_file_metadata(filepath)
        
        # Save the updated processed files record
        self._save_processed_files()

        # If we have new documents, process them and update the vector store
        if new_docs:
            print(f"Number of new documents to process: {len(new_docs)}")
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
            texts = text_splitter.split_documents(new_docs)
            print(f"Created {len(texts)} chunks from new documents")
            
            # If vector store exists, add to it; otherwise create new
            if os.path.exists(VECTOR_STORE_PATH):
                db = Chroma(persist_directory=VECTOR_STORE_PATH, 
                          embedding_function=self.embeddings)
                db.add_documents(texts)
                return db
            else:
                return Chroma.from_documents(texts, self.embeddings, 
                                          persist_directory=VECTOR_STORE_PATH)
        
        # If no new documents, just load existing vector store
        return Chroma(persist_directory=VECTOR_STORE_PATH, 
                     embedding_function=self.embeddings)

    def retrieve_documents(self, query: str, k=RETRIEVE_DOCS) -> List[Any]:
        """Retrieve similar documents for a given query."""
        return self.db.similarity_search(query, k)