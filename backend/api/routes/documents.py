"""
Document Upload API Routes — PDF upload, listing, and deletion.
"""
import os
import uuid
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.config import settings
from backend.rag.document_processor import get_document_processor
from backend.rag.vector_store import add_documents, delete_document, get_all_documents, get_stats

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/documents", tags=["Documents"])


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a PDF document to the knowledge base.
    The document is processed, chunked, embedded, and stored in ChromaDB.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    try:
        # Read file content
        content = await file.read()
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Empty file uploaded.")

        # Save file to disk
        doc_id = f"doc_{uuid.uuid4().hex[:8]}"
        save_path = os.path.join(settings.pdf_path, f"{doc_id}_{file.filename}")
        with open(save_path, "wb") as f:
            f.write(content)

        # Process and embed
        processor = get_document_processor()
        chunks = processor.process_pdf(save_path)

        if not chunks:
            raise HTTPException(status_code=422, detail="Could not extract text from PDF.")

        chunk_count = add_documents(chunks, doc_id)

        return {
            "message": f"Document '{file.filename}' uploaded and processed successfully.",
            "doc_id": doc_id,
            "filename": file.filename,
            "chunks_created": chunk_count,
            "file_path": save_path,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/")
async def list_documents():
    """List all documents in the knowledge base."""
    try:
        documents = get_all_documents()
        stats = get_stats()
        return {
            "documents": documents,
            "total_chunks": stats["total_chunks"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{doc_id}")
async def remove_document(doc_id: str):
    """Remove a document and its embeddings from the knowledge base."""
    try:
        chunks_deleted = delete_document(doc_id)
        if chunks_deleted == 0:
            raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found.")
        return {
            "message": f"Document '{doc_id}' deleted successfully.",
            "chunks_deleted": chunks_deleted,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def document_stats():
    """Get knowledge base statistics."""
    try:
        return get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
