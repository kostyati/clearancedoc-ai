"""Endpoints for asking questions against uploaded documents."""

from fastapi import APIRouter, HTTPException

from models.schemas import ChatRequest, ChatResponse
from services import document_store
from services.generator import GenerationError
from services.rag_pipeline import answer_question

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def ask_question(request: ChatRequest) -> ChatResponse:
    """Answer a question using retrieval-augmented generation."""
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question must not be empty")
    if not request.document_ids:
        raise HTTPException(status_code=400, detail="At least one document_id is required")

    missing = [doc_id for doc_id in request.document_ids if document_store.get(doc_id) is None]
    if missing:
        raise HTTPException(status_code=404, detail=f"Unknown document_ids: {', '.join(missing)}")

    try:
        return await answer_question(request.question, request.document_ids)
    except GenerationError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
