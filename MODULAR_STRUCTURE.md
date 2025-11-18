# Modular Code Structure

## Overview

The codebase has been refactored from a monolithic 532-line `app.py` into a modular architecture with clear separation of concerns. This makes the code more testable, maintainable, and reusable.

## Folder Structure

```
src/
├── app.py                    # Main application entry point (129 lines)
├── storage.py               # Data persistence utilities (97 lines)
└── rag/                      # RAG module with 4 submodules
    ├── __init__.py          # Module exports
    ├── config.py            # Configuration & logging (40 lines)
    ├── pipeline.py          # RAG pipeline setup
    ├── embeddings/
    │   ├── __init__.py
    │   ├── embeddings.py    # Embedding initialization
    │   └── vectorstore.py   # Vector store management (51 lines)
    ├── loaders/
    │   ├── __init__.py
    │   └── pdf_loader.py    # PDF loading utilities (23 lines)
    ├── retrievers/
    │   ├── __init__.py
    │   └── retriever.py     # Similarity search (35 lines)
    └── agents/
        ├── __init__.py
        └── psychology_agent.py  # Agent state & tools (88 lines)
```

## Module Details

### 1. `rag/config.py` - Configuration & Logging
**Responsibility**: Environment setup and logging configuration

```python
from rag.config import setup_logging, load_environment, logger, LANGSMITH_API_KEY, GOOGLE_API_KEY
```

**Functions**:
- `setup_logging()` → Returns configured logger (file + console)
- `load_environment()` → Validates and loads environment variables
- Module-level exports: `logger`, `LANGSMITH_API_KEY`, `GOOGLE_API_KEY`

**When to modify**: 
- Adding new configuration parameters
- Changing logging format or output

---

### 2. `rag/embeddings/vectorstore.py` - Vector Store Management
**Responsibility**: Initialize and manage embeddings and vector store

```python
from rag.embeddings.vectorstore import initialize_embeddings, initialize_vector_store
```

**Functions**:
- `initialize_embeddings(model)` → HuggingFace embeddings
- `initialize_vector_store(embeddings, collection_name, persist_directory)` → Chroma store

**When to modify**:
- Switching embedding models
- Changing vector store configuration
- Adding persistence options

---

### 3. `rag/loaders/pdf_loader.py` - Document Loading
**Responsibility**: Load and parse documents

```python
from rag.loaders.pdf_loader import load_pdf_documents
```

**Functions**:
- `load_pdf_documents(file_path)` → Load PDF and return documents

**When to modify**:
- Adding support for other document types (Word, TXT, etc.)
- Changing PDF parsing logic
- Adding document preprocessing

---

### 4. `rag/retrievers/retriever.py` - Semantic Search
**Responsibility**: Vector similarity search

```python
from rag.retrievers.retriever import retrieve_context
```

**Functions**:
- `retrieve_context(vector_store, query, k)` → Search and return top-k results

**When to modify**:
- Changing search strategy
- Adding filters or re-ranking
- Modifying result formatting

---

### 5. `rag/agents/psychology_agent.py` - Agent Definition
**Responsibility**: Agent state schema and tool definitions

```python
from rag.agents.psychology_agent import (
    PsychologyAgentState,
    create_retrieve_context_tool,
    update_diagnosis
)
```

**Classes**:
- `PsychologyAgentState` → State schema with fields: `user_id`, `score`, `content`, `total_guess`

**Functions**:
- `create_retrieve_context_tool(vector_store)` → Factory for retrieve_context tool
- `update_diagnosis(score, content, total_guess, runtime)` → Tool for updating diagnosis

**When to modify**:
- Adding new state fields
- Adding new tools
- Changing tool behavior

---

### 6. `storage.py` - Data Persistence
**Responsibility**: Save and load chat history and diagnosis data

```python
from storage import save_chat_history, load_chat_history, save_to_backend_api
```

**Functions**:
- `save_chat_history(user_id, thread_id, message_history, diagnosis_data)` → Save to JSON
- `load_chat_history(user_id, thread_id)` → Load from JSON
- `save_to_backend_api(thread_id, message_history, diagnosis_data, user_session_id)` → API call

