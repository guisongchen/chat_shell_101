"""
Example 05: Advanced Streaming - Event Handling and Real-time Processing

This example demonstrates advanced streaming patterns including event handling,
cancellation, error recovery, and building real-time applications.

Prerequisites:
    1. Copy .env.example to .env: `cp .env.example .env`
    2. Edit .env and set your OPENAI_API_KEY
"""

import asyncio
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from chat_shell_101.agent.agent import ChatAgent
from chat_shell_101.agent.config import AgentConfig


async def basic_event_streaming():
    """Example 1: Understanding all event types in streaming."""
    print("=" * 60)
    print("Example 1: Complete Event Type Breakdown")
    print("=" * 60)

    config = AgentConfig(
        model="deepseek-chat",
        temperature=0.7,
    )
    agent = ChatAgent(config)
    await agent.initialize()

    messages = [
        {"role": "user", "content": "Calculate 123 * 456 and explain the result"}
    ]

    print("Streaming events:\n")

    event_counts = {}
    async for event in agent.stream(messages, show_thinking=True):
        event_type = event["type"]
        event_counts[event_type] = event_counts.get(event_type, 0) + 1

        # Display event details
        if event_type == "content":
            print(f"[CONTENT] {event['data']['text']!r}")

        elif event_type == "thinking":
            print(f"[THINKING] {event['data']['text']}")

        elif event_type == "tool_call":
            data = event["data"]
            print(f"[TOOL_CALL] {data['tool']}({data['input']})")
            print(f"            call_id: {data['tool_call_id']}")

        elif event_type == "tool_result":
            data = event['data']
            print(f"[TOOL_RESULT] {data['tool']}: {data['result']}")

        elif event_type == "error":
            print(f"[ERROR] {event['data']}")

        # Show offset if present
        if "offset" in event:
            print(f"        (offset: {event['offset']})")

    print(f"\nEvent summary: {event_counts}")
    print()


async def streaming_with_cancellation():
    """Example 2: Cancelling a stream mid-way."""
    print("=" * 60)
    print("Example 2: Stream Cancellation")
    print("=" * 60)

    config = AgentConfig(
        model="deepseek-chat",
        temperature=0.7,
    )
    agent = ChatAgent(config)
    await agent.initialize()

    # Create cancellation event
    cancellation_event = asyncio.Event()

    messages = [
        {"role": "user", "content": "Write a very long story about a dragon"}
    ]

    print("Starting stream (will cancel after 1 second)...")
    print("Output: ", end="", flush=True)

    # Schedule cancellation
    async def cancel_after_delay():
        await asyncio.sleep(1.0)
        print("\n[Cancelling...]")
        cancellation_event.set()

    # Run stream and cancellation together
    cancel_task = asyncio.create_task(cancel_after_delay())

    try:
        async for event in agent.stream(
            messages,
            cancellation_event=cancellation_event
        ):
            if event["type"] == "content":
                print(event["data"]["text"], end="", flush=True)

    except asyncio.CancelledError:
        print("\n[Stream was cancelled]")
    except Exception as e:
        print(f"\n[Error: {e}]")

    await cancel_task
    print()


async def streaming_with_timeout():
    """Example 3: Adding timeout to streaming."""
    print("=" * 60)
    print("Example 3: Stream with Timeout")
    print("=" * 60)

    config = AgentConfig(
        model="deepseek-chat",
        temperature=0.7,
    )
    agent = ChatAgent(config)
    await agent.initialize()

    messages = [
        {"role": "user", "content": "Count from 1 to 100"}
    ]

    print("Streaming with 2-second timeout...")
    print("Output: ", end="", flush=True)

    try:
        async with asyncio.timeout(2.0):
            async for event in agent.stream(messages):
                if event["type"] == "content":
                    print(event["data"]["text"], end="", flush=True)

    except asyncio.TimeoutError:
        print("\n[Timeout reached]")

    print("\n")


async def collecting_stream_results():
    """Example 4: Collecting and processing stream results."""
    print("=" * 60)
    print("Example 4: Collecting Stream Results")
    print("=" * 60)

    config = AgentConfig(
        model="deepseek-chat",
        temperature=0.7,
    )
    agent = ChatAgent(config)
    await agent.initialize()

    messages = [
        {"role": "user", "content": "What is 100 factorial?"}
    ]

    # Collect all events
    events = []
    content_parts = []
    tool_calls = []

    async for event in agent.stream(messages, show_thinking=True):
        events.append(event)

        if event["type"] == "content":
            content_parts.append(event["data"]["text"])
        elif event["type"] == "tool_call":
            tool_calls.append(event["data"])

    # Process collected data
    full_response = "".join(content_parts)

    print(f"Total events collected: {len(events)}")
    print(f"Content pieces: {len(content_parts)}")
    print(f"Tool calls made: {len(tool_calls)}")
    print(f"\nFull response length: {len(full_response)} characters")
    print(f"Response preview: {full_response[:200]}...")

    if tool_calls:
        print(f"\nTools used:")
        for tc in tool_calls:
            print(f"  - {tc['tool']}: {tc['input']}")

    print()


async def parallel_streaming():
    """Example 5: Running multiple streams in parallel."""
    print("=" * 60)
    print("Example 5: Parallel Streaming")
    print("=" * 60)

    queries = [
        "What is 2 + 2?",
        "What is 5 * 5?",
        "What is 10 - 3?",
    ]

    async def stream_query(query: str, query_id: int) -> str:
        """Stream a single query and return the result."""
        config = AgentConfig(
            model="deepseek-chat",
            temperature=0.7,
        )
        agent = ChatAgent(config)
        await agent.initialize()

        messages = [{"role": "user", "content": query}]
        response_parts = []

        async for event in agent.stream(messages):
            if event["type"] == "content":
                response_parts.append(event["data"]["text"])

        return f"Query {query_id} ({query}): {''.join(response_parts)}"

    print("Running 3 queries in parallel...\n")

    # Run all queries concurrently
    tasks = [
        stream_query(q, i+1)
        for i, q in enumerate(queries)
    ]

    results = await asyncio.gather(*tasks)

    for result in results:
        print(result)

    print()


