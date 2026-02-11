"""Tests for the vector store index module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from llama_index.core import Settings
from llama_index.core.schema import Document

from textbook_ai.config import AppConfig, HuggingFaceEmbeddingsConfig
from textbook_ai.index import _configure_global_settings, _get_collection_name, get_or_create_index, index_exists


@pytest.fixture(autouse=True)
def _use_mock_embeddings(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set IS_TESTING so LlamaIndex uses MockEmbedding instead of OpenAI."""
    monkeypatch.setenv("IS_TESTING", "1")
    # Reset the cached embed_model so it picks up IS_TESTING
    Settings.embed_model = "default"


def test_get_collection_name_includes_hash() -> None:
    """Collection name should include a hash of the source path."""
    config = AppConfig()
    config.source.path = "/path/to/book.pdf"
    name = _get_collection_name(config)

    assert name.startswith("textbook_")
    assert len(name) > len("textbook_")


def test_get_collection_name_different_paths() -> None:
    """Different source paths should produce different collection names."""
    config1 = AppConfig()
    config1.source.path = "/path/to/book1.pdf"

    config2 = AppConfig()
    config2.source.path = "/path/to/book2.pdf"

    assert _get_collection_name(config1) != _get_collection_name(config2)


def test_get_collection_name_no_path() -> None:
    """Empty source path should return the base collection name."""
    config = AppConfig()
    config.source.path = ""
    assert _get_collection_name(config) == "textbook"


def test_index_exists_returns_false_for_new(tmp_path: Path) -> None:
    """index_exists should return False when no collection exists."""
    config = AppConfig()
    config.vector_store.persist_dir = str(tmp_path / "chroma_empty")
    config.source.path = "/nonexistent.pdf"

    assert index_exists(config) is False


@patch("textbook_ai.index._configure_global_settings")
def test_get_or_create_index_creates_new(mock_settings: MagicMock, tmp_path: Path) -> None:
    """get_or_create_index should create a new index from documents."""
    config = AppConfig()
    config.vector_store.persist_dir = str(tmp_path / "chroma_new")
    config.source.path = "/path/to/test.pdf"

    documents = [
        Document(text="This is chapter one of the textbook with important content."),
        Document(text="This is chapter two with more information about the topic."),
    ]

    index = get_or_create_index(documents, config)

    assert index is not None
    # Verify the index was persisted
    assert index_exists(config) is True


@patch("textbook_ai.index._configure_global_settings")
def test_get_or_create_index_loads_existing(mock_settings: MagicMock, tmp_path: Path) -> None:
    """get_or_create_index should load an existing index."""
    config = AppConfig()
    config.vector_store.persist_dir = str(tmp_path / "chroma_existing")
    config.source.path = "/path/to/test.pdf"

    documents = [Document(text="Test content for persistence.")]

    # Create first
    get_or_create_index(documents, config)
    assert index_exists(config) is True

    # Load existing (no documents needed)
    index = get_or_create_index(None, config)
    assert index is not None


@patch("textbook_ai.index.HuggingFaceEmbedding")
@patch("textbook_ai.index.OpenAILike")
@patch("llama_index.core.settings.resolve_embed_model", side_effect=lambda em, **kw: em)
@patch("llama_index.core.settings.resolve_llm", side_effect=lambda llm, **kw: llm)
def test_configure_global_settings_passes_device_to_embeddings(
    _mock_resolve_llm: MagicMock, _mock_resolve_embed: MagicMock, mock_llm: MagicMock, mock_hf_embed: MagicMock
) -> None:
    """_configure_global_settings should pass device from config to HuggingFaceEmbedding."""
    config = AppConfig()
    config.embeddings.huggingface = HuggingFaceEmbeddingsConfig(device="cuda")
    _configure_global_settings(config)

    mock_hf_embed.assert_called_once_with(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        device="cuda",
    )


@patch("textbook_ai.index.HuggingFaceEmbedding")
@patch("textbook_ai.index.OpenAILike")
@patch("llama_index.core.settings.resolve_embed_model", side_effect=lambda em, **kw: em)
@patch("llama_index.core.settings.resolve_llm", side_effect=lambda llm, **kw: llm)
def test_configure_global_settings_defaults_device_to_cpu(
    _mock_resolve_llm: MagicMock, _mock_resolve_embed: MagicMock, mock_llm: MagicMock, mock_hf_embed: MagicMock
) -> None:
    """_configure_global_settings should default HuggingFace device to cpu."""
    config = AppConfig()
    _configure_global_settings(config)

    mock_hf_embed.assert_called_once_with(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        device="cpu",
    )
