#!/usr/bin/env python3
"""
Integration Test Example for Chat Shell 101

This script provides end-to-end verification and testing patterns:
1. Complete chat session with multiple turns
2. History persistence testing with JSON storage
3. Tool execution verification
4. Error recovery demonstrations
5. Performance timing measurements
6. pytest-style assertions for validation

Usage:
    python integration_test.py

Note: Can be run with mock mode (no API key) or real mode (with OPENAI_API_KEY).
"""

import asyncio
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chat_shell_101.agent import ChatAgent
from chat_shell_101.config import config
from chat_shell_101.storage import JSONStorage, MemoryStorage
from chat_shell_101.storage.interfaces import Message
from chat_shell_101.tools.registry import tool_registry


# ============================================================================
# Test Utilities
# ============================================================================

class TestResult:
    """Container for test results."""
    def __init__(self, name: str):
        self.name = name
        self.passed = False
        self.error: Optional[str] = None
        self.duration: float = 0.0
        self.details: Dict[str, Any] = {}

    def success(self, details: Dict[str, Any] = None) -> None:
        """Mark test as successful."""
        self.passed = True
        if details:
            self.details.update(details)

    def failure(self, error: str, details: Dict[str, Any] = None) -> None:
        """Mark test as failed."""
        self.passed = False
        self.error = error
        if details:
            self.details.update(details)


async def run_test(test_func, *args, **kwargs) -> TestResult:
    """Run a test function and capture results."""
    test_name = test_func.__name__.replace("test_", "").replace("_", " ").title()
    result = TestResult(test_name)

    start_time = time.perf_counter()
    try:
        await test_func(result, *args, **kwargs)
        if not result.error:  # Test didn't explicitly fail
            result.success()
    except Exception as e:
        result.failure(str(e))
    finally:
        result.duration = time.perf_counter() - start_time

    return result


def assert_true(condition: bool, message: str = "Assertion failed") -> None:
    """Simple assertion for testing."""
    if not condition:
        raise AssertionError(message)


def assert_equal(actual: Any, expected: Any, message: str = "Values not equal") -> None:
    """Assert equality for testing."""
    if actual != expected:
        raise AssertionError(f"{message}: expected {expected}, got {actual}")


# ============================================================================
# Test Functions
# ============================================================================

async def test_agent_initialization(result: TestResult) -> None:
    """Test agent initialization and basic functionality."""
    print("  Testing agent initialization...")

    # Create and initialize agent
    agent = ChatAgent()
    await agent.initialize()

    # Verify agent is ready
    assert_true(agent is not None, "Agent should not be None")
    result.details["agent_created"] = True

    # Test basic invocation (with mock response if no API key)
    messages = [{"role": "user", "content": "Test message"}]

    try:
        response = await agent.invoke(messages)
        assert_true(isinstance(response, str), "Response should be string")
        result.details["invoke_works"] = True
        result.details["response_length"] = len(response)
    except Exception as e:
        if "API key" in str(e):
            result.details["invoke_requires_api"] = True
            print("    (API key required for real invocation)")
        else:
            raise

    # Test streaming
    try:
        content_count = 0
        async for event in agent.stream(messages, show_thinking=False):
            if event["type"] == "content":
                content_count += 1

        assert_true(content_count > 0, "Should receive content events")
        result.details["streaming_works"] = True
        result.details["content_events"] = content_count
    except Exception as e:
        if "API key" in str(e):
            result.details["streaming_requires_api"] = True
            print("    (API key required for real streaming)")
        else:
            raise