**When to modify**:
- Changing storage format (JSON → database)
- Adding new storage backends
- Modifying API integration

---

### 7. `app.py` - Main Application
**Responsibility**: Orchestrate components and handle user interactions

**Sections**:
1. Module docstring & imports
2. RAG initialization
3. Document loading & indexing
4. Agent creation
5. Chainlit event handlers
6. Entry point

**When to modify**:
- Adding new chat handlers
- Changing UI flow
- Modifying agent configuration

---

## How to Extend

### Add a New Tool
1. Create a new function in `rag/agents/psychology_agent.py`
2. Decorate with `@tool`
3. Add to `tools` list in `app.py`

```python
# In rag/agents/psychology_agent.py
@tool
def my_new_tool(param: str) -> str:
    """Description of the tool."""
    return "result"

# In app.py
tools = [retrieve_context, update_diagnosis, my_new_tool]
```

### Add a New Document Loader
1. Create new file in `rag/loaders/` (e.g., `doc_loader.py`)
2. Implement loading function
3. Import in `app.py`

```python
# In rag/loaders/doc_loader.py
def load_word_documents(file_path: str):
    """Load Word documents."""
    # Implementation
    pass
```

### Add a New Retriever
1. Create new file in `rag/retrievers/` (e.g., `hybrid_retriever.py`)
2. Implement retrieval function
3. Use in agent tools

```python
# In rag/retrievers/hybrid_retriever.py
def hybrid_search(vector_store, query: str):
    """Hybrid search combining semantic and keyword."""
    # Implementation
    pass
```

### Change Storage Backend
1. Modify `storage.py` functions
2. Keep the same function signatures
3. Update implementation details

```python
# In storage.py
def save_chat_history(user_id, thread_id, message_history, diagnosis_data=None):
    # Switch from JSON to database
    db = connect_database()
    db.save(...)
```

---

## Testing Individual Modules

```python
# Test config
from rag.config import setup_logging
logger = setup_logging()
logger.info("Test message")

# Test embeddings
from rag.embeddings.vectorstore import initialize_embeddings
embeddings = initialize_embeddings()

# Test PDF loader
from rag.loaders.pdf_loader import load_pdf_documents
docs = load_pdf_documents("data/documents/file.pdf")

# Test storage
from storage import save_chat_history, load_chat_history
save_chat_history("user_123", "thread_456", [], {})
messages, diagnosis = load_chat_history("user_123", "thread_456")
```

---

## Import Best Practices

✅ **DO**: Import from specific modules
```python
from rag.config import logger
from rag.embeddings.vectorstore import initialize_embeddings
```

❌ **DON'T**: Use relative imports (except within same package)
```python
# Don't do this
from ..rag.config import logger
```

✅ **DO**: Keep imports organized in app.py
```python
# Standard library
import uuid

# Third-party
import chainlit as cl

# Project modules
from rag.config import logger
```

---

## Performance Considerations

- **Embeddings**: Initialized once at startup and reused
- **Vector Store**: Persistent directory avoids re-indexing
- **Async Storage**: Backend API calls are async to avoid blocking
- **Logging**: File + console handlers with minimal overhead

---

## Troubleshooting

**Import errors**: Ensure you're running from project root
```bash
cd /home/hienlong/projects/RAG-agent
python3 -c "from rag.config import logger"
```

**Module not found**: Check that `__init__.py` files exist in subpackages

**Circular imports**: Avoid importing app.py from modules; use dependency injection instead

---

## Summary

| Module | Lines | Responsibility |
|--------|-------|-----------------|
| `rag/config.py` | 40 | Logging & environment |
| `rag/embeddings/vectorstore.py` | 51 | Embeddings & vector store |
| `rag/loaders/pdf_loader.py` | 23 | Document loading |
| `rag/retrievers/retriever.py` | 35 | Semantic search |
| `rag/agents/psychology_agent.py` | 88 | Agent state & tools |
| `storage.py` | 97 | Data persistence |
| `app.py` | 129 | Main application |
| **Total** | **463** | **Modular architecture** |

