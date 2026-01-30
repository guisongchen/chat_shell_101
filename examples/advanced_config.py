#!/usr/bin/env python3
"""
Advanced Configuration Example for Chat Shell 101

This script demonstrates advanced customization and configuration options:
1. Creating and registering custom tools
2. Comparing JSON vs Memory storage backends
3. Batch processing with asyncio.gather()
4. Programmatic configuration overrides
5. Storage operations and session management
6. Tool registration lifecycle

Usage:
    python advanced_config.py

Note: Requires OPENAI_API_KEY environment variable for real API calls.
"""

import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pydantic import Field

from chat_shell_101.agent import ChatAgent, get_agent
from chat_shell_101.config import config
from chat_shell_101.storage import JSONStorage, MemoryStorage
from chat_shell_101.storage.interfaces import Message
from chat_shell_101.tools.base import BaseTool, ToolInput, ToolOutput
from chat_shell_101.tools.registry import tool_registry


# ============================================================================
# Custom Tool Implementation
# ============================================================================

class CurrentTimeInput(ToolInput):
    """Input schema for CurrentTimeTool."""
    format: str = Field(
        default="%Y-%m-%d %H:%M:%S",
        description="Python datetime format string (e.g., '%Y-%m-%d' for date only)"
    )


class CurrentTimeTool(BaseTool):
    """Custom tool that returns current date and time."""
    name = "current_time"
    description = "Get the current date and time in specified format"
    input_schema = CurrentTimeInput

    async def execute(self, input_data: CurrentTimeInput) -> ToolOutput:
        """Execute the tool to get current time."""
        try:
            current_time = datetime.now().strftime(input_data.format)
            return ToolOutput(result=current_time)
        except Exception as e:
            return ToolOutput(result="", error=f"Invalid format string: {e}")


class FileInfoInput(ToolInput):
    """Input schema for FileInfoTool."""
    path: str = Field(..., description="File or directory path to check")


class FileInfoTool(BaseTool):
    """Custom tool that checks if a file or directory exists."""
    name = "file_info"
    description = "Check if a file or directory exists and get basic info"
    input_schema = FileInfoInput

    async def execute(self, input_data: FileInfoInput) -> ToolOutput:
        """Execute the tool to check file/directory existence."""
        try:
            path = Path(input_data.path)
            if path.exists():
                info = {
                    "exists": True,
                    "is_file": path.is_file(),
                    "is_dir": path.is_dir(),
                    "size": path.stat().st_size if path.is_file() else 0,
                    "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat()
                }
                return ToolOutput(result=info)
            else:
                return ToolOutput(result={"exists": False})
        except Exception as e:
            return ToolOutput(result={}, error=f"Error checking path: {e}")


# ============================================================================
# Demonstration Functions
# ============================================================================

