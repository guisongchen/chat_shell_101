"""
Example 03: Storage Backends - Working with Chat History

This example demonstrates the different storage backends available in Chat Shell 101
including JSON file storage, SQLite storage, and in-memory storage.

Prerequisites:
    1. Copy .env.example to .env: `cp .env.example .env`
    2. Edit .env and set your OPENAI_API_KEY
"""

import asyncio
import tempfile
import shutil
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from chat_shell_101.storage import JSONStorage, MemoryStorage, SQLiteStorage
from chat_shell_101.storage.interfaces import Message
from chat_shell_101.agent.agent import ChatAgent
from chat_shell_101.agent.config import AgentConfig


async def memory_storage_example():
    """Example 1: In-memory storage (non-persistent)."""
    print("=" * 60)
    print("Example 1: Memory Storage (Non-persistent)")
    print("=" * 60)

    # Create memory storage
    storage = MemoryStorage()
    await storage.initialize()

    session_id = "test-session-1"

    # Add some messages
    messages = [
        Message(role="user", content="Hello!"),
        Message(role="assistant", content="Hi there! How can I help you?"),
        Message(role="user", content="What's the weather like?"),
    ]

    await storage.history.append_messages(session_id, messages)

    # Retrieve messages
    history = await storage.history.get_history(session_id)
    print(f"Session: {session_id}")
    print(f"Messages: {len(history)}")
    for msg in history:
        print(f"  [{msg.role}] {msg.content}")

    # Clear history
    await storage.history.clear_history(session_id)
    history = await storage.history.get_history(session_id)
    print(f"After clear: {len(history)} messages")

    await storage.close()
    print()


async def json_storage_example():
    """Example 2: JSON file storage (persistent)."""
    print("=" * 60)
    print("Example 2: JSON File Storage (Persistent)")
    print("=" * 60)

    # Create temporary directory for storage
    temp_dir = tempfile.mkdtemp()
    print(f"Storage path: {temp_dir}")

    try:
        # Create JSON storage
        storage = JSONStorage(storage_path=temp_dir)
        await storage.initialize()

        session_id = "persistent-session"

        # Add messages
        messages = [
            Message(role="user", content="Remember this number: 42"),
            Message(role="assistant", content="I'll remember that the number is 42."),
        ]

        await storage.history.append_messages(session_id, messages)

        # Retrieve messages
        history = await storage.history.get_history(session_id)
        print(f"Session: {session_id}")
        for msg in history:
            timestamp = msg.timestamp.strftime("%H:%M:%S") if msg.timestamp else "?"
            print(f"  [{timestamp}] {msg.role}: {msg.content}")

        await storage.close()

        # Re-open storage (simulating new session) and verify persistence
        print("\nRe-opening storage...")
        storage2 = JSONStorage(storage_path=temp_dir)
        await storage2.initialize()

        history2 = await storage2.history.get_history(session_id)
        print(f"Retrieved {len(history2)} messages after re-opening")

        await storage2.close()

    finally:
        # Clean up
        shutil.rmtree(temp_dir)
        print(f"Cleaned up: {temp_dir}")

    print()


async def sqlite_storage_example():
    """Example 3: SQLite storage (persistent with query capabilities)."""
    print("=" * 60)
    print("Example 3: SQLite Storage (Persistent + Queryable)")
    print("=" * 60)

    # Create temporary database
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "chat.db")
    print(f"Database path: {db_path}")

    try:
        # Create SQLite storage
        storage = SQLiteStorage(db_path=db_path)
        await storage.initialize()

        # Create multiple sessions
        sessions = {
            "session-1": [
                Message(role="user", content="Session 1 message 1"),
                Message(role="assistant", content="Session 1 response 1"),
            ],
            "session-2": [
                Message(role="user", content="Session 2 message 1"),
                Message(role="assistant", content="Session 2 response 1"),
                Message(role="user", content="Session 2 message 2"),
            ],
        }

        # Add messages to each session
        for session_id, messages in sessions.items():
            await storage.history.append_messages(session_id, messages)

        # List all sessions (SQLite-specific feature)
        if hasattr(storage.history, "list_sessions"):
            all_sessions = await storage.history.list_sessions()
            print(f"All sessions: {all_sessions}")

        # Get history for specific session
        history = await storage.history.get_history("session-2")
        print(f"\nSession-2 messages:")
        for msg in history:
            print(f"  [{msg.role}] {msg.content}")

        # Clear one session
        await storage.history.clear_history("session-1")
        print("\nCleared session-1")

        if hasattr(storage.history, "list_sessions"):
            remaining = await storage.history.list_sessions()
            print(f"Remaining sessions: {remaining}")

        await storage.close()

    finally:
        shutil.rmtree(temp_dir)
        print(f"Cleaned up: {temp_dir}")

    print()


