"""
Psychology RAG Chatbot using LangChain, Chroma, and Chainlit

A retrieval-augmented generation (RAG) chatbot that uses DSM-5 documents
to provide psychology-informed support and analysis.

Architecture:
- LLM: Google Gemini (gemini-2.5-flash-lite)
- Embeddings: HuggingFace (all-MiniLM-L6-v2)
- Vector Store: Chroma (persistent SQLite)
- Chat UI: Chainlit
- State Management: LangGraph with InMemorySaver
- Storage: Local JSON + Optional Flask Backend API
"""

# ============================================================================
# IMPORTS
# ============================================================================

# Standard library
import os
import uuid

# Third-party
import chainlit as cl

# LangChain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

# Project modules
from rag.config import logger, LANGSMITH_API_KEY, GOOGLE_API_KEY
from rag.embeddings.vectorstore import initialize_embeddings, initialize_vector_store
from rag.loaders.pdf_loader import load_pdf_documents
from rag.agents.psychology_agent import PsychologyAgentState, create_retrieve_context_tool, update_diagnosis
from storage import save_chat_history, load_chat_history, save_to_backend_api
from pathlib import Path


# ============================================================================
# RAG INITIALIZATION
# ============================================================================

print("\nInitializing RAG components...")
embeddings = initialize_embeddings()
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite")
print("✓ Chat model initialized")
vector_store = initialize_vector_store(embeddings)


# ============================================================================
# DOCUMENT LOADING & INDEXING
# ============================================================================

def load_and_index_documents() -> None:
    """Load PDF documents and index them into the vector store."""
    pdf_path = Path("data/documents/DSM-5 Các tiêu chuẩn chẩn đoán.pdf")
    
    if not pdf_path.exists():
        logger.warning(f"PDF not found at {pdf_path}")
        logger.info("Using empty vector store. Add documents manually or provide the PDF file.")
        return
    
    # Check if documents already indexed (smart caching)
    collection_count = vector_store._collection.count()
    if collection_count > 0:
        logger.info(f"✓ Documents already indexed ({collection_count} chunks in vector store)")
        logger.info("✓ Skipping re-indexing (pass)")
        return
    
    logger.info(f"Loading documents from {pdf_path}...")
    
    try:
        # Load PDF
        docs = load_pdf_documents(pdf_path)
        logger.info(f"✓ Loaded {len(docs)} pages")
        
        # Split into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            add_start_index=True,
        )
        all_splits = text_splitter.split_documents(docs)
        logger.info(f"✓ Split into {len(all_splits)} chunks")
        
        # Add to vector store
        document_ids = vector_store.add_documents(documents=all_splits)
        logger.info(f"✓ Indexed {len(document_ids)} documents into vector store")
        
    except Exception as e:
        logger.error(f"✗ Error loading documents: {e}")


# Initialize documents on startup
load_and_index_documents()


# ============================================================================
# AGENT CREATION
# ============================================================================

SYSTEM_PROMPT = """
Bạn là một chuyên gia tâm lý AI chuyên chăm sóc sức khỏe tâm thần.

Bước 1: Thu thập thông tin triệu chứng của người dùng...
Bước 2: Khi đủ thông tin, dùng retrieve_context, update_diagnosis...
Bước 3: Đánh giá theo 4 mức độ: kém, trung bình, bình thường, tốt...
"""

# Create tools with vector store binding
retrieve_context = create_retrieve_context_tool(vector_store)
tools = [retrieve_context, update_diagnosis]
checkpointer = InMemorySaver()

agent = create_agent(
    model=model,
    tools=tools,
    state_schema=PsychologyAgentState,
    checkpointer=checkpointer,
    system_prompt=SYSTEM_PROMPT,
)

print("✓ Psychology Agent with RAG initialized successfully\n")


# ============================================================================
# CHAINLIT EVENT HANDLERS
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
    
    # Get user session ID from cookies (passed by frontend)
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
            "(•ˋ _ ˊ•) **Welcome to Psychology Assistant**\n\n"
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
    user_session_id = cl.user_session.get("user_session_id")

    # Add user message to history
    message_history.append({"role": "user", "content": message.content})

    config = {"configurable": {"thread_id": thread_id}}
    
    # Check if this is the first message
    current_state = checkpointer.get(config)
    
    # Prepare inputs for agent
    inputs = {
        "messages": [("user", message.content)]
    }
    
    # Initialize user_id on first message
    if current_state is None:
        logger.info(f"📝 [NEW SESSION] User: {user_id}, Thread: {thread_id}")
        inputs["user_id"] = user_id
    
    # Send response placeholder
    response = cl.Message(content="")
    await response.send()
    
    try:
        # Stream agent response
        is_first_token = True
        async for event in agent.astream(inputs, config, stream_mode="values"):
            last_message = event["messages"][-1]

            if last_message.type == "ai":
                # Stream content from AI
                if hasattr(last_message, "content") and last_message.content:
                    if is_first_token:
                        is_first_token = False
                        logger.info(f"✍️  [AI RESPONSE STARTED]")

                    await response.stream_token(last_message.content)

                # Update history with agent response
                message_history.append({
                    "role": "assistant",
                    "content": last_message.content
                })

        # Update message in UI
        await response.update()

        # Get diagnosis data from session
        diagnosis_data = cl.user_session.get("diagnosis_data", {})
        
        # Save to local storage
        cl.user_session.set("message_history", message_history)
        save_chat_history(user_id, thread_id, message_history, diagnosis_data)
        
        # Save to backend API (if configured)
        await save_to_backend_api(thread_id, message_history, diagnosis_data, user_session_id)
        
        logger.info(f"✓ Message processed and saved")
                
    except Exception as e:
        logger.error(f"✗ Error during agent execution: {e}", exc_info=True)
        await response.update()
        await cl.Message(
            content=f"Sorry, I encountered an error: {str(e)}\n\nPlease try again."
        ).send()


@cl.on_chat_end
def on_chat_end():
    """Called when the user disconnects."""
    logger.info("👋 User disconnected")


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Psychology RAG Chatbot Ready!")
    print("=" * 70)
    print("\nTo start the chatbot, run:")
    print("  chainlit run src/app.py")
    print("\nThen open: http://localhost:8000")
    print("=" * 70)
