"""Tests for the retrieve-then-generate RAG orchestration."""

import pytest

from services import generator, rag_pipeline
from services.retriever import RetrievedChunk


@pytest.fixture
def _stub_embed(monkeypatch):
    monkeypatch.setattr("services.rag_pipeline.embed_texts", lambda texts: [[0.1, 0.2]])


async def test_answer_question_returns_generated_answer_and_citations(monkeypatch, _stub_embed):
    chunk = RetrievedChunk(text="clearance is valid for 5 years", document_id="doc-1", page_number=2, distance=0.1)
    monkeypatch.setattr("services.rag_pipeline.retriever.query", lambda *a, **k: [chunk])

    async def fake_generate(question, chunks):
        return "5 years (Page 2)"

    monkeypatch.setattr(generator, "generate_answer", fake_generate)

    response = await rag_pipeline.answer_question("How long is clearance valid?", ["doc-1"])

    assert response.answer == "5 years (Page 2)"
    assert len(response.citations) == 1
    assert response.citations[0].document_id == "doc-1"
    assert response.citations[0].page_number == 2


async def test_answer_question_with_no_chunks_skips_generation(monkeypatch, _stub_embed):
    monkeypatch.setattr("services.rag_pipeline.retriever.query", lambda *a, **k: [])

    async def fail_generate(question, chunks):
        raise AssertionError("generate_answer should not be called with no context")

    monkeypatch.setattr(generator, "generate_answer", fail_generate)

    response = await rag_pipeline.answer_question("How long is clearance valid?", ["doc-1"])

    assert response.citations == []
    assert "couldn't find" in response.answer
