# Contributing

Contributions are welcome! This guide covers dev setup, testing, code style, and how to extend the project.

## Dev Setup

```bash
git clone https://github.com/PierreExeter/textbook-AI-assistant.git
cd textbook-AI-assistant
uv sync
cp .env.example .env
```

## Running Tests

```bash
uv run --frozen pytest                         # full suite
uv run --frozen pytest tests/test_config.py -v # single file
```

Tests set `IS_TESTING=1` so LlamaIndex substitutes `MockEmbedding` -- no real model downloads or LLM calls are needed.

## Code Quality

```bash
# Formatting
uv run --frozen ruff format .

# Linting (with auto-fix)
uv run --frozen ruff check . --fix

# Type checking
uv run --frozen pyright
```

Run all three before submitting a PR. CI will fail on formatting or type errors.

## Code Style

- **Type hints** on all function signatures
- **Docstrings** on public APIs
- **120 character** max line length
- **Imports at the top** of each file (never inside functions)
- **No `Test`-prefixed classes** -- use plain test functions
- **Package manager**: `uv` only (never `pip`)

## Project Structure

```
config/default.yaml              # Default configuration (all options with defaults)
src/textbook_ai/
  cli.py                         # CLI entry point with argparse
  chainlit_app.py                # Chainlit web UI handlers
  engine.py                      # Central orchestrator -- build_chat_engine()
  config.py                      # Dataclasses + 3-tier config loading
  index.py                       # ChromaDB index creation/loading + LlamaIndex Settings
  types.py                       # Shared dataclasses (SourceInfo, ChatResponse)
  ingest/
    __init__.py                  # Type-based dispatcher to pdf/web loaders
    pdf.py                       # PDF ingestion via DoclingReader
    web.py                       # Web ingestion via SimpleWebPageReader
tests/                           # Test suite
```

## Extension Guides

### Adding a New Source Type

1. Create `src/textbook_ai/ingest/mytype.py` with a function matching this signature:

   ```python
   def load_mytype(path: str, config: IngestConfig) -> list[Document]:
       ...
   ```

2. Import it in `src/textbook_ai/ingest/__init__.py`.

3. Add an `elif` branch in `load_source()`:

   ```python
   elif source_config.type == "mytype":
       return load_mytype(source_config.path, ingest_config)
   ```

4. Add tests in `tests/test_ingest_mytype.py`.

### Adding a New Embedding Provider

1. Add a config dataclass in `config.py` (follow the pattern of `HuggingFaceEmbeddingsConfig`).

2. Add the new dataclass as a field on `EmbeddingsConfig`.

3. Add a default section in `config/default.yaml`.

4. Add an `elif` branch in `_configure_global_settings()` in `index.py` to instantiate the embedding model.

5. Add tests for the new configuration and embedding setup.

## Submitting Changes

1. Open an issue describing the problem or feature.
2. Fork the repo and create a branch.
3. Make your changes, run the linters and tests locally.
4. Submit a pull request referencing the issue.
