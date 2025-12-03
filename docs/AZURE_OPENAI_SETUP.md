# Azure OpenAI Setup Guide

This guide explains how to configure LightRAG backend to use Azure OpenAI services instead of local Ollama.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Azure OpenAI Configuration](#azure-openai-configuration)
- [Environment Variables](#environment-variables)
- [Configuration Steps](#configuration-steps)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Azure Requirements

1. **Azure Subscription** - Active Azure subscription
2. **Azure OpenAI Resource** - Created in Azure Portal
3. **Model Deployments** - Deploy required models:
   - GPT-4o (or gpt-4, gpt-35-turbo) for LLM
   - text-embedding-3-small (or text-embedding-ada-002) for embeddings

### Get Azure OpenAI Credentials

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your Azure OpenAI resource
3. Get the following information:
   - **Endpoint**: `https://your-resource-name.openai.azure.com/`
   - **API Key**: Found in "Keys and Endpoint" section
   - **API Version**: e.g., `2024-02-15-preview`
   - **Deployment Names**: Names you gave to your model deployments

---

## Azure OpenAI Configuration

### Required Models

#### 1. LLM Model (for text generation)
- **Recommended**: `gpt-4o` or `gpt-4`
- **Alternative**: `gpt-35-turbo` (faster, lower cost)
- **Deployment Name**: Choose a name (e.g., `gpt-4o`)

#### 2. Embedding Model (for vector embeddings)
- **Recommended**: `text-embedding-3-small` (1536 dimensions)
- **Alternative**: `text-embedding-ada-002` (1536 dimensions)
- **Deployment Name**: Choose a name (e.g., `text-embedding-3-small`)

---

## Environment Variables

### Complete Configuration

Copy these settings to your `.env` file and replace with your actual values:

```env
# ============================================
# LLM Configuration (Azure OpenAI)
# ============================================
LLM_BINDING=azure_openai
LLM_MODEL=gpt-4o
LLM_BINDING_HOST=
LLM_BINDING_API_KEY=

# Azure OpenAI specific settings for LLM
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/

# ============================================
# Embedding Configuration (Azure OpenAI)
# ============================================
EMBEDDING_BINDING=azure_openai
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIM=1536
EMBEDDING_BINDING_API_KEY=your_azure_embedding_api_key_here
EMBEDDING_BINDING_HOST=

# Azure OpenAI specific settings for Embeddings
AZURE_EMBEDDING_DEPLOYMENT=text-embedding-3-small
AZURE_EMBEDDING_API_VERSION=2024-02-15-preview
AZURE_EMBEDDING_ENDPOINT=https://your-resource-name.openai.azure.com/

# ============================================
# Performance Settings
# ============================================
MAX_ASYNC=8
MAX_PARALLEL_INSERT=4
EMBEDDING_FUNC_MAX_ASYNC=16
EMBEDDING_BATCH_NUM=32
```

### Variable Descriptions

| Variable | Description | Example |
|----------|-------------|---------|
| `LLM_BINDING` | LLM provider | `azure_openai` |
| `LLM_MODEL` | Model name | `gpt-4o` |
| `AZURE_OPENAI_API_KEY` | Your Azure API key | `abc123...` |
| `AZURE_OPENAI_ENDPOINT` | Your Azure endpoint | `https://myresource.openai.azure.com/` |
| `AZURE_OPENAI_DEPLOYMENT` | Your LLM deployment name | `gpt-4o` |
| `AZURE_OPENAI_API_VERSION` | API version | `2024-02-15-preview` |
| `EMBEDDING_BINDING` | Embedding provider | `azure_openai` |
| `EMBEDDING_MODEL` | Embedding model | `text-embedding-3-small` |
| `EMBEDDING_DIM` | Embedding dimensions | `1536` |
| `AZURE_EMBEDDING_API_KEY` | Your Azure API key (can be same) | `abc123...` |
| `AZURE_EMBEDDING_ENDPOINT` | Your Azure endpoint (can be same) | `https://myresource.openai.azure.com/` |
| `AZURE_EMBEDDING_DEPLOYMENT` | Your embedding deployment name | `text-embedding-3-small` |
| `AZURE_EMBEDDING_API_VERSION` | API version | `2024-02-15-preview` |

---

## Configuration Steps

### Step 1: Create Azure OpenAI Resource

```bash
# Using Azure CLI (optional)
az cognitiveservices account create \
  --name myopenai \
  --resource-group myResourceGroup \
  --kind OpenAI \
  --sku S0 \
  --location eastus
```

Or create via [Azure Portal](https://portal.azure.com).

### Step 2: Deploy Models

In Azure Portal:

1. Navigate to your Azure OpenAI resource
2. Go to "Model deployments" → "Manage Deployments"
3. Click "Create new deployment"

**Deploy LLM Model:**
- Model: `gpt-4o` (or `gpt-4`, `gpt-35-turbo`)
- Deployment name: `gpt-4o` (or your choice)
- Deployment type: Standard

**Deploy Embedding Model:**
- Model: `text-embedding-3-small` (or `text-embedding-ada-002`)
- Deployment name: `text-embedding-3-small` (or your choice)
- Deployment type: Standard

### Step 3: Get Credentials

1. Go to "Keys and Endpoint" in your Azure OpenAI resource
2. Copy:
   - **KEY 1** or **KEY 2** (your API key)
   - **Endpoint** URL

### Step 4: Update .env File

```bash
# Copy example file
cp .env.example .env

# Edit with your values
nano .env
```

Replace these placeholders:
- `your_azure_openai_api_key_here` → Your actual API key
- `your_azure_embedding_api_key_here` → Your actual API key (can be same)
- `your-resource-name` → Your Azure resource name
- `gpt-4o` → Your LLM deployment name (if different)
- `text-embedding-3-small` → Your embedding deployment name (if different)

### Step 5: Update Database Schema (if needed)

If you were using a different embedding dimension before (e.g., 1024 for bge-m3), you need to update the database:

```sql
-- Connect to your database
psql -h localhost -p 5433 -U postgres -d airag

-- Drop existing vector columns (WARNING: This will delete existing embeddings)
ALTER TABLE lightrag_vdb_chunks DROP COLUMN IF EXISTS content_vector;
ALTER TABLE lightrag_vdb_entity DROP COLUMN IF EXISTS content_vector;
ALTER TABLE lightrag_vdb_relation DROP COLUMN IF EXISTS content_vector;

-- Recreate with new dimensions (1536 for Azure OpenAI)
ALTER TABLE lightrag_vdb_chunks ADD COLUMN content_vector VECTOR(1536);
ALTER TABLE lightrag_vdb_entity ADD COLUMN content_vector VECTOR(1536);
ALTER TABLE lightrag_vdb_relation ADD COLUMN content_vector VECTOR(1536);

-- Recreate indexes
CREATE INDEX idx_lightrag_vdb_chunks_hnsw_cosine 
ON lightrag_vdb_chunks 
USING hnsw (content_vector vector_cosine_ops);

CREATE INDEX idx_lightrag_vdb_entity_hnsw_cosine 
ON lightrag_vdb_entity 
USING hnsw (content_vector vector_cosine_ops);

CREATE INDEX idx_lightrag_vdb_relation_hnsw_cosine 
ON lightrag_vdb_relation 
USING hnsw (content_vector vector_cosine_ops);
```

**Note:** If starting fresh, the system will automatically create tables with correct dimensions.

---

## Verification

### Test Configuration

```bash
# Start the server
python -m lightrag.api.lightrag_server
```

Check the startup logs for:
```
✅ LLM binding: azure_openai
✅ LLM model: gpt-4o
✅ Embedding binding: azure_openai
✅ Embedding model: text-embedding-3-small
✅ Embedding dimensions: 1536
```

### Test API

```bash
# Test LLM
curl -X POST "http://localhost:9621/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Hello, how are you?", "mode": "local"}'

# Test document upload (will test embeddings)
curl -X POST "http://localhost:9621/documents/upload" \
  -F "file=@test.pdf"
```

### Verify in Python

```python
import os
from dotenv import load_dotenv

load_dotenv()

# Check configuration
print(f"LLM Binding: {os.getenv('LLM_BINDING')}")
print(f"LLM Model: {os.getenv('LLM_MODEL')}")
print(f"Embedding Binding: {os.getenv('EMBEDDING_BINDING')}")
print(f"Embedding Model: {os.getenv('EMBEDDING_MODEL')}")
print(f"Embedding Dim: {os.getenv('EMBEDDING_DIM')}")
print(f"Azure Endpoint: {os.getenv('AZURE_OPENAI_ENDPOINT')}")
```

---

## Troubleshooting

### Common Issues

#### 1. Authentication Error

**Error:** `401 Unauthorized` or `Access denied`

**Solution:**
- Verify API key is correct
- Check if key is active in Azure Portal
- Ensure no extra spaces in `.env` file

```bash
# Test API key
curl -X POST "https://your-resource-name.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-02-15-preview" \
  -H "Content-Type: application/json" \
  -H "api-key: YOUR_API_KEY" \
  -d '{"messages":[{"role":"user","content":"Hello"}]}'
```

#### 2. Deployment Not Found

**Error:** `DeploymentNotFound` or `404 Not Found`

**Solution:**
- Verify deployment name matches exactly
- Check deployment is in "Succeeded" state
- Ensure API version is correct

```bash
# List deployments
az cognitiveservices account deployment list \
  --name myopenai \
  --resource-group myResourceGroup
```

#### 3. Rate Limit Exceeded

**Error:** `429 Too Many Requests`

**Solution:**
- Reduce `MAX_ASYNC` and `EMBEDDING_FUNC_MAX_ASYNC`
- Increase `EMBEDDING_BATCH_NUM` to batch requests
- Check your quota in Azure Portal

```env
# Reduce concurrency
MAX_ASYNC=4
EMBEDDING_FUNC_MAX_ASYNC=8
EMBEDDING_BATCH_NUM=16
```

#### 4. Wrong Embedding Dimensions

**Error:** `Vector dimension mismatch`

**Solution:**
- Ensure `EMBEDDING_DIM=1536` for Azure OpenAI
- Update database schema (see Step 5 above)
- Reprocess all documents

#### 5. Endpoint Format Error

**Error:** `Invalid endpoint format`

**Solution:**
- Ensure endpoint ends with `/`
- Format: `https://your-resource-name.openai.azure.com/`
- No `/openai/` or other paths

---

## Cost Optimization

### Tips to Reduce Costs

1. **Use GPT-3.5-Turbo for testing**
   ```env
   LLM_MODEL=gpt-35-turbo
   AZURE_OPENAI_DEPLOYMENT=gpt-35-turbo
   ```

2. **Reduce batch sizes**
   ```env
   DOCUMENT_PROCESSING_BATCH_SIZE=5
   MAX_ASYNC=4
   ```

3. **Use smaller embedding model** (if available)
   ```env
   EMBEDDING_MODEL=text-embedding-ada-002
   ```

4. **Monitor usage in Azure Portal**
   - Set up cost alerts
   - Review usage metrics
   - Implement rate limiting

---

## Performance Tuning

### Recommended Settings

#### For High Throughput
```env
MAX_ASYNC=16
MAX_PARALLEL_INSERT=8
EMBEDDING_FUNC_MAX_ASYNC=32
EMBEDDING_BATCH_NUM=64
```

#### For Rate Limit Compliance
```env
MAX_ASYNC=4
MAX_PARALLEL_INSERT=2
EMBEDDING_FUNC_MAX_ASYNC=8
EMBEDDING_BATCH_NUM=16
```

#### For Cost Optimization
```env
MAX_ASYNC=2
MAX_PARALLEL_INSERT=1
EMBEDDING_FUNC_MAX_ASYNC=4
EMBEDDING_BATCH_NUM=8
```

---

## Migration from Ollama

If you're migrating from Ollama to Azure OpenAI:

### 1. Backup Data
```bash
# Backup database
pg_dump -h localhost -p 5433 -U postgres airag > backup.sql
```

### 2. Update Configuration
- Change `.env` as shown above
- Update `EMBEDDING_DIM` from 1024 to 1536

### 3. Clear Old Embeddings
```sql
-- Option 1: Clear all embeddings (keep documents)
UPDATE lightrag_vdb_chunks SET content_vector = NULL;
UPDATE lightrag_vdb_entity SET content_vector = NULL;
UPDATE lightrag_vdb_relation SET content_vector = NULL;

-- Option 2: Start fresh (delete everything)
TRUNCATE TABLE lightrag_vdb_chunks CASCADE;
TRUNCATE TABLE lightrag_vdb_entity CASCADE;
TRUNCATE TABLE lightrag_vdb_relation CASCADE;
TRUNCATE TABLE lightrag_doc_status CASCADE;
```

### 4. Reprocess Documents
```bash
# Reprocess all documents
python ingest_from_folder.py
```

---

## Security Best Practices

### 1. Protect API Keys
```bash
# Never commit .env file
echo ".env" >> .gitignore

# Use environment variables in production
export AZURE_OPENAI_API_KEY="your-key"
```

### 2. Use Azure Key Vault (Production)
```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

credential = DefaultAzureCredential()
client = SecretClient(vault_url="https://myvault.vault.azure.net/", credential=credential)
api_key = client.get_secret("openai-api-key").value
```

### 3. Rotate Keys Regularly
- Use KEY 1 in production
- Rotate to KEY 2
- Regenerate KEY 1
- Update applications

### 4. Monitor Usage
- Set up Azure Monitor alerts
- Track API calls and costs
- Implement logging

---

## Additional Resources

- **Azure OpenAI Documentation**: https://learn.microsoft.com/en-us/azure/ai-services/openai/
- **API Reference**: https://learn.microsoft.com/en-us/azure/ai-services/openai/reference
- **Pricing**: https://azure.microsoft.com/en-us/pricing/details/cognitive-services/openai-service/
- **Quota Management**: https://learn.microsoft.com/en-us/azure/ai-services/openai/quotas-limits

---

## Support

For issues:
1. Check Azure OpenAI service health
2. Review application logs
3. Verify configuration with test scripts
4. Open issue on GitHub with error details

---

**Last Updated:** December 3, 2025
