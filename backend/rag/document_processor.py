"""
Document Processor — Extracts text from PDFs and splits into chunks.
Pure Python implementation — no langchain needed.
"""
import logging
from PyPDF2 import PdfReader
from backend.config import settings

logger = logging.getLogger(__name__)


def split_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> list[str]:
    """Split text into overlapping chunks by sentences/paragraphs."""
    if not text or not text.strip():
        return []

    # Split by double newlines first (paragraphs), then sentences
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    chunks = []
    current_chunk = ""

    for para in paragraphs:
        if len(current_chunk) + len(para) + 1 <= chunk_size:
            current_chunk += (" " if current_chunk else "") + para
        else:
            if current_chunk:
                chunks.append(current_chunk)
            # If paragraph itself is too long, split by sentences
            if len(para) > chunk_size:
                sentences = para.replace(". ", ".\n").split("\n")
                for sent in sentences:
                    if len(current_chunk) + len(sent) + 1 <= chunk_size:
                        current_chunk += (" " if current_chunk else "") + sent
                    else:
                        if current_chunk:
                            chunks.append(current_chunk)
                        current_chunk = sent
            else:
                current_chunk = para

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


class DocumentProcessor:
    """Process PDF documents into text chunks for RAG."""

    def __init__(self):
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP

    def process_pdf(self, file_path: str) -> list[dict]:
        """
        Extract text from a PDF and split into chunks.
        Returns list of dicts with 'text', 'source', 'metadata'.
        """
        try:
            reader = PdfReader(file_path)
            full_text = ""
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                full_text += page_text + "\n\n"

            if not full_text.strip():
                logger.warning(f"No text extracted from {file_path}")
                return []

            # Split into chunks
            text_chunks = split_text(full_text, self.chunk_size, self.chunk_overlap)

            # Build chunk dicts
            import os
            filename = os.path.basename(file_path)
            chunks = []
            for i, chunk_text in enumerate(text_chunks):
                chunks.append({
                    "text": chunk_text.strip(),
                    "source": filename,
                    "metadata": {
                        "chunk_index": i,
                        "total_chunks": len(text_chunks),
                        "file_path": file_path,
                    },
                })

            logger.info(f"Processed '{filename}': {len(chunks)} chunks from {len(reader.pages)} pages.")
            return chunks

        except Exception as e:
            logger.error(f"Failed to process PDF '{file_path}': {e}")
            return []


# Singleton
_processor = None


def get_document_processor() -> DocumentProcessor:
    global _processor
    if _processor is None:
        _processor = DocumentProcessor()
    return _processor
