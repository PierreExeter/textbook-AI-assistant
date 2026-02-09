"""Document ingestion modules for PDF and web sources."""

from llama_index.core.schema import Document

from textbook_ai.config import IngestConfig, SourceConfig
from textbook_ai.ingest.pdf import load_pdf
from textbook_ai.ingest.web import load_web


def load_source(source_config: SourceConfig, ingest_config: IngestConfig) -> list[Document]:
    """Dispatch to the appropriate loader based on source type.

    Args:
        source_config: Source configuration with type and path.
        ingest_config: Ingestion configuration with PDF/web options.

    Returns:
        List of LlamaIndex Documents.

    Raises:
        ValueError: If source type is unknown or path is empty.
    """
    if not source_config.path:
        raise ValueError("Source path must not be empty")

    if source_config.type == "pdf":
        return load_pdf(source_config.path, ingest_config)
    elif source_config.type == "web":
        return load_web(source_config.path, ingest_config)
    else:
        raise ValueError(f"Unknown source type: {source_config.type!r}. Supported: 'pdf', 'web'")
