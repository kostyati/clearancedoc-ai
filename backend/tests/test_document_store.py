"""Tests for SQLite-backed document metadata storage."""

from datetime import datetime, timezone

import pytest

from config import get_settings
from models.schemas import DocumentResponse, DocumentStatus
from services import document_store


@pytest.fixture(autouse=True)
def _isolated_db(tmp_path, monkeypatch):
    """Point the metadata DB at a fresh temp file per test."""
    monkeypatch.setenv("CLEARANCEDOC_DB_PATH", str(tmp_path / "clearancedoc.db"))
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def _document(document_id: str = "doc-1", status: DocumentStatus = DocumentStatus.READY) -> DocumentResponse:
    return DocumentResponse(
        id=document_id,
        filename="test.pdf",
        status=status,
        page_count=3,
        uploaded_at=datetime.now(timezone.utc),
    )


def test_save_and_list_round_trips_document():
    document_store.save(_document())

    documents = document_store.list_all()

    assert len(documents) == 1
    assert documents[0].id == "doc-1"
    assert documents[0].status == DocumentStatus.READY
    assert documents[0].page_count == 3


def test_save_upserts_existing_document():
    document_store.save(_document(status=DocumentStatus.PROCESSING))
    document_store.save(_document(status=DocumentStatus.READY))

    documents = document_store.list_all()

    assert len(documents) == 1
    assert documents[0].status == DocumentStatus.READY


def test_delete_removes_document():
    document_store.save(_document())

    document_store.delete("doc-1")

    assert document_store.list_all() == []


def test_list_all_empty_by_default():
    assert document_store.list_all() == []
