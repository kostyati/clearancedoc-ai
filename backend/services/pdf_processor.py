"""PDF text extraction with OCR fallback for scanned/image-only pages."""

from __future__ import annotations

import io
from dataclasses import dataclass

import fitz  # PyMuPDF
import pytesseract
from PIL import Image

OCR_DPI = 300
MIN_CHARS_FOR_NATIVE_TEXT = 20


class PDFProcessingError(Exception):
    """Raised when a PDF cannot be opened or has no usable pages."""


@dataclass
class PageContent:
    """Extracted content for a single page."""

    page_number: int  # 1-indexed
    text: str
    used_ocr: bool


@dataclass
class ProcessedDocument:
    """Extracted content for an entire document."""

    page_count: int
    pages: list[PageContent]

    @property
    def full_text(self) -> str:
        return "\n\n".join(page.text for page in self.pages)


def extract_text(pdf_bytes: bytes) -> ProcessedDocument:
    """Extract text from a PDF, falling back to OCR for pages with no native text layer."""
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    except Exception as exc:
        raise PDFProcessingError(f"Could not open PDF: {exc}") from exc

    try:
        if doc.page_count == 0:
            raise PDFProcessingError("PDF has no pages")

        pages: list[PageContent] = []
        for index in range(doc.page_count):
            page = doc.load_page(index)
            text = page.get_text().strip()
            used_ocr = False

            if len(text) < MIN_CHARS_FOR_NATIVE_TEXT:
                ocr_text = _ocr_page(page)
                if ocr_text:
                    text = ocr_text
                    used_ocr = True

            pages.append(PageContent(page_number=index + 1, text=text, used_ocr=used_ocr))
    finally:
        doc.close()

    return ProcessedDocument(page_count=len(pages), pages=pages)


def _ocr_page(page: fitz.Page) -> str:
    """Render a page to an image and run Tesseract OCR on it."""
    zoom = OCR_DPI / 72
    pixmap = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
    image = Image.open(io.BytesIO(pixmap.tobytes("png")))
    try:
        return pytesseract.image_to_string(image).strip()
    except pytesseract.TesseractNotFoundError:
        return ""
