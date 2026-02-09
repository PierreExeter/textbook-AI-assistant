"""Chainlit web UI for textbook-ai."""

import logging

import chainlit as cl

from textbook_ai.config import load_config
from textbook_ai.engine import build_chat_engine

logger = logging.getLogger(__name__)


@cl.on_chat_start
async def on_chat_start() -> None:
    """Initialize chat engine when a new session starts."""
    config = load_config()

    if not config.source.path:
        await cl.Message(
            content=(
                "No source path configured. Set `TEXTBOOK_AI_SOURCE__PATH` environment variable "
                "or provide a config file with `source.path`."
            )
        ).send()
        return

    await cl.Message(content="Loading your textbook... This may take a moment on first run.").send()

    engine, source_info = build_chat_engine(config=config)

    cl.user_session.set("chat_engine", engine)
    cl.user_session.set("source_info", source_info)

    await cl.Message(content=f"Ready! Ask me anything about: **{source_info.name}**").send()


@cl.on_message
async def on_message(message: cl.Message) -> None:
    """Handle incoming chat messages."""
    engine = cl.user_session.get("chat_engine")

    if engine is None:
        await cl.Message(content="Chat engine not initialized. Please configure a source path and restart.").send()
        return

    response = await cl.make_async(engine.chat)(message.content)

    source_text = ""
    if response.source_nodes:
        source_text = "\n\n---\n**Sources:**\n"
        for i, node in enumerate(response.source_nodes, 1):
            score = f" (score: {node.score:.3f})" if node.score is not None else ""
            text_preview = node.text[:150].replace("\n", " ")
            source_text += f"\n{i}.{score} {text_preview}..."

    await cl.Message(content=str(response.response) + source_text).send()
