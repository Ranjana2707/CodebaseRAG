"""
Comprehensive tests for document chunking.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app.chunking import DocumentChunk, DocumentChunker
from app.ingestion.models import RepositoryDocument


def create_doc(
    path: str,
    content: str,
    file_type: str = "text",
) -> RepositoryDocument:
    """Helper to create a RepositoryDocument for testing."""
    return RepositoryDocument(
        path=path,
        absolute_path=f"/repo/{path}",
        extension=".txt",
        file_type=file_type,
        content=content,
        size_bytes=len(content.encode("utf-8")),
    )


class TestDocumentChunker:
    """Tests for DocumentChunker."""

    def test_chunker_initialization(self) -> None:
        """Test chunker can be initialized with valid parameters."""
        chunker = DocumentChunker(chunk_size=1000, overlap_size=150)
        assert chunker.chunk_size == 1000
        assert chunker.overlap_size == 150

    def test_chunker_rejects_invalid_chunk_size(self) -> None:
        """Test chunker rejects non-positive chunk size."""
        with pytest.raises(ValueError):
            DocumentChunker(chunk_size=0)

    def test_chunker_rejects_negative_overlap(self) -> None:
        """Test chunker rejects negative overlap."""
        with pytest.raises(ValueError):
            DocumentChunker(chunk_size=1000, overlap_size=-1)

    def test_chunker_rejects_overlap_gte_chunk_size(self) -> None:
        """Test chunker rejects overlap >= chunk_size."""
        with pytest.raises(ValueError):
            DocumentChunker(chunk_size=100, overlap_size=100)

    def test_small_document_produces_single_chunk(self) -> None:
        """Test that a small document produces exactly one chunk."""
        chunker = DocumentChunker(chunk_size=1000)
        doc = create_doc("test.py", "hello world\n")
        chunks, stats = chunker.chunk_documents([doc])

        assert len(chunks) == 1
        assert chunks[0].content == "hello world"
        assert chunks[0].source_path == "test.py"
        assert chunks[0].start_line == 1
        assert chunks[0].end_line == 1
        assert stats.total_chunks == 1

    def test_large_document_produces_multiple_chunks(self) -> None:
        """Test that a large document produces multiple chunks."""
        chunker = DocumentChunker(chunk_size=100, overlap_size=20)
        # Create a document with many lines
        lines = [f"line {i}: " + "x" * 50 for i in range(20)]
        content = "\n".join(lines)
        doc = create_doc("large.py", content)

        chunks, stats = chunker.chunk_documents([doc])

        assert len(chunks) > 1
        assert stats.total_chunks == len(chunks)

    def test_empty_document_produces_no_chunks(self) -> None:
        """Test that empty documents produce no chunks."""
        chunker = DocumentChunker()
        doc = create_doc("empty.py", "")
        chunks, stats = chunker.chunk_documents([doc])

        assert len(chunks) == 0
        assert stats.total_chunks == 0
        assert stats.documents_without_chunks == 1

    def test_whitespace_only_document_produces_no_chunks(self) -> None:
        """Test that whitespace-only documents produce no chunks."""
        chunker = DocumentChunker()
        doc = create_doc("whitespace.py", "   \n  \n   \n")
        chunks, stats = chunker.chunk_documents([doc])

        assert len(chunks) == 0
        assert stats.documents_without_chunks == 1

    def test_chunk_ids_are_deterministic(self) -> None:
        """Test that chunk IDs are deterministic and include path and index."""
        chunker = DocumentChunker(chunk_size=50)
        doc = create_doc("test.py", "a" * 200 + "\n")
        chunks1, _ = chunker.chunk_documents([doc])

        chunks2, _ = chunker.chunk_documents([doc])

        assert len(chunks1) == len(chunks2)
        for c1, c2 in zip(chunks1, chunks2):
            assert c1.chunk_id == c2.chunk_id

    def test_chunk_ids_contain_path_and_index(self) -> None:
        """Test that chunk IDs contain the source path and index."""
        chunker = DocumentChunker(chunk_size=50)
        doc = create_doc("path/to/file.py", "a" * 200 + "\n")
        chunks, _ = chunker.chunk_documents([doc])

        for i, chunk in enumerate(chunks):
            assert chunk.chunk_id == f"path/to/file.py::chunk_{i:04d}"

    def test_chunk_indices_are_sequential(self) -> None:
        """Test that chunk indices are sequential starting from 0."""
        chunker = DocumentChunker(chunk_size=50)
        doc = create_doc("test.py", "a" * 200 + "\n")
        chunks, _ = chunker.chunk_documents([doc])

        for i, chunk in enumerate(chunks):
            assert chunk.chunk_index == i

    def test_source_path_is_preserved(self) -> None:
        """Test that source_path is preserved in chunks."""
        chunker = DocumentChunker()
        doc = create_doc("src/main/example.py", "content\n")
        chunks, _ = chunker.chunk_documents([doc])

        for chunk in chunks:
            assert chunk.source_path == "src/main/example.py"

    def test_file_type_is_preserved(self) -> None:
        """Test that file_type is preserved in chunks."""
        chunker = DocumentChunker()
        doc = create_doc("test.md", "# Heading\n", file_type="markdown")
        chunks, _ = chunker.chunk_documents([doc])

        for chunk in chunks:
            assert chunk.file_type == "markdown"

    def test_line_numbers_are_accurate(self) -> None:
        """Test that start_line and end_line are accurate."""
        chunker = DocumentChunker(chunk_size=1000)
        content = "line 1\nline 2\nline 3\n"
        doc = create_doc("test.py", content)
        chunks, _ = chunker.chunk_documents([doc])

        # Should be a single chunk with 3 lines
        assert len(chunks) == 1
        assert chunks[0].start_line == 1
        assert chunks[0].end_line == 3

    def test_line_numbers_with_multiple_chunks(self) -> None:
        """Test that line numbers are correct across multiple chunks."""
        chunker = DocumentChunker(chunk_size=50, overlap_size=10)
        # Create content with exactly 10 lines, each ~20 chars
        lines = [f"Line {i}: " + "x" * 10 for i in range(1, 11)]
        content = "\n".join(lines)
        doc = create_doc("test.py", content)
        chunks, _ = chunker.chunk_documents([doc])

        # Check that chunks cover all lines
        assert len(chunks) > 1
        assert chunks[0].start_line == 1
        assert chunks[-1].end_line == 10

        # Check no gaps
        for i in range(len(chunks) - 1):
            # There should be overlap, so end_line of chunk i might be >= start_line of chunk i+1
            assert chunks[i].end_line >= chunks[i + 1].start_line - 1

    def test_markdown_document_chunking(self) -> None:
        """Test chunking of markdown documents."""
        chunker = DocumentChunker(chunk_size=100)
        content = """# Title
        
