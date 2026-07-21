# 🛍️ ShopEase AI Customer Support Assistant

An intelligent AI-powered customer support system for e-commerce, featuring multi-agent orchestration, RAG-based knowledge retrieval, and automated order management.

## 📋 Features

### Core Requirements
- ✅ **Upload PDF Policies & FAQs** — Process and embed company documents for AI retrieval
- ✅ **RAG-based Information Retrieval** — Semantic search across uploaded documents using ChromaDB
- ✅ **Chat History** — Persistent conversation history with session management

### Tools (AI Agent decides which to use)
- ✅ **Order Lookup API** — Search orders by number, email, or phone
- ✅ **Refund Eligibility Checker** — Automated refund rule validation (30-day window, status checks, digital product rules)
- ✅ **Knowledge Base Search** — RAG-powered document search
- ✅ **Sentiment Analyzer** — Customer mood detection and escalation triggers

### CrewAI Multi-Agent System
- ✅ **Research Agent** — Searches policies, FAQs, and knowledge base for answers
- ✅ **Customer Resolution Agent** — Handles order lookups, refunds, and transactions
- ✅ **Escalation Agent** — Manages frustrated customers with empathy and authority

### Advanced Features
- ✅ **Sentiment Analysis** — Detects angry/frustrated customers, auto-escalates
- ✅ **Multi-language Support** — Responds in the customer's language
- ✅ **Analytics Dashboard** — Plotly charts showing sentiment trends, agent usage, conversation metrics

## 🏗️ Architecture

```
Frontend (Streamlit) → FastAPI Backend → CrewAI Agents → GROQ LLM
                                       ↓
                            ┌─────────────────────┐
                            │  Tools:              │
                            │  • Order Lookup      │
                            │  • Refund Checker    │
                            │  • Knowledge Search  │
                            │  • Sentiment Analyzer│
                            └─────────────────────┘
                                       ↓
                            ┌─────────────────────┐
                            │  Data:               │
                            │  • ChromaDB (RAG)    │
                            │  • SQLite (Orders)   │
                            │  • SQLite (Chat)     │
                            └─────────────────────┘
```

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Streamlit |
| Backend | FastAPI |
| LLM | GROQ API (LLaMA 3.3 70B) |
| Agent Framework | CrewAI |
| Vector Database | ChromaDB |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Database | SQLite + SQLAlchemy |
| Sentiment | TextBlob |
| Charts | Plotly |

## 🚀 Setup & Installation

### Prerequisites
- Python 3.10+
- GROQ API Key

### Step 1: Clone & Install

```bash
cd Customer_Support_Ecommerce_ai_assistant

# Create virtual environment
python -m venv venv
venv\Scripts\activate     # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment

```bash
# Copy and edit the environment file
copy .env.example .env
# Edit .env with your GROQ API key
```

### Step 3: Run

```bash
# Start both servers with one command
python run.py
```

This starts:
- **FastAPI** backend at `http://localhost:8000`
- **Streamlit** frontend at `http://localhost:8501`

Or run separately:
```bash
# Terminal 1: Backend
uvicorn backend.main:app --reload --port 8000

# Terminal 2: Frontend
streamlit run frontend/app.py --server.port 8501
```

## 📖 API Documentation

Once the backend is running, visit: `http://localhost:8000/docs`

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat/` | Send message, get AI response |
| POST | `/api/documents/upload` | Upload PDF document |
| GET | `/api/orders/{order_number}` | Look up order details |
| POST | `/api/refunds/check` | Check refund eligibility |
| GET | `/api/analytics/overview` | Get analytics metrics |
| GET | `/api/health` | System health check |

## 🧪 Test Scenarios

| Scenario | Expected Behavior |
|----------|-------------------|
| "What is your return policy?" | Research Agent → RAG search → policy answer |
| "Where is my order ORD-1023?" | Resolution Agent → Order Lookup → status info |
| "I want a refund for ORD-1005" | Resolution Agent → Refund Checker → eligibility |
| "This is TERRIBLE service!" | Escalation Agent → empathetic response |
| "How long does shipping take?" | Research Agent → shipping policy → time details |

## 📂 Project Structure

```
├── backend/
│   ├── main.py              # FastAPI app
│   ├── config.py            # Environment config
│   ├── core/                # LLM client, embeddings, exceptions
│   ├── rag/                 # Document processing, ChromaDB, retrieval
│   ├── agents/              # CrewAI agents & crew orchestration
│   ├── tools/               # Order lookup, refund checker, etc.
│   ├── database/            # Models, connection, seed data, chat history
│   ├── services/            # Chat & analytics services
│   └── api/routes/          # FastAPI route handlers
├── frontend/
│   ├── app.py               # Streamlit main app
│   ├── pages/               # Chat, Upload, Analytics, Order Lookup
│   └── utils/               # API client
├── data/                    # Databases & PDFs (auto-generated)
├── run.py                   # Single entry point
└── requirements.txt
```

## 📝 License

This project is for internal company use.
