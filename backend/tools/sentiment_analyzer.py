"""
Sentiment Analyzer Tool — Detects customer sentiment for escalation.
"""
import logging
from textblob import TextBlob

logger = logging.getLogger(__name__)


def sentiment_analyzer_fn(text: str) -> str:
    """Analyze sentiment and return formatted result."""
    try:
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity

        if polarity <= -0.5:
            sentiment, emoji, escalation = "Very Negative", "😡", "HIGH — Immediate escalation"
        elif polarity <= -0.2:
            sentiment, emoji, escalation = "Negative", "😟", "MEDIUM — Monitor closely"
        elif polarity <= 0.1:
            sentiment, emoji, escalation = "Neutral", "😐", "LOW"
        elif polarity <= 0.5:
            sentiment, emoji, escalation = "Positive", "😊", "NONE"
        else:
            sentiment, emoji, escalation = "Very Positive", "😄", "NONE"

        return (
            f"Sentiment: {sentiment} {emoji}\n"
            f"Polarity: {polarity:.2f}\n"
            f"Subjectivity: {subjectivity:.2f}\n"
            f"Escalation Level: {escalation}"
        )

    except Exception as e:
        logger.error(f"Sentiment analysis failed: {e}")
        return "Sentiment: Neutral (analysis error)"


def get_sentiment_score(text: str) -> float:
    """Quick polarity score. Used by chat service."""
    try:
        return TextBlob(text).sentiment.polarity
    except Exception:
        return 0.0
