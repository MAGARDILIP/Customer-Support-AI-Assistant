"""
Streamlit API Client — Wrapper for all FastAPI backend calls.
"""
import requests
import logging

logger = logging.getLogger(__name__)

BACKEND_URL = "http://localhost:8000"


def _handle_response(response: requests.Response) -> dict:
    """Handle API response and raise errors."""
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        logger.error(f"API error: {e}")
        try:
            detail = response.json().get("detail", str(e))
        except Exception:
            detail = str(e)
        return {"error": detail}
    except Exception as e:
        logger.error(f"Request failed: {e}")
        return {"error": str(e)}


# === Chat ===

def send_message(session_id: str, message: str) -> dict:
    """Send a chat message and get AI response."""
    try:
        resp = requests.post(
            f"{BACKEND_URL}/api/chat/",
            json={"session_id": session_id, "message": message},
            timeout=120,
        )
        return _handle_response(resp)
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to backend. Make sure the FastAPI server is running on port 8000."}
    except Exception as e:
        return {"error": str(e)}


def get_chat_history(session_id: str) -> dict:
    """Get chat history for a session."""
    try:
        resp = requests.get(f"{BACKEND_URL}/api/chat/history/{session_id}", timeout=10)
        return _handle_response(resp)
    except Exception as e:
        return {"error": str(e)}


def get_sessions() -> dict:
    """List all chat sessions."""
    try:
        resp = requests.get(f"{BACKEND_URL}/api/chat/sessions", timeout=10)
        return _handle_response(resp)
    except Exception as e:
        return {"error": str(e)}


def delete_session(session_id: str) -> dict:
    """Delete a chat session."""
    try:
        resp = requests.delete(f"{BACKEND_URL}/api/chat/sessions/{session_id}", timeout=10)
        return _handle_response(resp)
    except Exception as e:
        return {"error": str(e)}


# === Documents ===

def upload_document(file_bytes: bytes, filename: str) -> dict:
    """Upload a PDF document."""
    try:
        files = {"file": (filename, file_bytes, "application/pdf")}
        resp = requests.post(f"{BACKEND_URL}/api/documents/upload", files=files, timeout=120)
        return _handle_response(resp)
    except Exception as e:
        return {"error": str(e)}


def list_documents() -> dict:
    """List all uploaded documents."""
    try:
        resp = requests.get(f"{BACKEND_URL}/api/documents/", timeout=10)
        return _handle_response(resp)
    except Exception as e:
        return {"error": str(e)}


def delete_document(doc_id: str) -> dict:
    """Delete a document."""
    try:
        resp = requests.delete(f"{BACKEND_URL}/api/documents/{doc_id}", timeout=10)
        return _handle_response(resp)
    except Exception as e:
        return {"error": str(e)}


# === Orders ===

def lookup_order(order_number: str) -> dict:
    """Look up an order by number."""
    try:
        resp = requests.get(f"{BACKEND_URL}/api/orders/{order_number.upper()}", timeout=10)
        return _handle_response(resp)
    except Exception as e:
        return {"error": str(e)}


def search_orders_by_email(email: str) -> dict:
    """Search orders by email."""
    try:
        resp = requests.get(f"{BACKEND_URL}/api/orders/search/by-email", params={"email": email}, timeout=10)
        return _handle_response(resp)
    except Exception as e:
        return {"error": str(e)}


def check_refund(order_number: str) -> dict:
    """Check refund eligibility."""
    try:
        resp = requests.post(
            f"{BACKEND_URL}/api/refunds/check",
            json={"order_number": order_number.upper()},
            timeout=10,
        )
        return _handle_response(resp)
    except Exception as e:
        return {"error": str(e)}


# === Analytics ===

def get_analytics_overview() -> dict:
    """Get analytics overview."""
    try:
        resp = requests.get(f"{BACKEND_URL}/api/analytics/overview", timeout=10)
        return _handle_response(resp)
    except Exception as e:
        return {"error": str(e)}


def get_sentiment_data() -> dict:
    """Get sentiment distribution."""
    try:
        resp = requests.get(f"{BACKEND_URL}/api/analytics/sentiment", timeout=10)
        return _handle_response(resp)
    except Exception as e:
        return {"error": str(e)}


def get_conversations_data() -> dict:
    """Get conversations over time."""
    try:
        resp = requests.get(f"{BACKEND_URL}/api/analytics/conversations", timeout=10)
        return _handle_response(resp)
    except Exception as e:
        return {"error": str(e)}


def health_check() -> dict:
    """Check backend health."""
    try:
        resp = requests.get(f"{BACKEND_URL}/api/health", timeout=5)
        return _handle_response(resp)
    except requests.exceptions.ConnectionError:
        return {"error": "Backend not reachable", "status": "offline"}
    except Exception as e:
        return {"error": str(e), "status": "error"}
