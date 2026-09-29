# CodebaseRAG — AI Engineering Documentation & Codebase Assistant

CodebaseRAG is a retrieval-augmented generation (RAG) system for asking natural-language questions about a local GitHub repository and receiving answers grounded in the repository's source code and documentation.

## Problem

Understanding an unfamiliar codebase is slow. Keyword search can miss semantic intent, while a general-purpose LLM does not know the current implementation and may invent details. CodebaseRAG indexes the repository, retrieves relevant code chunks, and provides answers with file and line references.

## Example Questions

- How does authentication work in this project?
- Where is JWT refresh-token rotation implemented?
- Which class handles code review requests?
- Explain the request flow from React to Spring Boot.
- Which files are responsible for PostgreSQL review history?
- What would I need to modify to add a new user role?
- Where is the external LLM API called?

## Architecture

```text
Local Repository
      │
      ▼
Ingestion and file filtering
      │
      ▼
Parsing and metadata preservation
      │
      ▼
Chunking with overlap and line ranges
      │
      ▼
Sentence Transformer embeddings
      │
      ▼
FAISS vector index
      │
      ├── Query embedding
      │          │
      │          ▼
      └── Top-K semantic retrieval
                     │
                     ▼
           Prompt with code context
                     │
                     ▼
                 Gemini LLM
                     │
                     ▼
          Grounded answer and sources
```

## How It Works

### Indexing

1. Recursively scan a local repository.
2. Include relevant source and documentation files.
3. Exclude dependencies, build output, caches, binary files, and oversized files.
4. Preserve file paths, language, line ranges, and source text.
5. Split files into practical overlapping chunks.
6. Convert chunks into vectors using Sentence Transformers.
7. Store vectors in a FAISS index and preserve a mapping to chunk metadata.

### Querying

1. Convert the user's question into an embedding using the same model.
2. Search FAISS for the most similar chunks.
3. Build a context containing the retrieved chunks and their source metadata.
4. Ask Gemini to answer using only the supplied repository context.
5. Return the answer, retrieved sources, similarity scores, and relevant snippets.

## Why RAG Instead of a Generic LLM?

| Generic LLM | CodebaseRAG |
|---|---|
| Relies primarily on training data | Uses the current repository as its knowledge source |
| May guess project-specific behavior | Grounds answers in retrieved evidence |
| Usually lacks source references | Returns repository file and line references |
| Cannot automatically inspect a private local codebase | Indexes a repository supplied by the developer |

RAG does not eliminate hallucinations, but retrieval quality, strict prompting, source metadata, and insufficient-evidence handling reduce unsupported answers.

## Technology Stack

- Python
- Sentence Transformers (`all-MiniLM-L6-v2`)
- NumPy
- FAISS
- Gemini API
- LangChain, introduced after the manual pipeline is understood
- FastAPI
- Streamlit
- Git/GitHub

## Project Structure

```text
CodebaseRAG/
├── app/
│   ├── ingestion/       # Repository discovery and file filtering
│   ├── chunking/        # Source-aware chunk creation
│   ├── embeddings/      # Embedding generation
│   ├── retrieval/       # FAISS indexing and search
│   ├── generation/      # Gemini prompt and answer generation
│   ├── evaluation/      # Retrieval evaluation
│   ├── api/             # FastAPI routes
│   └── models/          # Documents and chunks
├── tests/
├── evaluation/          # Questions and measured results
├── sample_data/
├── .env.example
├── .gitignore
├── requirements.txt
├── main.py
└── README.md
```

## MVP Scope

The MVP will support:

- Local repository ingestion
- Source-code and documentation filtering
- Metadata-preserving chunking
- Sentence Transformer embeddings
- FAISS similarity search
- Top-K retrieval without an LLM
- Gemini-based grounded answer generation
- Source file references
- FastAPI endpoints: `GET /health`, `POST /index`, and `POST /query`
- A minimal Streamlit interface
- Recall@K evaluation on a manually created question set

The initial version intentionally excludes GitHub OAuth, real-time synchronization, user authentication, multi-turn conversation, AST parsing, hybrid search, reranking, and production deployment.

## Setup

```bash
git clone https://github.com/Ranjana2707/CodebaseRAG.git
cd CodebaseRAG
python -m venv .venv

# macOS/Linux
source .venv/bin/activate

# Windows PowerShell
# .venv\Scripts\Activate.ps1

pip install -r requirements.txt
cp .env.example .env
```

Set local configuration in `.env`. Never commit API keys:

```env
REPO_PATH=../CodeGuardAI
GEMINI_API_KEY=your_key_here
DEBUG=false
```

## Development Plan

| Day | Deliverable |
|---|---|
| 1 | Environment, project structure, and repository ingestion |
| 2 | Parsing, metadata, chunking, and manual embeddings |
| 3 | FAISS index and retrieval without an LLM |
| 4 | Gemini prompt construction and grounded generation |
| 5 | Manual RAG pipeline and LangChain comparison |
| 6 | FastAPI endpoints and Streamlit UI |
| 7 | Evaluation, documentation, testing, and GitHub polish |

## Evaluation

The evaluation dataset will contain approximately 30–50 questions about the indexed repository. Each question will record expected relevant files, retrieved files, whether evidence was retrieved, answer correctness, and groundedness.

The primary quantitative retrieval metric is **Recall@K**:

```text
Recall@K = questions with at least one relevant result in top K
           ---------------------------------------------------
                         total questions
```

Results will be recorded only after experiments are actually run. Possible experiments include chunk size, overlap, and top-K changes. No performance or accuracy values will be claimed before measurement.

## Limitations

- If relevant code is not indexed or retrieved, generation cannot reliably answer the question.
- Large files may lose cross-section context when chunked.
- The LLM can still hallucinate despite grounding instructions.
- The local index must be rebuilt when the repository changes.
- FAISS is suitable for this local MVP but does not provide a hosted multi-tenant database.

## Future Improvements

After the MVP is stable, possible extensions include hybrid keyword and semantic search, reranking, AST-aware chunking, GitHub URL ingestion, repository tree visualization, conversational history, and evidence scoring. These will be added only if they do not threaten MVP completion.

## Status

The repository is being built incrementally as a seven-day learning and engineering project. Evaluation results and example outputs will be updated after they are genuinely measured.

## Author

Ranjana2707
