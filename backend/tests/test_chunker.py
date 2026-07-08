"""Tests for token-based page chunking."""

from services.chunker import chunk_pages
from services.pdf_processor import PageContent


def test_short_page_produces_single_chunk():
    pages = [PageContent(page_number=1, text="short document", used_ocr=False)]
    chunks = chunk_pages(pages, chunk_size=512, chunk_overlap=50)

    assert len(chunks) == 1
    assert chunks[0].page_number == 1
    assert chunks[0].chunk_index == 0


def test_long_page_splits_into_overlapping_chunks():
    long_text = " ".join(f"word{i}" for i in range(2000))
    pages = [PageContent(page_number=1, text=long_text, used_ocr=False)]
    chunks = chunk_pages(pages, chunk_size=100, chunk_overlap=20)

    assert len(chunks) > 1
    assert all(chunk.page_number == 1 for chunk in chunks)
    assert [chunk.chunk_index for chunk in chunks] == list(range(len(chunks)))


def test_chunks_never_span_pages():
    pages = [
        PageContent(page_number=1, text="first page content here", used_ocr=False),
        PageContent(page_number=2, text="second page content here", used_ocr=False),
    ]
    chunks = chunk_pages(pages, chunk_size=512, chunk_overlap=50)

    page_numbers = {chunk.page_number for chunk in chunks}
    assert page_numbers == {1, 2}


def test_empty_page_text_is_skipped():
    pages = [
        PageContent(page_number=1, text="", used_ocr=False),
        PageContent(page_number=2, text="real content", used_ocr=False),
    ]
    chunks = chunk_pages(pages, chunk_size=512, chunk_overlap=50)

    assert len(chunks) == 1
    assert chunks[0].page_number == 2
