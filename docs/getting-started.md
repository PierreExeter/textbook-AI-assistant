# Getting Started

Get from zero to your first AI-assisted textbook question in a few minutes.

## Prerequisites

- **Python 3.11+**
- **[uv](https://docs.astral.sh/uv/)** package manager
- **[Ollama](https://ollama.com/)** (for the default local LLM) -- or any OpenAI-compatible API

## Install

```bash
git clone https://github.com/PierreExeter/textbook-AI-assistant.git
cd textbook-AI-assistant
uv sync
cp .env.example .env
```

## Pull a Model

If using Ollama (the default):

```bash
ollama pull llama3.2
```

Ollama serves on `http://localhost:11434` by default -- no API key required.

## First Question (CLI)

```bash
uv run textbook-ai path/to/textbook.pdf
```

The first run downloads the embedding model and indexes the PDF (this may take a while). Subsequent runs reuse the stored index.

Type a question, press Enter, and get an answer with source citations. Type `quit` or `exit` to stop.

## First Question (Web UI)

```bash
TEXTBOOK_AI_SOURCE__PATH=path/to/textbook.pdf uv run chainlit run src/textbook_ai/chainlit_app.py
```

Opens at `http://localhost:8000`.

## Next Steps

- [Usage](usage.md) -- CLI flags, web UI details, LLM and embedding provider switching
- [Configuration](configuration.md) -- Full reference for all config fields