async def storage_with_agent_example():
    """Example 4: Using storage with agent for persistent conversations."""
    print("=" * 60)
    print("Example 4: Storage + Agent Integration")
    print("=" * 60)

    # Create temporary storage
    temp_dir = tempfile.mkdtemp()

    try:
        storage = JSONStorage(storage_path=temp_dir)
        await storage.initialize()

        session_id = "agent-session"

        # Simulate a conversation
        config = AgentConfig(model="deepseek-chat", temperature=0.7)
        agent = ChatAgent(config)
        await agent.initialize()

        # First user message
        user_input = "What is 2 + 2?"
        messages = [{"role": "user", "content": user_input}]

        print(f"User: {user_input}")
        response = await agent.invoke(messages)
        print(f"Assistant: {response}")

        # Save to storage
        await storage.history.append_messages(session_id, [
            Message(role="user", content=user_input),
            Message(role="assistant", content=response),
        ])

        # Second user message (with history)
        user_input2 = "Multiply that by 3"
        history = await storage.history.get_history(session_id)
        messages = []
        for msg in history:
            messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": user_input2})

        print(f"\nUser: {user_input2}")
        response2 = await agent.invoke(messages)
        print(f"Assistant: {response2}")

        # Save second exchange
        await storage.history.append_messages(session_id, [
            Message(role="user", content=user_input2),
            Message(role="assistant", content=response2),
        ])

        # Show final history
        final_history = await storage.history.get_history(session_id)
        print(f"\nFinal history ({len(final_history)} messages):")
        for msg in final_history:
            print(f"  [{msg.role}] {msg.content[:50]}...")

        await storage.close()

    finally:
        shutil.rmtree(temp_dir)

    print()


async def storage_comparison_example():
    """Example 5: Comparing storage backends."""
    print("=" * 60)
    print("Example 5: Storage Backend Comparison")
    print("=" * 60)

    temp_dir = tempfile.mkdtemp()

    try:
        # Test all three storage types
        storages = {
            "Memory": MemoryStorage(),
            "JSON": JSONStorage(storage_path=temp_dir / Path("json_test")),
            "SQLite": SQLiteStorage(db_path=temp_dir / Path("test.db")),
        }

        for name, storage in storages.items():
            await storage.initialize()

            # Add test messages
            session_id = "comparison-test"
            messages = [
                Message(role="user", content="Test message 1"),
                Message(role="assistant", content="Test response 1"),
                Message(role="user", content="Test message 2"),
                Message(role="assistant", content="Test response 2"),
            ]

            start = asyncio.get_event_loop().time()
            await storage.history.append_messages(session_id, messages)
            history = await storage.history.get_history(session_id)
            elapsed = asyncio.get_event_loop().time() - start

            # Check features
            has_list_sessions = hasattr(storage.history, "list_sessions")

            print(f"\n{name} Storage:")
            print(f"  - Persistent: {name != 'Memory'}")
            print(f"  - List sessions: {has_list_sessions}")
            print(f"  - Messages stored: {len(history)}")
            print(f"  - Operation time: {elapsed:.4f}s")

            await storage.close()

    finally:
        shutil.rmtree(temp_dir)

    print()


async def message_format_example():
    """Example 6: Understanding message format and timestamps."""
    print("=" * 60)
    print("Example 6: Message Format and Metadata")
    print("=" * 60)

    storage = MemoryStorage()
    await storage.initialize()

    # Create messages with different roles
    messages = [
        Message(role="system", content="You are a helpful assistant."),
        Message(role="user", content="Hello!"),
        Message(role="assistant", content="Hi! How can I help?"),
        Message(role="user", content="What's 2+2?"),
    ]

    session_id = "format-test"
    await storage.history.append_messages(session_id, messages)

    # Retrieve and inspect
    history = await storage.history.get_history(session_id)

    for i, msg in enumerate(history):
        print(f"Message {i+1}:")
        print(f"  Role: {msg.role}")
        print(f"  Content: {msg.content}")
        print(f"  Timestamp: {msg.timestamp}")
        print(f"  Type: {type(msg.timestamp)}")
        print()

    await storage.close()


from pathlib import Path


async def main():
    """Run all storage examples."""
    print("\n")
    print("*" * 60)
    print("Chat Shell 101 - Storage Backends Examples")
    print("*" * 60)
    print("\n")

    try:
        await memory_storage_example()
        await json_storage_example()
        await sqlite_storage_example()
        await storage_with_agent_example()
        await storage_comparison_example()
        await message_format_example()

    except Exception as e:
        print(f"Error running examples: {e}")
        raise

    print("*" * 60)
    print("All examples completed!")
    print("*" * 60)


if __name__ == "__main__":
    asyncio.run(main())
