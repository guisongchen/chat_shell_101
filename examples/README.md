# Chat Shell 101 Examples

This directory contains example scripts demonstrating various usage patterns for the Chat Shell 101 library.

## Overview

The examples are designed to help users understand how to:

1. **Use the library programmatically** - Import and use ChatAgent in your own code
2. **Create custom tools** - Extend the tool system with new capabilities
3. **Configure storage backends** - Use JSON (persistent) or Memory (temporary) storage
4. **Test functionality** - Run integration tests and verify tool execution

## Example Scripts

### 1. `basic_usage.py`

**Purpose**: Core library usage patterns for new users.

**Demonstrates**:
- Importing and initializing `ChatAgent`
- Using `invoke()` for simple chat interactions
- Using `stream()` for streaming responses with thinking process
- Calculator tool usage with arithmetic queries
- Error handling for missing API keys and invalid expressions
- CLI integration using `subprocess`

**Usage**:
```bash
python examples/basic_usage.py
```

**Key Features**:
- Self-contained script with mock mode (no API key required)
- Step-by-step demonstrations with clear output
- Shows both streaming and non-streaming approaches
- Demonstrates error handling patterns

### 2. `advanced_config.py`

**Purpose**: Advanced customization and configuration options.

**Demonstrates**:
- Creating custom tools (`CurrentTimeTool`, `FileInfoTool`)
- Registering tools with the global tool registry
- Comparing JSON vs Memory storage backends
- Batch processing with `asyncio.gather()`
- Programmatic configuration overrides
- Storage operations (append, retrieve, clear)
- Tool registration lifecycle

**Usage**:
```bash
python examples/advanced_config.py
```

**Key Features**:
- Complete custom tool implementation examples
- Storage backend comparison with practical examples
- Parallel processing demonstrations
- Configuration management patterns

### 3. `integration_test.py`

**Purpose**: End-to-end verification and testing patterns.

**Demonstrates**:
- Complete chat session with multiple turns
- History persistence testing with JSON storage
- Tool execution verification (calculator tool)
- Error recovery demonstrations
- Performance timing measurements
- pytest-style assertions for validation

**Usage**:
```bash
python examples/integration_test.py
```

**Key Features**:
- Can run in mock mode (no API key) or real mode
- Comprehensive test suite with detailed reporting
- Performance benchmarking
- Storage persistence verification
- Error handling validation

## Prerequisites

### Python Version
- Python 3.10 or higher (3.10-3.13 recommended)
- Python 3.14 has compatibility issues with LangChain

### Dependencies
All dependencies are installed with the main package:
```bash
# Install package with development dependencies
uv sync --extra dev
```

### Environment Variables
For real API calls, set:
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

For demonstration purposes (mock mode), the examples will run without a valid API key.

## Running Examples

### Basic Setup
```bash
# Navigate to project root
cd /home/ccc/vibe_projects/chat_shell_101

# Activate virtual environment (if using)
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Run examples
python examples/basic_usage.py
python examples/advanced_config.py
python examples/integration_test.py
```

### With Real API Key
```bash
# Set API key
export OPENAI_API_KEY="sk-..."

# Run with real API calls
python examples/basic_usage.py
```

### Mock Mode (No API Key)
If no `OPENAI_API_KEY` is set, examples will run in demonstration mode:
- Show expected behavior and output patterns
- Use mock responses where API calls would be needed
- Demonstrate error handling for missing API keys

## Example Output

Each script provides structured output:

```
Chat Shell 101 - Basic Usage Examples
============================================================

DEMONSTRATION 1: Basic Agent Invocation
============================================================

1. Creating and initializing ChatAgent...
   ✅ Agent initialized successfully

2. Testing calculator tool with arithmetic queries:

   Query: What is 15 * 27?
   Response: 15 * 27 equals 405.

...
```

## Extending Examples

### Adding New Examples
1. Create a new Python file in the `examples/` directory
2. Follow the async pattern with `asyncio.run(main())`
3. Include comprehensive docstrings and comments
4. Test with both mock and real API modes

### Custom Tool Creation
See `advanced_config.py` for complete examples:
1. Extend `BaseTool` abstract class
2. Define `ToolInput` subclass with Pydantic fields
3. Implement `async execute()` method
4. Register with `tool_registry.register()`

### Storage Backend Integration
See examples for:
- `JSONStorage`: Persistent storage to disk
- `MemoryStorage`: Temporary in-memory storage
- Both implement the same `StorageProvider` interface

## Integration with Tests

The `integration_test.py` script demonstrates testing patterns that can be integrated into the project's test suite:

```python
# Example test pattern
async def test_calculator_tool():
    calculator = tool_registry.get_tool("calculator")
    input_data = CalculatorInput(expression="2 + 2")
    output = await calculator.execute(input_data)
    assert "4" in output.result
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're running from project root or have added it to `sys.path`
2. **API Key Errors**: Set `OPENAI_API_KEY` environment variable or run in mock mode
3. **Async Runtime Errors**: Use `asyncio.run()` for standalone scripts
4. **Storage Path Issues**: Check permissions for JSON storage directory

### Debug Mode
Enable debug output:
```bash
CHAT_SHELL_DEBUG=1 python examples/basic_usage.py
```

## Related Documentation

- [Main README.md](../README.md) - Project overview and setup
- [CLAUDE.md](../CLAUDE.md) - Development guidelines and architecture
- [todo.md](../todo.md) - Project roadmap and tasks
- Source code documentation in docstrings

## Contributing

When adding new examples:
1. Follow existing code style (black, isort)
2. Include comprehensive docstrings
3. Test with both mock and real API modes
4. Update this README.md with new example documentation

## License

Same as main project: Apache 2.0

---

**Last Updated**: 2026-01-30
**Examples Version**: 1.0.0
**Compatibility**: Chat Shell 101 v0.1.0+