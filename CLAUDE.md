# ClearanceDoc AI

## What this project is
A self-hosted web application for government document analysis. Users upload PDFs, ask natural language questions, and get cited answers with page references. Designed for government/enterprise document workflows (contracts, RFPs, policy docs).

## Why it exists
This is a portfolio project for an AI Engineer job search. It must demonstrate production-quality engineering, not tutorial-level code. Key differentiators from typical GitHub RAG projects:
- Evaluation pipeline with real metrics (RAGAS)
- Edge case handling (scanned PDFs, tables, corrupted files)
- Multi-provider LLM support (Ollama local, OpenAI, Anthropic, Groq)
- Professional React frontend (not Streamlit)
- One-command Docker deployment
- CI/CD with GitHub Actions

## Tech stack
- **Backend:** Python, FastAPI, LangChain, ChromaDB, sentence-transformers
- **Frontend:** React, Axios
- **Document processing:** PyMuPDF, pytesseract (OCR)
- **LLM:** Ollama (local, free) or OpenAI/Anthropic/Groq API (user brings own key)
- **Embedding:** all-MiniLM-L6-v2 (local, free)
- **Infrastructure:** Docker, docker-compose, GitHub Actions
- **Testing:** pytest, RAGAS evaluation

## Architecture
```
User Browser (React :3000)
    ↓ HTTP/REST
FastAPI Backend (:8000)
    ├── PDF Processor (PyMuPDF + OCR)
    ├── Chunker (512 tokens, 50 overlap)
    ├── Embedder (sentence-transformers)
    ├── Retriever (ChromaDB)
    └── Generator (Ollama or Cloud LLM)
```

## Distribution
- GitHub repo with clean commit history
- DockerHub pre-built image
- `docker compose up` → everything runs → localhost:3000

## File structure
```
clearancedoc-ai/
├── docker-compose.yml
├── README.md
├── CLAUDE.md (this file)
├── .github/workflows/ci.yml
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py                     # FastAPI entry point
│   ├── config.py                   # Settings & env vars
│   ├── routers/
│   │   ├── documents.py            # Upload, list, delete
│   │   ├── chat.py                 # Ask questions
│   │   └── settings.py             # LLM provider config
│   ├── services/
│   │   ├── pdf_processor.py        # Extract text, tables, OCR
│   │   ├── chunker.py              # Smart chunking with overlap
│   │   ├── embedder.py             # sentence-transformers
│   │   ├── retriever.py            # ChromaDB search
│   │   ├── generator.py            # LLM answer generation
│   │   └── rag_pipeline.py         # Orchestrates everything
│   ├── models/
│   │   └── schemas.py              # Pydantic models
│   ├── evaluation/
│   │   ├── eval_dataset.json       # 50 Q&A pairs
│   │   ├── run_eval.py             # RAGAS evaluation
│   │   └── results/
│   └── tests/
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   └── src/
│       ├── App.jsx
│       ├── App.css
│       ├── components/
│       │   ├── DocumentSidebar.jsx
│       │   ├── ChatPanel.jsx
│       │   ├── PdfViewer.jsx
│       │   └── UploadZone.jsx
│       └── api/
│           └── client.js
└── sample_docs/
```

## Build plan (14 days)

### Week 1 — Backend
- Day 1: Project setup, Docker skeleton, FastAPI health endpoint ✅ DONE
- Day 2: PDF processing (PyMuPDF + OCR fallback) ✅ DONE
- Day 3: Chunking + embedding + ChromaDB storage ✅ DONE
- Day 4: RAG retrieval + LLM generation with citations ✅ DONE
- Day 5: Polish API endpoints, error handling ✅ DONE

### Week 2 — Frontend + Polish
- Day 6-7: React UI (upload, chat, document sidebar) ✅ DONE
- Day 8: PDF viewer with citation highlighting
- Day 9: Multi-document comparison
- Day 10: RAGAS evaluation pipeline (50 Q&A test pairs)
- Day 11: pytest + GitHub Actions CI/CD
- Day 12: README with screenshots + architecture diagram
- Day 13: Edge cases (scanned PDFs, large files, errors)
- Day 14: Demo GIF, final polish, push to GitHub + DockerHub

## Key design decisions
- **Chroma over Pinecone:** Free, local, no account needed to demo
- **sentence-transformers over OpenAI embeddings:** Free, no API key needed
- **React over Streamlit:** Production look, not tutorial vibes
- **FastAPI over Flask:** Async, auto-docs, modern
- **Multi-provider LLM:** User picks Ollama (free local) or cloud API with own key
- **RAGAS evaluation:** This is what separates this project from every other RAG demo

