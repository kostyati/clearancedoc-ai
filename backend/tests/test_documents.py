"""Integration tests for the document upload/list/delete endpoints."""

import fitz
import pytest
from fastapi.testclient import TestClient

import services.retriever as retriever
from config import get_settings


@pytest.fixture(autouse=True)
def _isolated_storage(tmp_path, monkeypatch):
    """Point uploads, ChromaDB, and the metadata DB at fresh temp paths and reset cached clients."""
    monkeypatch.setenv("CLEARANCEDOC_UPLOAD_DIR", str(tmp_path / "uploads"))
    monkeypatch.setenv("CLEARANCEDOC_CHROMA_PERSIST_DIR", str(tmp_path / "chroma"))
    monkeypatch.setenv("CLEARANCEDOC_DB_PATH", str(tmp_path / "clearancedoc.db"))
    get_settings.cache_clear()
    retriever._client = None
    yield
    retriever._client = None
    get_settings.cache_clear()


@pytest.fixture
def client():
    from main import app

    return TestClient(app)


def _make_pdf_bytes(text: str = "This is a test document about clearance policy.") -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def test_upload_document_returns_ready_status(client):
    response = client.post(
        "/documents",
        files={"file": ("test.pdf", _make_pdf_bytes(), "application/pdf")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready"
    assert body["page_count"] == 1


def test_upload_document_stores_searchable_chunks(client):
    response = client.post(
        "/documents",
        files={"file": ("test.pdf", _make_pdf_bytes(), "application/pdf")},
    )
    document_id = response.json()["id"]

    from services.embedder import embed_texts

    query_embedding = embed_texts(["clearance policy"])[0]
    results = retriever.query(query_embedding, document_ids=[document_id], n_results=5)

    assert len(results) > 0
    assert results[0].document_id == document_id


def test_upload_rejects_non_pdf(client):
    response = client.post(
        "/documents",
        files={"file": ("test.txt", b"not a pdf", "text/plain")},
    )
    assert response.status_code == 400


def test_list_documents_includes_uploaded_document(client):
    upload_response = client.post(
        "/documents",
        files={"file": ("test.pdf", _make_pdf_bytes(), "application/pdf")},
    )
    document_id = upload_response.json()["id"]

    list_response = client.get("/documents")

    assert any(doc["id"] == document_id for doc in list_response.json())


def test_delete_document_returns_404_for_unknown_id(client):
    response = client.delete("/documents/does-not-exist")
    assert response.status_code == 404


def test_upload_marks_document_error_on_unexpected_processing_failure(client, monkeypatch):
    def broken_chunk_pages(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr("routers.documents.chunk_pages", broken_chunk_pages)

    response = client.post(
        "/documents",
        files={"file": ("test.pdf", _make_pdf_bytes(), "application/pdf")},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "error"


def test_delete_document_removes_it_and_its_chunks(client):
    upload_response = client.post(
        "/documents",
        files={"file": ("test.pdf", _make_pdf_bytes(), "application/pdf")},
    )
    document_id = upload_response.json()["id"]

    delete_response = client.delete(f"/documents/{document_id}")
    assert delete_response.status_code == 200

    list_response = client.get("/documents")
    assert all(doc["id"] != document_id for doc in list_response.json())

    from services.embedder import embed_texts

    query_embedding = embed_texts(["clearance policy"])[0]
    results = retriever.query(query_embedding, document_ids=[document_id], n_results=5)
    assert results == []
