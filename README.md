# textbook-ai

Interactive AI tutor for textbooks using RAG (Retrieval-Augmented Generation).

Supports PDF and web URL sources with configurable LLM backends (Ollama, OpenAI-compatible), ChromaDB vector store, and both CLI and web interfaces.

## Quick Start

```bash
# Install
uv sync

# Run CLI with a PDF
uv run textbook-ai path/to/textbook.pdf

# Run web UI
TEXTBOOK_AI_SOURCE__PATH=path/to/textbook.pdf uv run chainlit run src/textbook_ai/chainlit_app.py
```

## Configuration

Copy `.env.example` to `.env` and edit as needed. See `config/default.yaml` for all configuration options.
