"""Tests for PDF ingestion."""

from unittest.mock import MagicMock, patch

from llama_index.core.schema import Document

from textbook_ai.config import IngestConfig
from textbook_ai.ingest.pdf import load_pdf


def test_load_pdf_calls_docling_reader() -> None:
    """load_pdf should create a DoclingReader with a converter and call load_data."""
    mock_reader_instance = MagicMock()
    mock_reader_instance.load_data.return_value = [Document(text="Chapter 1 content", metadata={"source": "test.pdf"})]

    with (
        patch("textbook_ai.ingest.pdf.DoclingReader", return_value=mock_reader_instance) as mock_reader_cls,
        patch("textbook_ai.ingest.pdf._build_converter") as mock_build,
    ):
        mock_converter = MagicMock()
        mock_build.return_value = mock_converter
        config = IngestConfig()
        result = load_pdf("/path/to/test.pdf", config)

    mock_build.assert_called_once_with(config)
    mock_reader_cls.assert_called_once()
    call_kwargs = mock_reader_cls.call_args.kwargs
    assert call_kwargs["doc_converter"] is mock_converter

    mock_reader_instance.load_data.assert_called_once_with(file_path="/path/to/test.pdf")
    assert len(result) == 1
    assert result[0].text == "Chapter 1 content"


def test_load_pdf_custom_config() -> None:
    """load_pdf should pass custom config to _build_converter."""
    mock_reader_instance = MagicMock()
    mock_reader_instance.load_data.return_value = []

    with (
        patch("textbook_ai.ingest.pdf.DoclingReader", return_value=mock_reader_instance),
        patch("textbook_ai.ingest.pdf._build_converter") as mock_build,
    ):
        mock_build.return_value = MagicMock()
        config = IngestConfig()
        config.pdf.do_ocr = False
        config.pdf.num_threads = 4
        load_pdf("/path/to/test.pdf", config)

    mock_build.assert_called_once_with(config)
