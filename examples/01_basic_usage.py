"""
Example 01: Basic Usage - Getting Started with Chat Shell 101

This example demonstrates the fundamental usage patterns of the Chat Shell 101
library including agent initialization, simple queries, and streaming responses.

Prerequisites:
    1. Copy .env.example to .env: `cp .env.example .env`
    2. Edit .env and set your OPENAI_API_KEY
"""

import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from chat_shell_101.agent.agent import ChatAgent
from chat_shell_101.agent.config import AgentConfig


async def basic_invoke_example():
    """Example 1: Simple invoke - get complete response at once."""
    print("=" * 60)
    print("Example 1: Basic Invoke (Non-streaming)")
    print("=" * 60)

    # Create agent with default configuration
    config = AgentConfig(
        model="deepseek-chat",
        temperature=0.7,
    )
    agent = ChatAgent(config)
    await agent.initialize()

    # Simple question - get full response
    messages = [
        {"role": "user", "content": "What is 2 + 2?"}
    ]

    response = await agent.invoke(messages)
    print(f"User: What is 2 + 2?")
    print(f"Assistant: {response}")
    print()


async def streaming_example():
    """Example 2: Streaming - get tokens as they arrive."""
    print("=" * 60)
    print("Example 2: Streaming Response")
    print("=" * 60)

    config = AgentConfig(
        model="deepseek-chat",
        temperature=0.7,
    )
    agent = ChatAgent(config)
    await agent.initialize()

    messages = [
        {"role": "user", "content": "Count from 1 to 5"}
    ]

    print("User: Count from 1 to 5")
    print("Assistant: ", end="", flush=True)

    # Stream tokens as they arrive from the LLM
    async for event in agent.stream(messages):
        if event["type"] == "content":
            print(event["data"]["text"], end="", flush=True)

    print("\n")


async def multi_turn_conversation_example():
    """Example 3: Multi-turn conversation with history."""
    print("=" * 60)
    print("Example 3: Multi-turn Conversation")
    print("=" * 60)

    config = AgentConfig(
        model="deepseek-chat",
        temperature=0.7,
    )
    agent = ChatAgent(config)
    await agent.initialize()

    # Conversation with context
    messages = [
        {"role": "user", "content": "My name is Alice"},
    ]

    print("User: My name is Alice")
    response1 = await agent.invoke(messages)
    print(f"Assistant: {response1}")

    # Add assistant response to history
    messages.append({"role": "assistant", "content": response1})

    # Follow-up question that requires context
    messages.append({"role": "user", "content": "What's my name?"})

    print("User: What's my name?")
    response2 = await agent.invoke(messages)
    print(f"Assistant: {response2}")
    print()


async def system_prompt_example():
    """Example 4: Using system prompts to customize behavior."""
    print("=" * 60)
    print("Example 4: System Prompt Customization")
    print("=" * 60)

    # Agent with custom system prompt
    config = AgentConfig(
        model="deepseek-chat",
        temperature=0.7,
        system_prompt="You are a helpful coding assistant. Always provide code examples when relevant."
    )
    agent = ChatAgent(config)
    await agent.initialize()

    messages = [
        {"role": "user", "content": "How do I read a file in Python?"}
    ]

    print("User: How do I read a file in Python?")
    response = await agent.invoke(messages)
    print(f"Assistant: {response}")
    print()


async def event_types_example():
    """Example 5: Handling different event types in streaming."""
    print("=" * 60)
    print("Example 5: Understanding Event Types")
    print("=" * 60)

    config = AgentConfig(
        model="deepseek-chat",
        temperature=0.7,
    )
    agent = ChatAgent(config)
    await agent.initialize()

    messages = [
        {"role": "user", "content": "Calculate 15 * 23"}
    ]

    print("User: Calculate 15 * 23")
    print("Events:")

    async for event in agent.stream(messages, show_thinking=True):
        event_type = event["type"]
        data = event["data"]

        if event_type == "content":
            # Regular text content from the model
            print(f"  [CONTENT] {data['text']}")

        elif event_type == "thinking":
            # Model's thinking process (when show_thinking=True)
            print(f"  [THINKING] {data['text']}")

        elif event_type == "tool_call":
            # Tool being called
            print(f"  [TOOL_CALL] {data['tool']}({data['input']})")

        elif event_type == "tool_result":
            # Result from tool execution
            print(f"  [TOOL_RESULT] {data['result']}")

        elif event_type == "error":
            # Error occurred
            print(f"  [ERROR] {data['message']}")

    print()


async def temperature_comparison_example():
    """Example 6: Comparing different temperature settings."""
    print("=" * 60)
    print("Example 6: Temperature Comparison")
    print("=" * 60)

    prompt = "Describe the color blue in one creative sentence."

    for temp in [0.0, 0.7, 1.5]:
        config = AgentConfig(
            model="deepseek-chat",
            temperature=temp,
        )
        agent = ChatAgent(config)
        await agent.initialize()

        messages = [{"role": "user", "content": prompt}]
        response = await agent.invoke(messages)

        print(f"Temperature {temp}: {response}")

    print()


async def main():
    """Run all basic usage examples."""
    print("\n")
    print("*" * 60)
    print("Chat Shell 101 - Basic Usage Examples")
    print("*" * 60)
    print("\n")

    try:
        await basic_invoke_example()
        await streaming_example()
        await multi_turn_conversation_example()
        await system_prompt_example()
        await event_types_example()
        await temperature_comparison_example()

    except Exception as e:
        print(f"Error running examples: {e}")
        print("\nMake sure to:")
        print("  1. Copy .env.example to .env: cp .env.example .env")
        print("  2. Set your OPENAI_API_KEY in the .env file")
        raise

    print("*" * 60)
    print("All examples completed!")
    print("*" * 60)


if __name__ == "__main__":
    asyncio.run(main())
