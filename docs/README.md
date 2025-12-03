# Documentation

This directory contains comprehensive documentation for the LightRAG backend system.

## 📚 Available Documentation

### Setup & Configuration

- **[POSTGRESQL_SETUP.md](POSTGRESQL_SETUP.md)** - Complete PostgreSQL setup guide
  - Installation instructions for PostgreSQL 16
  - pgvector extension setup
  - Apache AGE installation
  - Database creation and configuration

- **[AZURE_OPENAI_SETUP.md](AZURE_OPENAI_SETUP.md)** - Azure OpenAI configuration guide
  - Azure OpenAI setup and deployment
  - LLM and embedding configuration
  - Migration from Ollama
  - Cost optimization and troubleshooting

- **[ENVIRONMENT_VARIABLES.md](ENVIRONMENT_VARIABLES.md)** - Environment variables reference
  - Complete list of all configuration options
  - Database connection settings
  - LLM and embedding configuration
  - Security best practices

### Verification & Testing

- **[VERIFICATION_SUMMARY.md](VERIFICATION_SUMMARY.md)** - Quick verification guide
  - How to verify PDF processing
  - Database connection testing
  - Quick reference for common checks

- **[PDF_PROCESSING_VERIFICATION_REPORT.md](PDF_PROCESSING_VERIFICATION_REPORT.md)** - Detailed verification report
  - Comprehensive system verification
  - Processing statistics
  - Troubleshooting guide

### Database

- **[QUICK_DATABASE_QUERIES.sql](QUICK_DATABASE_QUERIES.sql)** - Database inspection queries
  - 20+ ready-to-use SQL queries
  - Document status checks
  - Vector embedding verification
  - Performance monitoring

### Development

- **[GIT_PUSH_SUMMARY.md](GIT_PUSH_SUMMARY.md)** - Repository push summary
  - What was added to the repository
  - Commit history
  - File structure overview

## 🚀 Quick Start

1. **Setup Database:** Follow [POSTGRESQL_SETUP.md](POSTGRESQL_SETUP.md)
2. **Configure Azure OpenAI:** See [AZURE_OPENAI_SETUP.md](AZURE_OPENAI_SETUP.md)
3. **Configure Environment:** See [ENVIRONMENT_VARIABLES.md](ENVIRONMENT_VARIABLES.md)
4. **Verify Installation:** Use [VERIFICATION_SUMMARY.md](VERIFICATION_SUMMARY.md)
5. **Inspect Database:** Run queries from [QUICK_DATABASE_QUERIES.sql](QUICK_DATABASE_QUERIES.sql)

## 📖 Main Documentation

For general usage and API documentation, see the main [README.md](../README.md) in the root directory.

## 🔗 Related Files

- **Root README:** `../README.md` - Main project documentation
- **Environment Template:** `../.env.example` - Configuration template
- **Verification Script:** `../verify_pdf_storage.py` - Automated verification
- **Requirements:** `../requirements.txt` - Python dependencies
