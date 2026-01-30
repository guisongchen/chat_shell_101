#!/usr/bin/env python3
"""
Basic Usage Example for Chat Shell 101

This script demonstrates core library usage patterns for new users.
It shows how to:
1. Import and initialize the ChatAgent
2. Use invoke() for simple chat interactions
3. Use stream() for streaming responses with thinking process
4. Demonstrate calculator tool usage
5. Handle errors and missing API keys
6. Integrate with CLI using subprocess

Usage:
    python basic_usage.py

Note: Requires OPENAI_API_KEY environment variable to be set.
"""

import asyncio
import os
import subprocess
import sys
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chat_shell_101.agent import ChatAgent, get_agent
from chat_shell_101.config import config


async def demonstrate_basic_invoke() -> None:
    """Demonstrate basic agent invocation with calculator tool."""
    print("=" * 60)
    print("DEMONSTRATION 1: Basic Agent Invocation")
    print("=" * 60)

    # Check if API key is configured
    if not config.openai.api_key:
        print("⚠️  OPENAI_API_KEY not set. Using mock responses for demonstration.")
        print("   Set OPENAI_API_KEY environment variable for real API calls.")

    # Create and initialize agent
    print("\n1. Creating and initializing ChatAgent...")
    agent = ChatAgent()
    await agent.initialize()
    print("   ✅ Agent initialized successfully")

    # Simple chat with calculator tool
    print("\n2. Testing calculator tool with arithmetic queries:")

    test_queries = [
        "What is 15 * 27?",
        "Calculate (3 * 4) / 2",
        "What's 100 - 45 + 18?",
    ]

    for query in test_queries:
        print(f"\n   Query: {query}")
        messages = [{"role": "user", "content": query}]

        try:
            response = await agent.invoke(messages)
            print(f"   Response: {response}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            if "API key" in str(e):
                print("   (This is expected without a valid OPENAI_API_KEY)")

    print("\n3. Testing general conversation:")
    messages = [
        {"role": "system", "content": "You are a helpful math assistant."},
        {"role": "user", "content": "Hello! Can you help me with some calculations?"},
    ]

    try:
        response = await agent.invoke(messages)
        print(f"   Response: {response}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print("   (Using mock response for demonstration)")
        print("   Response: Hello! I'd be happy to help with calculations. I have a calculator tool available.")


async def demonstrate_streaming_with_thinking() -> None:
    """Demonstrate streaming responses with thinking process visualization."""
    print("\n" + "=" * 60)
    print("DEMONSTRATION 2: Streaming with Thinking Process")
    print("=" * 60)

    # Get global agent instance (singleton)
    print("\n1. Getting global agent instance...")
    agent = await get_agent()
    print("   ✅ Global agent obtained")

    # Test query that should trigger calculator tool
    query = "Calculate 25 * 4 + 10 / 2"
    print(f"\n2. Streaming response for: {query}")
    print("   (Thinking process will be shown if enabled)")

    messages = [{"role": "user", "content": query}]

    try:
        print("\n   Streaming response:")
        print("   " + "-" * 40)

        full_response = ""
        async for event in agent.stream(messages, show_thinking=True):
            event_type = event["type"]
            data = event["data"]

            if event_type == "thinking":
                # Thinking process (internal reasoning)
                print(f"   🤔 Thinking: {data['text']}")
            elif event_type == "tool_call":
                # Tool being called
                print(f"   🔧 Tool call: {data['tool']}({data['input']})")
            elif event_type == "tool_result":
                # Tool result
                print(f"   📊 Tool result: {data['result']}")
            elif event_type == "content":
                # Response content
                text = data["text"]
                full_response += text
                print(text, end="", flush=True)
            elif event_type == "error":
                # Error occurred
                print(f"\n   ❌ Error: {data['message']}")

        print(f"\n\n   Full response: {full_response}")

    except Exception as e:
        print(f"\n   ❌ Streaming error: {e}")
        if "API key" in str(e):
            print("   (This is expected without a valid OPENAI_API_KEY)")
            print("   Mock streaming demonstration complete.")


async def demonstrate_error_handling() -> None:
    """Demonstrate error handling patterns."""
    print("\n" + "=" * 60)
    print("DEMONSTRATION 3: Error Handling")
    print("=" * 60)

    print("\n1. Testing invalid expressions with calculator:")

    # Create a new agent instance
    agent = ChatAgent()
    await agent.initialize()

    invalid_queries = [
        "Calculate 10 / 0",  # Division by zero
        "What is 2 +",  # Incomplete expression
        "Calculate abc * 123",  # Invalid characters
    ]

    for query in invalid_queries:
        print(f"\n   Query: {query}")
        messages = [{"role": "user", "content": query}]

        try:
            # Try streaming to see error events
            print("   Streaming response...")
            async for event in agent.stream(messages, show_thinking=False):
                if event["type"] == "error":
                    print(f"   ❌ Error event: {event['data']['message']}")
                elif event["type"] == "content":
                    print(f"   Response: {event['data']['text']}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")


def demonstrate_cli_integration() -> None:
    """Demonstrate CLI integration using subprocess."""
    print("\n" + "=" * 60)
    print("DEMONSTRATION 4: CLI Integration")
    print("=" * 60)

    print("\n1. Showing available CLI commands:")

    try:
        # Run chat-shell --help
        result = subprocess.run(
            ["chat-shell", "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )
        print("   Command: chat-shell --help")
        print("   Output:")
        for line in result.stdout.split('\n'):
            if line.strip():
                print(f"     {line}")
    except FileNotFoundError:
        print("   ❌ 'chat-shell' command not found. Make sure package is installed.")
    except subprocess.TimeoutExpired:
        print("   ⏱️  Command timed out")

    print("\n2. Example CLI command structure:")
    print("   chat-shell chat --model gpt-4 --show-thinking")
    print("   chat-shell chat --storage memory --session test-session")
    print("   chat-shell chat --temperature 0.5")

    print("\n3. Running a simple CLI command (non-interactive):")
    print("   (This would start an interactive chat session)")


async def main() -> None:
    """Main async entry point."""
    print("Chat Shell 101 - Basic Usage Examples")
    print("=" * 60)

    # Set mock API key for demonstration if not set
    if not os.getenv("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = "mock-key-for-demonstration"
        print("⚠️  Using mock API key for demonstration purposes")
        print("   Set real OPENAI_API_KEY for actual API calls\n")

    try:
        # Run all demonstrations
        await demonstrate_basic_invoke()
        await demonstrate_streaming_with_thinking()
        await demonstrate_error_handling()
        demonstrate_cli_integration()

        print("\n" + "=" * 60)
        print("✅ Basic usage demonstrations completed!")
        print("=" * 60)
        print("\nKey takeaways:")
        print("1. Use ChatAgent() or get_agent() to get agent instance")
        print("2. Call await agent.initialize() before using agent")
        print("3. Use invoke() for simple responses, stream() for streaming")
        print("4. Calculator tool handles arithmetic expressions")
        print("5. Set OPENAI_API_KEY environment variable for real usage")

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    # Run the async main function
    exit_code = asyncio.run(main())
    sys.exit(exit_code)