#!/usr/bin/env python3
"""
Database Cleanup Script for LightRAG
This script deletes all LightRAG data, graphs, and entities from PostgreSQL database.

WARNING: This operation is IRREVERSIBLE. All your data will be permanently deleted.
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    import asyncpg
except ImportError:
    print("❌ Error: asyncpg is not installed.")
    print("Install it with: pip install asyncpg")
    sys.exit(1)

# Database connection parameters from environment variables
DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": int(os.getenv("POSTGRES_PORT", "5432")),
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", "postgres"),
    "database": os.getenv("POSTGRES_DATABASE", "postgres")
}

# All LightRAG tables to be cleaned
LIGHTRAG_TABLES = [
    'lightrag_llm_cache',
    'lightrag_doc_full',
    'lightrag_doc_chunks',
    'lightrag_doc_status',
    'lightrag_vdb_chunks',
    'lightrag_vdb_entity',
    'lightrag_vdb_relation',
    'lightrag_full_entities',
    'lightrag_full_relations',
]


async def check_database_connection():
    """Test database connection"""
    try:
        conn = await asyncpg.connect(**DB_CONFIG)
        await conn.close()
        return True
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        return False


async def get_existing_tables(conn):
    """Get list of existing LightRAG tables"""
    query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name LIKE 'lightrag_%'
        ORDER BY table_name;
    """
    rows = await conn.fetch(query)
    return [row['table_name'] for row in rows]


async def get_table_counts(conn, tables):
    """Get row counts for all tables"""
    counts = {}
    for table in tables:
        try:
            query = f"SELECT COUNT(*) as count FROM {table}"
            result = await conn.fetchval(query)
            counts[table] = result
        except Exception as e:
            counts[table] = f"Error: {e}"
    return counts


async def truncate_table(conn, table_name):
    """Truncate a single table"""
    try:
        await conn.execute(f"TRUNCATE TABLE {table_name} CASCADE")
        return True, None
    except Exception as e:
        return False, str(e)


async def drop_table(conn, table_name):
    """Drop a single table"""
    try:
        await conn.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE")
        return True, None
    except Exception as e:
        return False, str(e)


async def clean_apache_age_graphs(conn):
    """Clean Apache AGE graph data if it exists"""
    try:
        # Check if ag_catalog schema exists
        check_schema = """
            SELECT schema_name
            FROM information_schema.schemata
            WHERE schema_name = 'ag_catalog'
        """
        schema_exists = await conn.fetch(check_schema)
        
        if not schema_exists:
            print("ℹ️  Apache AGE not installed, skipping graph cleanup")
            return True, None
        
        # Get all graphs
        get_graphs = """
            SELECT name FROM ag_catalog.ag_graph
        """
        graphs = await conn.fetch(get_graphs)
        
        if not graphs:
            print("ℹ️  No Apache AGE graphs found")
            return True, None
        
        print(f"\n📊 Found {len(graphs)} Apache AGE graph(s):")
        for graph in graphs:
            print(f"   - {graph['name']}")
        
        # Drop each graph
        for graph in graphs:
            graph_name = graph['name']
            try:
                await conn.execute('SET search_path = ag_catalog, "$user", public')
                await conn.execute(f"SELECT drop_graph('{graph_name}', true)")
                print(f"   ✅ Dropped graph: {graph_name}")
            except Exception as e:
                print(f"   ⚠️  Error dropping graph {graph_name}: {e}")
        
        return True, None
        
    except Exception as e:
        return False, str(e)


async def show_database_status(conn):
    """Show current database status"""
    print("\n" + "=" * 70)
    print("📊 CURRENT DATABASE STATUS")
    print("=" * 70)
    
    existing_tables = await get_existing_tables(conn)
    
    if not existing_tables:
        print("\n✨ No LightRAG tables found in database")
        return
    
    print(f"\nFound {len(existing_tables)} LightRAG table(s):\n")
    
    counts = await get_table_counts(conn, existing_tables)
    
    total_rows = 0
    for table, count in counts.items():
        if isinstance(count, int):
            total_rows += count
            print(f"  📋 {table.upper():<35} {count:>10,} rows")
        else:
            print(f"  📋 {table.upper():<35} {count}")
    
    print(f"\n  {'TOTAL ROWS:':<35} {total_rows:>10,}")
    print("=" * 70)


