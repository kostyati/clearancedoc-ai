"""Tests for multi-provider LLM answer generation."""

import httpx
import pytest

from config import get_settings
from services import generator
from services.retriever import RetrievedChunk


@pytest.fixture(autouse=True)
def _reset_settings():
    yield
    get_settings.cache_clear()


def _chunks() -> list[RetrievedChunk]:
    return [RetrievedChunk(text="clearance is valid for 5 years", document_id="doc-1", page_number=2, distance=0.1)]


async def test_generate_answer_ollama(monkeypatch):
    monkeypatch.setenv("CLEARANCEDOC_LLM_PROVIDER", "ollama")
    get_settings.cache_clear()

    async def fake_post(self, url, **kwargs):
        assert url.endswith("/api/generate")
        return httpx.Response(200, json={"response": "5 years (Page 2)"}, request=httpx.Request("POST", url))

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)

    answer = await generator.generate_answer("How long is clearance valid?", _chunks())

    assert answer == "5 years (Page 2)"


async def test_generate_answer_openai(monkeypatch):
    monkeypatch.setenv("CLEARANCEDOC_LLM_PROVIDER", "openai")
    monkeypatch.setenv("CLEARANCEDOC_OPENAI_API_KEY", "sk-test")
    get_settings.cache_clear()

    async def fake_post(self, url, **kwargs):
        assert url.endswith("/chat/completions")
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": "5 years (Page 2)"}}]},
            request=httpx.Request("POST", url),
        )

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)

    answer = await generator.generate_answer("How long is clearance valid?", _chunks())

    assert answer == "5 years (Page 2)"


async def test_generate_answer_anthropic(monkeypatch):
    monkeypatch.setenv("CLEARANCEDOC_LLM_PROVIDER", "anthropic")
    monkeypatch.setenv("CLEARANCEDOC_ANTHROPIC_API_KEY", "sk-ant-test")
    get_settings.cache_clear()

    async def fake_post(self, url, **kwargs):
        assert url == "https://api.anthropic.com/v1/messages"
        return httpx.Response(
            200,
            json={"content": [{"type": "text", "text": "5 years (Page 2)"}]},
            request=httpx.Request("POST", url),
        )

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)

    answer = await generator.generate_answer("How long is clearance valid?", _chunks())

    assert answer == "5 years (Page 2)"


async def test_generate_answer_openai_missing_api_key_raises(monkeypatch):
    monkeypatch.setenv("CLEARANCEDOC_LLM_PROVIDER", "openai")
    monkeypatch.delenv("CLEARANCEDOC_OPENAI_API_KEY", raising=False)
    get_settings.cache_clear()

    with pytest.raises(generator.GenerationError):
        await generator.generate_answer("How long is clearance valid?", _chunks())


async def test_generate_answer_http_error_raises_generation_error(monkeypatch):
    monkeypatch.setenv("CLEARANCEDOC_LLM_PROVIDER", "ollama")
    get_settings.cache_clear()

    async def fake_post(self, url, **kwargs):
        raise httpx.ConnectError("connection refused", request=httpx.Request("POST", url))

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)

    with pytest.raises(generator.GenerationError):
        await generator.generate_answer("How long is clearance valid?", _chunks())


async def test_generate_answer_unsupported_provider_raises(monkeypatch):
    monkeypatch.setenv("CLEARANCEDOC_LLM_PROVIDER", "bedrock")
    get_settings.cache_clear()

    with pytest.raises(generator.GenerationError):
        await generator.generate_answer("How long is clearance valid?", _chunks())
