"""
Analytics Dashboard Page — Visualize support metrics with Plotly charts.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from frontend.utils.api_client import get_analytics_overview, get_sentiment_data, get_conversations_data

st.set_page_config(page_title="Analytics - ShopEase Support", page_icon="📊", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    .stApp { font-family: 'Inter', sans-serif; }
    .analytics-header {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        color: white;
    }
    .analytics-header h2 { color: white !important; margin: 0; }
    .analytics-header p { color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="analytics-header">
    <h2>📊 Analytics Dashboard</h2>
    <p>Track conversation metrics, sentiment trends, and agent performance</p>
</div>
""", unsafe_allow_html=True)

# --- Load Data ---
overview = get_analytics_overview()

if "error" in overview:
    st.error(f"⚠️ Could not load analytics: {overview['error']}")
    st.info("Make sure the backend is running and you've had some conversations.")
    st.stop()

# --- Top Metrics ---
st.subheader("📈 Overview")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("💬 Total Conversations", overview.get("total_conversations", 0))
with col2:
    st.metric("📨 Total Messages", overview.get("total_messages", 0))
with col3:
    avg_sent = overview.get("avg_sentiment", 0)
    emoji = "😊" if avg_sent > 0.1 else "😐" if avg_sent > -0.1 else "😟"
    st.metric(f"💭 Avg Sentiment {emoji}", f"{avg_sent:.2f}")
with col4:
    pos_pct = overview.get("positive_pct", 0)
    st.metric("👍 Positive Rate", f"{pos_pct}%")

st.markdown("---")

# --- Charts Row 1 ---
if overview.get("total_messages", 0) > 0:
    col_left, col_right = st.columns(2)

    # Sentiment Distribution
    with col_left:
        st.subheader("😊 Sentiment Distribution")
        sent_data = get_sentiment_data()
        if sent_data and sent_data.get("labels") and "error" not in sent_data:
            colors = ["#e53e3e", "#ed8936", "#a0aec0", "#48bb78", "#38a169"]
            fig = go.Figure(data=[go.Pie(
                labels=sent_data["labels"],
                values=sent_data["values"],
                hole=0.45,
                marker_colors=colors,
                textinfo="label+percent",
                textfont_size=11,
            )])
            fig.update_layout(
                height=350,
                margin=dict(t=20, b=20, l=20, r=20),
                showlegend=False,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No sentiment data yet. Start chatting to see trends!")

    # Agent Usage
    with col_right:
        st.subheader("🤖 Agent Usage")
        agents = overview.get("agents_used", {})
        if agents:
            agent_colors = {
                "Research Agent": "#4299e1",
                "Resolution Agent": "#ecc94b",
                "Escalation Agent": "#fc8181",
                "Fallback Agent": "#a0aec0",
            }
            fig = go.Figure(data=[go.Bar(
                x=list(agents.keys()),
                y=list(agents.values()),
                marker_color=[agent_colors.get(a, "#667eea") for a in agents.keys()],
                text=list(agents.values()),
                textposition="auto",
            )])
            fig.update_layout(
                height=350,
                margin=dict(t=20, b=40, l=40, r=20),
                xaxis_title="Agent",
                yaxis_title="Queries Handled",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No agent data yet.")

    st.markdown("---")

    # --- Charts Row 2 ---
    col_left2, col_right2 = st.columns(2)

    # Conversations Over Time
    with col_left2:
        st.subheader("📅 Conversations Over Time")
        conv_data = get_conversations_data()
        if conv_data and conv_data.get("dates") and "error" not in conv_data:
            fig = go.Figure(data=[go.Scatter(
                x=conv_data["dates"],
                y=conv_data["counts"],
                mode="lines+markers",
                line=dict(color="#667eea", width=3),
                marker=dict(size=8, color="#764ba2"),
                fill="tozeroy",
                fillcolor="rgba(102,126,234,0.1)",
            )])
            fig.update_layout(
                height=300,
                margin=dict(t=20, b=40, l=40, r=20),
                xaxis_title="Date",
                yaxis_title="Conversations",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No time-series data yet.")

    # Tools Usage
    with col_right2:
        st.subheader("🔧 Tools Usage")
        tools = overview.get("tools_used", {})
        if tools:
            tool_colors = {
                "Order Lookup": "#48bb78",
                "Refund Eligibility Checker": "#ed8936",
                "Knowledge Base Search": "#4299e1",
                "Sentiment Analyzer": "#9f7aea",
            }
            fig = go.Figure(data=[go.Pie(
                labels=list(tools.keys()),
                values=list(tools.values()),
                hole=0.4,
                marker_colors=[tool_colors.get(t, "#667eea") for t in tools.keys()],
            )])
            fig.update_layout(
                height=300,
                margin=dict(t=20, b=20, l=20, r=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No tool usage data yet.")

    # --- Sentiment Breakdown ---
    st.markdown("---")
    st.subheader("📊 Sentiment Breakdown")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("😊 Positive", f"{overview.get('positive_pct', 0)}%")
    with col_b:
        st.metric("😐 Neutral", f"{overview.get('neutral_pct', 0)}%")
    with col_c:
        st.metric("😟 Negative", f"{overview.get('negative_pct', 0)}%")

else:
    st.info("📭 No conversation data yet. Start chatting with the AI to see analytics here!")
    st.markdown("""
    ### 🚀 Getting Started
    1. Go to the **💬 Chat** page
    2. Ask some questions (try different types: orders, policies, complaints)
    3. Come back here to see the metrics update
    """)
