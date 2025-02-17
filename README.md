# JurisGuide

JurisGuide is a Retrieval-Augmented Generation (RAG) based legal issues advisor chatbot. It leverages a state graph workflow to decide when to retrieve external legal documents and when to generate a response directly using an LLM. The project is designed as a conceptual MVP that can be adapted for various domains by simply updating the configuration variables.

> **Note:** This project is open to contributions. If you have ideas for improvements, bug fixes, or new features, please feel free to open an issue or submit a pull request.

## Features

- **Legal Advisor Chatbot:** Provides context-aware legal advice, definitions, and explanations.
- **Retrieval-Augmented Generation:** Uses external documents as context when needed.
- **Real-Time Streaming:** Displays the LLM’s response token-by-token.
- **Session Management:** Supports multiple chat sessions with persistent conversation history.
- **Configurable:** Easily update API keys, model names, and other parameters via environment variables.
- **File Upload & Chunking:** Upload files to a dedicated `processed` folder that are automatically chunked when running the app.

## Folder Structure

The project is organized as follows:

```
JurisGuide/
│
├── core/                    
│   ├── config.py            # Configuration settings (loads from .env)
│   ├── database.py          # Chat database management
│   ├── models.py            # LangGraph workflow, state definitions, and LLM integrations
│   ├── retriever.py         # Document retrieval functionality
│
├── data/                    
│   ├── chat_history.db      # Chat history database (auto-created)
│   ├── chroma_db/           # Vector store for document retrieval
│   └── processed/           # Uploaded files are saved and automatically chunked
│
├── .env                     # Environment variables file
├── chatbot.py               # Chat interface that integrates with the workflow
├── app.py                   # Streamlit application UI
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following contents:

```env
LLM_API_KEY="YOUR-LLM-API-KEY"
LLM_MODEL="llama-3.2-3b-preview"
VECTOR_STORE_PATH="data/chroma_db"
DB_PATH="data/chat_history.db"
```
For LLM, I have used the Groq API key but you can update it accordingly.

### Core Configuration

The `core/config.py` file loads these values and defines additional settings:

```python
import os
from dotenv import load_dotenv

# Load .env from the parent directory
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
load_dotenv(env_path)

# Database and Vector Store paths
DB_PATH = os.getenv("DB_PATH", "data/chat_history.db")
VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH", "data/chroma_db")
PROCESSED_FOLDER = "data/processed"

# LLM and History Configuration
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL")
HISTORY_CONTEXT = 5    # How many previous messages LLM needs to consider during conversation
RETRIEVE_DOCS = 3      # How many chunks to retrieve for an LLM response
```

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/zubayr-ahmad/JurisGuide.git
   cd JurisGuide
   ```

2. **Create and Activate a Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

Launch the chatbot application with Streamlit:

```bash
streamlit run app.py
```

This will open the app in your default web browser. The chatbot supports real-time streaming of responses as you interact with it.

## Data Folders

- **data/chat_history.db:** The chat history database will be created automatically in the `data` folder.
- **data/chroma_db:** This folder is used as the vector store for document retrieval.
- **data/processed:** Upload your files here. The app will automatically chunk these files when it runs.

## Contributing

JurisGuide is designed as a conceptual MVP for a RAG-based chatbot and is open to improvements and enhancements. Contributions are welcome! Please feel free to:

- Open issues to report bugs or suggest enhancements.
- Submit pull requests with improvements.
- Update configuration settings or extend the functionality for different domains.

Your contributions will help evolve JurisGuide into a versatile tool for building domain-specific chatbots.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [LangGraph](https://github.com/langgraph/langgraph)
- [Streamlit](https://www.streamlit.io/)
- [LangChain](https://github.com/hwchase17/langchain)

---

Happy coding and thank you for your contributions!
