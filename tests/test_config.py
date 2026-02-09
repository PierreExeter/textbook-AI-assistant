"""Tests for the configuration system."""

from pathlib import Path

import pytest
import yaml

from textbook_ai.config import AppConfig, load_config


def test_load_default_config() -> None:
    """Loading without arguments should return defaults from default.yaml."""
    config = load_config()

    assert isinstance(config, AppConfig)
    assert config.source.type == "pdf"
    assert config.source.path == ""
    assert config.llm.model == "llama3.2"
    assert config.llm.api_base == "http://localhost:11434/v1"
    assert config.embeddings.provider == "huggingface"
    assert config.embeddings.huggingface.model_name == "sentence-transformers/all-MiniLM-L6-v2"
    assert config.ingest.chunk_size == 1000
    assert config.ingest.chunk_overlap == 200
    assert config.retriever.top_k == 5


def test_load_user_config_override(tmp_path: Path) -> None:
    """User config YAML should override default values."""
    user_yaml = tmp_path / "user_config.yaml"
    user_yaml.write_text(
        yaml.dump(
            {
                "llm": {"model": "mistral", "temperature": 0.5},
                "retriever": {"top_k": 10},
            }
        )
    )

    config = load_config(str(user_yaml))

    assert config.llm.model == "mistral"
    assert config.llm.temperature == 0.5
    # Non-overridden values should remain at defaults
    assert config.llm.api_base == "http://localhost:11434/v1"
    assert config.retriever.top_k == 10
    assert config.embeddings.provider == "huggingface"


def test_env_var_override(monkeypatch: pytest.MonkeyPatch) -> None:
    """Environment variables should override YAML values."""
    monkeypatch.setenv("TEXTBOOK_AI_SOURCE__TYPE", "web")
    monkeypatch.setenv("TEXTBOOK_AI_SOURCE__PATH", "https://example.com")
    monkeypatch.setenv("TEXTBOOK_AI_LLM__MODEL", "gpt-4")
    monkeypatch.setenv("TEXTBOOK_AI_LLM__TEMPERATURE", "0.7")
    monkeypatch.setenv("TEXTBOOK_AI_RETRIEVER__TOP_K", "3")

    config = load_config()

    assert config.source.type == "web"
    assert config.source.path == "https://example.com"
    assert config.llm.model == "gpt-4"
    assert config.llm.temperature == 0.7
    assert config.retriever.top_k == 3


def test_env_var_bool_coercion(monkeypatch: pytest.MonkeyPatch) -> None:
    """Boolean env vars should be coerced correctly."""
    monkeypatch.setenv("TEXTBOOK_AI_INGEST__PDF__DO_OCR", "false")

    config = load_config()

    assert config.ingest.pdf.do_ocr is False


def test_user_config_plus_env_override(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Env vars should take priority over user config YAML."""
    user_yaml = tmp_path / "user.yaml"
    user_yaml.write_text(yaml.dump({"llm": {"model": "from-yaml"}}))

    monkeypatch.setenv("TEXTBOOK_AI_LLM__MODEL", "from-env")

    config = load_config(str(user_yaml))

    assert config.llm.model == "from-env"


def test_empty_user_config(tmp_path: Path) -> None:
    """An empty user config file should return defaults."""
    user_yaml = tmp_path / "empty.yaml"
    user_yaml.write_text("")

    config = load_config(str(user_yaml))

    assert config.llm.model == "llama3.2"


def test_nested_defaults_preserved() -> None:
    """Nested config objects should have correct defaults."""
    config = load_config()

    assert config.ingest.pdf.do_ocr is True
    assert config.ingest.pdf.do_table_structure is True
    assert config.ingest.pdf.num_threads == 8
    assert config.embeddings.openai.model_name == "text-embedding-3-small"
    assert config.vector_store.collection_name == "textbook"
