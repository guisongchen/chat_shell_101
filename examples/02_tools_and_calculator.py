"""
Example 02: Tools and Calculator - Working with Tool Execution

This example demonstrates how to use tools in Chat Shell 101, focusing on
the calculator tool and showing how the agent decides when to use tools.

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
from chat_shell_101.tools.registry import tool_registry
from chat_shell_101.tools.calculator import CalculatorTool


async def calculator_basic_example():
    """Example 1: Basic calculator usage through agent."""
    print("=" * 60)
    print("Example 1: Calculator Tool - Basic Math")
    print("=" * 60)

    config = AgentConfig(
        model="deepseek-chat",
        temperature=0.7,
    )
    agent = ChatAgent(config)
    await agent.initialize()

    # The agent will automatically use the calculator tool for math
    messages = [
        {"role": "user", "content": "What is 1234 * 5678?"}
    ]

    print("User: What is 1234 * 5678?")
    print("Assistant: ", end="", flush=True)

    async for event in agent.stream(messages, show_thinking=True):
        if event["type"] == "content":
            print(event["data"]["text"], end="", flush=True)
        elif event["type"] == "thinking":
            print(f"\n[Thinking: {event['data']['text']}]")
        elif event["type"] == "tool_call":
            print(f"\n[Using calculator: {event['data']['input']}]")
        elif event["type"] == "tool_result":
            print(f"[Result: {event['data']['result']}]")

    print("\n")


async def calculator_complex_example():
    """Example 2: Complex calculations with multiple steps."""
    print("=" * 60)
    print("Example 2: Complex Multi-step Calculation")
    print("=" * 60)

    config = AgentConfig(
        model="deepseek-chat",
        temperature=0.7,
    )
    agent = ChatAgent(config)
    await agent.initialize()

    # Complex expression that requires multiple calculations
    messages = [
        {"role": "user", "content": "Calculate (150 + 230) * 12 - 500 / 25"}
    ]

    print("User: Calculate (150 + 230) * 12 - 500 / 25")
    print("Assistant: ", end="", flush=True)

    async for event in agent.stream(messages, show_thinking=True):
        if event["type"] == "content":
            print(event["data"]["text"], end="", flush=True)
        elif event["type"] == "tool_call":
            print(f"\n[Tool: {event['data']['tool']}({event['data']['input']})]")
        elif event["type"] == "tool_result":
            print(f"[Result: {event['data']['result']}]", end=" ")

    print("\n")


async def direct_calculator_example():
    """Example 3: Using calculator tool directly (without agent)."""
    print("=" * 60)
    print("Example 3: Direct Calculator Tool Usage")
    print("=" * 60)

    # Create calculator instance directly
    calculator = CalculatorTool()

    # Test various expressions
    expressions = [
        "2 + 2",
        "100 / 3",
        "2 ** 10",
        "15 % 4",
        "100 // 3",
        "-5 + 10",
        "(2 + 3) * 4",
    ]

    for expr in expressions:
        from chat_shell_101.tools.calculator import CalculatorInput
        input_data = CalculatorInput(expression=expr)
        result = await calculator.execute(input_data)

        if result.error:
            print(f"  {expr} = ERROR: {result.error}")
        else:
            print(f"  {expr} = {result.result}")

    print()


async def tool_registry_example():
    """Example 4: Exploring the tool registry."""
    print("=" * 60)
    print("Example 4: Tool Registry")
    print("=" * 60)

    # Get the global tool registry
    registry = tool_registry

    print(f"Registered tools: {registry.get_tool_names()}")
    print()

    # Get tool schemas
    schemas = registry.get_tool_schemas()
    for name, schema in schemas.items():
        print(f"Tool: {name}")
        print(f"  Schema: {schema}")
        print()

    # Check if specific tool exists
    has_calculator = registry.has_tool("calculator")
    print(f"Has 'calculator' tool: {has_calculator}")

    # Get specific tool
    calc_tool = registry.get_tool("calculator")
    print(f"Calculator description: {calc_tool.description}")
    print()


async def math_vs_no_math_example():
    """Example 5: Comparing math vs non-math queries."""
    print("=" * 60)
    print("Example 5: When Does the Agent Use Tools?")
    print("=" * 60)

    config = AgentConfig(
        model="deepseek-chat",
        temperature=0.7,
    )
    agent = ChatAgent(config)
    await agent.initialize()

    queries = [
        "What is 999 * 888?",  # Should use calculator
        "Tell me a joke",       # Should not use calculator
        "Calculate the square root of 144",  # Might use calculator
        "What is the capital of France?",    # Should not use calculator
    ]

    for query in queries:
        print(f"\nQuery: {query}")
        messages = [{"role": "user", "content": query}]

        tool_used = False
        async for event in agent.stream(messages):
            if event["type"] == "tool_call":
                tool_used = True
                print(f"  -> Tool used: {event['data']['tool']}")
            elif event["type"] == "content":
                pass  # Collecting response

        if not tool_used:
            print("  -> No tool used (direct LLM response)")

    print()


async def calculator_edge_cases_example():
    """Example 6: Calculator edge cases and error handling."""
    print("=" * 60)
    print("Example 6: Calculator Edge Cases")
    print("=" * 60)

    calculator = CalculatorTool()

    # Test edge cases
    test_cases = [
        ("Division by zero", "1 / 0"),
        ("Large numbers", "999999999 * 999999999"),
        ("Nested parentheses", "((1 + 2) * (3 + 4)) / 2"),
        ("Whitespace handling", "  10   +   20  "),
        ("Negative numbers", "-5 * -5"),
        ("Power operation", "2 ** 10"),
        ("Floor division", "17 // 5"),
        ("Modulo", "17 % 5"),
    ]

    for description, expr in test_cases:
        from chat_shell_101.tools.calculator import CalculatorInput
        input_data = CalculatorInput(expression=expr)
        result = await calculator.execute(input_data)

        status = "✓" if not result.error else "✗"
        print(f"  {status} {description}: {expr}")
        if result.error:
            print(f"      Error: {result.error}")
        else:
            print(f"      Result: {result.result}")

    print()


async def main():
    """Run all tool examples."""
    print("\n")
    print("*" * 60)
    print("Chat Shell 101 - Tools and Calculator Examples")
    print("*" * 60)
    print("\n")

    try:
        await calculator_basic_example()
        await calculator_complex_example()
        await direct_calculator_example()
        await tool_registry_example()
        await math_vs_no_math_example()
        await calculator_edge_cases_example()

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
