"""SQLite-backed persistent storage for the active LLM provider configuration."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from config import get_settings
from models.schemas import LLMProvider, SettingsUpdateRequest

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS llm_settings (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    api_key TEXT
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


def get_active() -> SettingsUpdateRequest | None:
    """Return the persisted LLM provider configuration, or None if never saved."""
    with _connect() as conn:
        row = conn.execute(
            "SELECT provider, model, api_key FROM llm_settings WHERE id = 1"
        ).fetchone()
    if row is None:
        return None
    provider, model, api_key = row
    return SettingsUpdateRequest(provider=LLMProvider(provider), model=model, api_key=api_key)


def save(request: SettingsUpdateRequest) -> None:
    """Insert or update the active LLM provider configuration."""
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO llm_settings (id, provider, model, api_key)
            VALUES (1, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                provider = excluded.provider,
                model = excluded.model,
                api_key = excluded.api_key
            """,
            (request.provider.value, request.model, request.api_key),
        )
