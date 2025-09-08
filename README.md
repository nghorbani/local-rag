# Local-RAG System — Project Plan (Condensed)

A standalone library + Flask app for running retrieval-augmented generation (RAG) over scanned image documents stored locally.

TL;DR: Extract OCR from images, store as Markdown, chunk + embed text, index with Postgres+pgvector (HNSW), and provide search + chat UI powered by Ollama-compatible models.

This README has been updated to present a condensed 7-task incremental plan with testable milestones and a comprehensive checklist. Use the 7 tasks for step-by-step implementation and request one task at a time for visible progress.

- **Core flow:**
  1. Extract text from JPEG/PNG images using **Ollama OCR** (Qwen2.5-VL:3B model).
  2. Store extracted text as `.md` files under a document root directory.
  3. Chunk text, generate embeddings using **Snowflake Arctic Embed2**, and store vectors in **Postgres + pgvector (HNSW index)**.
  4. Run semantic similarity search over the embedded chunks.
  5. Provide a **chat interface** where queries are answered using document chunks as retrieval context, powered by **DeepSeek-R1:1.5B** through Ollama’s OpenAI-compatible API.

- **Infrastructure & tooling:**
  - Managed Python environment via `uv`.
  - Linting with `ruff`, testing with `pytest`.
  - Configuration via `.env` file with keys for OCR, embedding, chat models, pgvector DB, Flask app host/port, and doc root.
  - Library organized as:  
    ```
    local-rag/local_rag/[interface] [embedding] [chat agent] ...
    ```
  - Absolute imports only.
  - Test image located at `assets/sample.jpg`.

- **User Interface:**
  - Flask web app with:
    - Home page: lists documents with statuses (detected, OCR’d, embedded).
    - Document detail: image viewer (zoom/pan) side-by-side with read-only markdown text, plus buttons for OCR/embedding.
    - Search tab: semantic search on embeddings, results link to document detail.
    - Chat tab: conversational interface using embeddings as context.

---

## Condensed 7-Task Plan (incremental, testable, visible)

1) Scaffolding & Tooling
   - Repo skeleton, installable package `local_rag`, `pyproject.toml`, `.env.example`, `assets/sample.jpg`, basic tests.
   - Visible: package imports, `pytest` runs smoke test.

2) Config & DB bootstrap
   - Settings dataclass (load & validate `.env`), DB engine + session helpers, `db.bootstrap()` to create `pgvector` extension and tables (`documents`, `chunks`).
   - Visible: bootstrap script creates tables + extension against a local Postgres test instance; tests verify schema.

3) Storage & Document Discovery (crawler)
   - `MdStore` for Markdown read/write; scanner that discovers images under `DOC_ROOT` and registers `documents` rows with status flags.
   - Visible: scanner inserts document rows; MD read/write roundtrip tests pass.

4) OCR pipeline
   - Pluggable `OcrClient` (mockable), OCR runner that writes `.md` via `MdStore` and updates `documents.status_ocr`.
   - Visible: `.md` files created (or mocked), DB flags updated; tests mock OCR responses.

5) Chunking & Persistence
   - Deterministic `chunk_text(text, target_tokens, overlap)` and persist chunks into DB with `embedding NULL`.
   - Visible: chunk rows created for a document; tests assert boundaries, ordering, and NULL embeddings.

6) Embeddings & Indexing
   - `EmbedClient` with batching, persist vectors to `chunks.embedding` (pgvector), create HNSW index with tuned params.
   - Visible: chunks populated with embeddings; index exists; tests mock embeddings.

7) Search & Chat UI
   - pgvector KNN search helper, retriever logic, `ChatAgent` for RAG prompt assembly, and simple Flask UI (Home / Doc / Search / Chat).
   - Visible: Flask app runs; search returns results; chat uses retrieved context (mocked integration tests).

Notes:
- Optional items (CLI, batch jobs, tuning docs, CI lint gating) are follow-ups after core 7 tasks.
- Each task is designed to produce visible artifacts (files, DB objects, test assertions, or a running Flask endpoint).

