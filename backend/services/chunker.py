"""Splits page text into overlapping token-based chunks for embedding."""

from __future__ import annotations

from dataclasses import dataclass

from transformers import AutoTokenizer

from services.pdf_processor import PageContent

_TOKENIZER_NAME = "sentence-transformers/all-MiniLM-L6-v2"
_tokenizer = None


@dataclass
class Chunk:
    """A chunk of text tied back to the page it came from."""

    text: str
    page_number: int
    chunk_index: int


def _get_tokenizer() -> AutoTokenizer:
    global _tokenizer
    if _tokenizer is None:
        _tokenizer = AutoTokenizer.from_pretrained(_TOKENIZER_NAME)
    return _tokenizer


def chunk_pages(pages: list[PageContent], chunk_size: int, chunk_overlap: int) -> list[Chunk]:
    """Split each page's text into overlapping chunks of up to `chunk_size` tokens.

    Chunks never span multiple pages, so every chunk can be cited with a single
    page number.
    """
    tokenizer = _get_tokenizer()
    chunks: list[Chunk] = []
    chunk_index = 0

    for page in pages:
        if not page.text:
            continue

        token_ids = tokenizer.encode(page.text, add_special_tokens=False)
        if not token_ids:
            continue

        step = chunk_size - chunk_overlap
        for start in range(0, len(token_ids), step):
            window = token_ids[start : start + chunk_size]
            if not window:
                continue
            text = tokenizer.decode(window).strip()
            if text:
                chunks.append(
                    Chunk(text=text, page_number=page.page_number, chunk_index=chunk_index)
                )
                chunk_index += 1
            if start + chunk_size >= len(token_ids):
                break

    return chunks
