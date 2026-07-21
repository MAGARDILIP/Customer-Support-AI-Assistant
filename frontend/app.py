"""
ShopEase AI Customer Support Assistant — Main Streamlit App
"""
import streamlit as st

# --- Page Config ---
st.set_page_config(
    page_title="ShopEase AI Support",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom CSS for premium look ---
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global Styles */
    .stApp {
        font-family: 'Inter', sans-serif;
    }

    /* Header Styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    .main-header h1 {
        color: white !important;
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
    }
    .main-header p {
        color: rgba(255,255,255,0.85);
        font-size: 1.05rem;
        margin: 0;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    [data-testid="stSidebar"] .stMarkdown {
        color: #e0e0e0;
    }

    /* Card Style */
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e0e5ec;
        text-align: center;
        transition: transform 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #2d3748;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #718096;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Status badges */
    .badge-online {
        background: #48bb78;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .badge-offline {
        background: #f56565;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    /* Agent tag */
    .agent-tag {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 5px;
    }
    .agent-research { background: #ebf8ff; color: #2b6cb0; }
    .agent-resolution { background: #fefcbf; color: #975a16; }
    .agent-escalation { background: #fed7d7; color: #c53030; }

    /* Footer */
    .footer {
        text-align: center;
        padding: 1rem;
        color: #a0aec0;
        font-size: 0.8rem;
        margin-top: 3rem;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# --- Main Page ---
st.markdown("""
<div class="main-header">
    <h1>🛍️ ShopEase AI Customer Support</h1>
    <p>Powered by AI Agents • RAG Knowledge Base • Smart Routing</p>
</div>
""", unsafe_allow_html=True)


# --- Feature Cards ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="metric-card">
        <div style="font-size: 2.5rem;">💬</div>
        <div class="metric-value" style="font-size: 1.2rem;">Chat Support</div>
        <div class="metric-label">AI-powered conversations</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <div style="font-size: 2.5rem;">📄</div>
        <div class="metric-value" style="font-size: 1.2rem;">Knowledge Base</div>
        <div class="metric-label">Upload PDFs & FAQs</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <div style="font-size: 2.5rem;">📊</div>
        <div class="metric-value" style="font-size: 1.2rem;">Analytics</div>
        <div class="metric-label">Insights & metrics</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="metric-card">
        <div style="font-size: 2.5rem;">🔍</div>
        <div class="metric-value" style="font-size: 1.2rem;">Order Lookup</div>
        <div class="metric-label">Track & manage orders</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- System Status ---
st.subheader("🏥 System Status")

try:
    from frontend.utils.api_client import health_check
    health = health_check()
    if "error" in health:
        st.error(f"⚠️ Backend is offline. Please start the FastAPI server first.")
        st.code("python run.py", language="bash")
    else:
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            status = health.get("status", "unknown")
            color = "🟢" if status == "healthy" else "🟡"
            st.metric("Backend Status", f"{color} {status.title()}")
        with col_b:
            db_info = health.get("database", {})
            st.metric("Database Orders", db_info.get("orders", 0))
        with col_c:
            vs_info = health.get("vector_store", {})
            st.metric("Knowledge Chunks", vs_info.get("total_chunks", 0))
except Exception:
    st.warning("Could not connect to backend. Make sure it's running.")

st.markdown("---")

# --- How It Works ---
st.subheader("🧠 How It Works")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 🤖 Multi-Agent System")
    st.markdown("""
    - **Research Agent** — Searches policies & FAQs
    - **Resolution Agent** — Handles orders & refunds
    - **Escalation Agent** — Manages frustrated customers
    """)

with col2:
    st.markdown("#### 🔧 Smart Tools")
    st.markdown("""
    - **Order Lookup API** — Find orders by ID/email
    - **Refund Checker** — Verify refund eligibility
    - **Knowledge Search** — RAG-powered doc search
    - **Sentiment Analyzer** — Detect customer mood
    """)

with col3:
    st.markdown("#### ⚡ Intelligent Routing")
    st.markdown("""
    - Analyzes customer intent automatically
    - Routes to the best agent for each query
    - Uses tools as needed — the AI decides
    - Maintains full conversation history
    """)

# --- Sidebar ---
with st.sidebar:
    st.markdown("### 🛍️ ShopEase Support")
    st.markdown("---")
    st.markdown("#### 📌 Navigation")
    st.markdown("""
    - **💬 Chat** — Talk to the AI assistant
    - **📄 Upload Documents** — Add policy PDFs
    - **📊 Analytics** — View insights
    - **🔍 Order Lookup** — Search orders
    """)
    st.markdown("---")
    st.markdown("#### 🛠️ Tech Stack")
    st.markdown("""
    - 🎯 **Frontend**: Streamlit
    - ⚡ **Backend**: FastAPI
    - 🧠 **LLM**: GROQ API
    - 🤖 **Agents**: CrewAI
    - 📚 **RAG**: ChromaDB
    - 🗃️ **Database**: SQLite
    """)

st.markdown("""
<div class="footer">
    ShopEase AI Customer Support v1.0 • Powered by CrewAI, GROQ & RAG
</div>
""", unsafe_allow_html=True)
