"""
Lightweight TF-IDF Embeddings — No torch/sentence-transformers needed.
Uses pure Python math for text similarity.
"""
import math
import re
import logging
from collections import Counter

logger = logging.getLogger(__name__)


def tokenize(text: str) -> list[str]:
    """Simple tokenizer — lowercase, split on non-alphanumeric."""
    return re.findall(r'[a-z0-9]+', text.lower())


def compute_tfidf(documents: list[str]) -> tuple[list[dict], dict]:
    """
    Compute TF-IDF vectors for a list of documents.
    Returns (tfidf_vectors, idf_scores).
    """
    doc_count = len(documents)
    if doc_count == 0:
        return [], {}

    # Tokenize all docs
    tokenized = [tokenize(doc) for doc in documents]

    # Compute document frequency
    df = Counter()
    for tokens in tokenized:
        unique = set(tokens)
        for token in unique:
            df[token] += 1

    # Compute IDF
    idf = {}
    for term, freq in df.items():
        idf[term] = math.log(doc_count / (1 + freq)) + 1

    # Compute TF-IDF for each document
    tfidf_vectors = []
    for tokens in tokenized:
        tf = Counter(tokens)
        total = len(tokens) if tokens else 1
        vector = {}
        for term, count in tf.items():
            vector[term] = (count / total) * idf.get(term, 0)
        tfidf_vectors.append(vector)

    return tfidf_vectors, idf


def cosine_similarity(vec1: dict, vec2: dict) -> float:
    """Compute cosine similarity between two sparse vectors (dicts)."""
    common = set(vec1.keys()) & set(vec2.keys())
    dot = sum(vec1[k] * vec2[k] for k in common)

    norm1 = math.sqrt(sum(v * v for v in vec1.values()))
    norm2 = math.sqrt(sum(v * v for v in vec2.values()))

    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)


def get_query_vector(query: str, idf: dict) -> dict:
    """Convert a query string to a TF-IDF vector using existing IDF scores."""
    tokens = tokenize(query)
    tf = Counter(tokens)
    total = len(tokens) if tokens else 1
    vector = {}
    for term, count in tf.items():
        vector[term] = (count / total) * idf.get(term, 1.0)
    return vector
