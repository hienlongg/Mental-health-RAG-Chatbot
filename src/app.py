"""
Psychology RAG Chatbot using LangChain, Chroma, and Chainlit
A retrieval-augmented generation (RAG) chatbot that uses DSM-5 documents
to provide psychology-informed support and analysis.
"""

import os
import sys
import uuid
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
import chainlit as cl
from pydantic import BaseModel, Field

# LangChain imports
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.agents import create_agent, AgentState
from langchain.tools import tool, ToolRuntime
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command
from langchain_core.messages import ToolMessage

# ============================================================================
# CONFIGURATION & INITIALIZATION
# ============================================================================

# Load environment variables
load_dotenv()

# Add project root to path
project_root = Path.cwd()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Verify required environment variables
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not LANGSMITH_API_KEY:
    raise EnvironmentError("LANGSMITH_API_KEY not set in environment. Add it to your .env file.")
if not GOOGLE_API_KEY:
    raise EnvironmentError("GOOGLE_API_KEY not set in environment. Add it to your .env file.")

print("✓ Environment variables loaded successfully")

# ============================================================================
# INITIALIZE RAG COMPONENTS
# ============================================================================

print("Initializing RAG components...")

# Initialize embeddings (HuggingFace)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
print("✓ Embeddings initialized")

# Initialize chat model (Google Gemini)
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite")
print("✓ Chat model initialized")

# Initialize vector store (Chroma)
vector_store = Chroma(
    collection_name="psychology_knowledge_base",
    embedding_function=embeddings,
    persist_directory=".data/embeddings/chroma_langchain_db",
)
print("✓ Vector store initialized")

# ============================================================================
# LOAD AND INDEX DOCUMENTS
# ============================================================================

def load_and_index_documents():
    """Load PDF documents and index them into the vector store."""
    pdf_path = Path("data/documents/DSM-5 Các tiêu chuẩn chẩn đoán.pdf")
    
    if not pdf_path.exists():
        print(f"⚠ Warning: PDF not found at {pdf_path}")
        print("Using empty vector store. Add documents manually or provide the PDF file.")
        return
    
    # Check if documents already indexed
    collection_count = vector_store._collection.count()
    if collection_count > 0:
        print(f"✓ Documents already indexed ({collection_count} chunks in vector store)")
        print("✓ Skipping re-indexing (pass)")
        return
    
    print(f"Loading documents from {pdf_path}...")
    
    try:
        # Load PDF
        loader = PyPDFLoader(str(pdf_path))
        docs = loader.load()
        print(f"✓ Loaded {len(docs)} pages")
        
        # Split into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            add_start_index=True,
        )
        all_splits = text_splitter.split_documents(docs)
        print(f"✓ Split into {len(all_splits)} chunks")
        
        # Add to vector store
        document_ids = vector_store.add_documents(documents=all_splits)
        print(f"✓ Indexed {len(document_ids)} documents into vector store")
        
    except Exception as e:
        print(f"✗ Error loading documents: {e}")

# Load documents on startup
load_and_index_documents()

# ============================================================================
# DEFINE CUSTOM AGENT STATE
# ============================================================================

class PsychologyAgentState(AgentState):
    """
    Defines the memory state for the psychology chatbot.
    'messages' is included by default by AgentState.
    """
    user_id: str
    score: str = ""  # Mental health score (e.g., anxiety level)
    content: str = ""  # Content/summary of user's state
    total_guess: str = ""  # Total assessment/diagnosis

# ============================================================================
# DEFINE TOOLS
# ============================================================================

@tool
def retrieve_context(query: str) -> str:
    """
    Retrieve relevant psychological context or information from the knowledge base.
    Uses the vector store to find similar documents from DSM-5.
    """
    print(f"[Tool Call: retrieve_context] Query: {query}")
    
    try:
        retrieved_docs = vector_store.similarity_search(query, k=2)
        
        if retrieved_docs:
            serialized = "\n\n".join(
                (f"Source: {doc.metadata}\nContent: {doc.page_content[:500]}")
                for doc in retrieved_docs
            )
            return f"Retrieved relevant information:\n\n{serialized}"
        else:
            return f"No relevant information found for: {query}"
    except Exception as e:
        print(f"Error in retrieve_context: {e}")
        return f"Error retrieving information: {str(e)}"

