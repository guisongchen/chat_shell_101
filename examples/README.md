# Chat Shell 101 - Examples

This directory contains comprehensive examples demonstrating the features and capabilities of Chat Shell 101.

## Quick Start

1. **Set up your environment:**
   ```bash
   # Copy the example environment file
   cp .env.example .env

   # Edit .env and set your OPENAI_API_KEY
   # The other settings are optional
   ```

2. **Run an example:**
   ```bash
   python examples/01_basic_usage.py
   ```

## Examples Overview

### 01_basic_usage.py - Getting Started
Learn the fundamentals of Chat Shell 101:
- Agent initialization and configuration
- Simple invoke vs streaming responses
- Multi-turn conversations with history
- System prompts and customization
- Understanding event types in streaming
- Temperature comparison

**Key Concepts:** `ChatAgent`, `AgentConfig`, `stream()`, `invoke()`

### 02_tools_and_calculator.py - Working with Tools
Explore the tool system:
- Using the calculator tool through the agent
- Complex multi-step calculations
- Direct tool usage (without agent)
- Tool registry exploration
- When agents decide to use tools
- Calculator edge cases and error handling

**Key Concepts:** `CalculatorTool`, `tool_registry`, `ToolInput`, `ToolOutput`

### 03_storage_backends.py - Chat History Storage
Learn about different storage backends:
- In-memory storage (non-persistent)
- JSON file storage (persistent)
- SQLite storage (persistent with query capabilities)
- Storage with agent integration
- Storage backend comparison
- Message format and metadata

**Key Concepts:** `JSONStorage`, `MemoryStorage`, `SQLiteStorage`, `Message`

### 04_custom_tools.py - Creating Your Own Tools
Build custom tools for your use cases:
- Simple custom tool (Dice Roller)
- Tool with complex input (Weather Simulator)
- Stateful tool (Task Manager)
- Time and date tool
- Tool registration patterns
- Error handling in tools

**Key Concepts:** `BaseTool`, custom tool classes, `tool_registry.register()`

### 05_streaming_advanced.py - Advanced Streaming Patterns
Master streaming and real-time processing:
- Complete event type breakdown
- Stream cancellation
- Streaming with timeout
- Collecting and processing stream results
- Parallel streaming
- Progress tracking
- Error handling and recovery
- Building interactive streaming displays

**Key Concepts:** Event types, `cancellation_event`, `asyncio.timeout`, parallel streams

### 06_configuration.py - Configuration Management
Configure Chat Shell 101 for different environments:
- Environment variables
- Programmatic configuration
- Agent-specific configuration
- Configuration validation
- Configuration files
- Runtime configuration updates
- Hierarchical configuration
- Configuration serialization

**Key Concepts:** `Config`, `AgentConfig`, environment variables, validation

### 07_api_server.py - HTTP API Usage
Use the Chat Shell 101 HTTP API programmatically:
- API structure overview
- Simple chat requests
- Streaming chat requests (SSE)
- Session management
- Multiple concurrent sessions
- Error handling
- Batch request processing

**Key Concepts:** `ChatAPIClient`, HTTP endpoints, Server-Sent Events

## Running Examples

### Prerequisites

Ensure you have the required dependencies:
```bash
uv sync --extra dev
```

### Set Up Environment Variables

All examples read configuration from a `.env` file in the project root:

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API key
# OPENAI_API_KEY=sk-your-key-here
```

**Never hardcode API keys in your code!** Always use environment variables or `.env` files.

### Run Individual Examples

```bash
# Basic usage
python examples/01_basic_usage.py

# Tools and calculator
python examples/02_tools_and_calculator.py

# Storage backends
python examples/03_storage_backends.py

# Custom tools
python examples/04_custom_tools.py

# Advanced streaming
python examples/05_streaming_advanced.py

# Configuration
python examples/06_configuration.py

# API server (requires server running)
python examples/07_api_server.py --demo
```

## Example Patterns

### Basic Agent Usage
```python
from chat_shell_101.agent.agent import ChatAgent
from chat_shell_101.agent.config import AgentConfig

config = AgentConfig(model="deepseek-chat", temperature=0.7)
agent = ChatAgent(config)
await agent.initialize()

# Simple invoke
response = await agent.invoke([{"role": "user", "content": "Hello!"}])

# Streaming
async for event in agent.stream([{"role": "user", "content": "Hello!"}]):
    if event["type"] == "content":
        print(event["data"]["text"], end="")
```

### Custom Tool
```python
from chat_shell_101.tools.base import BaseTool, ToolInput, ToolOutput
from pydantic import Field

class MyInput(ToolInput):
    param: str = Field(..., description="Parameter description")

class MyTool(BaseTool):
    name = "my_tool"
    description = "What this tool does"
    input_schema = MyInput

    async def execute(self, input_data: MyInput) -> ToolOutput:
        result = do_something(input_data.param)
        return ToolOutput(result=result)

# Register and use
tool_registry.register(MyTool())
```

### Storage Usage
```python
from chat_shell_101.storage import JSONStorage
from chat_shell_101.storage.interfaces import Message

storage = JSONStorage()
await storage.initialize()

# Save messages
await storage.history.append_messages("session-1", [
    Message(role="user", content="Hello"),
    Message(role="assistant", content="Hi there!")
])

# Load history
history = await storage.history.get_history("session-1")
```

## Tips

1. **Start Simple**: Begin with `01_basic_usage.py` to understand the basics
2. **Explore Tools**: Check `02_tools_and_calculator.py` to see how tool execution works
3. **Try Custom Tools**: Use `04_custom_tools.py` as a template for your own tools
4. **Streaming is Powerful**: `05_streaming_advanced.py` shows how to build responsive applications
5. **API Integration**: `07_api_server.py` demonstrates how to integrate with the HTTP API

## Troubleshooting

### API Key Issues
If you see "OpenAI API key not set or invalid":
- Copy `.env.example` to `.env`: `cp .env.example .env`
- Edit `.env` and set your `OPENAI_API_KEY`
- Verify the key starts with "sk-"
- Never hardcode API keys in code - always use `.env` files

### Model Not Found
If you get model-related errors:
- Verify your `CHAT_SHELL_DEFAULT_MODEL` is valid
- Check that your API key has access to the requested model

### Connection Errors
If examples fail to connect:
- Check your internet connection
- Verify `BASE_URL` if using a custom endpoint
- Ensure API key is valid and has credits

## Next Steps

After exploring these examples:
1. Build your own tools based on `04_custom_tools.py`
2. Create a custom CLI using patterns from `01_basic_usage.py`
3. Deploy an API server and integrate with `07_api_server.py`
4. Explore the source code in `chat_shell_101/`
