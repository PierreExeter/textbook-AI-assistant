"""Tests for web ingestion."""

from unittest.mock import MagicMock, patch

from llama_index.core.schema import Document

from textbook_ai.config import IngestConfig
from textbook_ai.ingest.web import load_web


def test_load_web_calls_simple_web_reader() -> None:
    """load_web should create a SimpleWebPageReader and call load_data."""
    mock_reader_instance = MagicMock()
    mock_reader_instance.load_data.return_value = [
        Document(text="Web page content here", metadata={"source": "https://example.com"})
    ]

    with patch("textbook_ai.ingest.web.SimpleWebPageReader", return_value=mock_reader_instance) as mock_reader_cls:
        config = IngestConfig()
        result = load_web("https://example.com", config)

    mock_reader_cls.assert_called_once_with(html_to_text=True)
    mock_reader_instance.load_data.assert_called_once_with(urls=["https://example.com"])
    assert len(result) == 1
    assert result[0].text == "Web page content here"
