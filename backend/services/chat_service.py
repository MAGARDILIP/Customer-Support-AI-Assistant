"""
Chat Service — Orchestrates the full chat flow:
receive message → sentiment → agent routing → save history → return response.
"""
import logging
import uuid
from backend.database.chat_history import (
    save_message, get_recent_context, get_history, get_all_sessions, clear_session
)
from backend.agents.crew import run_crew
from backend.tools.sentiment_analyzer import get_sentiment_score

logger = logging.getLogger(__name__)


def process_message(session_id: str, message: str) -> dict:
    """
    Process a customer message through the full pipeline.

    Args:
        session_id: Unique session identifier.
        message: Customer's message text.

    Returns:
        dict with: response, agent_used, tools_used, sentiment_score, session_id
    """
    # Generate session ID if not provided
    if not session_id:
        session_id = str(uuid.uuid4())[:8]

    logger.info(f"Processing message for session {session_id}: {message[:100]}...")

    # Step 1: Save user message
    save_message(
        session_id=session_id,
        role="user",
        content=message,
    )

    # Step 2: Analyze sentiment
    sentiment_score = get_sentiment_score(message)
    logger.info(f"Sentiment score: {sentiment_score:.2f}")

    # Step 3: Get recent chat history for context
    chat_history = get_recent_context(session_id, limit=10)

    # Step 4: Run CrewAI crew
    result = run_crew(
        message=message,
        chat_history=chat_history,
        sentiment_score=sentiment_score,
    )

    # Step 5: Save assistant response
    save_message(
        session_id=session_id,
        role="assistant",
        content=result["response"],
        agent_used=result.get("agent_used"),
        tools_used=result.get("tools_used"),
        sentiment_score=sentiment_score,
    )

    # Step 6: Return response
    return {
        "response": result["response"],
        "session_id": session_id,
        "agent_used": result.get("agent_used", "Unknown"),
        "tools_used": result.get("tools_used", []),
        "sentiment_score": sentiment_score,
        "intent": result.get("intent", "unknown"),
    }


def get_chat_history(session_id: str, limit: int = 50) -> list[dict]:
    """Get full chat history for a session."""
    return get_history(session_id, limit)


def list_sessions() -> list[dict]:
    """List all chat sessions."""
    return get_all_sessions()


def delete_session(session_id: str) -> int:
    """Clear a chat session."""
    return clear_session(session_id)
