"""Chat history and data storage utilities."""

import os
import json
import logging
import httpx
from pathlib import Path
from typing import Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


def save_chat_history(
    user_id: str,
    thread_id: str,
    message_history: list,
    diagnosis_data: dict = None
) -> None:
    """Save chat history and diagnosis data to JSON file."""
    chat_dir = Path("data/chats")
    chat_dir.mkdir(exist_ok=True)
    
    filename = chat_dir / f"{user_id}_{thread_id}.json"
    
    chat_data = {
        "user_id": user_id,
        "thread_id": thread_id,
        "timestamp": datetime.now().isoformat(),
        "message_count": len(message_history),
        "messages": message_history,
        "diagnosis": diagnosis_data or {}
    }
    
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(chat_data, f, ensure_ascii=False, indent=2)
        logger.info(f"✓ Chat history saved: {filename}")
        if diagnosis_data:
            logger.info(f"✓ Diagnosis data saved: Score={diagnosis_data.get('score')}")
    except Exception as e:
        logger.error(f"✗ Error saving chat history: {e}")


def load_chat_history(user_id: str, thread_id: str) -> Tuple[list, dict]:
    """Load chat history and diagnosis data from JSON file."""
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


async def save_to_backend_api(
    thread_id: str,
    message_history: list,
    diagnosis_data: dict,
    user_session_id: str = None
) -> None:
    """Save conversation and diagnosis to Flask backend API."""
    try:
        # Only save if we have a user session ID
        if not user_session_id:
            logger.warning(f"⚠️  No user session ID, skipping backend save for thread: {thread_id}")
            return
        
        backend_url = os.getenv("BACKEND_URL", "http://localhost:5000")
        
        # Save conversation
        conversation_data = {
            "threadID": thread_id,
            "messages": message_history
        }
        
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
