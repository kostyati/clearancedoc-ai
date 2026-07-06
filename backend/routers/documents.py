"""Endpoints for uploading, listing, and deleting documents."""

import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile

from config import get_settings
from models.schemas import DocumentResponse, DocumentStatus
from services.pdf_processor import PDFProcessingError, extract_text

router = APIRouter(prefix="/documents", tags=["documents"])

# TODO(Day 3): replace this in-memory store with ChromaDB-backed metadata + chunks.
_documents: dict[str, DocumentResponse] = {}
_document_pages: dict[str, list[str]] = {}


@router.post("", response_model=DocumentResponse)
async def upload_document(file: UploadFile) -> DocumentResponse:
    """Upload a PDF, extract its text (with OCR fallback), and persist it to disk.

    TODO(Day 3): chunk extracted pages, embed, and store in ChromaDB.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    settings = get_settings()
    document_id = str(uuid.uuid4())
    pdf_bytes = await file.read()

    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    (upload_dir / f"{document_id}.pdf").write_bytes(pdf_bytes)

    try:
        processed = extract_text(pdf_bytes)
    except PDFProcessingError:
        document = DocumentResponse(
            id=document_id,
            filename=file.filename or "unknown.pdf",
            status=DocumentStatus.ERROR,
            page_count=None,
            uploaded_at=datetime.now(timezone.utc),
        )
        _documents[document_id] = document
        return document

    _document_pages[document_id] = [page.text for page in processed.pages]
    document = DocumentResponse(
        id=document_id,
        filename=file.filename or "unknown.pdf",
        status=DocumentStatus.READY,
        page_count=processed.page_count,
        uploaded_at=datetime.now(timezone.utc),
    )
    _documents[document_id] = document
    return document


@router.get("", response_model=list[DocumentResponse])
async def list_documents() -> list[DocumentResponse]:
    """List all uploaded documents."""
    return list(_documents.values())


@router.delete("/{document_id}")
async def delete_document(document_id: str) -> dict[str, str]:
    """Delete a document, its extracted pages, and its file on disk.

    TODO(Day 3): also remove its ChromaDB embeddings.
    """
    _documents.pop(document_id, None)
    _document_pages.pop(document_id, None)

    settings = get_settings()
    file_path = Path(settings.upload_dir) / f"{document_id}.pdf"
    file_path.unlink(missing_ok=True)

    return {"status": "deleted", "id": document_id}
