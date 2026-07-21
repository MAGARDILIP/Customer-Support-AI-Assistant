"""
Chat Page — Main AI-powered customer support chat interface.
"""
import streamlit as st
import uuid
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from frontend.utils.api_client import send_message, get_chat_history, get_sessions

st.set_page_config(page_title="Chat - ShopEase Support", page_icon="💬", layout="wide")

# --- Custom CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    .stApp { font-family: 'Inter', sans-serif; }

    .chat-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        color: white;
    }
    .chat-header h2 { color: white !important; margin: 0; }
    .chat-header p { color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem; }

    .agent-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 10px;
        font-size: 0.72rem;
        font-weight: 600;
    }
    .badge-research { background: #ebf8ff; color: #2b6cb0; }
    .badge-resolution { background: #fefcbf; color: #975a16; }
    .badge-escalation { background: #fed7d7; color: #c53030; }
    .badge-fallback { background: #e2e8f0; color: #4a5568; }

    .sentiment-indicator {
        font-size: 0.8rem;
        padding: 2px 8px;
        border-radius: 8px;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
<div class="chat-header">
    <h2>💬 AI Customer Support Chat</h2>
    <p>Ask about orders, refunds, shipping, policies, or anything else!</p>
</div>
""", unsafe_allow_html=True)

# --- Session State ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]
if "messages" not in st.session_state:
    st.session_state.messages = []
if "processing" not in st.session_state:
    st.session_state.processing = False

# --- Sidebar ---
with st.sidebar:
    st.markdown("### 💬 Chat Sessions")
    st.markdown(f"**Current Session:** `{st.session_state.session_id}`")

    if st.button("🆕 New Conversation", use_container_width=True):
        st.session_state.session_id = str(uuid.uuid4())[:8]
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")

    # Quick prompts
    st.markdown("### 💡 Try These Prompts")
    quick_prompts = [
        "What is your return policy?",
        "Where is my order ORD-1023?",
        "I want a refund for order ORD-1005",
        "This service is terrible! Nothing works!",
        "How long does shipping take?",
        "What payment methods do you accept?",
    ]
    for prompt in quick_prompts:
        if st.button(f"📝 {prompt}", key=f"qp_{prompt[:20]}", use_container_width=True):
            st.session_state.pending_prompt = prompt
            st.rerun()

    st.markdown("---")

    # Session history
    st.markdown("### 📋 Past Sessions")
    sessions_data = get_sessions()
    if sessions_data and "sessions" in sessions_data:
        for sess in sessions_data["sessions"][:5]:
            sid = sess["session_id"]
            count = sess["message_count"]
            if st.button(f"📂 {sid} ({count} msgs)", key=f"sess_{sid}", use_container_width=True):
                st.session_state.session_id = sid
                # Load history
                hist = get_chat_history(sid)
                if hist and "messages" in hist:
                    st.session_state.messages = [
                        {
                            "role": m["role"],
                            "content": m["content"],
                            "agent_used": m.get("agent_used"),
                            "tools_used": m.get("tools_used"),
                            "sentiment_score": m.get("sentiment_score"),
                        }
                        for m in hist["messages"]
                    ]
                st.rerun()


def get_agent_badge(agent: str) -> str:
    """Get HTML badge for agent type."""
    if not agent:
        return ""
    agent_lower = agent.lower()
    if "research" in agent_lower:
        return f'<span class="agent-badge badge-research">🔍 {agent}</span>'
    elif "resolution" in agent_lower:
        return f'<span class="agent-badge badge-resolution">🔧 {agent}</span>'
    elif "escalation" in agent_lower:
        return f'<span class="agent-badge badge-escalation">🚨 {agent}</span>'
    else:
        return f'<span class="agent-badge badge-fallback">🤖 {agent}</span>'


def get_sentiment_emoji(score: float | None) -> str:
    """Get emoji for sentiment score."""
    if score is None:
        return ""
    if score <= -0.5:
        return "😡"
    elif score <= -0.2:
        return "😟"
    elif score <= 0.1:
        return "😐"
    elif score <= 0.5:
        return "😊"
    else:
        return "😄"


# --- Display Messages ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧑" if msg["role"] == "user" else "🤖"):
        st.markdown(msg["content"])

        # Show metadata for assistant messages
        if msg["role"] == "assistant":
            meta_parts = []
            agent = msg.get("agent_used")
            tools = msg.get("tools_used")
            sentiment = msg.get("sentiment_score")

            if agent:
                meta_parts.append(f"**Agent:** {agent}")
            if tools:
                meta_parts.append(f"**Tools:** {', '.join(tools)}")
            if sentiment is not None:
                meta_parts.append(f"**Sentiment:** {get_sentiment_emoji(sentiment)} ({sentiment:.2f})")

            if meta_parts:
                with st.expander("ℹ️ Response Details"):
                    st.markdown(" | ".join(meta_parts))


# --- Handle pending quick prompt ---
if "pending_prompt" in st.session_state:
    prompt = st.session_state.pending_prompt
    del st.session_state.pending_prompt

    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)

    # Get AI response
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("🧠 AI is thinking..."):
            result = send_message(st.session_state.session_id, prompt)

        if "error" in result:
            st.error(f"❌ {result['error']}")
        else:
            response = result.get("response", "Sorry, I could not generate a response.")
            st.markdown(response)

            agent = result.get("agent_used", "")
            tools = result.get("tools_used", [])
            sentiment = result.get("sentiment_score")

            meta_parts = []
            if agent:
                meta_parts.append(f"**Agent:** {agent}")
            if tools:
                meta_parts.append(f"**Tools:** {', '.join(tools)}")
            if sentiment is not None:
                meta_parts.append(f"**Sentiment:** {get_sentiment_emoji(sentiment)} ({sentiment:.2f})")
            if meta_parts:
                with st.expander("ℹ️ Response Details"):
                    st.markdown(" | ".join(meta_parts))

            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "agent_used": agent,
                "tools_used": tools,
                "sentiment_score": sentiment,
            })


# --- Chat Input ---
if prompt := st.chat_input("Ask me anything about your order, policies, refunds..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)

    # Get AI response
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("🧠 AI is thinking..."):
            result = send_message(st.session_state.session_id, prompt)

        if "error" in result:
            st.error(f"❌ {result['error']}")
        else:
            response = result.get("response", "Sorry, I could not generate a response.")
            st.markdown(response)

            agent = result.get("agent_used", "")
            tools = result.get("tools_used", [])
            sentiment = result.get("sentiment_score")

            meta_parts = []
            if agent:
                meta_parts.append(f"**Agent:** {agent}")
            if tools:
                meta_parts.append(f"**Tools:** {', '.join(tools)}")
            if sentiment is not None:
                meta_parts.append(f"**Sentiment:** {get_sentiment_emoji(sentiment)} ({sentiment:.2f})")
            if meta_parts:
                with st.expander("ℹ️ Response Details"):
                    st.markdown(" | ".join(meta_parts))

            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "agent_used": agent,
                "tools_used": tools,
                "sentiment_score": sentiment,
            })