async def demonstrate_custom_tools() -> None:
    """Demonstrate creating and using custom tools."""
    print("=" * 60)
    print("DEMONSTRATION 1: Custom Tool Creation and Registration")
    print("=" * 60)

    print("\n1. Creating custom tools:")
    print("   - CurrentTimeTool: Returns current date/time")
    print("   - FileInfoTool: Checks file/directory existence")

    # Create tool instances
    time_tool = CurrentTimeTool()
    file_tool = FileInfoTool()

    print("\n2. Registering tools with global registry:")
    tool_registry.register(time_tool)
    tool_registry.register(file_tool)

    print(f"   ✅ Registered tools: {tool_registry.get_tool_names()}")

    print("\n3. Testing custom tools directly:")

    # Test CurrentTimeTool
    print("\n   Testing CurrentTimeTool:")
    time_input = CurrentTimeInput(format="%Y-%m-%d")
    result = await time_tool.execute(time_input)
    print(f"     Input: format='%Y-%m-%d'")
    print(f"     Result: {result.result}")
    print(f"     Error: {result.error if result.error else 'None'}")

    # Test with different format
    time_input2 = CurrentTimeInput(format="%A, %B %d, %Y at %I:%M %p")
    result2 = await time_tool.execute(time_input2)
    print(f"\n     Input: format='%A, %B %d, %Y at %I:%M %p'")
    print(f"     Result: {result2.result}")

    # Test FileInfoTool
    print("\n   Testing FileInfoTool:")
    file_input = FileInfoInput(path=__file__)  # This script file
    result3 = await file_tool.execute(file_input)
    print(f"     Input: path='{__file__}'")
    print(f"     Result: {result3.result}")

    # Test with non-existent path
    file_input2 = FileInfoInput(path="/non/existent/path.txt")
    result4 = await file_tool.execute(file_input2)
    print(f"\n     Input: path='/non/existent/path.txt'")
    print(f"     Result: {result4.result}")

    print("\n4. Using custom tools with ChatAgent:")

    # Create agent with custom tools
    agent = ChatAgent()
    await agent.initialize()

    # Test queries that should use custom tools
    test_queries = [
        "What's the current date?",
        "Check if this script file exists: " + __file__,
    ]

    for query in test_queries:
        print(f"\n   Query: {query}")
        messages = [{"role": "user", "content": query}]

        try:
            print("   Streaming response...")
            async for event in agent.stream(messages, show_thinking=True):
                if event["type"] == "tool_call":
                    print(f"     🔧 Tool call: {event['data']['tool']}")
                elif event["type"] == "tool_result":
                    print(f"     📊 Tool result: {event['data']['result']}")
                elif event["type"] == "content":
                    print(f"     Response: {event['data']['text']}", end="")
        except Exception as e:
            if "API key" in str(e):
                print("     (API key required for real tool usage)")
            else:
                print(f"     ❌ Error: {e}")

    print("\n5. Tool registry inspection:")
    print(f"   Available tools: {tool_registry.get_tool_names()}")
    for name in tool_registry.get_tool_names():
        tool = tool_registry.get_tool(name)
        print(f"   - {name}: {tool.description}")


async def demonstrate_storage_backends() -> None:
    """Demonstrate different storage backends."""
    print("\n" + "=" * 60)
    print("DEMONSTRATION 2: Storage Backend Comparison")
    print("=" * 60)

    print("\n1. JSON Storage (persistent to disk):")
    json_storage = JSONStorage()
    await json_storage.initialize()
    print(f"   ✅ Initialized. Storage path: {json_storage.storage_path}")

    print("\n2. Memory Storage (temporary):")
    memory_storage = MemoryStorage()
    await memory_storage.initialize()
    print("   ✅ Initialized (no-op for memory storage)")

    print("\n3. Comparing storage operations:")

    # Create test messages
    session_id = "test-session-" + datetime.now().strftime("%Y%m%d-%H%M%S")
    messages = [
        Message(role="user", content="Hello, storage test!", timestamp=datetime.now()),
        Message(role="assistant", content="Hi there! Storage test successful.", timestamp=datetime.now()),
    ]

    print(f"\n   Session ID: {session_id}")
    print(f"   Test messages: {len(messages)} messages")

    # Test both storage backends
    for storage_name, storage in [("JSON", json_storage), ("Memory", memory_storage)]:
        print(f"\n   Testing {storage_name} Storage:")

        # Append messages
        await storage.history.append_messages(session_id, messages)
        print(f"     ✅ Appended {len(messages)} messages")

        # Get history
        history = await storage.history.get_history(session_id)
        print(f"     ✅ Retrieved history: {len(history)} messages")

        # Verify content
        if history:
            print(f"     First message: '{history[0].content}'")

        # Clear history
        await storage.history.clear_history(session_id)
        print(f"     ✅ Cleared history")

        # Verify cleared
        history_after = await storage.history.get_history(session_id)
        print(f"     History after clear: {len(history_after)} messages")

    print("\n4. Storage persistence demonstration:")
    print("   JSON Storage: Messages persist to disk between runs")
    print("   Memory Storage: Messages lost when program exits")

    # Cleanup
    await json_storage.close()
    print("\n   ✅ JSON storage closed (cleanup complete)")


