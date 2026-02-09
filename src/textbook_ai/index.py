"""ChromaDB vector store index creation and management."""

import hashlib
import logging
import os

import chromadb
from chromadb.api import ClientAPI
from llama_index.core import Settings, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import Document
from llama_index.core.storage import StorageContext
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai_like import OpenAILike
from llama_index.vector_stores.chroma import ChromaVectorStore

from textbook_ai.config import AppConfig

logger = logging.getLogger(__name__)


def _configure_global_settings(config: AppConfig) -> None:
    """Configure LlamaIndex global Settings from app config."""
    # LLM
    api_key = os.environ.get(config.llm.api_key_env, "ollama")
    Settings.llm = OpenAILike(
        model=config.llm.model,
        api_base=config.llm.api_base,
        api_key=api_key,
        temperature=config.llm.temperature,
        context_window=config.llm.context_window,
        max_tokens=config.llm.max_tokens,
        is_chat_model=True,
    )

    # Embeddings
    if config.embeddings.provider == "huggingface":
        Settings.embed_model = HuggingFaceEmbedding(model_name=config.embeddings.huggingface.model_name)
    elif config.embeddings.provider == "openai":
        embed_api_key = os.environ.get(config.embeddings.openai.api_key_env, "")
        Settings.embed_model = OpenAIEmbedding(model_name=config.embeddings.openai.model_name, api_key=embed_api_key)
    else:
        raise ValueError(f"Unknown embeddings provider: {config.embeddings.provider!r}")

    # Chunking
    Settings.chunk_size = config.ingest.chunk_size
    Settings.chunk_overlap = config.ingest.chunk_overlap


def _get_collection_name(config: AppConfig) -> str:
    """Derive a collection name from the source path to avoid collisions."""
    if config.source.path:
        path_hash = hashlib.sha256(config.source.path.encode()).hexdigest()[:12]
        return f"{config.vector_store.collection_name}_{path_hash}"
    return config.vector_store.collection_name


def _get_chroma_client(config: AppConfig) -> ClientAPI:
    """Create a persistent ChromaDB client."""
    persist_dir = config.vector_store.persist_dir
    os.makedirs(persist_dir, exist_ok=True)
    return chromadb.PersistentClient(path=persist_dir)


def index_exists(config: AppConfig) -> bool:
    """Check if a ChromaDB collection already has documents.

    Args:
        config: Application configuration.

    Returns:
        True if the collection exists and has documents.
    """
    try:
        client = _get_chroma_client(config)
        collection_name = _get_collection_name(config)
        collection = client.get_collection(name=collection_name)
        return collection.count() > 0
    except Exception:
        return False


def get_or_create_index(documents: list[Document] | None, config: AppConfig) -> VectorStoreIndex:
    """Get an existing index or create a new one from documents.

    If the collection already has documents, loads from existing.
    Otherwise, indexes the provided documents.

    Args:
        documents: Documents to index (can be None if index exists).
        config: Application configuration.

    Returns:
        A VectorStoreIndex backed by ChromaDB.

    Raises:
        ValueError: If no documents provided and no existing index.
    """
    _configure_global_settings(config)

    client = _get_chroma_client(config)
    collection_name = _get_collection_name(config)

    if index_exists(config):
        logger.info("Loading existing index from collection: %s", collection_name)
        collection = client.get_collection(name=collection_name)
        vector_store = ChromaVectorStore(chroma_collection=collection)
        return VectorStoreIndex.from_vector_store(vector_store)

    if not documents:
        raise ValueError("No documents provided and no existing index found")

    logger.info("Creating new index in collection: %s", collection_name)
    collection = client.get_or_create_collection(name=collection_name)
    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    node_parser = SentenceSplitter(
        chunk_size=config.ingest.chunk_size,
        chunk_overlap=config.ingest.chunk_overlap,
    )

    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        transformations=[node_parser],
        show_progress=True,
    )
    logger.info("Index created with %d documents", len(documents))
    return index