## Section 1
This is content for section 1.

## Section 2
This is content for section 2.

### Subsection
More content here.
"""
        doc = create_doc("README.md", content, file_type="markdown")
        chunks, _ = chunker.chunk_documents([doc])

        assert len(chunks) > 0
        for chunk in chunks:
            assert chunk.file_type == "markdown"

    def test_no_silent_content_loss(self) -> None:
        """Test that no content is silently lost during chunking."""
        chunker = DocumentChunker(chunk_size=100, overlap_size=20)
        content = "".join(f"Line {i}: content here\n" for i in range(50))
        doc = create_doc("test.py", content)
        chunks, _ = chunker.chunk_documents([doc])

        # Reconstruct content from chunks (handling overlap)
        # Note: with overlap, we can't just concatenate
        # Instead, verify each line appears at least once
        all_chunk_content = "\n".join(c.content for c in chunks)

        # Check that at least the line markers appear
        for i in range(50):
            assert f"Line {i}:" in all_chunk_content

    def test_statistics_are_correct(self) -> None:
        """Test that chunking statistics are computed correctly."""
        chunker = DocumentChunker(chunk_size=100)
        doc1 = create_doc("file1.py", "a" * 50 + "\n")
        doc2 = create_doc("file2.py", "b" * 150 + "\n")
        chunks, stats = chunker.chunk_documents([doc1, doc2])

        assert stats.total_documents == 2
        assert stats.total_chunks == len(chunks)
        assert stats.chunk_size_target == 100
        assert stats.overlap_target == 0  # default

    def test_chunk_size_target_in_stats(self) -> None:
        """Test that chunk_size_target is recorded in statistics."""
        chunker = DocumentChunker(chunk_size=500, overlap_size=100)
        doc = create_doc("test.py", "x" * 1000)
        _, stats = chunker.chunk_documents([doc])

        assert stats.chunk_size_target == 500
        assert stats.overlap_target == 100

    def test_different_chunk_sizes(self) -> None:
        """Test chunking with different chunk sizes."""
        content = "".join(f"Line {i}: content\n" for i in range(100))
        doc = create_doc("test.py", content)

        chunker_small = DocumentChunker(chunk_size=50)
        chunks_small, _ = chunker_small.chunk_documents([doc])

        chunker_large = DocumentChunker(chunk_size=500)
        chunks_large, _ = chunker_large.chunk_documents([doc])

        # Smaller chunk size should produce more chunks
        assert len(chunks_small) > len(chunks_large)

    def test_different_overlap_sizes(self) -> None:
        """Test that different overlap sizes are used."""
        content = "".join(f"Line {i}: content\n" for i in range(100))
        doc = create_doc("test.py", content)

        chunker_no_overlap = DocumentChunker(chunk_size=100, overlap_size=0)
        chunks_no_overlap, _ = chunker_no_overlap.chunk_documents([doc])

        chunker_with_overlap = DocumentChunker(chunk_size=100, overlap_size=50)
        chunks_with_overlap, _ = chunker_with_overlap.chunk_documents([doc])

        # With overlap, chunk count might differ, but we're mainly testing no crashes
        assert len(chunks_no_overlap) > 0
        assert len(chunks_with_overlap) > 0

    def test_long_individual_line_handling(self) -> None:
        """Test that very long individual lines don't crash the chunker."""
        chunker = DocumentChunker(chunk_size=100)
        # Single line that's much longer than chunk_size
        long_line = "x" * 500
        doc = create_doc("test.py", long_line)
        chunks, _ = chunker.chunk_documents([doc])

        # Should produce at least one chunk with the long line
        assert len(chunks) > 0
        assert long_line in chunks[0].content

    def test_chunk_metadata_fields(self) -> None:
        """Test that chunk metadata contains expected fields."""
        chunker = DocumentChunker()
        doc = create_doc("test.py", "line 1\nline 2\nline 3\n")
        chunks, _ = chunker.chunk_documents([doc])

        chunk = chunks[0]
        assert "size_bytes" in chunk.metadata
        assert "line_count" in chunk.metadata
        assert chunk.metadata["line_count"] == 3

    def test_multiple_documents(self) -> None:
        """Test chunking multiple documents together."""
        chunker = DocumentChunker(chunk_size=100)
        doc1 = create_doc("file1.py", "a" * 50)
        doc2 = create_doc("file2.py", "b" * 150)
        doc3 = create_doc("file3.py", "c" * 200)

        chunks, stats = chunker.chunk_documents([doc1, doc2, doc3])

        assert stats.total_documents == 3
        assert len(chunks) > 0

        # Verify chunks are labeled with correct sources
        file1_chunks = [c for c in chunks if c.source_path == "file1.py"]
        file2_chunks = [c for c in chunks if c.source_path == "file2.py"]
        file3_chunks = [c for c in chunks if c.source_path == "file3.py"]

        assert len(file1_chunks) >= 1
        assert len(file2_chunks) >= 1
        assert len(file3_chunks) >= 1


