"""Interactive CLI for textbook-ai."""

import argparse
import logging

from textbook_ai.config import AppConfig, load_config
from textbook_ai.engine import build_chat_engine


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="textbook-ai",
        description="Interactive AI tutor for textbooks using RAG",
    )
    parser.add_argument("source_path", help="Path to PDF file or web URL")
    parser.add_argument("--config", dest="config_path", help="Path to custom config YAML")
    parser.add_argument(
        "--provider",
        choices=["huggingface", "openai"],
        help="Embeddings provider override",
    )
    parser.add_argument("--llm-api-base", help="LLM API base URL override")
    parser.add_argument("--llm-model", help="LLM model name override")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    return parser.parse_args(argv)


def _apply_cli_overrides(config: AppConfig, args: argparse.Namespace) -> AppConfig:
    """Apply CLI argument overrides to the config."""
    # Detect source type
    path = args.source_path
    if path.startswith("http://") or path.startswith("https://"):
        config.source.type = "web"
    else:
        config.source.type = "pdf"
    config.source.path = path

    if args.provider:
        config.embeddings.provider = args.provider
    if args.llm_api_base:
        config.llm.api_base = args.llm_api_base
    if args.llm_model:
        config.llm.model = args.llm_model

    return config


def run_interactive_loop(config: AppConfig) -> None:
    """Run the interactive Q&A loop."""
    print("Building chat engine... This may take a while on first run.")
    engine, source_info = build_chat_engine(config=config)

    print(f"\nReady to answer questions about: {source_info.name}")
    print("Type 'quit' or 'exit' to stop.\n")

    while True:
        try:
            question = input("Question: ")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        question = question.strip()
        if not question:
            continue
        if question.lower() in ("quit", "exit"):
            print("Goodbye!")
            break

        response = engine.chat(question)

        print(f"\nAnswer: {response.response}\n")

        if response.source_nodes:
            print("Sources:")
            for i, node in enumerate(response.source_nodes, 1):
                score = f" (score: {node.score:.3f})" if node.score is not None else ""
                text_preview = node.text[:120].replace("\n", " ")
                print(f"  [{i}]{score} {text_preview}...")
            print()


def main(argv: list[str] | None = None) -> None:
    """CLI entry point."""
    args = _parse_args(argv)

    log_level = logging.DEBUG if args.verbose else logging.WARNING
    logging.basicConfig(level=log_level, format="%(name)s - %(levelname)s - %(message)s")

    config = load_config(args.config_path)
    config = _apply_cli_overrides(config, args)

    run_interactive_loop(config)


if __name__ == "__main__":
    main()
