"""
Lightweight Vector Store — Pure Python, JSON persistence, TF-IDF search.
No external vector DB or ML libraries needed.
"""
import json
import logging
import uuid
from pathlib import Path
from backend.config import settings, PROJECT_ROOT
from backend.core.embeddings import tokenize, cosine_similarity, get_query_vector, compute_tfidf

logger = logging.getLogger(__name__)

STORE_DIR = PROJECT_ROOT / "data"
STORE_FILE = STORE_DIR / "vector_store.json"

_documents: list[dict] = []
_idf: dict = {}
_initialized = False


def _ensure_dir():
    STORE_DIR.mkdir(parents=True, exist_ok=True)


def _load_store():
    global _documents, _idf, _initialized
    if _initialized:
        return
    _ensure_dir()
    if STORE_FILE.exists():
        try:
            with open(STORE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            _documents = data.get("documents", [])
            _idf = data.get("idf", {})
            logger.info(f"Loaded {len(_documents)} chunks from vector store.")
        except Exception as e:
            logger.error(f"Failed to load vector store: {e}")
            _documents = []
            _idf = {}
    _initialized = True


def _save_store():
    _ensure_dir()
    try:
        with open(STORE_FILE, "w", encoding="utf-8") as f:
            json.dump({"documents": _documents, "idf": _idf}, f)
    except Exception as e:
        logger.error(f"Failed to save vector store: {e}")


def _rebuild_index():
    """Rebuild TF-IDF index from all documents."""
    global _idf
    texts = [d["text"] for d in _documents]
    vectors, _idf = compute_tfidf(texts)
    for doc, vec in zip(_documents, vectors):
        doc["vector"] = vec


def add_documents(chunks: list[dict], doc_id: str) -> int:
    _load_store()
    for chunk in chunks:
        _documents.append({
            "id": f"{doc_id}_{uuid.uuid4().hex[:6]}",
            "doc_id": doc_id,
            "text": chunk["text"],
            "source": chunk.get("source", "unknown"),
            "metadata": chunk.get("metadata", {}),
            "vector": {},
        })
    _rebuild_index()
    _save_store()
    logger.info(f"Added {len(chunks)} chunks for '{doc_id}'.")
    return len(chunks)


def search(query: str, top_k: int = 5, min_score: float = 0.1) -> list[dict]:
    _load_store()
    if not _documents:
        return []

    if not _idf:
        _rebuild_index()

    query_vec = get_query_vector(query, _idf)
    results = []
    for doc in _documents:
        vec = doc.get("vector", {})
        score = cosine_similarity(query_vec, vec)
        if score >= min_score:
            results.append({
                "text": doc["text"],
                "source": doc["source"],
                "score": round(score, 3),
                "doc_id": doc["doc_id"],
            })
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]


def delete_document(doc_id: str) -> int:
    _load_store()
    before = len(_documents)
    _documents[:] = [d for d in _documents if d["doc_id"] != doc_id]
    deleted = before - len(_documents)
    if deleted > 0:
        _rebuild_index()
        _save_store()
    return deleted


def get_all_documents() -> list[dict]:
    _load_store()
    doc_map = {}
    for doc in _documents:
        did = doc["doc_id"]
        if did not in doc_map:
            doc_map[did] = {"doc_id": did, "source": doc["source"], "chunk_count": 0}
        doc_map[did]["chunk_count"] += 1
    return list(doc_map.values())


def get_stats() -> dict:
    _load_store()
    doc_ids = set(d["doc_id"] for d in _documents)
    return {
        "total_chunks": len(_documents),
        "total_documents": len(doc_ids),
        "document_ids": list(doc_ids),
    }
