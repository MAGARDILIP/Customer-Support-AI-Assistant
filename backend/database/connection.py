"""
SQLite database connection manager using SQLAlchemy.
"""
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from backend.config import settings
from backend.database.models import Base

logger = logging.getLogger(__name__)

# --- E-commerce Database ---
_ecommerce_engine = None
_EcommerceSession = None

# --- Chat History Database ---
_chat_engine = None
_ChatSession = None


def get_ecommerce_engine():
    """Get or create the e-commerce database engine."""
    global _ecommerce_engine
    if _ecommerce_engine is None:
        _ecommerce_engine = create_engine(
            settings.sqlite_db_url,
            echo=False,
            connect_args={"check_same_thread": False},
        )
        logger.info(f"E-commerce DB engine created: {settings.sqlite_db_url}")
    return _ecommerce_engine


def get_chat_engine():
    """Get or create the chat history database engine."""
    global _chat_engine
    if _chat_engine is None:
        _chat_engine = create_engine(
            settings.chat_db_url,
            echo=False,
            connect_args={"check_same_thread": False},
        )
        logger.info(f"Chat DB engine created: {settings.chat_db_url}")
    return _chat_engine


def init_databases():
    """Create all tables in both databases."""
    from backend.database.models import Customer, Product, Order, Refund, ChatMessage

    ecommerce_engine = get_ecommerce_engine()
    chat_engine = get_chat_engine()

    # Create e-commerce tables
    Base.metadata.create_all(
        ecommerce_engine,
        tables=[
            Customer.__table__,
            Product.__table__,
            Order.__table__,
            Refund.__table__,
        ],
    )
    logger.info("E-commerce database tables created.")

    # Create chat tables
    Base.metadata.create_all(
        chat_engine,
        tables=[ChatMessage.__table__],
    )
    logger.info("Chat history database tables created.")


def get_ecommerce_session() -> Session:
    """Get a new e-commerce database session."""
    global _EcommerceSession
    if _EcommerceSession is None:
        _EcommerceSession = sessionmaker(bind=get_ecommerce_engine())
    return _EcommerceSession()


def get_chat_session() -> Session:
    """Get a new chat history database session."""
    global _ChatSession
    if _ChatSession is None:
        _ChatSession = sessionmaker(bind=get_chat_engine())
    return _ChatSession()
