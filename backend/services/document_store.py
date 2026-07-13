"""SQLite-backed persistent storage for document metadata."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Iterator

from config import get_settings
from models.schemas import DocumentResponse, DocumentStatus

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    status TEXT NOT NULL,
    page_count INTEGER,
    uploaded_at TEXT NOT NULL
)
"""


@contextmanager
def _connect() -> Iterator[sqlite3.Connection]:
    settings = get_settings()
    Path(settings.db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(settings.db_path)
    try:
        conn.execute(_CREATE_TABLE)
        yield conn
        conn.commit()
    finally:
        conn.close()


def _row_to_document(row: tuple) -> DocumentResponse:
    document_id, filename, status, page_count, uploaded_at = row
    return DocumentResponse(
        id=document_id,
        filename=filename,
        status=DocumentStatus(status),
        page_count=page_count,
        uploaded_at=datetime.fromisoformat(uploaded_at),
    )


def save(document: DocumentResponse) -> None:
    """Insert or update a document's metadata."""
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO documents (id, filename, status, page_count, uploaded_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                filename = excluded.filename,
                status = excluded.status,
                page_count = excluded.page_count,
                uploaded_at = excluded.uploaded_at
            """,
            (
                document.id,
                document.filename,
                document.status.value,
                document.page_count,
                document.uploaded_at.isoformat(),
            ),
        )


def get(document_id: str) -> DocumentResponse | None:
    """Return a single document's metadata, or None if it doesn't exist."""
    with _connect() as conn:
        row = conn.execute(
            "SELECT id, filename, status, page_count, uploaded_at FROM documents WHERE id = ?",
            (document_id,),
        ).fetchone()
    return _row_to_document(row) if row is not None else None


def list_all() -> list[DocumentResponse]:
    """Return metadata for every stored document."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT id, filename, status, page_count, uploaded_at FROM documents"
        ).fetchall()
    return [_row_to_document(row) for row in rows]


def delete(document_id: str) -> None:
    """Remove a document's metadata."""
    with _connect() as conn:
        conn.execute("DELETE FROM documents WHERE id = ?", (document_id,))
