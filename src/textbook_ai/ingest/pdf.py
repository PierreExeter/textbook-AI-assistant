"""PDF document ingestion using Docling."""

import logging

from docling.datamodel.accelerator_options import AcceleratorOptions
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from llama_index.core.schema import Document
from llama_index.readers.docling import DoclingReader

from textbook_ai.config import IngestConfig

logger = logging.getLogger(__name__)


def _build_converter(config: IngestConfig) -> DocumentConverter:
    """Build a Docling DocumentConverter with the given config."""
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = config.pdf.do_ocr
    pipeline_options.do_table_structure = config.pdf.do_table_structure
    pipeline_options.accelerator_options = AcceleratorOptions(
        device=config.pdf.accelerator_device,
        num_threads=config.pdf.num_threads,
    )

    return DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options),
        }
    )


def load_pdf(file_path: str, config: IngestConfig) -> list[Document]:
    """Load a PDF file using DoclingReader.

    Args:
        file_path: Path to the PDF file.
        config: Ingestion configuration.

    Returns:
        List of LlamaIndex Documents.
    """
    logger.info("Loading PDF: %s", file_path)

    converter = _build_converter(config)
    reader = DoclingReader(
        export_type=DoclingReader.ExportType.MARKDOWN,
        doc_converter=converter,
    )

    documents = reader.load_data(file_path=file_path)
    logger.info("Loaded %d document(s) from PDF", len(documents))
    return documents
