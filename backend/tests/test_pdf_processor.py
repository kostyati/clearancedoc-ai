"""Tests for PDF text extraction and OCR fallback."""

import fitz
import pytest

from services.pdf_processor import PDFProcessingError, extract_text


def _make_text_pdf(pages_text: list[str]) -> bytes:
    doc = fitz.open()
    for text in pages_text:
        page = doc.new_page()
        page.insert_text((72, 72), text)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def _make_blank_pdf(page_count: int = 1) -> bytes:
    doc = fitz.open()
    for _ in range(page_count):
        doc.new_page()
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def test_extract_text_from_native_pdf():
    pdf_bytes = _make_text_pdf(
        [
            "Hello ClearanceDoc, this is a native text page with plenty of characters.",
            "Second page also has enough native text to skip the OCR fallback path.",
        ]
    )

    result = extract_text(pdf_bytes)

    assert result.page_count == 2
    assert "Hello ClearanceDoc" in result.pages[0].text
    assert result.pages[0].used_ocr is False
    assert "Second page" in result.pages[1].text


def test_extract_text_raises_on_corrupted_pdf():
    with pytest.raises(PDFProcessingError):
        extract_text(b"not a real pdf")


def test_blank_page_falls_back_to_ocr_and_yields_no_text():
    pdf_bytes = _make_blank_pdf()

    result = extract_text(pdf_bytes)

    assert result.page_count == 1
    assert result.pages[0].used_ocr is False
    assert result.pages[0].text == ""
