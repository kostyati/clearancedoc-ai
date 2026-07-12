"""Orchestrates retrieval and generation to answer questions with citations."""

from __future__ import annotations

from config import get_settings
from models.schemas import ChatResponse, Citation
from services import generator, retriever
from services.embedder import embed_texts

_NO_CONTEXT_ANSWER = "I couldn't find any relevant information in the selected documents."


async def answer_question(question: str, document_ids: list[str]) -> ChatResponse:
    """Retrieve relevant chunks for `question` and generate a cited answer."""
    settings = get_settings()
    query_embedding = embed_texts([question])[0]
    chunks = retriever.query(
        query_embedding, document_ids=document_ids, n_results=settings.retrieval_top_k
    )

    if not chunks:
        return ChatResponse(answer=_NO_CONTEXT_ANSWER, citations=[])

    answer = await generator.generate_answer(question, chunks)
    citations = [
        Citation(document_id=chunk.document_id, page_number=chunk.page_number, text=chunk.text)
        for chunk in chunks
    ]
    return ChatResponse(answer=answer, citations=citations)
