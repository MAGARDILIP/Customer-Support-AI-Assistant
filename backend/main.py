"""
FastAPI Application — Main entry point for the backend server.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import settings
from backend.database.connection import init_databases
from backend.database.seed import seed_database
from backend.api.routes import chat, documents, orders, refunds, analytics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    # --- Startup ---
    logger.info("=" * 60)
    logger.info("Starting ShopEase AI Customer Support Backend")
    logger.info("=" * 60)

    # Initialize databases
    logger.info("Initializing databases...")
    init_databases()

    # Seed mock data
    logger.info("Seeding mock e-commerce data...")
    seed_database()

    # Generate sample PDFs
    logger.info("Generating sample policy PDFs...")
    try:
        from backend.rag.generate_sample_pdfs import generate_all_sample_pdfs
        generate_all_sample_pdfs()
    except Exception as e:
        logger.warning(f"Could not generate sample PDFs: {e}")

    # Pre-load and index sample PDFs into ChromaDB
    logger.info("Indexing sample PDFs into knowledge base...")
    try:
        _index_sample_pdfs()
    except Exception as e:
        logger.warning(f"Could not index sample PDFs: {e}")

    logger.info("Backend server ready!")
    logger.info(f"API docs: http://localhost:{settings.BACKEND_PORT}/docs")

    yield

    # --- Shutdown ---
    logger.info("Shutting down backend server.")


def _index_sample_pdfs():
    """Index the sample PDFs into ChromaDB if not already done."""
    import os
    from pathlib import Path
    from backend.rag.document_processor import get_document_processor
    from backend.rag.vector_store import add_documents, get_stats

    stats = get_stats()
    if stats["total_chunks"] > 0:
        logger.info(f"Knowledge base already has {stats['total_chunks']} chunks. Skipping indexing.")
        return

    sample_dir = Path(__file__).parent.parent / "data" / "sample_pdfs"
    if not sample_dir.exists():
        logger.warning(f"Sample PDFs directory not found: {sample_dir}")
        return

    processor = get_document_processor()
    for pdf_file in sample_dir.glob("*.pdf"):
        doc_id = f"sample_{pdf_file.stem}"
        chunks = processor.process_pdf(str(pdf_file))
        if chunks:
            add_documents(chunks, doc_id)
            logger.info(f"Indexed {len(chunks)} chunks from {pdf_file.name}")


# Create FastAPI app
app = FastAPI(
    title="ShopEase AI Customer Support API",
    description=(
        "AI-powered customer support backend with RAG, multi-agent system, "
        "order management, and analytics."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware (allow Streamlit frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(chat.router)
app.include_router(documents.router)
app.include_router(orders.router)
app.include_router(refunds.router)
app.include_router(analytics.router)


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "service": "ShopEase AI Customer Support",
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/api/health", tags=["Health"])
async def health_check():
    """Detailed health check."""
    from backend.rag.vector_store import get_stats
    from backend.database.connection import get_ecommerce_session
    from backend.database.models import Order

    # Check database
    try:
        session = get_ecommerce_session()
        order_count = session.query(Order).count()
        session.close()
        db_status = "healthy"
    except Exception:
        order_count = 0
        db_status = "unhealthy"

    # Check vector store
    try:
        vs_stats = get_stats()
        vs_status = "healthy"
    except Exception:
        vs_stats = {"total_chunks": 0}
        vs_status = "unhealthy"

    return {
        "status": "healthy" if db_status == "healthy" and vs_status == "healthy" else "degraded",
        "database": {"status": db_status, "orders": order_count},
        "vector_store": {"status": vs_status, **vs_stats},
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal error occurred. Please try again."},
    )
