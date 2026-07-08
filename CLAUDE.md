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
Day 3 complete. `services/chunker.py` splits each page's text into overlapping token windows (`chunk_size`/`chunk_overlap` from `config.py`, default 512/50) using the `all-MiniLM-L6-v2` tokenizer; chunks never span page boundaries so each one carries a single citable page number. `services/embedder.py` embeds chunk text locally via `sentence-transformers` (`all-MiniLM-L6-v2`). `services/retriever.py` wraps a persistent ChromaDB collection (`config.chroma_persist_dir`) with `add_chunks`, `query` (optionally scoped to `document_ids`), and `delete_document`. `routers/documents.py` wires these together: `POST /documents` now chunks, embeds, and stores each upload's text in ChromaDB instead of an in-memory dict, and `DELETE /documents/{id}` also purges the document's chunks from ChromaDB. Document *metadata* (id, filename, status) is still an in-memory dict — TODO(Day 4): move to persistent storage alongside wiring up retrieval + LLM generation with citations in `rag_pipeline.py`/`generator.py`. Tests: `tests/test_chunker.py`, `tests/test_embedder.py`, `tests/test_retriever.py` (unit), `tests/test_documents.py` (end-to-end upload/list/delete through the real chunk→embed→ChromaDB pipeline).
