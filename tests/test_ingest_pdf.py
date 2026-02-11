"""Tests for PDF ingestion."""

from unittest.mock import MagicMock, patch

from docling.datamodel.base_models import InputFormat
from llama_index.core.schema import Document

from textbook_ai.config import IngestConfig, PdfIngestConfig
from textbook_ai.ingest.pdf import _build_converter, load_pdf


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


@patch("textbook_ai.ingest.pdf.DocumentConverter")
def test_build_converter_sets_accelerator_options(mock_converter_cls: MagicMock) -> None:
    """_build_converter should configure AcceleratorOptions with device and num_threads."""
    config = IngestConfig(pdf=PdfIngestConfig(accelerator_device="cuda", num_threads=4))
    _build_converter(config)

    call_kwargs = mock_converter_cls.call_args.kwargs
    pipeline_options = call_kwargs["format_options"][InputFormat.PDF].pipeline_options
    assert pipeline_options.accelerator_options.device == "cuda"
    assert pipeline_options.accelerator_options.num_threads == 4


@patch("textbook_ai.ingest.pdf.DocumentConverter")
def test_build_converter_defaults_to_cpu(mock_converter_cls: MagicMock) -> None:
    """_build_converter should default to CPU accelerator device."""
    config = IngestConfig()
    _build_converter(config)

    call_kwargs = mock_converter_cls.call_args.kwargs
    pipeline_options = call_kwargs["format_options"][InputFormat.PDF].pipeline_options
    assert pipeline_options.accelerator_options.device == "cpu"
    assert pipeline_options.accelerator_options.num_threads == 8
