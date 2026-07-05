"""Endpoints for uploading, listing, and deleting documents."""

from fastapi import APIRouter, UploadFile

from models.schemas import DocumentResponse

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentResponse)
async def upload_document(file: UploadFile) -> DocumentResponse:
    """Upload a PDF for processing.

    TODO(Day 2): parse with pdf_processor and persist to disk.
    TODO(Day 3): chunk, embed, and store in ChromaDB.
    """
    raise NotImplementedError


@router.get("", response_model=list[DocumentResponse])
async def list_documents() -> list[DocumentResponse]:
    """List all uploaded documents.

    TODO(Day 3): read document metadata from the persistence layer.
    """
    return []


@router.delete("/{document_id}")
async def delete_document(document_id: str) -> dict[str, str]:
    """Delete a document and its embeddings.

    TODO(Day 3): remove file, ChromaDB entries, and metadata.
    """
    return {"status": "deleted", "id": document_id}
