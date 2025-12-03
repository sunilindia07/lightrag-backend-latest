# LightRAG Backend - Latest

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)](https://www.postgresql.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A powerful **document ingestion and knowledge-graph service** for LightRAG with comprehensive PDF processing capabilities and PostgreSQL storage.

## 🎯 Key Features

- ✅ **PDF Processing Pipeline** - Upload, preprocess, and extract content from PDF files
- ✅ **PostgreSQL Storage** - Full integration with PostgreSQL + pgvector + Apache AGE
- ✅ **Document Chunking** - Intelligent text splitting with configurable chunk sizes
- ✅ **Vector Embeddings** - Generate and store embeddings for semantic search
- ✅ **Knowledge Graph** - Extract entities and relations automatically
- ✅ **Status Tracking** - Monitor document processing with detailed status updates
- ✅ **RESTful API** - Comprehensive FastAPI endpoints for all operations
- ✅ **Web UI** - Modern interface for document management and visualization
- ✅ **Verification Tools** - Built-in scripts to verify PDF processing and storage

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Features](#-features)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Verification](#-verification)
- [Database Schema](#-database-schema)
- [Troubleshooting](#-troubleshooting)
- [Documentation](#-documentation)

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL 16 with pgvector and Apache AGE extensions
- WSL2 (for Windows users)

### Installation

```bash
# Clone the repository
git clone https://github.com/sunilindia07/lightrag-backend-latest.git
cd lightrag-backend-latest

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings
```

### Database Setup

Follow the instructions in `postgresSQL_setup.txt` to set up PostgreSQL with required extensions.

```bash
# Quick setup (from WSL)
sudo service postgresql start
psql -h localhost -p 5433 -U postgres -d airag
```

### Run the Server

```bash
python -m lightrag.api.lightrag_server
```

Access the API at `http://localhost:9621/docs`

## ✨ Features

### Document Processing

- **PDF Upload** - Upload PDF files via API or Web UI
- **Preprocessing** - Convert PDFs to Markdown for better text extraction
- **OCR Support** - Extract text from scanned PDFs (with Tesseract)
- **Batch Processing** - Upload and process multiple files simultaneously
- **Status Tracking** - Real-time monitoring of document processing

### Storage & Retrieval

- **PostgreSQL Backend** - All data stored in PostgreSQL database
- **Vector Search** - pgvector integration for semantic similarity search
- **Knowledge Graph** - Apache AGE for graph-based entity relationships
- **Full-Text Search** - PostgreSQL full-text search capabilities
- **Efficient Chunking** - Configurable chunk sizes with overlap

### API Endpoints

- `/documents/upload` - Upload single document
- `/documents/batch-upload` - Upload multiple documents
- `/documents/list` - List all documents with status
- `/documents/status/{doc_id}` - Get document processing status
- `/documents/delete/{doc_id}` - Delete document
- `/query` - Query the knowledge base
- `/graph/*` - Graph management endpoints

### Verification Tools

- **verify_pdf_storage.py** - Comprehensive verification script
- **QUICK_DATABASE_QUERIES.sql** - 20+ SQL queries for inspection
- **PDF_PROCESSING_VERIFICATION_REPORT.md** - Detailed verification report
- **VERIFICATION_SUMMARY.md** - Quick reference summary

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     LightRAG Backend                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │   FastAPI    │───▶│  Document    │───▶│ PostgreSQL   │ │
│  │   Server     │    │  Processing  │    │   Database   │ │
│  └──────────────┘    └──────────────┘    └──────────────┘ │
│         │                    │                    │         │
│         │                    ▼                    │         │
│         │            ┌──────────────┐             │         │
│         │            │     PDF      │             │         │
│         │            │ Preprocessing│             │         │
│         │            └──────────────┘             │         │
│         │                    │                    │         │
│         ▼                    ▼                    ▼         │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │   Web UI     │    │   Chunking   │    │   pgvector   │ │
│  │  Interface   │    │  & Embedding │    │   (Vectors)  │ │
│  └──────────────┘    └──────────────┘    └──────────────┘ │
│                              │                    │         │
│                              ▼                    ▼         │
│                      ┌──────────────┐    ┌──────────────┐ │
│                      │   Entity &   │    │ Apache AGE   │ │
│                      │   Relation   │    │   (Graph)    │ │
│                      │  Extraction  │    │              │ │
│                      └──────────────┘    └──────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 📦 Installation

### Step 1: PostgreSQL Setup

```bash
# Install PostgreSQL 16
sudo apt install -y postgresql-16 postgresql-server-dev-16

# Install pgvector extension
sudo apt install -y postgresql-16-pgvector

# Install Apache AGE
cd ~
git clone https://github.com/apache/age.git
cd age
make PG_CONFIG=/usr/lib/postgresql/16/bin/pg_config
sudo make PG_CONFIG=/usr/lib/postgresql/16/bin/pg_config install

# Start PostgreSQL
sudo service postgresql start

# Create database and extensions
psql -h localhost -p 5433 -U postgres
CREATE DATABASE airag;
\c airag
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS age;
LOAD 'age';
SET search_path = ag_catalog, "$user", public;
SELECT create_graph('lightrag_graph');
```

### Step 2: Python Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install PDF preprocessing dependencies (optional)
pip install pdfplumber pymupdf pytesseract pillow markdownify pandas
```

### Step 3: Configuration

Create `.env` file from template:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=airag

# LLM Configuration
LLM_MODEL=ollama/qwen2.5:7b
EMBEDDING_MODEL=ollama/bge-m3:latest
EMBEDDING_DIM=1024

# Server Configuration
API_PORT=9621
WORKING_DIR=./workspace
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_HOST` | PostgreSQL host | localhost |
| `POSTGRES_PORT` | PostgreSQL port | 5433 |
| `POSTGRES_USER` | Database user | postgres |
| `POSTGRES_PASSWORD` | Database password | postgres |
| `POSTGRES_DB` | Database name | airag |
| `LLM_MODEL` | LLM model for extraction | ollama/qwen2.5:7b |
| `EMBEDDING_MODEL` | Embedding model | ollama/bge-m3:latest |
| `EMBEDDING_DIM` | Embedding dimensions | 1024 |
| `API_PORT` | API server port | 9621 |
| `WORKING_DIR` | Working directory | ./workspace |
| `PDF_PREPROCESS_MAX_CONCURRENCY` | PDF processing concurrency | 2 |

## 🎮 Usage

### Starting the Server

```bash
# Start the FastAPI server
python -m lightrag.api.lightrag_server

# Server will be available at:
# - API: http://localhost:9621
# - Docs: http://localhost:9621/docs
# - Web UI: http://localhost:9621/webui
```

### Uploading Documents

#### Via API

```bash
# Upload single PDF
curl -X POST "http://localhost:9621/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf"

# Batch upload
curl -X POST "http://localhost:9621/documents/batch-upload" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@doc1.pdf" \
  -F "files=@doc2.pdf"
```

#### Via Python

```python
import requests

# Upload document
with open('document.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:9621/documents/upload',
        files={'file': f}
    )
    print(response.json())
```

#### Via Web UI

1. Navigate to `http://localhost:9621/webui`
2. Click "Upload Documents"
3. Select PDF files
4. Monitor processing status

### Querying Documents

```python
import requests

# Query the knowledge base
response = requests.post(
    'http://localhost:9621/query',
    json={
        'query': 'What is electromagnetic radiation?',
        'mode': 'hybrid'
    }
)
print(response.json())
```

### Checking Document Status

```bash
# List all documents
curl "http://localhost:9621/documents/list"

# Get specific document status
curl "http://localhost:9621/documents/status/doc-abc123"
```

## 📚 API Documentation

### Document Endpoints

- **POST** `/documents/upload` - Upload single document
- **POST** `/documents/batch-upload` - Upload multiple documents
- **GET** `/documents/list` - List all documents
- **GET** `/documents/status/{doc_id}` - Get document status
- **DELETE** `/documents/delete/{doc_id}` - Delete document
- **POST** `/documents/preprocess-pdf` - Preprocess PDF to Markdown

### Query Endpoints

- **POST** `/query` - Query the knowledge base
- **GET** `/query/modes` - Get available query modes

### Graph Endpoints

- **GET** `/graph/entities` - List all entities
- **GET** `/graph/relations` - List all relations
- **GET** `/graph/entity/{entity_id}` - Get entity details
- **DELETE** `/graph/entity/{entity_id}` - Delete entity

### Pipeline Endpoints

- **POST** `/pipeline/process` - Process pending documents
- **GET** `/pipeline/status` - Get pipeline status
- **POST** `/pipeline/cancel` - Cancel pipeline processing

Full API documentation available at `/docs` when server is running.

## ✅ Verification

### Verify PDF Processing

Run the verification script to check if PDFs are being processed and stored:

```bash
python verify_pdf_storage.py
```

This will check:
- ✅ Database connection
- ✅ Table existence
- ✅ PDF documents in database
- ✅ Document chunks
- ✅ Vector embeddings
- ✅ Entities and relations
- ✅ Processing statistics

### Database Inspection

Use the provided SQL queries:

```bash
# Connect to database
psql -h localhost -p 5433 -U postgres -d airag

# Run queries from file
\i QUICK_DATABASE_QUERIES.sql
```

### Verification Reports

- **PDF_PROCESSING_VERIFICATION_REPORT.md** - Comprehensive report with findings
- **VERIFICATION_SUMMARY.md** - Quick reference summary

## 🗄️ Database Schema

### Main Tables

#### LIGHTRAG_DOC_STATUS
Tracks document processing status
```sql
CREATE TABLE LIGHTRAG_DOC_STATUS (
    id VARCHAR(255),
    workspace VARCHAR(255),
    file_path TEXT,
    status VARCHAR(50),
    content_length INTEGER,
    chunks_count INTEGER,
    chunks_list JSONB,
    track_id VARCHAR(255),
    metadata JSONB,
    error_msg TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    PRIMARY KEY (workspace, id)
);
```

#### LIGHTRAG_DOC_FULL
Stores complete document content
```sql
CREATE TABLE LIGHTRAG_DOC_FULL (
    id VARCHAR(255),
    workspace VARCHAR(255),
    doc_name VARCHAR(1024),
    content TEXT,
    meta JSONB,
    create_time TIMESTAMP,
    update_time TIMESTAMP,
    PRIMARY KEY (workspace, id)
);
```

#### LIGHTRAG_DOC_CHUNKS
Stores document chunks
```sql
CREATE TABLE LIGHTRAG_DOC_CHUNKS (
    id VARCHAR(255),
    workspace VARCHAR(255),
    full_doc_id VARCHAR(256),
    chunk_order_index INTEGER,
    tokens INTEGER,
    content TEXT,
    file_path TEXT,
    llm_cache_list JSONB,
    create_time TIMESTAMP,
    update_time TIMESTAMP,
    PRIMARY KEY (workspace, id)
);
```

#### LIGHTRAG_VDB_CHUNKS
Stores vector embeddings
```sql
CREATE TABLE LIGHTRAG_VDB_CHUNKS (
    id VARCHAR(255),
    workspace VARCHAR(255),
    full_doc_id VARCHAR(256),
    content TEXT,
    content_vector VECTOR(1024),
    file_path TEXT,
    create_time TIMESTAMP,
    update_time TIMESTAMP,
    PRIMARY KEY (workspace, id)
);
```

## 🔧 Troubleshooting

### PDF Processing Failures

**Issue:** PDFs fail to process

**Solutions:**
1. Check if PDF preprocessing dependencies are installed:
   ```bash
   pip install pdfplumber pymupdf pytesseract pillow markdownify
   ```
2. Verify Tesseract is installed for OCR:
   ```bash
   sudo apt install tesseract-ocr
   ```
3. Check file size - large PDFs may timeout
4. Review error logs in document status table

### Database Connection Issues

**Issue:** Cannot connect to PostgreSQL

**Solutions:**
1. Verify PostgreSQL is running:
   ```bash
   sudo service postgresql status
   ```
2. Check connection settings in `.env`
3. Verify port 5433 is accessible
4. Check PostgreSQL logs

### Vector Search Not Working

**Issue:** Vector search returns no results

**Solutions:**
1. Verify pgvector extension is installed:
   ```sql
   SELECT * FROM pg_extension WHERE extname = 'vector';
   ```
2. Check if embeddings are generated:
   ```sql
   SELECT COUNT(*) FROM lightrag_vdb_chunks WHERE content_vector IS NOT NULL;
   ```
3. Verify embedding model is running

### Memory Issues

**Issue:** Server crashes with large PDFs

**Solutions:**
1. Reduce `PDF_PREPROCESS_MAX_CONCURRENCY` in `.env`
2. Increase system memory
3. Process files in smaller batches
4. Use `PDF_PREPROCESS_EXECUTOR=process` for multiprocessing

## 📊 Performance

### Benchmarks

- **PDF Processing:** ~2-5 seconds per page
- **Chunking:** ~1000 tokens per second
- **Embedding Generation:** Depends on model and hardware
- **Vector Search:** <100ms for 10k vectors

### Optimization Tips

1. Use SSD for database storage
2. Increase PostgreSQL shared_buffers
3. Use connection pooling
4. Enable query caching
5. Batch document uploads

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [LightRAG](https://github.com/HKUDS/LightRAG) - Original LightRAG framework
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [PostgreSQL](https://www.postgresql.org/) - Powerful database
- [pgvector](https://github.com/pgvector/pgvector) - Vector similarity search
- [Apache AGE](https://age.apache.org/) - Graph database extension

## 📚 Documentation

Comprehensive documentation is available in the [`docs/`](docs/) directory:

- **[PostgreSQL Setup](docs/POSTGRESQL_SETUP.md)** - Database installation and configuration
- **[Environment Variables](docs/ENVIRONMENT_VARIABLES.md)** - Complete configuration reference
- **[Verification Guide](docs/VERIFICATION_SUMMARY.md)** - Testing and verification
- **[Database Queries](docs/QUICK_DATABASE_QUERIES.sql)** - SQL queries for inspection
- **[Verification Report](docs/PDF_PROCESSING_VERIFICATION_REPORT.md)** - Detailed system report

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check the [documentation](docs/)
- Review verification reports
- Run `python verify_pdf_storage.py`

## 🔗 Links

- **Repository:** https://github.com/sunilindia07/lightrag-backend-latest
- **Documentation:** [`docs/`](docs/) directory
- **API Docs:** See `/docs` endpoint when server is running
- **Issues:** https://github.com/sunilindia07/lightrag-backend-latest/issues

---

**Made with ❤️ for the LightRAG community**
