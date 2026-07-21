"""
Chat API Routes — Main conversation endpoints.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services.chat_service import (
    process_message, get_chat_history, list_sessions, delete_session
)

router = APIRouter(prefix="/api/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    """Request body for chat endpoint."""
    session_id: str = ""
    message: str


class ChatResponse(BaseModel):
    """Response body for chat endpoint."""
    response: str
    session_id: str
    agent_used: str
    tools_used: list[str]
    sentiment_score: float
    intent: str


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message and get an AI-powered customer support response.
    The system automatically routes to the appropriate agent based on intent.
    """
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        result = process_message(
            session_id=request.session_id,
            message=request.message,
        )
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


@router.get("/sessions")
async def get_sessions():
    """List all chat sessions with metadata."""
    try:
        sessions = list_sessions()
        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{session_id}")
async def get_session_history(session_id: str, limit: int = 50):
    """Get full chat history for a specific session."""
    try:
        history = get_chat_history(session_id, limit)
        return {"session_id": session_id, "messages": history, "count": len(history)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/sessions/{session_id}")
async def delete_chat_session(session_id: str):
    """Delete a chat session and all its messages."""
    try:
        count = delete_session(session_id)
        return {"message": f"Deleted {count} messages from session {session_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