---

## Acceptance Criteria: First Task (Scaffolding & Tooling)

Start with Task 1. Acceptance criteria:
- `local_rag/` package exists and is importable.
- `pyproject.toml` present with placeholders for runtime and dev dependencies.
- `.env.example` created with all keys listed in the original README (OCR, EMBED, CHAT, PG, APP, DOC_ROOT, HNSW, EMBED_BATCH_SIZE).
- `assets/sample.jpg` placeholder added.
- `tests/test_bootstrap.py` contains a smoke test that imports `local_rag` and ensures the package loads.
- Running `pytest` should run the smoke test (or at least run without import errors).

If this is acceptable, the next step is to implement Task 1 files and the minimal `local_rag.config` stub so tests can import. Request one task at a time; after Task 1 is implemented and verified, proceed to Task 2.

---

## Comprehensive Checklist (project-level)

- [x] Analyze README and condense into an incremental 7-task plan
- [ ] Task 1 — Scaffolding & Tooling
  - [ ] Create package directory `local_rag/` and `__init__.py`
  - [ ] Add `pyproject.toml` with runtime and dev deps placeholders
  - [ ] Add `.env.example` with required keys
  - [ ] Add `assets/sample.jpg` (placeholder)
  - [ ] Add `tests/test_bootstrap.py` smoke test
  - [ ] Add minimal `local_rag/config.py` stub for import-time safety
- [ ] Task 2 — Config & DB bootstrap
  - [ ] `Settings` dataclass + `get_settings()`
  - [ ] DB engine factory and session helper
  - [ ] `db.bootstrap()` creating `pgvector` extension and tables
  - [ ] Tests for settings validation and bootstrap (mocked/local PG)
- [ ] Task 3 — Storage & Document Discovery
  - [ ] `MdStore.write/read`
  - [ ] Scanner to register images as `documents` rows
  - [ ] Tests: MD roundtrip and scanner DB rows
- [ ] Task 4 — OCR pipeline
  - [ ] `OcrClient` pluggable + mockable implementation
  - [ ] OCR runner writing MD and updating DB
  - [ ] Tests: mocked OCR, MD creation, DB flag updates
- [ ] Task 5 — Chunking & Persistence
  - [ ] `chunk_text` deterministic implementation
  - [ ] Persist chunk rows with `embedding NULL`
  - [ ] Tests: boundaries, ordering, counts
- [ ] Task 6 — Embeddings & Indexing
  - [ ] `EmbedClient` (batching)
  - [ ] Persist vectors to `chunks.embedding`
  - [ ] Create HNSW index and expose tuning envs
  - [ ] Tests: mock embeddings and verify persistence and indexing
- [ ] Task 7 — Search & Chat UI
  - [ ] pgvector search helper
  - [ ] `ChatAgent` prompt builder and client
  - [ ] Flask app skeleton: home, doc, search, chat
  - [ ] Tests: Flask test client with mocked endpoints
- [ ] Optional follow-ups
  - [ ] CLI entrypoints
  - [ ] Lint/test CI gating
  - [ ] Tuning and monitoring docs

---

## Mapping to original README sections

- Original Task 0 → Task 1 (Scaffolding & Tooling)
- Original Tasks 1–2 → Task 2 (Config & DB bootstrap)
- Original Task 3 → Task 3 (Storage & Discovery)
- Original Task 4 → Task 4 (OCR)
- Original Task 5 → Task 5 (Chunking)
- Original Task 6 → Task 6 (Embeddings)
- Original Task 7 & 8 → Task 7 (Search & Chat UI)
- Remaining original tasks (batch jobs, CLI, tuning) are follow-ups.

---

## Next step

If you approve, I will implement Task 1 (Scaffolding & Tooling) now: create package files, `pyproject.toml`, `.env.example`, `assets/sample.jpg` (placeholder), `tests/test_bootstrap.py`, and a minimal `local_rag/config.py` stub so the test can import. This will be done one step at a time; I will create files and then wait for confirmation that file creation succeeded before proceeding to run tests.
