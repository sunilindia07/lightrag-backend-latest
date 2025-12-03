# Environment Variables Reference

This document lists all environment variables used in the LightRAG backend system.

## 📋 Table of Contents

- [Database Configuration](#database-configuration)
- [Embedding Configuration](#embedding-configuration)
- [LLM Configuration](#llm-configuration)
- [Document Processing](#document-processing)
- [Server Configuration](#server-configuration)
- [Authentication](#authentication)
- [Web UI Configuration](#web-ui-configuration)

---

## Database Configuration

### PostgreSQL Connection

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `POSTGRES_HOST` | string | `localhost` | PostgreSQL server hostname |
| `POSTGRES_PORT` | integer | `5432` | PostgreSQL server port |
| `POSTGRES_USER` | string | `postgres` | Database username |
| `POSTGRES_PASSWORD` | string | `postgres` | Database password |
| `POSTGRES_DATABASE` | string | `postgres` | Database name |
| `POSTGRES_WORKSPACE` | string | `default` | Workspace identifier for multi-tenancy |

### Connection Pool Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `POSTGRES_MAX_CONNECTIONS` | integer | `50` | Maximum number of connections in pool |
| `POSTGRES_CONNECTION_RETRIES` | integer | `3` | Number of connection retry attempts |
| `POSTGRES_CONNECTION_RETRY_BACKOFF` | float | `0.5` | Initial retry backoff in seconds |
| `POSTGRES_CONNECTION_RETRY_BACKOFF_MAX` | float | `10.0` | Maximum retry backoff in seconds |
| `POSTGRES_POOL_CLOSE_TIMEOUT` | float | `5.0` | Pool close timeout in seconds |
| `POSTGRES_STATEMENT_CACHE_SIZE` | integer | `0` | Statement cache size (0 = disabled) |

### Vector Index Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `POSTGRES_VECTOR_INDEX_TYPE` | string | `HNSW` | Vector index type (`HNSW` or `IVFFLAT`) |
| `POSTGRES_HNSW_M` | integer | `16` | HNSW index M parameter |
| `POSTGRES_HNSW_EF` | integer | `64` | HNSW index EF parameter |
| `POSTGRES_IVFFLAT_LISTS` | integer | `100` | IVFFlat number of lists |

### SSL Configuration (Optional)

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `POSTGRES_SSL_MODE` | string | `None` | SSL mode (`disable`, `require`, `verify-ca`, `verify-full`) |
| `POSTGRES_SSL_CERT` | string | `None` | Path to client certificate |
| `POSTGRES_SSL_KEY` | string | `None` | Path to client key |
| `POSTGRES_SSL_ROOT_CERT` | string | `None` | Path to root certificate |
| `POSTGRES_SSL_CRL` | string | `None` | Path to certificate revocation list |

### Server Settings (Optional)

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `POSTGRES_SERVER_SETTINGS` | JSON | `None` | Server-specific settings (e.g., for Supabase) |

---

## Embedding Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `EMBEDDING_DIM` | integer | `1024` | Embedding vector dimensions |
| `EMBEDDING_BINDING` | string | `ollama` | Embedding provider (`ollama`, `openai`, etc.) |
| `EMBEDDING_MODEL` | string | `bge-m3:latest` | Embedding model name |
| `EMBEDDING_BINDING_HOST` | string | `http://localhost:11434` | Embedding service URL |

---

## LLM Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `LLM_BINDING` | string | `ollama` | LLM provider (`ollama`, `openai`, `azure`, etc.) |
| `LLM_MODEL` | string | `mistral-nemo:latest` | LLM model name |
| `LLM_BINDING_HOST` | string | `http://localhost:11434` | LLM service URL |

---

## Document Processing

### Batch Processing

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `DOCUMENT_PROCESSING_BATCH_SIZE` | integer | `10` | Number of documents per batch |
| `MAX_PARALLEL_INSERT` | integer | `2` | Maximum parallel document insertions |
| `MAX_ASYNC` | integer | `4` | Maximum async operations |

### Chunking Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `CHUNK_SIZE` | integer | `1200` | Maximum tokens per chunk |
| `CHUNK_OVERLAP_SIZE` | integer | `100` | Overlap tokens between chunks |

### PDF Preprocessing

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `PDF_PREPROCESS_MAX_CONCURRENCY` | integer | `2` | Maximum concurrent PDF preprocessing |
| `PDF_PREPROCESS_EXECUTOR` | string | `thread` | Executor type (`thread` or `process`) |

### Ingestion (for ingest_from_folder.py)

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `INGEST_FILE_BATCH_SIZE` | integer | `100` | Files per batch during folder ingestion |
| `INGEST_INPUT_DIR` | string | `None` | Override input directory for ingestion |

---

## Server Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `HOST` | string | `0.0.0.0` | Server bind address |
| `PORT` | integer | `9621` | Server port |
| `WORKING_DIR` | string | `./rag_storage` | Working directory for storage |
| `INPUT_DIR` | string | `./inputs` | Input directory for documents |

---

## Authentication

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `LIGHTRAG_API_KEY` | string | `None` | API key for authentication (optional) |

---

## Web UI Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `WEBUI_TITLE` | string | `LightRAG` | Web UI title |
| `WEBUI_DESCRIPTION` | string | `None` | Web UI description |

---

## Usage Examples

### Basic Configuration (.env file)

```env
# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DATABASE=airag
POSTGRES_WORKSPACE=default

# Embeddings
EMBEDDING_DIM=1024
EMBEDDING_MODEL=bge-m3:latest

# LLM
LLM_MODEL=mistral-nemo:latest

# Server
PORT=9621
WORKING_DIR=./rag_storage
```

### Production Configuration

```env
# Database with SSL
POSTGRES_HOST=your-db-server.com
POSTGRES_PORT=5432
POSTGRES_USER=lightrag_user
POSTGRES_PASSWORD=strong_password_here
POSTGRES_DATABASE=lightrag_prod
POSTGRES_SSL_MODE=verify-full
POSTGRES_SSL_ROOT_CERT=/path/to/ca-cert.pem

# Connection Pool
POSTGRES_MAX_CONNECTIONS=100
POSTGRES_CONNECTION_RETRIES=5

# Vector Index Optimization
POSTGRES_VECTOR_INDEX_TYPE=HNSW
POSTGRES_HNSW_M=32
POSTGRES_HNSW_EF=128

# Processing
DOCUMENT_PROCESSING_BATCH_SIZE=20
MAX_PARALLEL_INSERT=4
PDF_PREPROCESS_MAX_CONCURRENCY=4

# Authentication
LIGHTRAG_API_KEY=your_api_key_here
```

### Development Configuration

```env
# Local development
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DATABASE=airag_dev

# Local Ollama
LLM_BINDING_HOST=http://localhost:11434
EMBEDDING_BINDING_HOST=http://localhost:11434

# Debug settings
POSTGRES_STATEMENT_CACHE_SIZE=0
```

---

## Environment Variable Priority

The system loads environment variables in the following order (later sources override earlier ones):

1. **Default values** - Hardcoded in the application
2. **config.ini file** - Configuration file (if present)
3. **.env file** - Environment file in project root
4. **System environment** - OS-level environment variables

---

## Verification

To verify your environment variables are loaded correctly:

```bash
# Check if .env file exists
ls -la .env

# Test database connection with your settings
python verify_pdf_storage.py

# Start server and check logs
python -m lightrag.api.lightrag_server
```

---

## Security Best Practices

### ⚠️ Never Commit Sensitive Values

- ✅ **DO:** Use `.env` file (excluded by `.gitignore`)
- ✅ **DO:** Use `.env.example` for templates
- ❌ **DON'T:** Commit `.env` to version control
- ❌ **DON'T:** Hardcode passwords in code

### 🔒 Secure Your Database

```env
# Use strong passwords
POSTGRES_PASSWORD=use_a_strong_random_password_here

# Enable SSL in production
POSTGRES_SSL_MODE=verify-full
POSTGRES_SSL_ROOT_CERT=/path/to/ca-cert.pem
```

### 🔑 Protect API Keys

```env
# Use API key authentication
LIGHTRAG_API_KEY=generate_a_secure_random_key

# Rotate keys regularly
# Keep keys in secure secret management systems
```

---

## Troubleshooting

### Database Connection Issues

```bash
# Test connection manually
psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DATABASE

# Check if environment variables are loaded
python -c "import os; print(os.getenv('POSTGRES_HOST'))"
```

### Missing Environment Variables

```bash
# Copy example file
cp .env.example .env

# Edit with your values
nano .env

# Verify loading
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('POSTGRES_DATABASE'))"
```

### Port Conflicts

```bash
# Check if port is in use
netstat -an | grep 9621

# Change port in .env
PORT=9622
```

---

## References

- **PostgreSQL Documentation:** https://www.postgresql.org/docs/
- **pgvector Documentation:** https://github.com/pgvector/pgvector
- **Apache AGE Documentation:** https://age.apache.org/
- **Ollama Documentation:** https://ollama.ai/

---

**Last Updated:** December 3, 2025
