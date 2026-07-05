"""Endpoints for asking questions against uploaded documents."""

from fastapi import APIRouter

from models.schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def ask_question(request: ChatRequest) -> ChatResponse:
    """Answer a question using retrieval-augmented generation.

    TODO(Day 4): call rag_pipeline to retrieve chunks and generate a cited answer.
    """
    raise NotImplementedError
