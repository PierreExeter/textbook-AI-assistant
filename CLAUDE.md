# textbook-ai

RAG-based AI tutor for textbooks. Ingests PDF or web sources into a ChromaDB vector store, then answers questions via a LlamaIndex chat engine. Two interfaces: interactive CLI and Chainlit web UI.

## Tech Stack

- **RAG framework**: LlamaIndex (core, embeddings, readers, vector stores)
- **Vector store**: ChromaDB (persistent, local)
- **PDF parsing**: Docling (OCR + table structure)
- **Web parsing**: SimpleWebPageReader (html-to-text)
- **LLM**: OpenAI-compatible API (default: Ollama at localhost:11434)
- **Web UI**: Chainlit
- **Config**: YAML + env vars + CLI args cascade

## Directory Layout

```
config/default.yaml          # Default configuration (all options with defaults)
src/textbook_ai/
  engine.py                  # Central orchestrator — build_chat_engine()
  config.py                  # Dataclasses + 3-tier config loading
  index.py                   # ChromaDB index creation/loading + LlamaIndex Settings
  types.py                   # Shared dataclasses (SourceInfo, ChatResponse)
  cli.py                     # CLI entry point with argparse
  chainlit_app.py            # Chainlit web UI handlers
  ingest/
    __init__.py              # Type-based dispatcher to pdf/web loaders
    pdf.py                   # PDF ingestion via DoclingReader
    web.py                   # Web ingestion via SimpleWebPageReader
tests/
  conftest.py                # Shared fixtures (default_config, tmp_config, mock_document)
  test_config.py             # Config cascade and env var override tests
  test_engine.py             # Orchestrator tests with mocked dependencies
  test_index.py              # Index creation/loading + collection naming tests
  test_ingest_init.py        # Dispatcher routing tests
  test_ingest_pdf.py         # PDF loader tests
  test_ingest_web.py         # Web loader tests
```

## Commands

```bash
# Install dependencies
uv sync

# Run CLI
uv run textbook-ai path/to/textbook.pdf
uv run textbook-ai https://example.com/article --llm-model mistral

# Run web UI
TEXTBOOK_AI_SOURCE__PATH=path/to/book.pdf uv run chainlit run src/textbook_ai/chainlit_app.py

# Tests
uv run --frozen pytest
uv run --frozen pytest tests/test_config.py -v   # single file

# Linting and formatting
uv run --frozen ruff format .
uv run --frozen ruff check . --fix
uv run --frozen pyright
```

## Key Environment Variables

| Variable | Purpose | Default |
|---|---|---|
| `LLM_API_KEY` | API key for the LLM provider | `"ollama"` (no key needed for local Ollama) |
| `OPENAI_API_KEY` | API key when using OpenAI embeddings | — |
| `TEXTBOOK_AI_SOURCE__TYPE` | Override source type (`pdf` or `web`) | `"pdf"` |
| `TEXTBOOK_AI_SOURCE__PATH` | Source file/URL (required for web UI) | — |
| `TEXTBOOK_AI_LLM__MODEL` | Override LLM model name | `"llama3.2"` |
| `TEXTBOOK_AI_LLM__API_BASE` | Override LLM API URL | `"http://localhost:11434/v1"` |
| `TEXTBOOK_AI_EMBEDDINGS__PROVIDER` | `huggingface` or `openai` | `"huggingface"` |

Any config field can be overridden via `TEXTBOOK_AI_SECTION__KEY` (double underscore for nesting). See `config.py:139-155` for the env override logic.

## Testing Notes

- Tests use `IS_TESTING=1` env var so LlamaIndex substitutes `MockEmbedding` — no real model downloads needed (`test_index.py:15-19`)
- Index tests `@patch("..._configure_global_settings")` to skip real LLM setup (`test_index.py:62`)
- All tests are pure-function style (no `Test`-prefixed classes)

## Additional Documentation

- [Architectural Patterns](.claude/docs/architectural_patterns.md) — cross-cutting design patterns with file:line references