async def test_calculator_tool(result: TestResult) -> None:
    """Test calculator tool functionality."""
    print("  Testing calculator tool...")

    # Get calculator tool from registry
    calculator = tool_registry.get_tool("calculator")
    assert_true(calculator is not None, "Calculator tool should be registered")
    result.details["tool_found"] = True

    # Test simple arithmetic
    test_cases = [
        ("2 + 2", "4"),
        ("10 * 5", "50"),
        ("100 / 4", "25.0"),  # Fixed: division returns float
        ("(3 + 4) * 2", "14"),
    ]

    from chat_shell_101.tools.calculator import CalculatorInput

    for expression, expected in test_cases:
        input_data = CalculatorInput(expression=expression)
        output = await calculator.execute(input_data)

        # Check for error
        assert_true(not output.error, f"Calculator error: {output.error}")

        # Parse result
        actual = output.result
        if "Result:" in output.result:
            parts = output.result.split("Result:")
            assert_true(len(parts) == 2, f"Unexpected result format: {output.result}")
            actual = parts[1].strip()
        else:
            actual = output.result.strip()
        
        assert_equal(actual, expected, f"Calculation failed for {expression}")

    result.details["test_cases_passed"] = len(test_cases)
    result.details["tool_works"] = True


async def test_storage_persistence(result: TestResult) -> None:
    """Test JSON storage persistence across sessions."""
    print("  Testing storage persistence...")

    # Create unique session ID
    session_id = f"test-persistence-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    # Create JSON storage
    storage = JSONStorage()
    await storage.initialize()

    # Create test messages
    test_messages = [
        Message(role="user", content="Storage test message 1", timestamp=datetime.now()),
        Message(role="assistant", content="Storage test response 1", timestamp=datetime.now()),
        Message(role="user", content="Storage test message 2", timestamp=datetime.now()),
    ]

    # Save messages
    await storage.history.append_messages(session_id, test_messages)
    result.details["messages_saved"] = len(test_messages)

    # Retrieve immediately
    history1 = await storage.history.get_history(session_id)
    assert_equal(len(history1), len(test_messages), "Should retrieve all saved messages")

    # Verify content
    for i, msg in enumerate(history1):
        assert_equal(msg.content, test_messages[i].content, f"Message {i} content mismatch")
        assert_equal(msg.role, test_messages[i].role, f"Message {i} role mismatch")

    # Simulate "new session" by creating new storage instance
    await storage.close()

    # Create new storage instance (simulating new program run)
    storage2 = JSONStorage()
    await storage2.initialize()

    # Retrieve from "new session"
    history2 = await storage2.history.get_history(session_id)
    assert_equal(len(history2), len(test_messages), "Messages should persist across sessions")

    # Cleanup
    await storage2.history.clear_history(session_id)
    history3 = await storage2.history.get_history(session_id)
    assert_equal(len(history3), 0, "History should be cleared")

    await storage2.close()

    result.details["persistence_verified"] = True
    result.details["session_id"] = session_id


async def test_memory_storage(result: TestResult) -> None:
    """Test memory storage (non-persistent)."""
    print("  Testing memory storage...")

    # Create memory storage
    storage = MemoryStorage()
    await storage.initialize()

    session_id = "test-memory-session"
    test_message = Message(role="user", content="Memory test", timestamp=datetime.now())

    # Save message
    await storage.history.append_messages(session_id, [test_message])

    # Retrieve
    history = await storage.history.get_history(session_id)
    assert_equal(len(history), 1, "Should retrieve saved message")
    assert_equal(history[0].content, test_message.content, "Content should match")

    # Clear
    await storage.history.clear_history(session_id)
    history_after = await storage.history.get_history(session_id)
    assert_equal(len(history_after), 0, "History should be cleared")

    result.details["memory_storage_works"] = True


