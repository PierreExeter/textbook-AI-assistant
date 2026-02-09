"""Shared test fixtures."""

from pathlib import Path

import pytest
from llama_index.core.schema import Document

from textbook_ai.config import AppConfig, load_config


@pytest.fixture
def default_config() -> AppConfig:
    """Load the default configuration."""
    return load_config()


@pytest.fixture
def tmp_config(tmp_path: Path, default_config: AppConfig) -> AppConfig:
    """Config with vector store pointing to a temp directory."""
    default_config.vector_store.persist_dir = str(tmp_path / "chroma_test")
    default_config.source.type = "pdf"
    default_config.source.path = "/tmp/test.pdf"
    return default_config


@pytest.fixture
def mock_document() -> Document:
    """Create a test LlamaIndex Document."""
    return Document(text="This is test content about a textbook.", metadata={"source": "test.pdf"})
