"""
RAG Retriever — high-level interface for querying the knowledge base.
"""
import logging
from backend.rag.vector_store import search

logger = logging.getLogger(__name__)


def retrieve(query: str, top_k: int = 5, relevance_threshold: float = 1.5) -> list[dict]:
    """
    Retrieve relevant document chunks for a query.

    Args:
        query: User's question or search query.
        top_k: Maximum number of results.
        relevance_threshold: Maximum distance score to include (lower = more relevant).

    Returns:
        List of relevant chunks with text and metadata.
    """
    results = search(query, top_k=top_k)

    # Filter by relevance threshold (ChromaDB returns L2 distance, lower = better)
    filtered = [
        r for r in results
        if r.get("distance") is not None and r["distance"] <= relevance_threshold
    ]

    if not filtered and results:
        # If all results are above threshold, return top result anyway
        filtered = results[:1]
        logger.info("All results above threshold, returning top result as fallback.")

    return filtered


def format_context(chunks: list[dict]) -> str:
    """
    Format retrieved chunks into a context string for the LLM.

    Returns a formatted string with source attribution.
    """
    if not chunks:
        return "No relevant information found in the knowledge base."

    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        source = chunk.get("metadata", {}).get("source", "Unknown")
        text = chunk.get("text", "")
        context_parts.append(f"[Source: {source}]\n{text}")

    return "\n\n---\n\n".join(context_parts)


def search_knowledge_base(query: str) -> str:
    """
    High-level function: search and return formatted context.
    Used by CrewAI tools.
    """
    chunks = retrieve(query)
    if not chunks:
        return "No relevant information found in the uploaded documents."
    return format_context(chunks)