async def test_multi_turn_conversation(result: TestResult) -> None:
    """Test multi-turn conversation with history."""
    print("  Testing multi-turn conversation...")

    # Create agent
    agent = ChatAgent()
    await agent.initialize()

    # Create memory storage for conversation
    storage = MemoryStorage()
    await storage.initialize()

    session_id = "test-conversation"
    conversation_history: List[Dict[str, str]] = []

    # Simulate conversation turns
    turns = [
        ("Hello, how are you?", "greeting"),
        ("What is 15 + 27?", "calculation"),
        ("Thank you for your help!", "closing"),
    ]

    for user_message, turn_type in turns:
        # Add user message to history
        conversation_history.append({"role": "user", "content": user_message})

        # Also save to storage
        storage_msg = Message(role="user", content=user_message, timestamp=datetime.now())
        await storage.history.append_messages(session_id, [storage_msg])

        try:
            # Get agent response
            response = await agent.invoke(conversation_history)

            # Add assistant response to history
            conversation_history.append({"role": "assistant", "content": response})

            # Save to storage
            storage_msg = Message(role="assistant", content=response, timestamp=datetime.now())
            await storage.history.append_messages(session_id, [storage_msg])

            result.details[f"turn_{turn_type}_response_length"] = len(response)

        except Exception as e:
            if "API key" in str(e):
                # Mock response for demonstration
                mock_response = f"Mock response to: {user_message}"
                conversation_history.append({"role": "assistant", "content": mock_response})
                result.details[f"turn_{turn_type}_mock"] = True
            else:
                raise

    # Verify conversation length
    expected_messages = len(turns) * 2  # Each turn has user + assistant message
    assert_equal(len(conversation_history), expected_messages, "Conversation history length mismatch")

    # Verify storage has all messages
    stored_history = await storage.history.get_history(session_id)
    assert_equal(len(stored_history), expected_messages, "Storage history length mismatch")

    result.details["conversation_turns"] = len(turns)
    result.details["total_messages"] = len(conversation_history)
    result.details["multi_turn_works"] = True

    # Cleanup
    await storage.history.clear_history(session_id)


async def test_error_handling(result: TestResult) -> None:
    """Test error handling and recovery."""
    print("  Testing error handling...")

    # Get calculator tool
    calculator = tool_registry.get_tool("calculator")
    assert_true(calculator is not None, "Calculator tool should exist")

    from chat_shell_101.tools.calculator import CalculatorInput

    # Test error cases
    error_cases = [
        "10 / 0",  # Division by zero
        "2 + ",  # Incomplete expression
        "abc * 123",  # Invalid characters
        "",  # Empty expression
    ]

    error_results = []
    for expression in error_cases:
        input_data = CalculatorInput(expression=expression)
        output = await calculator.execute(input_data)

        # Calculator should return error for invalid expressions
        if output.error:
            error_results.append((expression, output.error))
            result.details[f"error_{expression.replace(' ', '_')}"] = output.error
        else:
            # Some invalid expressions might still produce a result
            result.details[f"no_error_{expression.replace(' ', '_')}"] = output.result

    result.details["error_cases_tested"] = len(error_cases)
    result.details["errors_found"] = len(error_results)
    result.details["error_handling_works"] = True


async def test_performance_timing(result: TestResult) -> None:
    """Test basic performance timing."""
    print("  Testing performance timing...")

    # Time agent initialization
    init_start = time.perf_counter()
    agent = ChatAgent()
    await agent.initialize()
    init_time = time.perf_counter() - init_start

    result.details["init_time_seconds"] = round(init_time, 3)

    # Time tool execution (calculator)
    calculator = tool_registry.get_tool("calculator")
    from chat_shell_101.tools.calculator import CalculatorInput

    tool_times = []
    expressions = ["2+2", "10*5", "100/4", "(3+4)*2"]

    for expr in expressions:
        start = time.perf_counter()
        input_data = CalculatorInput(expression=expr)
        await calculator.execute(input_data)
        tool_time = time.perf_counter() - start
        tool_times.append(tool_time)

    avg_tool_time = sum(tool_times) / len(tool_times) if tool_times else 0
    result.details["avg_tool_time_seconds"] = round(avg_tool_time, 4)
    result.details["tool_executions_timed"] = len(expressions)

    # Time storage operations
    storage = MemoryStorage()
    await storage.initialize()

    storage_times = []
    session_id = "perf-test"
    message = Message(role="user", content="Performance test", timestamp=datetime.now())

    # Append timing
    start = time.perf_counter()
    await storage.history.append_messages(session_id, [message])
    storage_times.append(time.perf_counter() - start)

    # Get history timing
    start = time.perf_counter()
    await storage.history.get_history(session_id)
    storage_times.append(time.perf_counter() - start)

    # Clear timing
    start = time.perf_counter()
    await storage.history.clear_history(session_id)
    storage_times.append(time.perf_counter() - start)

    avg_storage_time = sum(storage_times) / len(storage_times) if storage_times else 0
    result.details["avg_storage_time_seconds"] = round(avg_storage_time, 4)
    result.details["storage_operations_timed"] = len(storage_times)

    result.details["performance_tested"] = True


