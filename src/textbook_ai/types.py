"""Shared data types for the textbook-ai application."""

from dataclasses import dataclass, field


@dataclass
class SourceInfo:
    """Metadata about the ingested source."""

    name: str
    source_type: str
    path: str
    num_documents: int = 0


@dataclass
class ChatResponse:
    """A chat response with source information."""

    answer: str
    source_nodes: list[dict[str, str]] = field(default_factory=list)