class TestDocumentChunk:
    """Tests for DocumentChunk data model."""

    def test_chunk_creation(self) -> None:
        """Test basic chunk creation."""
        chunk = DocumentChunk(
            chunk_id="file.py::chunk_0000",
            content="hello world",
            source_path="file.py",
            file_type="python",
            chunk_index=0,
            start_line=1,
            end_line=2,
        )

        assert chunk.chunk_id == "file.py::chunk_0000"
        assert chunk.content == "hello world"
        assert chunk.source_path == "file.py"

    def test_chunk_validates_chunk_id(self) -> None:
        """Test that chunk validates chunk_id."""
        with pytest.raises(ValueError):
            DocumentChunk(
                chunk_id="",
                content="hello",
                source_path="file.py",
                file_type="python",
                chunk_index=0,
                start_line=1,
                end_line=1,
            )

    def test_chunk_validates_source_path(self) -> None:
        """Test that chunk validates source_path."""
        with pytest.raises(ValueError):
            DocumentChunk(
                chunk_id="file.py::chunk_0000",
                content="hello",
                source_path="",
                file_type="python",
                chunk_index=0,
                start_line=1,
                end_line=1,
            )

    def test_chunk_validates_content(self) -> None:
        """Test that chunk validates content."""
        with pytest.raises(ValueError):
            DocumentChunk(
                chunk_id="file.py::chunk_0000",
                content="",
                source_path="file.py",
                file_type="python",
                chunk_index=0,
                start_line=1,
                end_line=1,
            )

    def test_chunk_validates_chunk_index(self) -> None:
        """Test that chunk validates chunk_index."""
        with pytest.raises(ValueError):
            DocumentChunk(
                chunk_id="file.py::chunk_0000",
                content="hello",
                source_path="file.py",
                file_type="python",
                chunk_index=-1,
                start_line=1,
                end_line=1,
            )

    def test_chunk_validates_line_numbers(self) -> None:
        """Test that chunk validates line numbers."""
        # start_line < 1
        with pytest.raises(ValueError):
            DocumentChunk(
                chunk_id="file.py::chunk_0000",
                content="hello",
                source_path="file.py",
                file_type="python",
                chunk_index=0,
                start_line=0,
                end_line=1,
            )

        # end_line < start_line
        with pytest.raises(ValueError):
            DocumentChunk(
                chunk_id="file.py::chunk_0000",
                content="hello",
                source_path="file.py",
                file_type="python",
                chunk_index=0,
                start_line=5,
                end_line=3,
            )
