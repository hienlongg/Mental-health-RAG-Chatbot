# RAG Agent

A LangChain-based Retrieval-Augmented Generation (RAG) agent for document analysis and question-answering.

## Project Structure

```
RAG-agent/
├── src/                          # Source code
│   ├── rag/
│   │   ├── loaders/             # Document loaders
│   │   ├── embeddings/          # Embedding & vectorstore utilities
│   │   ├── retrievers/          # Retriever implementations
│   │   └── agents/              # Agent logic
│   └── __init__.py
├── data/                         # Data storage
│   ├── documents/               # Source documents (PDFs, etc.)
│   └── embeddings/              # Chroma DB and embeddings
├── notebooks/                    # Jupyter notebooks for exploration
│   └── rag-agent.ipynb          # Main notebook
├── tests/                        # Unit tests
├── config/                       # Configuration
│   └── settings.py              # Environment and app settings
├── logs/                         # Application logs
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables (do not commit)
└── README.md
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the project root:

```
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=your_key_here
LANGSMITH_PROJECT=your_project_name
OPENAI_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here
```

### 3. Run the Notebook

```bash
jupyter notebook notebooks/rag-agent.ipynb
```

## Components

### Document Loaders (`src/rag/loaders/`)
Load and preprocess documents (PDFs, text files, etc.)

### Embeddings (`src/rag/embeddings/`)
Initialize embeddings and vectorstore (Chroma, Pinecone, etc.)

### Retrievers (`src/rag/retrievers/`)
Implement custom retrieval strategies

### Agents (`src/rag/agents/`)
Build LangChain agents with tools and chains

## Environment Variables

- `LANGSMITH_API_KEY`: LangSmith API key for tracing
- `GOOGLE_API_KEY`: Google Gemini API key
- `OPENAI_API_KEY`: OpenAI API key (optional)

## Notes

- **Never commit `.env`** with real API keys
- Use `config/settings.py` to access configuration
- Notebooks are in `notebooks/` for experimentation
- Move tested code to `src/` for production use
