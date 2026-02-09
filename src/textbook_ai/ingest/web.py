"""Web URL document ingestion."""

import logging

from llama_index.core.schema import Document
from llama_index.readers.web import SimpleWebPageReader

from textbook_ai.config import IngestConfig

logger = logging.getLogger(__name__)


def load_web(url: str, config: IngestConfig) -> list[Document]:
    """Load a web page as a document.

    Args:
        url: URL of the web page.
        config: Ingestion configuration (unused for web, kept for interface consistency).

    Returns:
        List of LlamaIndex Documents.
    """
    logger.info("Loading web page: %s", url)

    reader = SimpleWebPageReader(html_to_text=True)
    documents = reader.load_data(urls=[url])
    logger.info("Loaded %d document(s) from URL", len(documents))
    return documents
