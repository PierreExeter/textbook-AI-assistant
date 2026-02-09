"""Configuration loading and dataclasses for textbook-ai."""

import os
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Any

import yaml

_DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "config" / "default.yaml"

# Environment variable prefix for overrides
_ENV_PREFIX = "TEXTBOOK_AI_"


@dataclass
class SourceConfig:
    """Source document configuration."""

    type: str = "pdf"
    path: str = ""


@dataclass
class PdfIngestConfig:
    """PDF-specific ingestion options."""

    do_ocr: bool = True
    do_table_structure: bool = True
    num_threads: int = 8


@dataclass
class IngestConfig:
    """Document ingestion configuration."""

    chunk_size: int = 1000
    chunk_overlap: int = 200
    pdf: PdfIngestConfig = field(default_factory=PdfIngestConfig)


@dataclass
class HuggingFaceEmbeddingsConfig:
    """HuggingFace embeddings configuration."""

    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"


@dataclass
class OpenAIEmbeddingsConfig:
    """OpenAI embeddings configuration."""

    model_name: str = "text-embedding-3-small"
    api_key_env: str = "OPENAI_API_KEY"


@dataclass
class EmbeddingsConfig:
    """Embeddings configuration."""

    provider: str = "huggingface"
    huggingface: HuggingFaceEmbeddingsConfig = field(default_factory=HuggingFaceEmbeddingsConfig)
    openai: OpenAIEmbeddingsConfig = field(default_factory=OpenAIEmbeddingsConfig)


@dataclass
class LLMConfig:
    """LLM configuration."""

    model: str = "llama3.2"
    api_base: str = "http://localhost:11434/v1"
    api_key_env: str = "LLM_API_KEY"
    temperature: float = 0.0
    context_window: int = 4096
    max_tokens: int = 1024


@dataclass
class RetrieverConfig:
    """Retriever configuration."""

    search_type: str = "mmr"
    top_k: int = 5


@dataclass
class VectorStoreConfig:
    """Vector store configuration."""

    persist_dir: str = ".textbook_ai_index"
    collection_name: str = "textbook"


@dataclass
class PromptConfig:
    """Prompt configuration."""

    system_prompt: str = (
        "You are a helpful assistant answering questions about the book: {book_name}.\n"
        "Use the following context to answer the question accurately and concisely."
    )


@dataclass
class AppConfig:
    """Top-level application configuration."""

    source: SourceConfig = field(default_factory=SourceConfig)
    ingest: IngestConfig = field(default_factory=IngestConfig)
    embeddings: EmbeddingsConfig = field(default_factory=EmbeddingsConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    retriever: RetrieverConfig = field(default_factory=RetrieverConfig)
    vector_store: VectorStoreConfig = field(default_factory=VectorStoreConfig)
    prompt: PromptConfig = field(default_factory=PromptConfig)


def _merge_dict(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Deep-merge override into base, returning a new dict."""
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _merge_dict(result[key], value)
        else:
            result[key] = value
    return result


def _coerce_value(value: str, target_type: type) -> Any:
    """Coerce a string environment variable value to the target type."""
    if target_type is bool:
        return value.lower() in ("true", "1", "yes")
    if target_type is int:
        return int(value)
    if target_type is float:
        return float(value)
    return value


def _apply_env_overrides(data: dict[str, Any], dataclass_type: type[Any], prefix: str = _ENV_PREFIX) -> dict[str, Any]:
    """Apply environment variable overrides using TEXTBOOK_AI_SECTION__KEY pattern."""
    result = dict(data)
    for f in fields(dataclass_type):
        env_key = f"{prefix}{f.name.upper()}"
        field_type = f.type
        if isinstance(field_type, type) and hasattr(field_type, "__dataclass_fields__"):
            # Nested dataclass — recurse
            nested_data = result.get(f.name, {})
            if not isinstance(nested_data, dict):
                nested_data = {}
            result[f.name] = _apply_env_overrides(nested_data, field_type, prefix=f"{env_key}__")
        else:
            env_value = os.environ.get(env_key)
            if env_value is not None and isinstance(field_type, type):
                result[f.name] = _coerce_value(env_value, field_type)
    return result


def _dict_to_dataclass(data: dict[str, Any], dataclass_type: type[Any]) -> Any:
    """Recursively convert a dict to a dataclass instance."""
    kwargs: dict[str, Any] = {}
    for f in fields(dataclass_type):
        if f.name not in data:
            continue
        value = data[f.name]
        field_type = f.type
        if isinstance(value, dict) and isinstance(field_type, type) and hasattr(field_type, "__dataclass_fields__"):
            kwargs[f.name] = _dict_to_dataclass(value, field_type)
        else:
            kwargs[f.name] = value
    return dataclass_type(**kwargs)


def load_config(user_config_path: str | None = None) -> AppConfig:
    """Load configuration from default YAML, optional user YAML, and env vars.

    Priority (highest to lowest):
    1. Environment variables (TEXTBOOK_AI_SECTION__KEY)
    2. User config YAML (if provided)
    3. Default config YAML

    Args:
        user_config_path: Optional path to a user config YAML file.

    Returns:
        Fully resolved AppConfig instance.
    """
    # Load default config
    with open(_DEFAULT_CONFIG_PATH) as f:
        data: dict[str, Any] = yaml.safe_load(f) or {}

    # Merge user config if provided
    if user_config_path:
        with open(user_config_path) as f:
            user_data: dict[str, Any] = yaml.safe_load(f) or {}
        data = _merge_dict(data, user_data)

    # Apply environment variable overrides
    data = _apply_env_overrides(data, AppConfig)

    return _dict_to_dataclass(data, AppConfig)