async def demonstrate_batch_processing() -> None:
    """Demonstrate batch processing with asyncio.gather()."""
    print("\n" + "=" * 60)
    print("DEMONSTRATION 3: Batch Processing")
    print("=" * 60)

    print("\n1. Creating multiple agent instances for parallel processing:")

    # Create multiple agents
    agents = []
    for i in range(3):
        agent = ChatAgent()
        await agent.initialize()
        agents.append(agent)
        print(f"   Created agent {i+1}")

    print("\n2. Batch processing queries with asyncio.gather():")

    queries = [
        "What is 10 * 20?",
        "Calculate 100 / 4",
        "What's 15 + 25?",
    ]

    async def process_query(agent: ChatAgent, query: str) -> str:
        """Process a single query with given agent."""
        try:
            response = await agent.invoke([{"role": "user", "content": query}])
            return response
        except Exception as e:
            return f"Error: {e}"

    # Process all queries in parallel
    print("   Processing queries in parallel...")
    tasks = [process_query(agents[i], queries[i]) for i in range(len(queries))]
    results = await asyncio.gather(*tasks)

    print("\n   Results:")
    for i, (query, result) in enumerate(zip(queries, results)):
        print(f"   {i+1}. Query: {query}")
        print(f"      Result: {result[:50]}..." if len(result) > 50 else f"      Result: {result}")

    print("\n3. Sequential vs parallel timing comparison:")
    print("   (Note: Actual timing depends on API rate limits)")


async def demonstrate_programmatic_config() -> None:
    """Demonstrate programmatic configuration overrides."""
    print("\n" + "=" * 60)
    print("DEMONSTRATION 4: Programmatic Configuration")
    print("=" * 60)

    print("\n1. Current configuration:")
    print(f"   Model: {config.openai.model}")
    print(f"   Temperature: {config.openai.temperature}")
    print(f"   Storage type: {config.storage.type}")
    print(f"   Show thinking: {config.show_thinking}")

    print("\n2. Configuration validation:")
    is_valid = config.validate_api_key()
    print(f"   API key valid: {is_valid}")

    print("\n3. Programmatic overrides (conceptual):")
    print("   # These would modify the config object:")
    print("   # config.openai.model = 'gpt-4-turbo'")
    print("   # config.openai.temperature = 0.5")
    print("   # config.storage.type = 'memory'")
    print("   # config.show_thinking = True")

    print("\n4. Environment variable overrides:")
    print("   Set these environment variables to override defaults:")
    print("   - CHAT_SHELL_DEFAULT_MODEL: Model name")
    print("   - CHAT_SHELL_STORAGE_TYPE: 'json' or 'memory'")
    print("   - CHAT_SHELL_SHOW_THINKING: 'true' or 'false'")
    print("   - CHAT_SHELL_STORAGE_PATH: Storage directory")

    print("\n5. Storage path utilities:")
    storage_path = config.get_storage_path()
    print(f"   Storage path: {storage_path}")
    print(f"   Path exists: {storage_path.exists()}")


async def main() -> None:
    """Main async entry point."""
    print("Chat Shell 101 - Advanced Configuration Examples")
    print("=" * 60)

    # Set mock API key for demonstration if not set
    if not os.getenv("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = "mock-key-for-demonstration"
        print("⚠️  Using mock API key for demonstration purposes")
        print("   Set real OPENAI_API_KEY for actual API calls\n")

    try:
        # Run all demonstrations
        await demonstrate_custom_tools()
        await demonstrate_storage_backends()
        await demonstrate_batch_processing()
        await demonstrate_programmatic_config()

        print("\n" + "=" * 60)
        print("✅ Advanced configuration demonstrations completed!")
        print("=" * 60)
        print("\nKey takeaways:")
        print("1. Create custom tools by extending BaseTool class")
        print("2. Register tools with tool_registry.register()")
        print("3. JSONStorage persists to disk, MemoryStorage is temporary")
        print("4. Use asyncio.gather() for parallel processing")
        print("5. Configuration can be overridden programmatically or via env vars")

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