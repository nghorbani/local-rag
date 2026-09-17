# Local-RAG

Retrieval-augmented generation over scanned documents that never leave your machine. Images are
OCR'd with a local Ollama model, the text is stored as Markdown, chunked and embedded into
PostgreSQL with pgvector, and a Flask UI offers semantic search and chat over the results.

## State of the code (2026-09-17)

Implemented:

- `local_rag.config`: a `Settings` dataclass loaded and validated from `.env` (`get_settings()`).
- `local_rag.db`: SQLAlchemy models `documents` and `chunks`, engine and session helpers, and
  `bootstrap(engine, settings)`, which creates the pgvector extension, the tables and the HNSW
  index (`HNSW_M`, `HNSW_EF_CONSTRUCTION`).

Not implemented yet: the OCR runner, the Markdown store and document scanner, chunking, the
embedding client, search, the chat agent and the Flask UI. The tests cover what exists.

## Prerequisites

- Python 3.12 and [uv](https://docs.astral.sh/uv/).
- [Ollama](https://ollama.com/) reachable at the URLs in `.env`, with the models pulled:
  `qwen2.5-vl:3b` for OCR, `snowflake-arctic-embed2` for embeddings and `deepseek-r1:1.5b` for
  chat. When Ollama is reached through a tunnel on `localhost:11434`, use its OpenAI-compatible
  endpoints (`/v1/chat/completions` for chat, `/v1/embeddings` for embeddings) rather than the
  native API.
- PostgreSQL with the [pgvector](https://github.com/pgvector/pgvector) extension, for example the
  `pgvector/pgvector:pg16` Docker image.

## Install

```bash
uv sync              # runtime dependencies
uv sync --extra dev  # plus pytest, ruff, mypy
```

## Configure

```bash
cp .env.example .env
```

Fill in the model names and API URLs for OCR, embedding and chat, the PostgreSQL connection
(`PG_HOST`, `PG_PORT`, `PG_USER`, `PG_PASSWORD`, `PG_DATABASE`), the app host and port, and
`DOC_ROOT`, the directory that holds the scanned images and the generated Markdown files.
`get_settings()` raises a `ValueError` when a key is missing or an integer is malformed.

## Run

Create the database objects:

```bash
uv run python -c "from local_rag.config import get_settings; from local_rag.db import bootstrap, get_engine; s = get_settings(); bootstrap(get_engine(s), s)"
```

The Flask application is not written yet; it will read `APP_HOST` and `APP_PORT` from `.env`.

## Tests

```bash
uv run pytest
```

The tests mock the database and need neither PostgreSQL nor Ollama. A sample scan for later OCR
tests lives at `assets/sample.jpg`.

## Licence

Apache-2.0, see [LICENSE](LICENSE).
