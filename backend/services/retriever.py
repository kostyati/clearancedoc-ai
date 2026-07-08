"""ChromaDB-backed storage and similarity search over document chunks."""

from __future__ import annotations

from dataclasses import dataclass

import chromadb

from config import get_settings
from services.chunker import Chunk

_COLLECTION_NAME = "documents"
_client: chromadb.ClientAPI | None = None


@dataclass
class RetrievedChunk:
    """A chunk returned from similarity search, with its source citation info."""

    text: str
    document_id: str
    page_number: int
    distance: float


def _get_collection() -> chromadb.Collection:
    global _client
    if _client is None:
        settings = get_settings()
        _client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    return _client.get_or_create_collection(_COLLECTION_NAME)


def add_chunks(document_id: str, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
    """Store a document's chunks and their embeddings in ChromaDB."""
    if not chunks:
        return

    collection = _get_collection()
    collection.add(
        ids=[f"{document_id}:{chunk.chunk_index}" for chunk in chunks],
        embeddings=embeddings,
        documents=[chunk.text for chunk in chunks],
        metadatas=[
            {"document_id": document_id, "page_number": chunk.page_number}
            for chunk in chunks
        ],
    )


def query(
    query_embedding: list[float],
    document_ids: list[str] | None = None,
    n_results: int = 5,
) -> list[RetrievedChunk]:
    """Find the most similar chunks to a query embedding, optionally scoped to documents."""
    collection = _get_collection()
    where = {"document_id": {"$in": document_ids}} if document_ids else None

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where=where,
    )

    retrieved: list[RetrievedChunk] = []
    documents = results["documents"][0] if results["documents"] else []
    metadatas = results["metadatas"][0] if results["metadatas"] else []
    distances = results["distances"][0] if results["distances"] else []

    for text, metadata, distance in zip(documents, metadatas, distances):
        retrieved.append(
            RetrievedChunk(
                text=text,
                document_id=metadata["document_id"],
                page_number=metadata["page_number"],
                distance=distance,
            )
        )

    return retrieved


def delete_document(document_id: str) -> None:
    """Remove all chunks belonging to a document from ChromaDB."""
    collection = _get_collection()
    collection.delete(where={"document_id": document_id})
