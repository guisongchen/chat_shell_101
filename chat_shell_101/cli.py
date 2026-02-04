"""
CLI entry point for Chat Shell 101.
"""

import asyncio
import time
import click

from .agent import get_agent
from .config import config
from .storage import JSONStorage, MemoryStorage
from .storage.interfaces import Message
from .utils import format_tool_call, format_tool_result, format_thinking


@click.group()
@click.version_option(version="0.1.0", prog_name="chat-shell")
def cli():
    """Chat Shell 101 - Simplified CLI chat tool with LangGraph and OpenAI."""
    pass


@cli.command()
@click.option(
    "--model",
    "-m",
    default="deepseek-chat",
    help="llm model to use",
)
@click.option(
    "--session",
    "-s",
    default=None,
    help="Session ID for multi-turn chat (default: auto-generated)",
)
@click.option(
    "--storage",
    default="json",
    type=click.Choice(["json", "memory"]),
    help="Storage backend",
)
@click.option(
    "--temperature",
    "-t",
    default=1.0,
    type=float,
    help="Sampling temperature (0.0-2.0)",
)
@click.option(
    "--show-thinking",
    is_flag=True,
    help="Show model thinking process",
)
@click.option(
    "--base-url",
    default="https://api.deepseek.com",
    help="OpenAI API base URL (optional, e.g., https://api.deepseek.com)"
)
def chat(model: str, session: str, storage: str, temperature: float, show_thinking: bool, base_url: str):
    """Start interactive chat session."""
    asyncio.run(
        chat_interactive(
            model=model,
            session=session,
            storage=storage,
            temperature=temperature,
            show_thinking=show_thinking,
            base_url=base_url,
        )
    )


async def chat_interactive(
    model: str,
    session: str,
    storage: str,
    temperature: float,
    show_thinking: bool,
    base_url: str,
):
    """Interactive chat main loop."""
    # Update config with CLI options
    config.openai.model = model
    config.openai.temperature = temperature
    if show_thinking:
        config.show_thinking = show_thinking
    if base_url:
        config.openai.base_url = base_url

    # Initialize storage
    if storage == "json":
        storage_provider = JSONStorage()
    else:
        storage_provider = MemoryStorage()

    await storage_provider.initialize()

    # Initialize agent
    agent = await get_agent()

    # Generate session ID if not provided
    session_id = session or f"cli-{int(time.time())}"

    # Print welcome message
    print("\n" + "=" * 50)
    print(f"Chat Shell 101 v0.1.0")
    print(f"Model: {model}")
    print(f"Session: {session_id}")
    print(f"Storage: {storage}")
    print("\nType 'exit' or 'quit' to end the session.")
    print("Type '/clear' to clear history.")
    print("Type '/history' to show history.")
    print("=" * 50 + "\n")

    try:
        while True:
            # Get user input
            try:
                user_input = input("You: ")
            except (EOFError, KeyboardInterrupt):
                break

            # Handle special commands
            if user_input.lower() in ("exit", "quit"):
                break

            if user_input.strip() == "/clear":
                await storage_provider.history.clear_history(session_id)
                print("History cleared.")
                continue

            if user_input.strip() == "/history":
                history = await storage_provider.history.get_history(session_id)
                if not history:
                    print("No history.")
                else:
                    for msg in history:
                        role_prefix = "user: " if msg.role == "user" else "assistant: "
                        content = str(msg.content)
                        # Truncate long content
                        if len(content) > 100:
                            content = content[:100] + "..."
                        print(f"{role_prefix}{content}")
                continue

            if not user_input.strip():
                continue

            # Load history
            history = await storage_provider.history.get_history(session_id)
            messages = []
            # Add system message if needed
            # For now, no system message
            for msg in history:
                messages.append({"role": msg.role, "content": msg.content})
            messages.append({"role": "user", "content": user_input})

            # Stream response
            print("Assistant: ", end="", flush=True)

            full_response = ""

            try:
                async for event in agent.stream(
                    messages=messages,
                    show_thinking=config.show_thinking,
                ):
                    event_type = event.get("type", "")
                    data = event.get("data", {})

                    if event_type == "content":
                        text = data.get("text", "")
                        print(text, end="", flush=True)
                        full_response += text

                    elif event_type == "thinking":
                        text = data.get("text", "")
                        print(f"\n{format_thinking(text)}", end="", flush=True)

                    elif event_type == "tool_call":
                        tool = data.get("tool", "")
                        tool_input = data.get("input", {})
                        print(f"\n{format_tool_call(tool, tool_input)}", end="", flush=True)

                    elif event_type == "tool_result":
                        result = data.get("result", "")
                        print(f"\n{format_tool_result(result)}", end=". ", flush=True)

                    elif event_type == "error":
                        error_msg = data.get("message", "Unknown error")
                        print(f"\nError: {error_msg}")

            except Exception as e:
                print(f"\nError: {e}")
                continue

            print()  # Newline after response

            # Save to history
            await storage_provider.history.append_messages(
                session_id,
                [
                    Message(role="user", content=user_input),
                    Message(role="assistant", content=full_response),
                ],
            )

    finally:
        await storage_provider.close()
        print("\nSession ended.")


def main():
    """Main entry point for CLI."""
    cli()


if __name__ == "__main__":
    main()