async def confirm_cleanup(mode='truncate'):
    """Ask user for confirmation"""
    action = "TRUNCATE (clear data)" if mode == 'truncate' else "DROP (delete tables)"
    
    print("\n" + "⚠️ " * 35)
    print("⚠️  WARNING: DESTRUCTIVE OPERATION")
    print("⚠️ " * 35)
    print(f"\nYou are about to {action} all LightRAG data:")
    print("  • All documents and chunks")
    print("  • All vector embeddings")
    print("  • All entities and relations")
    print("  • All knowledge graphs")
    print("  • All LLM cache")
    print("  • All processing status")
    
    if mode == 'drop':
        print("\n⚠️  DROP mode will permanently delete the table structures!")
    
    print("\n❗ THIS OPERATION CANNOT BE UNDONE!")
    print("\nDatabase:", DB_CONFIG['database'])
    print("Host:", DB_CONFIG['host'])
    print("Port:", DB_CONFIG['port'])
    
    response = input("\nType 'YES' (in capitals) to confirm: ")
    return response == "YES"


async def cleanup_database(mode='truncate', skip_confirmation=False):
    """
    Main cleanup function
    
    Args:
        mode: 'truncate' to clear data but keep tables, 'drop' to delete tables entirely
        skip_confirmation: Skip user confirmation (use with caution!)
    """
    print("\n" + "=" * 70)
    print("🧹 LIGHTRAG DATABASE CLEANUP TOOL")
    print("=" * 70)
    print(f"\nMode: {mode.upper()}")
    print(f"Database: {DB_CONFIG['database']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}")
    
    # Check connection
    print("\n🔌 Checking database connection...")
    if not await check_database_connection():
        return False
    print("✅ Database connection successful")
    
    # Connect to database
    conn = await asyncpg.connect(**DB_CONFIG)
    
    try:
        # Show current status
        await show_database_status(conn)
        
        existing_tables = await get_existing_tables(conn)
        
        if not existing_tables:
            print("\n✨ Database is already clean. Nothing to do.")
            return True
        
        # Ask for confirmation
        if not skip_confirmation:
            if not await confirm_cleanup(mode):
                print("\n❌ Operation cancelled by user")
                return False
        
        print("\n" + "=" * 70)
        print(f"🚀 Starting cleanup ({mode} mode)...")
        print("=" * 70)
        
        # Clean tables
        success_count = 0
        error_count = 0
        
        for table in existing_tables:
            if mode == 'truncate':
                success, error = await truncate_table(conn, table)
                action = "Truncated"
            else:  # drop
                success, error = await drop_table(conn, table)
                action = "Dropped"
            
            if success:
                print(f"✅ {action}: {table}")
                success_count += 1
            else:
                print(f"❌ Failed to {mode} {table}: {error}")
                error_count += 1
        
        # Clean Apache AGE graphs
        print("\n🔍 Checking for Apache AGE graphs...")
        graph_success, graph_error = await clean_apache_age_graphs(conn)
        if not graph_success:
            print(f"⚠️  Error cleaning graphs: {graph_error}")
        
        # Show final status
        print("\n" + "=" * 70)
        print("📊 CLEANUP SUMMARY")
        print("=" * 70)
        print(f"✅ Successfully processed: {success_count} tables")
        if error_count > 0:
            print(f"❌ Errors: {error_count} tables")
        
        if mode == 'truncate':
            print("\n✨ All LightRAG data has been cleared")
            print("   Tables still exist and can be reused")
        else:
            print("\n✨ All LightRAG tables have been dropped")
            print("   Tables will be recreated on next server start")
        
        # Show final database status
        await show_database_status(conn)
        
        print("\n" + "=" * 70)
        print("✅ CLEANUP COMPLETED SUCCESSFULLY")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during cleanup: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        await conn.close()


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Clean LightRAG database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Clear all data but keep table structures (default)
  python clean_database.py
  
  # Drop all tables completely
  python clean_database.py --drop
  
  # Truncate without confirmation (dangerous!)
  python clean_database.py --yes
  
  # Drop tables without confirmation (very dangerous!)
  python clean_database.py --drop --yes
        """
    )
    
    parser.add_argument(
        '--drop',
        action='store_true',
        help='Drop tables completely instead of truncating (more destructive)'
    )
    
    parser.add_argument(
        '--yes', '-y',
        action='store_true',
        help='Skip confirmation prompt (use with caution!)'
    )
    
    args = parser.parse_args()
    
    mode = 'drop' if args.drop else 'truncate'
    
    try:
        success = await cleanup_database(mode=mode, skip_confirmation=args.yes)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user (Ctrl+C)")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
