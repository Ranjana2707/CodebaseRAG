# Sample Data

This directory will contain sample repositories for testing and development.

## Usage

To test CodebaseRAG with a sample repository:

```bash
# Clone a small public repository
git clone https://github.com/pallets/flask.git .

# Or copy your own repository
cp -r /path/to/your/repo .
```

Then update `.env`:

```
REPO_PATH=./sample_data
```

And run indexing:

```bash
python main.py
```

## Recommendations

For initial testing, use small public repositories:
- Flask (Python web framework)
- FastAPI (Python web framework)
- A small personal project

Avoid large repositories (Linux kernel, Chromium, etc.) during development.
