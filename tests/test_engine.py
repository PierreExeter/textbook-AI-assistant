"""Tests for the chat engine module."""

from unittest.mock import MagicMock, patch

from textbook_ai.config import AppConfig
from textbook_ai.engine import _derive_book_name, build_chat_engine


def test_derive_book_name_pdf() -> None:
    """Should derive a readable name from a PDF path."""
    config = AppConfig()
    config.source.type = "pdf"
    config.source.path = "/path/to/my-great_textbook.pdf"

    assert _derive_book_name(config) == "My Great Textbook"


def test_derive_book_name_web() -> None:
    """Should return the URL for web sources."""
    config = AppConfig()
    config.source.type = "web"
    config.source.path = "https://example.com/article"

    assert _derive_book_name(config) == "https://example.com/article"


@patch("textbook_ai.engine.get_or_create_index")
@patch("textbook_ai.engine.index_exists", return_value=False)
@patch("textbook_ai.engine.load_source")
def test_build_chat_engine_orchestrates(
    mock_load: MagicMock,
    mock_exists: MagicMock,
    mock_index: MagicMock,
) -> None:
    """build_chat_engine should orchestrate loading and indexing."""
    from llama_index.core.schema import Document

    mock_load.return_value = [Document(text="test content")]

    mock_vector_index = MagicMock()
    mock_retriever = MagicMock()
    mock_vector_index.as_retriever.return_value = mock_retriever
    mock_index.return_value = mock_vector_index

    config = AppConfig()
    config.source.type = "pdf"
    config.source.path = "/path/to/book.pdf"

    with patch("textbook_ai.engine.CondensePlusContextChatEngine") as mock_engine_cls:
        mock_engine_instance = MagicMock()
        mock_engine_cls.from_defaults.return_value = mock_engine_instance

        engine, source_info = build_chat_engine(config=config)

    mock_load.assert_called_once()
    mock_index.assert_called_once()
    assert source_info.name == "Book"
    assert source_info.source_type == "pdf"
    assert engine is mock_engine_instance


@patch("textbook_ai.engine.get_or_create_index")
@patch("textbook_ai.engine.index_exists", return_value=True)
@patch("textbook_ai.engine.load_source")
def test_build_chat_engine_skips_ingestion_when_index_exists(
    mock_load: MagicMock,
    mock_exists: MagicMock,
    mock_index: MagicMock,
) -> None:
    """build_chat_engine should skip ingestion when index already exists."""
    mock_vector_index = MagicMock()
    mock_vector_index.as_retriever.return_value = MagicMock()
    mock_index.return_value = mock_vector_index

    config = AppConfig()
    config.source.type = "pdf"
    config.source.path = "/path/to/book.pdf"

    with patch("textbook_ai.engine.CondensePlusContextChatEngine") as mock_engine_cls:
        mock_engine_cls.from_defaults.return_value = MagicMock()
        build_chat_engine(config=config)

    mock_load.assert_not_called()
    mock_index.assert_called_once_with(None, config)
