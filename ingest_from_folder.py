from __future__ import annotations

import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv

from lightrag.api.lightrag_server import get_application
from lightrag.api.config import global_args
from lightrag.api.routers.document_routes import pipeline_enqueue_file
from lightrag.kg.shared_storage import (
    initialize_pipeline_status,
    finalize_share_data,
)
from lightrag.utils import logger


# Load environment from backend/.env (OS environment takes precedence)
load_dotenv(dotenv_path=".env", override=False)


def get_batch_size() -> int:
    """Get ingestion batch size from env, default to 100 files per batch."""
    try:
        return int(os.getenv("INGEST_FILE_BATCH_SIZE", "100"))
    except ValueError:
        logger.warning("Invalid INGEST_FILE_BATCH_SIZE, falling back to 100")
        return 100


async def ingest_from_input_dir() -> None:
    """Ingest files from the configured input directory in parallel batches.

    - Scans the DocumentManager input directory for files.
    - Processes files in batches of N (INGEST_FILE_BATCH_SIZE, default 100).
    - Within each batch, enqueues files in parallel using the existing
      LightRAG pipeline (`pipeline_enqueue_file`).
    - After each batch, triggers `apipeline_process_enqueue_documents` to
      run the full chunking + graph/embedding pipeline.
    - Logs detailed progress and results.
    """

    # Build application and reuse the configured LightRAG + DocumentManager
    app = get_application(global_args)
    rag = app.state.rag
    doc_manager = app.state.doc_manager

    # Initialize storages and shared status
    await rag.initialize_storages()
    await initialize_pipeline_status()
    await rag.check_and_migrate_data()

    # Determine input directory:
    # - Prefer INGEST_INPUT_DIR env var if set (e.g., "inputs").
    # - Otherwise, default to the original configured input root (global_args.input_dir).
    #   This intentionally ignores the workspace subdirectory so we always read from
    #   the plain inputs folder instead of inputs/<workspace>.
    env_input_dir = os.getenv("INGEST_INPUT_DIR")
    if env_input_dir:
        input_dir = Path(env_input_dir)
    else:
        input_dir = Path(global_args.input_dir)
    if not input_dir.exists() or not input_dir.is_dir():
        logger.error(f"Input directory does not exist or is not a directory: {input_dir}")
        return

    # Collect files in input directory (excluding __enqueued__ and hidden dirs)
    files = [
        p
        for p in sorted(input_dir.iterdir())
        if p.is_file()
    ]

    total_files = len(files)
    if total_files == 0:
        logger.info(f"No files found in input directory: {input_dir}")
        # Still finalize storages below
    else:
        logger.info(f"Found {total_files} files to ingest from: {input_dir}")

    batch_size = get_batch_size()
    logger.info(f"Using INGEST_FILE_BATCH_SIZE={batch_size}")

    processed_files = 0

    try:
        # Process files in batches
        for start in range(0, total_files, batch_size):
            batch_files = files[start : start + batch_size]
            batch_number = start // batch_size + 1
            total_batches = (total_files + batch_size - 1) // batch_size

            logger.info(
                f"Starting batch {batch_number}/{total_batches} with {len(batch_files)} file(s)"
            )

            # Enqueue files in parallel
            enqueue_tasks = [
                pipeline_enqueue_file(rag, file_path)
                for file_path in batch_files
            ]

            results = await asyncio.gather(*enqueue_tasks, return_exceptions=True)

            successes = 0
            failures = 0

            for file_path, result in zip(batch_files, results):
                if isinstance(result, Exception):
                    failures += 1
                    logger.error(
                        f"Unexpected error enqueuing {file_path.name}: {result}"
                    )
                    continue

                success, track_id = result
                if success:
                    successes += 1
                    logger.info(
                        f"Enqueued file {file_path.name} successfully (track_id={track_id})"
                    )
                else:
                    failures += 1
                    logger.error(
                        f"Failed to enqueue file {file_path.name} (track_id={track_id})"
                    )

            processed_files += len(batch_files)
            logger.info(
                f"Completed batch {batch_number}/{total_batches}: "
                f"{successes} success, {failures} failed; "
                f"{processed_files}/{total_files} files seen so far"
            )

            # After enqueuing this batch, process all queued documents
            if successes > 0:
                logger.info(
                    f"Starting document processing for batch {batch_number} (" f"{successes} successfully enqueued file(s))"
                )
                await rag.apipeline_process_enqueue_documents()

    finally:
        # Finalize storages and shared data
        await rag.finalize_storages()
        finalize_share_data()
        logger.info("Ingestion run completed. Storages finalized.")


def main() -> None:
    """Entry point for CLI usage.

    Usage (from backend/ directory):

        python ingest_from_folder.py

    Ensure that backend/.env and backend/requirements.txt are configured and
    installed, and that the input directory contains the files to ingest.
    """

    asyncio.run(ingest_from_input_dir())


if __name__ == "__main__":
    main()
