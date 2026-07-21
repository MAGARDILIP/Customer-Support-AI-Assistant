"""
Chat history CRUD operations.
"""
import logging
from datetime import datetime
from sqlalchemy import desc
from backend.database.connection import get_chat_session
from backend.database.models import ChatMessage

logger = logging.getLogger(__name__)


def save_message(
    session_id: str,
    role: str,
    content: str,
    agent_used: str | None = None,
    tools_used: list | None = None,
    sentiment_score: float | None = None,
    language: str | None = None,
) -> ChatMessage:
    """Save a chat message to the database."""
    session = get_chat_session()
    try:
        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            timestamp=datetime.utcnow(),
            agent_used=agent_used,
            tools_used=tools_used,
            sentiment_score=sentiment_score,
            language=language,
        )
        session.add(message)
        session.commit()
        session.refresh(message)
        return message
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to save message: {e}")
        raise
    finally:
        session.close()


def get_history(session_id: str, limit: int = 50) -> list[dict]:
    """Get chat history for a session, ordered by timestamp."""
    session = get_chat_session()
    try:
        messages = (
            session.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.timestamp.asc())
            .limit(limit)
            .all()
        )
        return [msg.to_dict() for msg in messages]
    finally:
        session.close()


def get_recent_context(session_id: str, limit: int = 10) -> list[dict]:
    """Get the most recent messages for LLM context."""
    session = get_chat_session()
    try:
        messages = (
            session.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.timestamp.desc())
            .limit(limit)
            .all()
        )
        # Reverse to get chronological order
        messages.reverse()
        return [{"role": msg.role, "content": msg.content} for msg in messages]
    finally:
        session.close()


def get_all_sessions() -> list[dict]:
    """Get a summary of all chat sessions."""
    session = get_chat_session()
    try:
        from sqlalchemy import func

        results = (
            session.query(
                ChatMessage.session_id,
                func.count(ChatMessage.id).label("message_count"),
                func.min(ChatMessage.timestamp).label("started_at"),
                func.max(ChatMessage.timestamp).label("last_message_at"),
            )
            .group_by(ChatMessage.session_id)
            .order_by(desc("last_message_at"))
            .all()
        )
        return [
            {
                "session_id": r.session_id,
                "message_count": r.message_count,
                "started_at": r.started_at.isoformat() if r.started_at else None,
                "last_message_at": r.last_message_at.isoformat() if r.last_message_at else None,
            }
            for r in results
        ]
    finally:
        session.close()


def clear_session(session_id: str) -> int:
    """Delete all messages for a session. Returns count deleted."""
    session = get_chat_session()
    try:
        count = (
            session.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .delete()
        )
        session.commit()
        return count
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to clear session: {e}")
        raise
    finally:
        session.close()


def get_all_messages_for_analytics() -> list[dict]:
    """Get all messages across all sessions for analytics."""
    session = get_chat_session()
    try:
        messages = session.query(ChatMessage).order_by(ChatMessage.timestamp.asc()).all()
        return [msg.to_dict() for msg in messages]
    finally:
        session.close()
