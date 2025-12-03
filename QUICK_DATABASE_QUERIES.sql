-- ============================================
-- Quick Database Queries for PDF Verification
-- Database: ${POSTGRES_DATABASE} @ ${POSTGRES_HOST}:${POSTGRES_PORT}
-- ============================================

-- Connect to database:
-- psql -h ${POSTGRES_HOST} -p ${POSTGRES_PORT} -U ${POSTGRES_USER} -d ${POSTGRES_DATABASE}
-- 
-- Default values (if not using environment variables):
-- psql -h localhost -p 5433 -U postgres -d airag

-- ============================================
-- 1. CHECK ALL PDF DOCUMENTS
-- ============================================
SELECT 
    id,
    file_path,
    status,
    content_length,
    chunks_count,
    created_at,
    updated_at
FROM lightrag_doc_status
WHERE file_path LIKE '%.pdf' OR file_path LIKE '%_processed.md'
ORDER BY created_at DESC;

-- ============================================
-- 2. COUNT DOCUMENTS BY STATUS
-- ============================================
SELECT 
    status,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
FROM lightrag_doc_status
GROUP BY status
ORDER BY count DESC;

-- ============================================
-- 3. CHECK FULL DOCUMENT STORAGE
-- ============================================
SELECT 
    id,
    doc_name,
    LENGTH(content) as content_length,
    create_time,
    update_time
FROM lightrag_doc_full
ORDER BY create_time DESC
LIMIT 20;

-- ============================================
-- 4. CHECK DOCUMENT CHUNKS
-- ============================================
SELECT 
    COUNT(*) as total_chunks,
    COUNT(DISTINCT full_doc_id) as unique_documents,
    SUM(tokens) as total_tokens,
    AVG(tokens) as avg_tokens_per_chunk,
    MIN(tokens) as min_tokens,
    MAX(tokens) as max_tokens
FROM lightrag_doc_chunks;

-- ============================================
-- 5. VIEW CHUNKS FOR A SPECIFIC DOCUMENT
-- ============================================
-- Replace 'doc-xxxxx' with actual document ID
SELECT 
    id,
    chunk_order_index,
    tokens,
    LEFT(content, 100) as content_preview,
    file_path
FROM lightrag_doc_chunks
WHERE full_doc_id = 'doc-e2a3fd9d5343a8ac3f72d98dfdd9a145'
ORDER BY chunk_order_index;

-- ============================================
-- 6. CHECK VECTOR EMBEDDINGS
-- ============================================
SELECT 
    COUNT(*) as total_vectors,
    COUNT(DISTINCT full_doc_id) as unique_documents,
    COUNT(CASE WHEN content_vector IS NOT NULL THEN 1 END) as vectors_with_embeddings
FROM lightrag_vdb_chunks;

-- ============================================
-- 7. CHECK ENTITIES EXTRACTED
-- ============================================
SELECT 
    COUNT(*) as total_entities,
    COUNT(DISTINCT entity_name) as unique_entity_names
FROM lightrag_full_entities;

-- Sample entities
SELECT 
    id,
    entity_name,
    LEFT(content, 100) as description,
    create_time
FROM lightrag_full_entities
ORDER BY create_time DESC
LIMIT 10;

-- ============================================
-- 8. CHECK RELATIONS EXTRACTED
-- ============================================
SELECT 
    COUNT(*) as total_relations
FROM lightrag_full_relations;

-- Sample relations
SELECT 
    id,
    src_id,
    tgt_id,
    LEFT(content, 100) as relation_description,
    create_time
FROM lightrag_full_relations
ORDER BY create_time DESC
LIMIT 10;

-- ============================================
-- 9. FIND FAILED DOCUMENTS
-- ============================================
SELECT 
    id,
    file_path,
    content_length,
    error_msg,
    created_at,
    updated_at
FROM lightrag_doc_status
WHERE status = 'failed'
ORDER BY updated_at DESC;

-- ============================================
-- 10. CHECK PROCESSING TIMELINE
-- ============================================
SELECT 
    DATE(created_at) as processing_date,
    COUNT(*) as documents_processed,
    SUM(CASE WHEN status = 'processed' THEN 1 ELSE 0 END) as successful,
    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed
FROM lightrag_doc_status
GROUP BY DATE(created_at)
ORDER BY processing_date DESC;

-- ============================================
-- 11. CHECK SPECIFIC PDF BY NAME
-- ============================================
-- Replace 'filename.pdf' with actual filename
SELECT 
    ds.id,
    ds.file_path,
    ds.status,
    ds.content_length,
    ds.chunks_count,
    df.doc_name,
    LENGTH(df.content) as stored_content_length,
    ds.created_at,
    ds.updated_at
FROM lightrag_doc_status ds
LEFT JOIN lightrag_doc_full df ON ds.id = df.id
WHERE ds.file_path = 'leph108.pdf';

