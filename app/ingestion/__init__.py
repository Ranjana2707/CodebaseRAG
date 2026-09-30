"""
Repository ingestion package.

This package is responsible for discovering repository files, filtering out
common generated/dependency artifacts, reading relevant source and documentation
files, and exposing clean metadata for the next pipeline stages.
"""

from .models import RepositoryDocument, RepositoryLoadSummary
from .file_filter import FileFilter
from .repository_loader import RepositoryLoader

__all__ = [
    "RepositoryDocument",
    "RepositoryLoadSummary",
    "FileFilter",
    "RepositoryLoader",
]
