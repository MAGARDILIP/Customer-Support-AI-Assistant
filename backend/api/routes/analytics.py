"""
Analytics API Routes — Dashboard data endpoints.
"""
from fastapi import APIRouter, HTTPException
from backend.services.analytics_service import (
    get_analytics_overview,
    get_sentiment_distribution,
    get_conversations_over_time,
)

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/overview")
async def analytics_overview():
    """Get high-level analytics metrics for the dashboard."""
    try:
        return get_analytics_overview()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sentiment")
async def sentiment_data():
    """Get sentiment distribution data for charts."""
    try:
        return get_sentiment_distribution()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations")
async def conversations_data():
    """Get conversations over time data for charts."""
    try:
        return get_conversations_over_time()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
