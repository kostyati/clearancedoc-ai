"""Tests for the /chat endpoint."""

from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from models.schemas import ChatResponse, Citation, DocumentResponse, DocumentStatus
from services.generator import GenerationError


def _client() -> TestClient:
    from main import app

    return TestClient(app)


def _known_document(document_id: str = "doc-1") -> DocumentResponse:
    return DocumentResponse(
        id=document_id,
        filename="test.pdf",
        status=DocumentStatus.READY,
        page_count=3,
        uploaded_at=datetime.now(timezone.utc),
    )


@pytest.fixture(autouse=True)
def _stub_document_lookup(monkeypatch):
    """Most tests assume `document_ids` refer to known documents unless overridden."""
    monkeypatch.setattr(
        "routers.chat.document_store.get",
        lambda document_id: _known_document(document_id),
    )


def test_ask_question_returns_answer_with_citations(monkeypatch):
    async def fake_answer_question(question, document_ids):
        return ChatResponse(
            answer="5 years (Page 2)",
            citations=[Citation(document_id="doc-1", page_number=2, text="clearance is valid for 5 years")],
        )

    monkeypatch.setattr("routers.chat.answer_question", fake_answer_question)

    response = _client().post("/chat", json={"document_ids": ["doc-1"], "question": "How long?"})

    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "5 years (Page 2)"
    assert body["citations"][0]["page_number"] == 2


def test_ask_question_returns_502_on_generation_error(monkeypatch):
    async def failing_answer_question(question, document_ids):
        raise GenerationError("Missing API key for the configured LLM provider")

    monkeypatch.setattr("routers.chat.answer_question", failing_answer_question)

    response = _client().post("/chat", json={"document_ids": ["doc-1"], "question": "How long?"})

    assert response.status_code == 502


def test_ask_question_rejects_empty_question():
    response = _client().post("/chat", json={"document_ids": ["doc-1"], "question": "   "})

    assert response.status_code == 400


def test_ask_question_rejects_empty_document_ids():
    response = _client().post("/chat", json={"document_ids": [], "question": "How long?"})

    assert response.status_code == 400


def test_ask_question_rejects_unknown_document_id(monkeypatch):
    monkeypatch.setattr("routers.chat.document_store.get", lambda document_id: None)

    response = _client().post("/chat", json={"document_ids": ["doc-missing"], "question": "How long?"})

    assert response.status_code == 404
