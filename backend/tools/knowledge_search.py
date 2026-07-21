"""
Knowledge Base Search Tool — RAG-powered document search.
"""
import logging
from backend.rag.vector_store import search

logger = logging.getLogger(__name__)


def knowledge_search_fn(query: str) -> str:
    """
    Search the knowledge base for relevant policy/FAQ information.
    Uses semantic similarity search over embedded documents.
    """
    try:
        results = search(query, top_k=3, min_score=0.3)

        if not results:
            return "No relevant information found in the knowledge base."

        output = "Relevant information found:\n\n"
        for i, r in enumerate(results, 1):
            output += f"[Source: {r['source']}] (relevance: {r['score']:.2f})\n"
            output += f"{r['text']}\n\n"

        return output

    except Exception as e:
        logger.error(f"Knowledge search failed: {e}")
        return f"Knowledge base search error: {str(e)}"
