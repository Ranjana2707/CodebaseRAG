"""Data models for the document chunking pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class DocumentChunk:
    """
    Represents a single chunk of a repository document.

    A chunk is a portion of a larger source file, sized for retrieval
    and embedding. Each chunk preserves metadata about its source location
    and the original document.
    """

    chunk_id: str
    """Deterministic ID in format: 'src/file.py::chunk_0001'"""

    content: str
    """The text content of this chunk."""

    source_path: str
    """Repository-relative path to the source file."""

    file_type: str
    """File type category (e.g., 'python', 'java', 'markdown')."""

    chunk_index: int
    """Zero-based index of this chunk within its source document."""

    start_line: int
    """Line number where this chunk begins (1-based indexing)."""

    end_line: int
    """Line number where this chunk ends (1-based indexing, inclusive)."""

    metadata: Dict[str, object] = field(default_factory=dict)
    """Additional metadata preserved from the original document."""

    @property
    def line_range(self) -> str:
        """Return formatted line range string."""
        return f"{self.start_line}-{self.end_line}"

    @property
    def size_chars(self) -> int:
        """Return the character count of this chunk's content."""
        return len(self.content)


@dataclass
class ChunkingStatistics:
    """Summary statistics computed from a chunking operation."""

    source_documents: int = 0
    """Number of source documents processed."""

    total_chunks: int = 0
    """Total number of chunks created."""

    total_source_chars: int = 0
    """Total characters across all source documents."""

    total_chunk_chars: int = 0
    """Total characters across all chunks (including overlap)."""

    min_chunk_size: int = 0
    """Minimum chunk size observed (in characters)."""

    max_chunk_size: int = 0
    """Maximum chunk size observed (in characters)."""

    chunks_by_file_type: Dict[str, int] = field(default_factory=dict)
    """Count of chunks per file type."""

    @property
    def average_chunk_size(self) -> float:
        """Return average chunk size in characters."""
        if self.total_chunks == 0:
            return 0.0
        return self.total_chunk_chars / self.total_chunks
