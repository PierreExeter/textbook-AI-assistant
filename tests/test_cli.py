"""Tests for the CLI module."""

from unittest.mock import MagicMock, patch

import openai
import pytest

from textbook_ai.cli import run_interactive_loop
from textbook_ai.config import AppConfig


@patch("textbook_ai.cli.build_chat_engine")
def test_connection_error_prints_message_and_continues(
    mock_build: MagicMock,
) -> None:
    """CLI should catch APIConnectionError and continue the loop."""
    mock_engine = MagicMock()
    mock_engine.chat.side_effect = openai.APIConnectionError(request=MagicMock())
    mock_build.return_value = (mock_engine, MagicMock(name="test-book"))

    config = AppConfig()
    config.source.path = "/tmp/test.pdf"
    config.llm.api_base = "http://localhost:11434/v1"

    with patch("builtins.input", side_effect=["What is AI?", "exit"]):
        run_interactive_loop(config)

    mock_engine.chat.assert_called_once_with("What is AI?")


@patch("textbook_ai.cli.build_chat_engine")
def test_connection_error_shows_api_base(
    mock_build: MagicMock,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Error message should include the configured api_base URL."""
    mock_engine = MagicMock()
    mock_engine.chat.side_effect = openai.APIConnectionError(request=MagicMock())
    mock_build.return_value = (mock_engine, MagicMock(name="test-book"))

    config = AppConfig()
    config.source.path = "/tmp/test.pdf"
    config.llm.api_base = "http://custom-host:9999/v1"

    with patch("builtins.input", side_effect=["hello", "exit"]):
        run_interactive_loop(config)

    captured = capsys.readouterr()
    assert "http://custom-host:9999/v1" in captured.out
    assert "Could not connect to the LLM server" in captured.out