-- ============================================
-- 12. GET DOCUMENT PROCESSING DETAILS
-- ============================================
-- Replace 'doc-xxxxx' with actual document ID
SELECT 
    'Document Status' as info_type,
    json_build_object(
        'id', id,
        'file_path', file_path,
        'status', status,
        'content_length', content_length,
        'chunks_count', chunks_count,
        'created_at', created_at,
        'updated_at', updated_at
    ) as details
FROM lightrag_doc_status
WHERE id = 'doc-e2a3fd9d5343a8ac3f72d98dfdd9a145'

UNION ALL

SELECT 
    'Chunks Info' as info_type,
    json_build_object(
        'total_chunks', COUNT(*),
        'total_tokens', SUM(tokens),
        'avg_tokens', AVG(tokens)
    ) as details
FROM lightrag_doc_chunks
WHERE full_doc_id = 'doc-e2a3fd9d5343a8ac3f72d98dfdd9a145';

-- ============================================
-- 13. CHECK DATABASE SIZE
-- ============================================
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
    AND tablename LIKE 'lightrag%'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- ============================================
-- 14. CHECK RECENT PROCESSING ACTIVITY
-- ============================================
SELECT 
    file_path,
    status,
    content_length,
    chunks_count,
    updated_at,
    AGE(NOW(), updated_at) as time_since_update
FROM lightrag_doc_status
ORDER BY updated_at DESC
LIMIT 20;

-- ============================================
-- 15. VERIFY DATA CONSISTENCY
-- ============================================
-- Check if all documents in status table have full content
SELECT 
    ds.id,
    ds.file_path,
    ds.status,
    CASE 
        WHEN df.id IS NULL THEN 'Missing in doc_full'
        ELSE 'Present'
    END as full_doc_status,
    CASE 
        WHEN dc.full_doc_id IS NULL THEN 'No chunks'
        ELSE 'Has chunks'
    END as chunks_status
FROM lightrag_doc_status ds
LEFT JOIN lightrag_doc_full df ON ds.id = df.id
LEFT JOIN (
    SELECT DISTINCT full_doc_id 
    FROM lightrag_doc_chunks
) dc ON ds.id = dc.full_doc_id
WHERE ds.status = 'processed'
ORDER BY ds.created_at DESC;

-- ============================================
-- 16. SEARCH DOCUMENT CONTENT
-- ============================================
-- Replace 'search_term' with your search term
SELECT 
    df.id,
    df.doc_name,
    ds.file_path,
    ds.status,
    LEFT(df.content, 200) as content_preview
FROM lightrag_doc_full df
JOIN lightrag_doc_status ds ON df.id = ds.id
WHERE df.content ILIKE '%electromagnetic%'
LIMIT 10;

-- ============================================
-- 17. CHECK VECTOR SEARCH CAPABILITY
-- ============================================
-- Verify vector extension is installed
SELECT 
    extname,
    extversion
FROM pg_extension
WHERE extname = 'vector';

-- Check vector dimensions
SELECT 
    COUNT(*) as total_vectors,
    vector_dims(content_vector) as embedding_dimensions
FROM lightrag_vdb_chunks
WHERE content_vector IS NOT NULL
LIMIT 1;

-- ============================================
-- 18. GET WORKSPACE STATISTICS
-- ============================================
SELECT 
    workspace,
    COUNT(*) as total_documents,
    SUM(CASE WHEN status = 'processed' THEN 1 ELSE 0 END) as processed,
    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
    SUM(CASE WHEN status = 'processing' THEN 1 ELSE 0 END) as processing
FROM lightrag_doc_status
GROUP BY workspace;

-- ============================================
-- 19. CHECK AGE GRAPH EXTENSION
-- ============================================
-- Verify AGE extension is installed
SELECT 
    extname,
    extversion
FROM pg_extension
WHERE extname = 'age';

-- Check if lightrag_graph exists
SELECT * FROM ag_catalog.ag_graph WHERE name = 'lightrag_graph';

-- ============================================
-- 20. EXPORT DOCUMENT LIST TO CSV
-- ============================================
-- Run this to export document list
\copy (SELECT id, file_path, status, content_length, chunks_count, created_at FROM lightrag_doc_status ORDER BY created_at DESC) TO 'documents_list.csv' WITH CSV HEADER;

-- ============================================
-- USEFUL COMMANDS
-- ============================================
-- List all tables:
-- \dt

-- Describe table structure:
-- \d lightrag_doc_status

-- Show table sizes:
-- \dt+

-- Exit psql:
-- \q

-- ============================================
-- MAINTENANCE QUERIES
-- ============================================

-- Vacuum and analyze tables (run periodically)
VACUUM ANALYZE lightrag_doc_status;
VACUUM ANALYZE lightrag_doc_full;
VACUUM ANALYZE lightrag_doc_chunks;
VACUUM ANALYZE lightrag_vdb_chunks;

-- Check for dead tuples
SELECT 
    schemaname,
    tablename,
    n_live_tup,
    n_dead_tup,
    last_vacuum,
    last_autovacuum
FROM pg_stat_user_tables
WHERE schemaname = 'public'
    AND tablename LIKE 'lightrag%';