## Settings UI
First launch shows a model settings screen:
- Local mode: Pick Ollama model from dropdown, no key needed
- Cloud API mode: Pick provider (OpenAI/Anthropic/Groq), paste API key, test connection
- Settings accessible from gear icon in sidebar afterward

## Code style
- Python: type hints, docstrings, proper error handling
- Clean separation: routers handle HTTP, services handle logic
- Every TODO comment references which Day it will be implemented
- Commit messages should be descriptive, not "update files"

## Current status
Day 6-7 complete. `frontend/src/api/client.js` gained `listDocuments`, `uploadDocument` (multipart `FormData`), `deleteDocument`, and `askQuestion`, all calling through the existing `/api` Axios instance (proxied to the backend by `vite.config.js`). `UploadZone.jsx` is a click-or-drag PDF dropzone that uploads immediately on file selection and reports the resulting `DocumentResponse` (including `error` status — the backend already returns 200 with `status: "error"` for failed processing, so the UI just renders that state rather than treating it as a request failure). `DocumentSidebar.jsx` renders the document list with a status badge per doc (`ready`/`processing`/`error`), a checkbox per document to scope chat (disabled unless `status === "ready"`), a delete button, and embeds `UploadZone`. `ChatPanel.jsx` holds a local message list (not persisted — resets on reload), disables the input/send until at least one document is selected, and renders citations (`Page N: text`) under each assistant message; failures from `POST /chat` (e.g. the `502` a misconfigured LLM provider produces) surface as an inline error message rather than breaking the panel. `App.jsx` now owns `documents` and `selectedIds` state, fetches the document list once on mount alongside the existing health check, and wires upload/delete/select callbacks down to the two components; `PdfViewer.jsx` is still a Day-8 stub. `App.css` was rewritten for a two-pane layout (sidebar + chat) instead of the single centered health-check box. Verified by running the actual backend (`uvicorn`) and frontend (`vite`) dev servers and exercising upload → list → chat (502, no local Ollama available in this environment, which correctly triggered the chat panel's error path) → delete through the real `/api` proxy path, plus `npm run build` to confirm no build errors. No new frontend tests were added — this project doesn't have a JS test runner configured yet. TODO(Day 8+): `PdfViewer.jsx` (citation highlighting), settings UI for the persisted `PUT /settings` from Day 5, chat history persistence.

Day 5 complete. `services/settings_store.py` persists the active LLM provider/model/API key in the same SQLite file as document metadata (single-row `llm_settings` table), mirroring `document_store.py`'s connect/save pattern. `routers/settings.py` `GET /settings` now returns the persisted override if one exists, else the env-configured provider/model from `config.py`; `PUT /settings` calls `services/generator.test_connection()` — a real request to the given provider using a trivial prompt — before persisting, returning `400` if the provider/key is unreachable or invalid instead of blindly saving. `services/generator.py` was refactored so `generate_answer()` resolves its provider/model/api_key via `_active_provider_config()` (persisted override first, env defaults as fallback) and both it and `test_connection()` share a common `_dispatch()` path to the per-provider `_generate_*` functions, which now take `model`/`api_key` as parameters instead of reading `config.py` directly. `services/document_store.py` gained a `get(document_id)` lookup used by two new validation paths: `DELETE /documents/{id}` now 404s for unknown IDs instead of silently no-op'ing, and `POST /chat` 400s on an empty question or empty `document_ids`, and 404s if any `document_id` doesn't exist in the store, before calling into `rag_pipeline`. `routers/documents.py`'s upload flow now wraps chunking/embedding/ChromaDB-store in a `try/except Exception` that marks the document `error` (matching the existing `PDFProcessingError` handling) instead of letting an unexpected failure surface as a raw `500`. No new third-party deps. Tests: new `tests/test_settings.py` (get defaults, put persists, put rejects missing key / failed connection, failed validation doesn't persist); `tests/test_documents.py` gained delete-404 and upload-marks-error cases; `tests/test_chat.py` gained empty-question/empty-document_ids/unknown-document_id cases and now stubs `routers.chat.document_store.get` via an autouse fixture since the chat router validates document existence before answering; `tests/test_generator.py` needed a `CLEARANCEDOC_DB_PATH` env override added to its fixture (it wasn't isolating the SQLite path before, so `generate_answer()` calls now fail under the default `/data/...` path outside Docker without it). All 44 backend tests pass. TODO(Day 6+): no persisted-settings UI yet on the frontend side; still only reachable via `PUT /settings` directly.
