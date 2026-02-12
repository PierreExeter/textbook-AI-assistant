# Usage

## CLI

### Basic Examples

```bash
# Ask questions about a PDF textbook
uv run textbook-ai textbook/attention-is-all-you-need.pdf

# Ask questions about a web page
uv run textbook-ai https://example.com/article
```

The CLI auto-detects the source type from the path: URLs starting with `http://` or `https://` are treated as web sources, everything else as PDF.

Once the engine is ready, type your questions interactively. Type `quit` or `exit` to stop. Each answer includes source citations with relevance scores and text previews.

### CLI Flags

| Flag | Description | Example |
|---|---|---|
| `source_path` | Path to PDF file or web URL (required) | `textbook.pdf` |
| `--config` | Path to a custom config YAML | `--config my_config.yaml` |
| `--provider` | Embeddings provider override (`huggingface` or `openai`) | `--provider openai` |
| `--llm-api-base` | LLM API base URL override | `--llm-api-base http://localhost:8080/v1` |
| `--llm-model` | LLM model name override | `--llm-model mistral` |
| `--verbose`, `-v` | Enable verbose logging | `-v` |

### Combined Examples

```bash
# Use a different model with verbose output
uv run textbook-ai textbook.pdf --llm-model mistral -v

# Use OpenAI embeddings with a custom config
uv run textbook-ai textbook.pdf --provider openai --config my_config.yaml
```

## Web UI

The Chainlit web UI provides a browser-based chat interface. The source path must be set via environment variable since there is no file picker:

```bash
TEXTBOOK_AI_SOURCE__PATH=textbook/attention-is-all-you-need.pdf uv run chainlit run src/textbook_ai/chainlit_app.py
```

Opens at `http://localhost:8000` in your browser.

![Chainlit web UI](assets/images/chainlit-screenshot.png)

## LLM Providers

textbook-ai works with any OpenAI-compatible API. The LLM is configured via `api_base` and `api_key_env`.

### Ollama (default)

No configuration needed. Install [Ollama](https://ollama.com/), pull a model, and go:

```bash
ollama pull llama3.2
uv run textbook-ai textbook.pdf
```

The default `api_base` points to `http://localhost:11434/v1` and no real API key is required.

### OpenAI

```bash
export LLM_API_KEY=sk-...
export TEXTBOOK_AI_LLM__API_BASE=https://api.openai.com/v1
export TEXTBOOK_AI_LLM__MODEL=gpt-4o
uv run textbook-ai textbook.pdf
```

### Other OpenAI-Compatible Providers (vLLM, LM Studio, etc.)

Point `api_base` at your provider's endpoint:

```bash
export TEXTBOOK_AI_LLM__API_BASE=http://localhost:8080/v1
export TEXTBOOK_AI_LLM__MODEL=my-model
uv run textbook-ai textbook.pdf
```

## Embedding Providers

### HuggingFace (default)

Runs locally, no API key needed. The model (`sentence-transformers/all-MiniLM-L6-v2`) is downloaded automatically on first use.

```bash
uv run textbook-ai textbook.pdf
```

To use a different model:

```bash
export TEXTBOOK_AI_EMBEDDINGS__HUGGINGFACE__MODEL_NAME=sentence-transformers/all-mpnet-base-v2
uv run textbook-ai textbook.pdf
```

### OpenAI

Requires an API key:

```bash
export OPENAI_API_KEY=sk-...
uv run textbook-ai textbook.pdf --provider openai
```

See [Configuration](configuration.md) for the full list of embedding options.
