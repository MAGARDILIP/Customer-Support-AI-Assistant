"""
Analytics Service — Aggregates chat data for the dashboard.
"""
import logging
from collections import Counter
from datetime import datetime, timedelta
from backend.database.chat_history import get_all_messages_for_analytics

logger = logging.getLogger(__name__)


def get_analytics_overview() -> dict:
    """Get high-level analytics metrics."""
    messages = get_all_messages_for_analytics()

    if not messages:
        return {
            "total_conversations": 0,
            "total_messages": 0,
            "avg_sentiment": 0.0,
            "positive_pct": 0,
            "negative_pct": 0,
            "neutral_pct": 0,
            "agents_used": {},
            "top_intents": {},
        }

    # Unique sessions
    sessions = set(m["session_id"] for m in messages)

    # User messages only
    user_messages = [m for m in messages if m["role"] == "user"]
    assistant_messages = [m for m in messages if m["role"] == "assistant"]

    # Sentiment analysis
    sentiments = [m["sentiment_score"] for m in assistant_messages if m.get("sentiment_score") is not None]
    avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.0

    positive = sum(1 for s in sentiments if s > 0.1)
    negative = sum(1 for s in sentiments if s < -0.1)
    neutral = len(sentiments) - positive - negative
    total_s = len(sentiments) or 1

    # Agent usage
    agents = [m["agent_used"] for m in assistant_messages if m.get("agent_used")]
    agent_counts = dict(Counter(agents))

    # Tools usage
    all_tools = []
    for m in assistant_messages:
        if m.get("tools_used"):
            all_tools.extend(m["tools_used"])
    tool_counts = dict(Counter(all_tools))

    return {
        "total_conversations": len(sessions),
        "total_messages": len(messages),
        "user_messages": len(user_messages),
        "assistant_messages": len(assistant_messages),
        "avg_sentiment": round(avg_sentiment, 3),
        "positive_pct": round(positive / total_s * 100, 1),
        "negative_pct": round(negative / total_s * 100, 1),
        "neutral_pct": round(neutral / total_s * 100, 1),
        "agents_used": agent_counts,
        "tools_used": tool_counts,
    }


def get_sentiment_distribution() -> dict:
    """Get sentiment distribution data for charts."""
    messages = get_all_messages_for_analytics()
    sentiments = [m["sentiment_score"] for m in messages if m.get("sentiment_score") is not None]

    if not sentiments:
        return {"labels": [], "values": []}

    bins = {
        "Very Negative (-1 to -0.5)": 0,
        "Negative (-0.5 to -0.1)": 0,
        "Neutral (-0.1 to 0.1)": 0,
        "Positive (0.1 to 0.5)": 0,
        "Very Positive (0.5 to 1)": 0,
    }

    for s in sentiments:
        if s <= -0.5:
            bins["Very Negative (-1 to -0.5)"] += 1
        elif s <= -0.1:
            bins["Negative (-0.5 to -0.1)"] += 1
        elif s <= 0.1:
            bins["Neutral (-0.1 to 0.1)"] += 1
        elif s <= 0.5:
            bins["Positive (0.1 to 0.5)"] += 1
        else:
            bins["Very Positive (0.5 to 1)"] += 1

    return {"labels": list(bins.keys()), "values": list(bins.values())}


def get_conversations_over_time() -> dict:
    """Get conversation counts per day for the last 30 days."""
    messages = get_all_messages_for_analytics()
    if not messages:
        return {"dates": [], "counts": []}

    # Count unique sessions per day
    day_sessions = {}
    for m in messages:
        if m.get("timestamp"):
            try:
                dt = datetime.fromisoformat(m["timestamp"])
                day_key = dt.strftime("%Y-%m-%d")
                if day_key not in day_sessions:
                    day_sessions[day_key] = set()
                day_sessions[day_key].add(m["session_id"])
            except (ValueError, TypeError):
                pass

    sorted_days = sorted(day_sessions.keys())
    return {
        "dates": sorted_days,
        "counts": [len(day_sessions[d]) for d in sorted_days],
    }
