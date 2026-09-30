#!/usr/bin/env python3
"""Manual document chunking test script for developers."""

from __future__ import annotations

import argparse
import logging

from app.ingestion.repository_loader import RepositoryLoader
from app.chunking.chunker import DocumentChunker

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(description="Load a repository and inspect its chunking output.")
    parser.add_argument("repository_path", help="Path to a local repository to ingest and chunk.")
    parser.add_argument("--chunk-size", type=int, default=1000, help="Target chunk size in characters.")
    parser.add_argument("--chunk-overlap", type=int, default=150, help="Overlap between adjacent chunks in characters.")
    args = parser.parse_args()

    loader = RepositoryLoader()
    documents = loader.load(args.repository_path)
    chunker = DocumentChunker(chunk_size=args.chunk_size, chunk_overlap=args.chunk_overlap)
    chunks = chunker.chunk_documents(documents)

    print("=" * 80)
    print("CHUNKING SUMMARY")
    print("=" * 80)
    print(f"Repository: {args.repository_path}")
    print(f"Source documents: {len(documents)}")
    print(f"Generated chunks: {len(chunks)}")
    if chunks:
        print(f"Min chunk size: {min(len(c.content) for c in chunks)} chars")
        print(f"Max chunk size: {max(len(c.content) for c in chunks)} chars")
        print(f"Average chunk size: {sum(len(c.content) for c in chunks) / len(chunks):.1f} chars")

    for i, chunk in enumerate(chunks[:5]):
        print(f"\n[{i}] {chunk.chunk_id}")
        print(f"  source_path={chunk.source_path}")
        print(f"  file_type={chunk.file_type}")
        print(f"  lines={chunk.start_line}-{chunk.end_line}")
        print(f"  preview={chunk.content[:160]!r}")

    if len(chunks) > 5:
        print(f"\n... and {len(chunks) - 5} more chunks")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
