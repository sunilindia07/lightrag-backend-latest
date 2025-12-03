# LightRAG Backend Service

This `backend/` directory contains the **API-only ingestion and knowledge-graph service** for LightRAG.

## Responsibilities

- **Document ingestion & indexing**
  - Accept documents via the FastAPI server (`lightrag.api.lightrag_server` / `create_document_routes`).
  - Chunk documents and compute embeddings.
  - Build and persist:
    - Chunk vectors
    - Entities & relations
    - Chunk–entity–relation graph
- **Graph & storage management**
  - Expose APIs to inspect and edit entities, relations, and their mappings (`create_graph_routes`).
  - Persist all data into the configured storages (e.g., PostgreSQL + Apache AGE via `PGKVStorage` / `PostgreSQLDB`).
- **No UI / retrieval**
  - Does **not** serve the Web UI.
  - Does **not** expose query / retrieval or Ollama emulation routes; those live in the separate `frontend/` copy.

## How to run (development)

From this `backend/` directory:

```bash
python -m lightrag.api.lightrag_server
```

The server starts a FastAPI app that exposes ingestion and graph APIs (see `/docs` for interactive documentation).

## Configuration

- Environment variables and `.env` in `backend/` configure:
  - LLM provider & model
  - Embedding provider & model
  - Storage backends (KV / vector / graph / doc status)
  - PostgreSQL connection details (when using Postgres-based storages)

## Dependencies

Python dependencies for this backend service are listed in `requirements.txt` in this directory. Install them into a virtual environment before running the server.
