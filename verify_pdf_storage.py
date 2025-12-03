"""
Verification Script: Check PDF Processing and Storage in PostgreSQL
This script verifies that PDF files are processed and stored in the airag database.
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime
import asyncpg
from typing import Dict, List, Any

# Database connection parameters
DB_CONFIG = {
    "host": "localhost",
    "port": 5433,
    "user": "postgres",
    "password": "postgres",
    "database": "airag"
}

async def check_database_connection():
    """Test database connection"""
    try:
        conn = await asyncpg.connect(**DB_CONFIG)
        print("✅ Successfully connected to PostgreSQL database 'airag'")
        await conn.close()
        return True
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        return False

async def check_tables_exist():
    """Check if LightRAG tables exist"""
    try:
        conn = await asyncpg.connect(**DB_CONFIG)
        
        # List of expected tables
        expected_tables = [
            'lightrag_doc_full',
            'lightrag_doc_chunks',
            'lightrag_doc_status',
            'lightrag_vdb_chunks',
            'lightrag_vdb_entity',
            'lightrag_vdb_relation',
            'lightrag_full_entities',
            'lightrag_full_relations'
        ]
        
        print("\n📊 Checking for LightRAG tables:")
        print("-" * 60)
        
        for table in expected_tables:
            query = f"""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = '{table}'
                );
            """
            exists = await conn.fetchval(query)
            status = "✅" if exists else "❌"
            print(f"{status} {table.upper()}")
        
        await conn.close()
        return True
    except Exception as e:
        print(f"❌ Error checking tables: {e}")
        return False

async def check_pdf_documents():
    """Check for PDF documents in the database"""
    try:
        conn = await asyncpg.connect(**DB_CONFIG)
        
        print("\n📄 Checking PDF Documents:")
        print("-" * 60)
        
        # Check LIGHTRAG_DOC_STATUS for PDF files
        query = """
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
            ORDER BY created_at DESC
            LIMIT 10;
        """
        
        rows = await conn.fetch(query)
        
        if rows:
            print(f"Found {len(rows)} PDF-related documents:\n")
            for i, row in enumerate(rows, 1):
                print(f"{i}. Document ID: {row['id']}")
                print(f"   File Path: {row['file_path']}")
                print(f"   Status: {row['status']}")
                print(f"   Content Length: {row['content_length']} chars")
                print(f"   Chunks Count: {row['chunks_count']}")
                print(f"   Created: {row['created_at']}")
                print(f"   Updated: {row['updated_at']}")
                print()
        else:
            print("⚠️  No PDF documents found in LIGHTRAG_DOC_STATUS table")
        
        await conn.close()
        return len(rows) > 0
    except Exception as e:
        print(f"❌ Error checking PDF documents: {e}")
        return False

async def check_full_documents():
    """Check full document content storage"""
    try:
        conn = await asyncpg.connect(**DB_CONFIG)
        
        print("\n📝 Checking Full Document Storage:")
        print("-" * 60)
        
        # Check LIGHTRAG_DOC_FULL for document content
        query = """
            SELECT 
                id,
                doc_name,
                LENGTH(content) as content_length,
                create_time,
                update_time
            FROM lightrag_doc_full
            ORDER BY create_time DESC
            LIMIT 10;
        """
        
        rows = await conn.fetch(query)
        
        if rows:
            print(f"Found {len(rows)} full documents stored:\n")
            for i, row in enumerate(rows, 1):
                print(f"{i}. Document ID: {row['id']}")
                print(f"   Doc Name: {row['doc_name']}")
                print(f"   Content Length: {row['content_length']} chars")
                print(f"   Created: {row['create_time']}")
                print(f"   Updated: {row['update_time']}")
                print()
        else:
            print("⚠️  No full documents found in LIGHTRAG_DOC_FULL table")
        
        await conn.close()
        return len(rows) > 0
    except Exception as e:
        print(f"❌ Error checking full documents: {e}")
        return False

async def check_document_chunks():
    """Check document chunks storage"""
    try:
        conn = await asyncpg.connect(**DB_CONFIG)
        
        print("\n🧩 Checking Document Chunks:")
        print("-" * 60)
        
        # Check LIGHTRAG_DOC_CHUNKS for chunks
        query = """
            SELECT 
                COUNT(*) as total_chunks,
                COUNT(DISTINCT full_doc_id) as unique_documents,
                SUM(tokens) as total_tokens
            FROM lightrag_doc_chunks;
        """
        
        row = await conn.fetchrow(query)
        
        if row and row['total_chunks'] > 0:
            print(f"✅ Total Chunks: {row['total_chunks']}")
            print(f"✅ Unique Documents: {row['unique_documents']}")
            print(f"✅ Total Tokens: {row['total_tokens']}")
            
            # Get sample chunks
            sample_query = """
                SELECT 
                    id,
                    full_doc_id,
                    file_path,
                    chunk_order_index,
                    tokens,
                    LEFT(content, 100) as content_preview
                FROM lightrag_doc_chunks
                ORDER BY create_time DESC
                LIMIT 5;
            """
            
            samples = await conn.fetch(sample_query)
            print(f"\nSample chunks (showing {len(samples)}):")
            for i, chunk in enumerate(samples, 1):
                print(f"\n{i}. Chunk ID: {chunk['id']}")
                print(f"   Doc ID: {chunk['full_doc_id']}")
                print(f"   File Path: {chunk['file_path']}")
                print(f"   Order: {chunk['chunk_order_index']}")
                print(f"   Tokens: {chunk['tokens']}")
                print(f"   Preview: {chunk['content_preview']}...")
        else:
            print("⚠️  No document chunks found in LIGHTRAG_DOC_CHUNKS table")
        
        await conn.close()
        return row and row['total_chunks'] > 0
    except Exception as e:
        print(f"❌ Error checking document chunks: {e}")
        return False

async def check_vector_embeddings():
    """Check vector embeddings storage"""
    try:
        conn = await asyncpg.connect(**DB_CONFIG)
        
        print("\n🔢 Checking Vector Embeddings:")
        print("-" * 60)
        
        # Check LIGHTRAG_VDB_CHUNKS for vector embeddings
        query = """
            SELECT 
                COUNT(*) as total_vectors,
                COUNT(DISTINCT full_doc_id) as unique_documents
            FROM lightrag_vdb_chunks
            WHERE content_vector IS NOT NULL;
        """
        
        row = await conn.fetchrow(query)
        
        if row and row['total_vectors'] > 0:
            print(f"✅ Total Vector Embeddings: {row['total_vectors']}")
            print(f"✅ Unique Documents with Vectors: {row['unique_documents']}")
        else:
            print("⚠️  No vector embeddings found in LIGHTRAG_VDB_CHUNKS table")
        
        await conn.close()
        return row and row['total_vectors'] > 0
    except Exception as e:
        print(f"❌ Error checking vector embeddings: {e}")
        return False

async def check_entities_and_relations():
    """Check extracted entities and relations"""
    try:
        conn = await asyncpg.connect(**DB_CONFIG)
        
        print("\n🔗 Checking Entities and Relations:")
        print("-" * 60)
        
        # Check entities
        entity_query = """
            SELECT COUNT(*) as total_entities
            FROM lightrag_full_entities;
        """
        
        entity_count = await conn.fetchval(entity_query)
        print(f"✅ Total Entities Extracted: {entity_count}")
        
        # Check relations
        relation_query = """
            SELECT COUNT(*) as total_relations
            FROM lightrag_full_relations;
        """
        
        relation_count = await conn.fetchval(relation_query)
        print(f"✅ Total Relations Extracted: {relation_count}")
        
        await conn.close()
        return entity_count > 0 or relation_count > 0
    except Exception as e:
        print(f"❌ Error checking entities and relations: {e}")
        return False

async def get_processing_statistics():
    """Get overall processing statistics"""
    try:
        conn = await asyncpg.connect(**DB_CONFIG)
        
        print("\n📈 Processing Statistics:")
        print("-" * 60)
        
        # Get status breakdown
        status_query = """
            SELECT 
                status,
                COUNT(*) as count
            FROM lightrag_doc_status
            GROUP BY status
            ORDER BY count DESC;
        """
        
        rows = await conn.fetch(status_query)
        
        if rows:
            print("Document Status Breakdown:")
            for row in rows:
                print(f"  {row['status']}: {row['count']} documents")
        else:
            print("⚠️  No documents in status table")
        
        await conn.close()
        return True
    except Exception as e:
        print(f"❌ Error getting statistics: {e}")
        return False

async def main():
    """Main verification function"""
    print("=" * 60)
    print("PDF Processing & Storage Verification")
    print("Database: airag (PostgreSQL)")
    print("=" * 60)
    
    # Run all checks
    checks = [
        ("Database Connection", check_database_connection()),
        ("Tables Existence", check_tables_exist()),
        ("PDF Documents", check_pdf_documents()),
        ("Full Documents", check_full_documents()),
        ("Document Chunks", check_document_chunks()),
        ("Vector Embeddings", check_vector_embeddings()),
        ("Entities & Relations", check_entities_and_relations()),
        ("Processing Statistics", get_processing_statistics()),
    ]
    
    results = []
    for name, check in checks:
        try:
            result = await check
            results.append((name, result))
        except Exception as e:
            print(f"❌ Error in {name}: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All checks passed! PDF files are being processed and stored correctly.")
    elif passed > 0:
        print("\n⚠️  Some checks passed. Review the failures above.")
    else:
        print("\n❌ All checks failed. Please verify database setup and configuration.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Verification interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