@tool
def update_diagnosis(
    score: str = Field(description="Score of the user's mental health (e.g., anxiety level 1-10)."),
    content: str = Field(description="Summary/content of the user's mental health state."),
    total_guess: str = Field(description="Total assessment/diagnosis of the user's mental health."),
    runtime: ToolRuntime = None
) -> Command:
    """
    Update the agent's internal analysis of the user's mental health state.
    Use this when you have gathered enough information to form an assessment.
    """
    print(f"[Tool Call: update_diagnosis] Score: {score}, Content: {content}")
    
    return Command(
        update={
            "score": score,
            "content": content,
            "total_guess": total_guess,
            "messages": [
                ToolMessage(
                    content=f"Diagnosis updated. Score: {score}, Analysis: {content}",
                    tool_call_id=runtime.tool_call_id if runtime else "manual",
                )
            ],
        }
    )

# ============================================================================
# CREATE AGENT
# ============================================================================

tools = [retrieve_context, update_diagnosis]
checkpointer = InMemorySaver()

agent = create_agent(
    model=model,
    tools=tools,
    state_schema=PsychologyAgentState,
    checkpointer=checkpointer,
)

print("✓ Psychology Agent with RAG initialized successfully\n")

# ============================================================================
# CHAINLIT CHAT HANDLERS
# ============================================================================

@cl.on_chat_start
async def on_chat_start():
    """Called when a new user session starts."""
    # Create unique thread_id for this session
    thread_id = str(uuid.uuid4())
    cl.user_session.set("thread_id", thread_id)
    
    # Create user_id from thread_id
    user_id = "user_" + thread_id[:8]
    cl.user_session.set("user_id", user_id)
    
    # Send welcome message
    await cl.Message(
        content=(
            "🧠 **Welcome to Psychology Assistant**\n\n"
            "I'm here to provide psychological support and guidance based on DSM-5 standards. "
            "Feel free to share your concerns, and I'll do my best to help.\n\n"
            "**Note:** This is for informational purposes only and not a substitute for professional mental health treatment."
        )
    ).send()

@cl.on_message
async def on_message(message: cl.Message):
    """Called every time the user sends a message."""
    # Get session information
    thread_id = cl.user_session.get("thread_id")
    user_id = cl.user_session.get("user_id")
    
    config = {"configurable": {"thread_id": thread_id}}
    
    # Check if this is the first message
    current_state = checkpointer.get(config)
    
    # Prepare inputs for agent
    inputs = {
        "messages": [{"role": "user", "content": message.content}]
    }
    
    # Initialize user_id on first message
    if current_state is None:
        print(f"[New Session] User: {user_id}, Thread: {thread_id}")
        inputs["user_id"] = user_id
    
    # Send response placeholder
    response = cl.Message(content="")
    await response.send()
    
    try:
        # Stream agent response
        async for event in agent.astream(inputs, config, stream_mode="events"):
            kind = event["event"]
            
            # Stream LLM response tokens
            if kind == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                if chunk.content:
                    await response.stream_token(chunk.content)
            
            # Show tool usage
            elif kind == "on_tool_start":
                tool_info = event["data"]["input"]
                tool_name = tool_info.get("tool", "unknown")
                await response.stream_token(f"\n*[Using tool: {tool_name}]*\n")
                print(f"[Tool] {tool_name}")
            
            # Log tool results
            elif kind == "on_tool_end":
                output = event["data"]["output"]
                if isinstance(output, dict) and output.get("messages"):
                    print(f"[Tool Output] Success")
        
        # Update message
        await response.update()
        
    except Exception as e:
        print(f"Error during agent execution: {e}")
        await response.update()
        await cl.Message(
            content=f"Sorry, I encountered an error: {str(e)}\n\nPlease try again."
        ).send()

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Psychology RAG Chatbot Ready!")
    print("=" * 70)
    print("\nTo start the chatbot, run:")
    print("  chainlit run app.py")
    print("\nThen open: http://localhost:8000")
    print("=" * 70)
