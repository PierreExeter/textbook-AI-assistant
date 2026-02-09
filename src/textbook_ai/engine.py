"""Chat engine builder — the sole orchestrator for CLI and web UI."""

import logging
from pathlib import Path

from llama_index.core import VectorStoreIndex
from llama_index.core.chat_engine import CondensePlusContextChatEngine
from llama_index.core.vector_stores.types import VectorStoreQueryMode

from textbook_ai.config import AppConfig, load_config
from textbook_ai.index import get_or_create_index, index_exists
from textbook_ai.ingest import load_source
from textbook_ai.types import SourceInfo

logger = logging.getLogger(__name__)

_QUERY_MODES = {
    "default": VectorStoreQueryMode.DEFAULT,
    "mmr": VectorStoreQueryMode.MMR,
    "hybrid": VectorStoreQueryMode.HYBRID,
}


def _derive_book_name(config: AppConfig) -> str:
    """Derive a human-readable name from the source path."""
    path = config.source.path
    if config.source.type == "web":
        return path
    return Path(path).stem.replace("_", " ").replace("-", " ").title()


def create_chat_engine_from_index(
    index: VectorStoreIndex,
    config: AppConfig,
    book_name: str,
) -> CondensePlusContextChatEngine:
    """Create a chat engine from an existing index.

    Args:
        index: The vector store index.
        config: Application configuration.
        book_name: Name of the book for the system prompt.

    Returns:
        A configured CondensePlusContextChatEngine.
    """
    query_mode = _QUERY_MODES.get(config.retriever.search_type, VectorStoreQueryMode.DEFAULT)

    retriever = index.as_retriever(
        similarity_top_k=config.retriever.top_k,
        vector_store_query_mode=query_mode,
    )

    system_prompt = config.prompt.system_prompt.format(book_name=book_name)

    return CondensePlusContextChatEngine.from_defaults(
        retriever=retriever,
        system_prompt=system_prompt,
        verbose=False,
    )


def build_chat_engine(
    config: AppConfig | None = None,
    config_path: str | None = None,
) -> tuple[CondensePlusContextChatEngine, SourceInfo]:
    """Build a chat engine from configuration.

    Orchestrates: load config -> load source -> create/load index -> build engine.

    Args:
        config: Pre-loaded configuration (takes priority).
        config_path: Path to user config YAML (used if config is None).

    Returns:
        Tuple of (chat_engine, source_info).
    """
    if config is None:
        config = load_config(config_path)

    book_name = _derive_book_name(config)

    # Load documents only if index doesn't exist yet
    documents = None
    if not index_exists(config):
        logger.info("No existing index found, ingesting source...")
        documents = load_source(config.source, config.ingest)
    else:
        logger.info("Existing index found, skipping ingestion")

    index = get_or_create_index(documents, config)
    engine = create_chat_engine_from_index(index, config, book_name)

    source_info = SourceInfo(
        name=book_name,
        source_type=config.source.type,
        path=config.source.path,
        num_documents=len(documents) if documents else 0,
    )

    return engine, source_info