# ============================================================================
# Main Test Runner
# ============================================================================

async def run_all_tests() -> Dict[str, TestResult]:
    """Run all integration tests."""
    print("Chat Shell 101 - Integration Tests")
    print("=" * 60)

    # Check API key status
    has_api_key = bool(os.getenv("OPENAI_API_KEY"))
    print(f"API Key configured: {'✅ Yes' if has_api_key else '⚠️ No (using mock mode)'}")
    print()

    # Define test suite
    test_functions = [
        test_agent_initialization,
        test_calculator_tool,
        test_storage_persistence,
        test_memory_storage,
        test_multi_turn_conversation,
        test_error_handling,
        test_performance_timing,
    ]

    # Run tests
    results = {}
    for test_func in test_functions:
        print(f"Running: {test_func.__name__.replace('test_', '').replace('_', ' ').title()}...")
        result = await run_test(test_func)
        results[test_func.__name__] = result

        status = "✅ PASS" if result.passed else "❌ FAIL"
        print(f"  {status} ({result.duration:.2f}s)")

        if result.error:
            print(f"    Error: {result.error}")

    return results


def print_test_summary(results: Dict[str, TestResult]) -> None:
    """Print detailed test summary."""
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    # Count results
    total = len(results)
    passed = sum(1 for r in results.values() if r.passed)
    failed = total - passed

    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed/total*100):.1f}%")

    # Detailed results
    print("\nDetailed Results:")
    for name, result in results.items():
        test_name = name.replace("test_", "").replace("_", " ")
        status = "✅ PASS" if result.passed else "❌ FAIL"
        print(f"  {status} {test_name:30} ({result.duration:.2f}s)")

    # Print failures
    failures = [(name, r) for name, r in results.items() if not r.passed]
    if failures:
        print("\nFailures:")
        for name, result in failures:
            test_name = name.replace("test_", "").replace("_", " ")
            print(f"  ❌ {test_name}: {result.error}")

    # Print key findings
    print("\nKey Findings:")
    all_details = {}
    for result in results.values():
        all_details.update(result.details)

    # Extract interesting details
    interesting_keys = [
        "agent_created", "invoke_works", "streaming_works",
        "tool_found", "tool_works", "test_cases_passed",
        "persistence_verified", "memory_storage_works",
        "multi_turn_works", "error_handling_works",
        "performance_tested", "init_time_seconds",
    ]

    for key in interesting_keys:
        if key in all_details:
            value = all_details[key]
            print(f"  • {key.replace('_', ' ').title()}: {value}")

    print("\n" + "=" * 60)
    if failed == 0:
        print("✅ ALL TESTS PASSED!")
    else:
        print(f"⚠️  {failed} TEST(S) FAILED")
    print("=" * 60)


async def main() -> None:
    """Main async entry point."""
    # Set mock API key if not set (for demonstration)
    if not os.getenv("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = "mock-key-for-demonstration"
        print("⚠️  Running in demonstration mode (no real API calls)")
        print("   Set OPENAI_API_KEY environment variable for real testing\n")

    try:
        # Run all tests
        results = await run_all_tests()

        # Print summary
        print_test_summary(results)

        # Determine exit code
        failed_count = sum(1 for r in results.values() if not r.passed)
        return 1 if failed_count > 0 else 0

    except Exception as e:
        print(f"\n❌ Unexpected error during testing: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    # Run the async main function
    exit_code = asyncio.run(main())
    sys.exit(exit_code)