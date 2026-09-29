#!/usr/bin/env python3
"""
CodebaseRAG — Main Entry Point

A Retrieval-Augmented Generation (RAG) system for asking natural-language
questions about local software repositories.

This is Day 1 / Step 1: Project Foundation
Current implementation: Basic project initialization and structure validation
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_banner():
    """Print CodebaseRAG banner."""
    banner = """
╔════════════════════════════════════════════════════════════════╗
║                      CodebaseRAG v0.1.0                        ║
║   AI-Powered Codebase Question Answering with RAG             ║
╚════════════════════════════════════════════════════════════════╝

📚 Project Status: Day 1 / Step 1 - Foundation

This is the initial foundation phase of CodebaseRAG development.
The following components are planned but not yet implemented:
  - Repository ingestion
  - Source code parsing
  - Intelligent chunking
  - Semantic embeddings
  - FAISS vector indexing
  - Retrieval pipeline
  - Gemini LLM integration
  - RAG answer generation
  - FastAPI backend
  - Streamlit UI
  - Quantitative evaluation

🎯 Current capabilities:
  ✓ Project structure and imports
  ✓ Environment configuration
  ✓ Development foundation

═══════════════════════��═══════════════════════════════════════════
    """
    print(banner)


def validate_project_structure():
    """
    Validate that the project structure is correctly initialized.
    
    Returns:
        bool: True if all required directories and files exist
    """
    logger.info("Validating project structure...")
    
    required_dirs = [
        "app",
        "app/ingestion",
        "app/chunking",
        "app/embeddings",
        "app/retrieval",
        "app/generation",
        "app/evaluation",
        "app/api",
        "tests",
        "evaluation",
        "sample_data",
    ]
    
    required_files = [
        ".gitignore",
        ".env.example",
        "requirements.txt",
        "README.md",
        "main.py",
        "app/__init__.py",
    ]
    
    project_root = Path(".")
    
    # Check directories
    missing_dirs = []
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if not full_path.exists():
            missing_dirs.append(dir_path)
    
    # Check files
    missing_files = []
    for file_path in required_files:
        full_path = project_root / file_path
        if not full_path.exists():
            missing_files.append(file_path)
    
    validation_passed = len(missing_dirs) == 0 and len(missing_files) == 0
    
    if validation_passed:
        logger.info("✓ Project structure validation passed")
        logger.info(f"  - {len(required_dirs)} required directories found")
        logger.info(f"  - {len(required_files)} required files found")
    else:
        logger.warning("✗ Project structure validation failed")
        if missing_dirs:
            logger.warning(f"  Missing directories: {', '.join(missing_dirs)}")
        if missing_files:
            logger.warning(f"  Missing files: {', '.join(missing_files)}")
    
    return validation_passed


def check_environment():
    """
    Check that the development environment is properly configured.
    
    Returns:
        dict: Environment configuration status
    """
    logger.info("Checking environment configuration...")
    
    env_status = {
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "env_file_exists": os.path.exists(".env"),
        "env_example_exists": os.path.exists(".env.example"),
        "has_gemini_key": bool(os.getenv("GEMINI_API_KEY")),
    }
    
    logger.info(f"  Python version: {env_status['python_version']}")
    logger.info(f"  .env file exists: {env_status['env_file_exists']}")
    logger.info(f"  .env.example file exists: {env_status['env_example_exists']}")
    logger.info(f"  GEMINI_API_KEY configured: {env_status['has_gemini_key']}")
    
    if not env_status["env_file_exists"]:
        logger.info("  ℹ  To configure, copy .env.example to .env and update values")
    
    return env_status


def main():
    """
    Main entry point for CodebaseRAG.
    
    Performs initial validation and setup checks.
    """
    print_banner()
    
    try:
        # Validate project structure
        structure_valid = validate_project_structure()
        
        # Check environment
        env_status = check_environment()
        
        logger.info("\n" + "="*65)
        
        if structure_valid:
            logger.info("✓ CodebaseRAG foundation initialized successfully")
            logger.info("\nNext steps:")
            logger.info("  1. Copy .env.example to .env")
            logger.info("  2. Review the README.md for architecture overview")
            logger.info("  3. Proceed to Day 2 for repository ingestion implementation")
            logger.info("\nDocumentation: See README.md for detailed information")
        else:
            logger.error("✗ Project structure is incomplete")
            logger.error("Please ensure all required directories and files are created")
            sys.exit(1)
        
        logger.info("="*65 + "\n")
        
        return 0
    
    except Exception as e:
        logger.error(f"\n✗ Unexpected error during initialization: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
