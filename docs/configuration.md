# Configuration

textbook-ai uses a layered configuration system. Every setting has a sensible default, so you only need to override what you want to change.

## Resolution Order

Configuration is resolved in this order (highest priority first):

1. **CLI flags** (`--llm-model`, `--provider`, etc.)
2. **Environment variables** (`TEXTBOOK_AI_SECTION__KEY`)
3. **User config YAML** (passed via `--config`)
4. **Default config** (`config/default.yaml`)

Each layer only needs to specify the fields it wants to override. Values are deep-merged so you can override a single nested field without repeating the rest.

## Config File Usage

Pass a custom YAML file with `--config`:

```bash
uv run textbook-ai textbook.pdf --config my_config.yaml
```

A partial config file is fine. For example, to only change the LLM model:

```yaml
llm:
  model: "mistral"
```

All other fields keep their defaults.

## Environment Variable Convention

Any config field can be set via an environment variable using the pattern:

```
TEXTBOOK_AI_<SECTION>__<KEY>
```

- Use **double underscores** (`__`) to separate nesting levels
- Names are **uppercase**
- Type coercion is automatic: `"true"/"1"/"yes"` become `True` for booleans, numeric strings become `int`/`float`

Examples:

```bash
export TEXTBOOK_AI_LLM__MODEL=mistral
export TEXTBOOK_AI_INGEST__CHUNK_SIZE=500
export TEXTBOOK_AI_INGEST__PDF__DO_OCR=false
```

## Full Configuration Reference

### source

| Field | Env Var | Type | Default | Description |
|---|---|---|---|---|
| `type` | `TEXTBOOK_AI_SOURCE__TYPE` | `str` | `"pdf"` | Source type: `"pdf"` or `"web"`. Auto-detected by CLI from the path. |
| `path` | `TEXTBOOK_AI_SOURCE__PATH` | `str` | `""` | Path to PDF file or web URL. Required for web UI. |

### ingest

| Field | Env Var | Type | Default | Description |
|---|---|---|---|---|
| `chunk_size` | `TEXTBOOK_AI_INGEST__CHUNK_SIZE` | `int` | `1000` | Number of characters per text chunk for indexing. |
| `chunk_overlap` | `TEXTBOOK_AI_INGEST__CHUNK_OVERLAP` | `int` | `200` | Overlap between consecutive chunks (improves retrieval at chunk boundaries). |

### ingest.pdf

| Field | Env Var | Type | Default | Description |
|---|---|---|---|---|
| `do_ocr` | `TEXTBOOK_AI_INGEST__PDF__DO_OCR` | `bool` | `true` | Enable OCR for scanned pages. |
| `do_table_structure` | `TEXTBOOK_AI_INGEST__PDF__DO_TABLE_STRUCTURE` | `bool` | `true` | Extract table structure from PDFs. |
| `num_threads` | `TEXTBOOK_AI_INGEST__PDF__NUM_THREADS` | `int` | `8` | Number of threads for PDF processing. |
| `accelerator_device` | `TEXTBOOK_AI_INGEST__PDF__ACCELERATOR_DEVICE` | `str` | `"cpu"` | Device for Docling acceleration (`"cpu"` or `"cuda"`). |

### embeddings

| Field | Env Var | Type | Default | Description |
|---|---|---|---|---|
| `provider` | `TEXTBOOK_AI_EMBEDDINGS__PROVIDER` | `str` | `"huggingface"` | Embeddings provider: `"huggingface"` (local, free) or `"openai"` (API key required). |

### embeddings.huggingface

| Field | Env Var | Type | Default | Description |
|---|---|---|---|---|
| `model_name` | `TEXTBOOK_AI_EMBEDDINGS__HUGGINGFACE__MODEL_NAME` | `str` | `"sentence-transformers/all-MiniLM-L6-v2"` | HuggingFace model for embeddings. Downloaded automatically on first use. |
| `device` | `TEXTBOOK_AI_EMBEDDINGS__HUGGINGFACE__DEVICE` | `str` | `"cpu"` | Device for embedding computation (`"cpu"` or `"cuda"`). |

### embeddings.openai

| Field | Env Var | Type | Default | Description |
|---|---|---|---|---|
| `model_name` | `TEXTBOOK_AI_EMBEDDINGS__OPENAI__MODEL_NAME` | `str` | `"text-embedding-3-small"` | OpenAI embedding model name. |
| `api_key_env` | `TEXTBOOK_AI_EMBEDDINGS__OPENAI__API_KEY_ENV` | `str` | `"OPENAI_API_KEY"` | Name of the environment variable holding the OpenAI API key. |

### llm

| Field | Env Var | Type | Default | Description |
|---|---|---|---|---|
| `model` | `TEXTBOOK_AI_LLM__MODEL` | `str` | `"llama3.2"` | LLM model name (must be available on your provider). |
| `api_base` | `TEXTBOOK_AI_LLM__API_BASE` | `str` | `"http://localhost:11434/v1"` | Base URL for the OpenAI-compatible API. |
| `api_key_env` | `TEXTBOOK_AI_LLM__API_KEY_ENV` | `str` | `"LLM_API_KEY"` | Name of the environment variable holding the LLM API key. |
| `temperature` | `TEXTBOOK_AI_LLM__TEMPERATURE` | `float` | `0.0` | Sampling temperature (0.0 = deterministic). |
| `context_window` | `TEXTBOOK_AI_LLM__CONTEXT_WINDOW` | `int` | `4096` | Maximum context window size in tokens. |
| `max_tokens` | `TEXTBOOK_AI_LLM__MAX_TOKENS` | `int` | `1024` | Maximum tokens in the LLM response. |

### retriever

| Field | Env Var | Type | Default | Description |
|---|---|---|---|---|
| `search_type` | `TEXTBOOK_AI_RETRIEVER__SEARCH_TYPE` | `str` | `"mmr"` | Search mode: `"default"` (similarity), `"mmr"` (maximal marginal relevance), or `"hybrid"`. |
| `top_k` | `TEXTBOOK_AI_RETRIEVER__TOP_K` | `int` | `5` | Number of chunks retrieved per query. |

### vector_store

| Field | Env Var | Type | Default | Description |
|---|---|---|---|---|
| `persist_dir` | `TEXTBOOK_AI_VECTOR_STORE__PERSIST_DIR` | `str` | `".textbook_ai_index"` | Directory for ChromaDB persistent storage. |
| `collection_name` | `TEXTBOOK_AI_VECTOR_STORE__COLLECTION_NAME` | `str` | `"textbook"` | Base name for the ChromaDB collection (a hash suffix is appended per source). |

### prompt

| Field | Env Var | Type | Default | Description |
|---|---|---|---|---|
| `system_prompt` | `TEXTBOOK_AI_PROMPT__SYSTEM_PROMPT` | `str` | *(see below)* | System prompt template. Use `{book_name}` as a placeholder. |

Default system prompt:

```
You are a helpful assistant answering questions about the book: {book_name}.
Use the following context to answer the question accurately and concisely.
```
