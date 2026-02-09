"""Tests for the load_source dispatcher."""

from unittest.mock import patch

import pytest
from llama_index.core.schema import Document

from textbook_ai.config import IngestConfig, SourceConfig
from textbook_ai.ingest import load_source


def test_load_source_dispatches_pdf() -> None:
    """load_source should dispatch to load_pdf for pdf type."""
    mock_docs = [Document(text="pdf content")]
    with patch("textbook_ai.ingest.load_pdf", return_value=mock_docs) as mock_load:
        source = SourceConfig(type="pdf", path="/path/to/file.pdf")
        result = load_source(source, IngestConfig())

    mock_load.assert_called_once_with("/path/to/file.pdf", IngestConfig())
    assert result == mock_docs


def test_load_source_dispatches_web() -> None:
    """load_source should dispatch to load_web for web type."""
    mock_docs = [Document(text="web content")]
    with patch("textbook_ai.ingest.load_web", return_value=mock_docs) as mock_load:
        source = SourceConfig(type="web", path="https://example.com")
        result = load_source(source, IngestConfig())

    mock_load.assert_called_once_with("https://example.com", IngestConfig())
    assert result == mock_docs


def test_load_source_unknown_type_raises() -> None:
    """load_source should raise ValueError for unknown types."""
    source = SourceConfig(type="unknown", path="/some/path")
    with pytest.raises(ValueError, match="Unknown source type"):
        load_source(source, IngestConfig())


def test_load_source_empty_path_raises() -> None:
    """load_source should raise ValueError if path is empty."""
    source = SourceConfig(type="pdf", path="")
    with pytest.raises(ValueError, match="Source path must not be empty"):
        load_source(source, IngestConfig())
