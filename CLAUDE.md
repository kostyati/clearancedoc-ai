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
- Day 3: Chunking + embedding + ChromaDB storage
- Day 4: RAG retrieval + LLM generation with citations
- Day 5: Polish API endpoints, error handling

### Week 2 — Frontend + Polish
- Day 6-7: React UI (upload, chat, document sidebar)
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
Day 2 complete. `services/pdf_processor.py` extracts text per-page via PyMuPDF and falls back to Tesseract OCR (rendering the page to an image) when a page has under 20 characters of native text. `routers/documents.py` wires this into `POST /documents`: saves the upload to `settings.upload_dir`, extracts text, and returns `status=ready` with `page_count`, or `status=error` for corrupted/unreadable PDFs. Documents and extracted page text are held in an in-memory dict for now — TODO(Day 3): replace with ChromaDB-backed storage after chunking/embedding. Tests in `tests/test_pdf_processor.py` cover native-text extraction, corrupted files, and the OCR fallback path.
