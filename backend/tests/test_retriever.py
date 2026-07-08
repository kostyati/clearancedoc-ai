"""Tests for ChromaDB-backed chunk storage and similarity search."""

import pytest

import services.retriever as retriever
from config import get_settings
from services.chunker import Chunk


@pytest.fixture(autouse=True)
def _isolated_chroma(tmp_path, monkeypatch):
    """Point ChromaDB at a fresh temp directory and reset cached clients per test."""
    monkeypatch.setenv("CLEARANCEDOC_CHROMA_PERSIST_DIR", str(tmp_path / "chroma"))
    get_settings.cache_clear()
    retriever._client = None
    yield
    retriever._client = None
    get_settings.cache_clear()


def _chunks(texts: list[str]) -> list[Chunk]:
    return [Chunk(text=text, page_number=i + 1, chunk_index=i) for i, text in enumerate(texts)]


def test_add_and_query_returns_stored_chunks():
    chunks = _chunks(["alpha content", "beta content"])
    embeddings = [[1.0, 0.0], [0.0, 1.0]]
    retriever.add_chunks("doc-1", chunks, embeddings)

    results = retriever.query([1.0, 0.0], n_results=1)

    assert len(results) == 1
    assert results[0].text == "alpha content"
    assert results[0].document_id == "doc-1"
    assert results[0].page_number == 1


def test_query_scoped_to_document_ids():
    retriever.add_chunks("doc-1", _chunks(["doc1 chunk"]), [[1.0, 0.0]])
    retriever.add_chunks("doc-2", _chunks(["doc2 chunk"]), [[1.0, 0.0]])

    results = retriever.query([1.0, 0.0], document_ids=["doc-2"], n_results=5)

    assert len(results) == 1
    assert results[0].document_id == "doc-2"


def test_delete_document_removes_its_chunks():
    retriever.add_chunks("doc-1", _chunks(["will be deleted"]), [[1.0, 0.0]])
    retriever.delete_document("doc-1")

    results = retriever.query([1.0, 0.0], n_results=5)

    assert results == []


def test_add_chunks_with_empty_list_is_noop():
    retriever.add_chunks("doc-1", [], [])
    results = retriever.query([1.0, 0.0], n_results=5)
    assert results == []
