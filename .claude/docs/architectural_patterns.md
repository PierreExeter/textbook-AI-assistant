# Architectural Patterns

Cross-cutting design patterns used throughout the textbook-ai codebase.

## Central Orchestrator

`engine.py:63-101` — `build_chat_engine()` is the **single entry point** for both interfaces. Neither `cli.py` nor `chainlit_app.py` imports LlamaIndex directly; they both call `build_chat_engine()` and receive a ready-to-use chat engine plus metadata.

- CLI calls it at `cli.py:51`
- Web UI calls it at `chainlit_app.py:29`

The orchestrator sequence: load config -> check index -> ingest if needed -> create/load index -> build chat engine -> return `(engine, SourceInfo)`.

## Three-Tier Config Cascade

`config.py:173-200` — Configuration resolves in priority order:

1. **Environment variables** (highest) — `TEXTBOOK_AI_SECTION__KEY` pattern, applied by `_apply_env_overrides()` at `config.py:139-155`
2. **User YAML** (middle) — merged via recursive `_merge_dict()` at `config.py:117-125`
3. **Default YAML** (lowest) — `config/default.yaml`, loaded at `config.py:188-189`

Type coercion for env vars happens at `config.py:128-136` (handles bool, int, float, str). The final dict is recursively converted into nested dataclasses via `_dict_to_dataclass()` at `config.py:158-170`.

## Type-Based Dispatcher

`ingest/__init__.py:10-31` — `load_source()` routes to the correct loader based on `source_config.type`:

- `"pdf"` -> `load_pdf(path, config)` at line 27
- `"web"` -> `load_web(path, config)` at line 29
- unknown -> `ValueError` at line 31

Both loaders share the same signature: `(str, IngestConfig) -> list[Document]`. Adding a new source type means writing a loader with that signature and adding one `elif` branch.

## Hash-Based Collection Isolation

`index.py:51-56` — Each source gets its own ChromaDB collection. The collection name is derived by appending a truncated SHA-256 hash of the source path to the base name (e.g., `textbook_a1b2c3d4e5f6`). This prevents collisions when indexing multiple books into the same `persist_dir`.

## Global State Configuration

`index.py:23-48` — `_configure_global_settings()` sets LlamaIndex's `Settings.llm`, `Settings.embed_model`, `Settings.chunk_size`, and `Settings.chunk_overlap` as module-level globals. This is called once per `get_or_create_index()` invocation (`index.py:100`). The approach follows LlamaIndex's recommended pattern where these globals are configured before any index operations.

## API Key Indirection

Config stores environment variable **names**, not actual keys. For example, `llm.api_key_env: "LLM_API_KEY"` in YAML. The actual `os.environ.get()` call happens at runtime in `index.py:26`. This keeps secrets out of config files and allows different environments to use different variable names.

## Lazy Index Creation

`engine.py:84-89` checks `index_exists()` before ingesting. If a ChromaDB collection with documents already exists, ingestion is skipped entirely and the existing index is loaded from disk (`index.py:104-109`). This makes subsequent runs near-instant since PDF/web parsing is the most expensive step.

## Test Isolation via IS_TESTING

`test_index.py:15-19` — An autouse fixture sets `IS_TESTING=1` so LlamaIndex uses `MockEmbedding` instead of downloading real embedding models. Combined with `@patch("textbook_ai.index._configure_global_settings")` at `test_index.py:62`, this ensures index tests run without any real LLM or embedding infrastructure.
