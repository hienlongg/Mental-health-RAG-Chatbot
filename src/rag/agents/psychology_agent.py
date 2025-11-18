"""Agent state and tool definitions."""

import logging
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from langchain.agents import AgentState
from langchain.tools import tool, ToolRuntime
from langgraph.types import Command
from langchain_core.messages import ToolMessage
import chainlit as cl

logger = logging.getLogger(__name__)


class PsychologyAgentState(AgentState):
    """
    State schema for the psychology chatbot agent.
    Extends AgentState with domain-specific fields.
    """
    user_id: str = ""
    score: str = ""
    content: str = ""
    total_guess: str = ""


def create_retrieve_context_tool(vector_store):
    """Create the retrieve_context tool with vector store binding."""
    
    @tool
    def retrieve_context(query: str) -> str:
        """
        Search DSM-5 psychology database for information matching the query.
        Use this to find relevant diagnostic criteria, symptoms, or treatments.
        """
        logger.info(f"🔍 [TOOL: retrieve_context] Query: '{query}'")
        
        try:
            retrieved_docs = vector_store.similarity_search(query, k=2)
            
            if retrieved_docs:
                serialized = "\n\n".join(
                    (f"Source: {doc.metadata}\nContent: {doc.page_content[:500]}")
                    for doc in retrieved_docs
                )
                logger.info(f"   ✓ Found {len(retrieved_docs)} documents")
                return f"Retrieved relevant information:\n\n{serialized}"
            else:
                logger.warning(f"   ⚠ No documents found for query: {query}")
                return f"No relevant information found for: {query}"
        except Exception as e:
            logger.error(f"   ✗ Error in retrieve_context: {e}")
            return f"Error retrieving information: {str(e)}"
    
    return retrieve_context


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
    logger.info(f"📊 [TOOL: update_diagnosis]")
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
