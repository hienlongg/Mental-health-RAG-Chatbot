"""
Psychology RAG Chatbot using LangChain, Chroma, and Chainlit
A retrieval-augmented generation (RAG) chatbot that uses DSM-5 documents
to provide psychology-informed support and analysis.
"""

import os
import sys
import uuid
import logging
import json
from pathlib import Path
from typing import Optional
from datetime import datetime

from dotenv import load_dotenv
import chainlit as cl
from pydantic import BaseModel, Field
import httpx  # Add this for HTTP requests

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

# ============================================================================
# CHAT HISTORY PERSISTENCE
# ============================================================================

def save_chat_history(user_id: str, thread_id: str, message_history: list, diagnosis_data: dict = None):
    """Save chat history to JSON file with optional diagnosis metadata."""
    chat_dir = Path("data/chats")
    chat_dir.mkdir(exist_ok=True)
    
    # Filename format: user_id_thread_id.json
    filename = chat_dir / f"{user_id}_{thread_id}.json"
    
    chat_data = {
        "user_id": user_id,
        "thread_id": thread_id,
        "timestamp": datetime.now().isoformat(),
        "message_count": len(message_history),
        "messages": message_history,
        "diagnosis": diagnosis_data or {}  # Store diagnosis/assessment data
    }
    
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(chat_data, f, ensure_ascii=False, indent=2)
        logger.info(f"✓ Chat history saved: {filename}")
        if diagnosis_data:
            logger.info(f"✓ Diagnosis data saved: Score={diagnosis_data.get('score')}")
    except Exception as e:
        logger.error(f"✗ Error saving chat history: {e}")

def load_chat_history(user_id: str, thread_id: str) -> tuple:
    """Load chat history from JSON file. Returns (messages, diagnosis_data)."""
    chat_dir = Path("data/chats")
    filename = chat_dir / f"{user_id}_{thread_id}.json"
    
    if filename.exists():
        try:
            with open(filename, "r", encoding="utf-8") as f:
                chat_data = json.load(f)
            logger.info(f"✓ Chat history loaded: {filename}")
            messages = chat_data.get("messages", [])
            diagnosis = chat_data.get("diagnosis", {})
            return messages, diagnosis
        except Exception as e:
            logger.error(f"✗ Error loading chat history: {e}")
    
    return [], {}

# Load documents on startup
load_and_index_documents()

# SETUP LOGGING

