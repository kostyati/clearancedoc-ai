"""Endpoints for asking questions against uploaded documents."""

from fastapi import APIRouter, HTTPException

from models.schemas import ChatRequest, ChatResponse
from services.generator import GenerationError
from services.rag_pipeline import answer_question

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def ask_question(request: ChatRequest) -> ChatResponse:
    """Answer a question using retrieval-augmented generation."""
    try:
        return await answer_question(request.question, request.document_ids)
    except GenerationError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