async def progress_tracking_streaming():
    """Example 6: Tracking progress during streaming."""
    print("=" * 60)
    print("Example 6: Progress Tracking")
    print("=" * 60)

    config = AgentConfig(
        model="deepseek-chat",
        temperature=0.7,
    )
    agent = ChatAgent(config)
    await agent.initialize()

    messages = [
        {"role": "user", "content": "Write a haiku about programming"}
    ]

    # Track progress
    stats = {
        "tokens_received": 0,
        "chars_received": 0,
        "tool_calls": 0,
        "start_time": asyncio.get_event_loop().time(),
    }

    print("Streaming with progress tracking...")
    print("-" * 40)

    async for event in agent.stream(messages):
        current_time = asyncio.get_event_loop().time()
        elapsed = current_time - stats["start_time"]

        if event["type"] == "content":
            text = event["data"]["text"]
            stats["tokens_received"] += 1  # Approximate
            stats["chars_received"] += len(text)

            # Show progress every 10 tokens (approximate)
            if stats["tokens_received"] % 10 == 0:
                print(f"\rProgress: {stats['tokens_received']} tokens, "
                      f"{stats['chars_received']} chars, "
                      f"{elapsed:.2f}s elapsed", end="")

        elif event["type"] == "tool_call":
            stats["tool_calls"] += 1

    total_time = asyncio.get_event_loop().time() - stats["start_time"]

    print(f"\n\nFinal stats:")
    print(f"  Total tokens (approx): {stats['tokens_received']}")
    print(f"  Total characters: {stats['chars_received']}")
    print(f"  Tool calls: {stats['tool_calls']}")
    print(f"  Total time: {total_time:.2f}s")
    print(f"  Chars/second: {stats['chars_received'] / total_time:.1f}")

    print()


async def error_recovery_streaming():
    """Example 7: Error handling and recovery."""
    print("=" * 60)
    print("Example 7: Error Handling in Streaming")
    print("=" * 60)

    config = AgentConfig(
        model="deepseek-chat",
        temperature=0.7,
    )
    agent = ChatAgent(config)
    await agent.initialize()

    messages = [
        {"role": "user", "content": "What is 500 / 0?"}  # Division by zero
    ]

    print("Query: What is 500 / 0?")
    print("Assistant: ", end="", flush=True)

    error_occurred = False
    error_details = None

    async for event in agent.stream(messages, show_thinking=True):
        if event["type"] == "content":
            print(event["data"]["text"], end="", flush=True)
        elif event["type"] == "error":
            error_occurred = True
            error_details = event["data"]
            print(f"\n[Error occurred: {error_details.get('error_code', 'UNKNOWN')}]")

    if error_occurred and error_details:
        print(f"\nError details: {error_details}")

    print("\n")


async def interactive_streaming_demo():
    """Example 8: Building an interactive streaming display."""
    print("=" * 60)
    print("Example 8: Interactive Streaming Display")
    print("=" * 60)

    config = AgentConfig(
        model="deepseek-chat",
        temperature=0.7,
    )
    agent = ChatAgent(config)
    await agent.initialize()

    messages = [
        {"role": "user", "content": "List 5 interesting facts about space"}
    ]

    # Build a rich display
    content_buffer = []
    current_section = None

    print("┌" + "─" * 58 + "┐")
    print("│" + " " * 58 + "│")

    line_width = 56
    current_line = "│ "

    async for event in agent.stream(messages):
        if event["type"] == "content":
            text = event["data"]["text"]
            content_buffer.append(text)

            # Simple word wrap
            words = text.split(" ")
            for word in words:
                if len(current_line) + len(word) + 1 > line_width + 2:
                    # Pad and print current line
                    padding = " " * (line_width + 2 - len(current_line))
                    print(current_line + padding + "│")
                    current_line = "│ " + word
                else:
                    current_line += " " + word if current_line != "│ " else word

        elif event["type"] == "tool_call":
            # Pad current line
            padding = " " * (line_width + 2 - len(current_line))
            print(current_line + padding + "│")
            current_line = "│ "
            print(f"│ [Tool: {event['data']['tool']}]" + " " * (line_width - len(event['data']['tool']) - 8) + "│")

    # Print final line
    if current_line != "│ ":
        padding = " " * (line_width + 2 - len(current_line))
        print(current_line + padding + "│")

    print("│" + " " * 58 + "│")
    print("└" + "─" * 58 + "┘")

    print(f"\nTotal content length: {len(''.join(content_buffer))} chars")
    print()


async def main():
    """Run all advanced streaming examples."""
    print("\n")
    print("*" * 60)
    print("Chat Shell 101 - Advanced Streaming Examples")
    print("*" * 60)
    print("\n")

    try:
        await basic_event_streaming()
        await streaming_with_cancellation()
        await streaming_with_timeout()
        await collecting_stream_results()
        await parallel_streaming()
        await progress_tracking_streaming()
        await error_recovery_streaming()
        await interactive_streaming_demo()

    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()
        raise

    print("*" * 60)
    print("All examples completed!")
    print("*" * 60)


if __name__ == "__main__":
    asyncio.run(main())