Path(".logs").mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('.logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

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
    Search DSM-5 psychology database for information matching the query.
    Use this to find relevant diagnostic criteria, symptoms, or treatments.
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
    logger.info(f"📊 [DIAGNOSIS UPDATE]")
    logger.info(f"   Score: {score}")
    logger.info(f"   Content: {content[:100]}...")
    logger.info(f"   Assessment: {total_guess[:100]}...")
    
    # Store diagnosis in session
    diagnosis_data = {
        "score": score,
        "content": content,
        "total_guess": total_guess,
        "timestamp": datetime.now().isoformat()
    }
    cl.user_session.set("diagnosis_data", diagnosis_data)
    
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

SYSTEM_PROMPT = """
Bạn là một chuyên gia tâm lý AI chuyên chăm sóc sức khỏe tâm thần.

Bước 1: Thu thập thông tin triệu chứng của người dùng...
Bước 2: Khi đủ thông tin, dùng retrieve_context, update_diagnosis...
Bước 3: Đánh giá theo 4 mức độ: kém, trung bình, bình thường, tốt...
"""

agent = create_agent(
    model=model,
    tools=tools,
    state_schema=PsychologyAgentState,
    checkpointer=checkpointer,
    system_prompt=SYSTEM_PROMPT,
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
    
    # Try to get user session ID from request (passed by frontend in cookies)
    user_session_id = cl.user_session.get("user_session_id")
    logger.info(f"🔑 User Session ID: {user_session_id}")
    
    # Try to load existing chat history
    message_history, diagnosis_data = load_chat_history(user_id, thread_id)
    if message_history:
        logger.info(f"✓ Loaded existing chat history for {user_id}")
        logger.info(f"✓ Previous diagnosis: {diagnosis_data}")
    else:
        logger.info(f"✓ Starting new chat session for {user_id}")
        message_history = []
        diagnosis_data = {}
    
    cl.user_session.set("message_history", message_history)
    cl.user_session.set("diagnosis_data", diagnosis_data)
    
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
    message_history = cl.user_session.get("message_history")
    
    # Get user_id from session cookie (passed by frontend)
    user_session_id = cl.user_session.get("user_session_id")

    # Add user message to history
    message_history.append({"role": "user", "content": message.content})

    config = {"configurable": {"thread_id": thread_id}}
    
    # Check if this is the first message
    current_state = checkpointer.get(config)
    
    # Prepare inputs for agent
    inputs = {
        "messages": [("user", message.content)] 
        # đúng format LangChain
    }
    
    # Initialize user_id on first message
    if current_state is None:
        print(f"[New Session] User: {user_id}, Thread: {thread_id}")
        inputs["user_id"] = user_id
    
    
    # Send response placeholder
    response = cl.Message(content="")
    await response.send()
    
    try:
        # Stream agent response - use "values" mode for actual state
        is_first_token = True
        async for event in agent.astream(inputs, config, stream_mode="values"):
            # Get the last message from the agent
            last_message = event["messages"][-1]

            if last_message.type == "ai":
                    # Only stream content from AI
                    if hasattr(last_message, "content") and last_message.content:
                        if is_first_token:
                            is_first_token = False

                        await response.stream_token(last_message.content)

                    # Update history with agent
                    message_history.append({
                        "role": "assistant",
                        "content": last_message.content
                    })

        print()

        # Update message
        await response.update()

        # Get diagnosis data from session
        diagnosis_data = cl.user_session.get("diagnosis_data", {})
        
        # Save updated message history to disk with diagnosis
        cl.user_session.set("message_history", message_history)
        save_chat_history(user_id, thread_id, message_history, diagnosis_data)
        
        # 🔥 NEW: Save to MongoDB via Flask backend API
        await save_to_backend_api(thread_id, message_history, diagnosis_data, user_session_id)
                
    except Exception as e:
        logger.error(f"Error during agent execution: {e}", exc_info=True)
        print(f"Error during agent execution: {e}")
        await response.update()
        await cl.Message(
            content=f"Sorry, I encountered an error: {str(e)}\n\nPlease try again."
        ).send()

async def save_to_backend_api(thread_id: str, message_history: list, diagnosis_data: dict, user_session_id: str = None):
    """
    Save conversation and diagnosis to Flask backend API
    """
    try:
        # Only save if we have a user session ID (frontend provided it)
        if not user_session_id:
            logger.warning(f"⚠️  No user session ID, skipping backend save for thread: {thread_id}")
            return
        
        backend_url = os.getenv("BACKEND_URL", "http://localhost:5000")
        
        # Prepare conversation data
        conversation_data = {
            "threadID": thread_id,
            "messages": message_history
        }
        
        # Save conversation
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{backend_url}/api/chatbot/save-conversation",
                    json=conversation_data,
                    cookies={"user_session_id": user_session_id},
                    timeout=10.0
                )
                if response.status_code == 200:
                    logger.info(f"✅ Conversation saved to backend: {thread_id}")
                else:
                    logger.warning(f"⚠️  Backend returned {response.status_code}: {response.text}")
            except Exception as e:
                logger.error(f"❌ Failed to save conversation to backend: {e}")
        
        # Save diagnosis if available
        if diagnosis_data:
            diagnosis_payload = {
                "threadID": thread_id,
                "score": diagnosis_data.get("score"),
                "content": diagnosis_data.get("content"),
                "totalGuess": diagnosis_data.get("total_guess")
            }
            
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.post(
                        f"{backend_url}/api/chatbot/save-diagnosis",
                        json=diagnosis_payload,
                        cookies={"user_session_id": user_session_id},
                        timeout=10.0
                    )
                    if response.status_code == 200:
                        logger.info(f"✅ Diagnosis saved to backend: {thread_id}")
                    else:
                        logger.warning(f"⚠️  Backend returned {response.status_code}")
                except Exception as e:
                    logger.error(f"❌ Failed to save diagnosis to backend: {e}")
                    
    except Exception as e:
        logger.error(f"Error in save_to_backend_api: {e}")

@cl.on_chat_end
def on_chat_end():
    print("The user disconnected!")

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