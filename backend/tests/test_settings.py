"""Tests for the /settings endpoint."""

import httpx
import pytest
from fastapi.testclient import TestClient

from config import get_settings


@pytest.fixture(autouse=True)
def _isolated_settings(tmp_path, monkeypatch):
    """Point the settings DB at a fresh temp file per test."""
    monkeypatch.setenv("CLEARANCEDOC_DB_PATH", str(tmp_path / "clearancedoc.db"))
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def _client() -> TestClient:
    from main import app

    return TestClient(app)


def test_get_settings_returns_env_defaults_when_nothing_persisted():
    response = _client().get("/settings")

    assert response.status_code == 200
    assert response.json() == {"provider": "ollama", "model": "llama3"}


def test_put_settings_persists_and_get_returns_it(monkeypatch):
    async def fake_post(self, url, **kwargs):
        assert url.endswith("/api/generate")
        return httpx.Response(200, json={"response": "OK"}, request=httpx.Request("POST", url))

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)

    put_response = _client().put("/settings", json={"provider": "ollama", "model": "mistral"})
    assert put_response.status_code == 200
    assert put_response.json() == {"provider": "ollama", "model": "mistral"}

    get_response = _client().get("/settings")
    assert get_response.json() == {"provider": "ollama", "model": "mistral"}


def test_put_settings_rejects_missing_api_key():
    response = _client().put("/settings", json={"provider": "openai", "model": "gpt-4o-mini"})

    assert response.status_code == 400


def test_put_settings_rejects_failed_connection(monkeypatch):
    async def fake_post(self, url, **kwargs):
        raise httpx.ConnectError("connection refused", request=httpx.Request("POST", url))

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)

    response = _client().put(
        "/settings", json={"provider": "openai", "model": "gpt-4o-mini", "api_key": "sk-test"}
    )

    assert response.status_code == 400


def test_put_settings_does_not_persist_on_failed_validation(monkeypatch):
    async def fake_post(self, url, **kwargs):
        raise httpx.ConnectError("connection refused", request=httpx.Request("POST", url))

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)

    _client().put("/settings", json={"provider": "openai", "model": "gpt-4o-mini", "api_key": "sk-test"})

    get_response = _client().get("/settings")
    assert get_response.json() == {"provider": "ollama", "model": "llama3"}
