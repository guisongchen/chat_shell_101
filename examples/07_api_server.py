"""
Example 07: API Server - HTTP Endpoints and Programmatic Access

This example demonstrates how to use the Chat Shell 101 HTTP API programmatically,
including session management, streaming responses, and history access.

Note: This example requires the server to be running. Start it with:
    chat-shell serve --port 8000

Or run this example with the --demo flag to see the API structure without
making actual requests.

Prerequisites:
    1. Copy .env.example to .env: `cp .env.example .env`
    2. Edit .env and set your OPENAI_API_KEY
"""

import asyncio
import json
import argparse
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Optional imports - only needed for actual API calls
try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False
    print("Note: Install httpx to make actual API calls: pip install httpx")


@dataclass
class ChatSession:
    """Represents a chat session with the API."""
    session_id: str
    base_url: str = "http://localhost:8000"


class ChatAPIClient:
    """Client for the Chat Shell 101 HTTP API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.client = None
        if HAS_HTTPX:
            self.client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)

    async def health_check(self) -> dict:
        """Check if the server is running."""
        if not self.client:
            return {"status": "demo_mode", "message": "httpx not installed"}

        response = await self.client.get("/health")
        return response.json()

    async def chat(self, message: str, session_id: Optional[str] = None) -> dict:
        """Send a chat message and get response."""
        if not self.client:
            return self._demo_response("chat", {"message": message, "session_id": session_id})

        payload = {"message": message}
        if session_id:
            payload["session_id"] = session_id

        response = await self.client.post("/chat", json=payload)
        return response.json()

    async def chat_stream(self, message: str, session_id: Optional[str] = None):
        """Send a chat message and stream the response."""
        if not self.client:
            yield self._demo_response("stream", {"message": message})
            return

        payload = {"message": message}
        if session_id:
            payload["session_id"] = session_id

        async with self.client.stream("POST", "/chat/stream", json=payload) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]  # Remove "data: " prefix
                    if data == "[DONE]":
                        break
                    try:
                        yield json.loads(data)
                    except json.JSONDecodeError:
                        pass

    async def get_history(self, session_id: str) -> dict:
        """Get chat history for a session."""
        if not self.client:
            return self._demo_response("history", {"session_id": session_id})

        response = await self.client.get(f"/history/{session_id}")
        return response.json()

    async def list_sessions(self) -> dict:
        """List all chat sessions."""
        if not self.client:
            return self._demo_response("sessions", {})

        response = await self.client.get("/sessions")
        return response.json()

    async def clear_session(self, session_id: str) -> dict:
        """Clear a chat session."""
        if not self.client:
            return self._demo_response("clear", {"session_id": session_id})

        response = await self.client.delete(f"/session/{session_id}")
        return response.json()

    def _demo_response(self, endpoint: str, params: dict) -> dict:
        """Generate demo response when httpx is not available."""
        return {
            "demo": True,
            "endpoint": endpoint,
            "params": params,
            "message": "This is a demo response. Install httpx for real API calls."
        }

    async def close(self):
        """Close the HTTP client."""
        if self.client:
            await self.client.aclose()


async def api_structure_demo():
    """Example 1: Show API structure without making calls."""
    print("=" * 60)
    print("Example 1: API Structure Overview")
    print("=" * 60)

    api_structure = {
        "endpoints": [
            {
                "path": "GET /health",
                "description": "Health check endpoint",
                "response": {"status": "healthy", "version": "0.1.0"}
            },
            {
                "path": "POST /chat",
                "description": "Send a message and get response",
                "request": {
                    "message": "string (required)",
                    "session_id": "string (optional)",
                    "model": "string (optional)",
                    "temperature": "float (optional)"
                },
                "response": {
                    "response": "string",
                    "session_id": "string",
                    "model": "string"
                }
            },
            {
                "path": "POST /chat/stream",
                "description": "Send a message and stream response (SSE)",
                "request": {
                    "message": "string (required)",
                    "session_id": "string (optional)"
                },
                "response": "Server-Sent Events stream"
            },
            {
                "path": "GET /history/{session_id}",
                "description": "Get chat history for a session",
                "response": {
                    "session_id": "string",
                    "messages": [
                        {"role": "user", "content": "...", "timestamp": "..."}
                    ]
                }
            },
            {
                "path": "GET /sessions",
                "description": "List all active sessions",
                "response": {
                    "sessions": ["session-id-1", "session-id-2"]
                }
            },
            {
                "path": "DELETE /session/{session_id}",
                "description": "Clear a session",
                "response": {"status": "cleared", "session_id": "..."}
            },
        ]
    }

    for endpoint in api_structure["endpoints"]:
        print(f"\n{endpoint['path']}")
        print(f"  {endpoint['description']}")
        if "request" in endpoint:
            print(f"  Request: {json.dumps(endpoint['request'], indent=4)}")
        print(f"  Response: {json.dumps(endpoint['response'], indent=4)}")

    print()


async def simple_chat_example(client: ChatAPIClient):
    """Example 2: Simple chat request."""
    print("=" * 60)
    print("Example 2: Simple Chat Request")
    print("=" * 60)

    response = await client.chat("What is 2 + 2?")

    if response.get("demo"):
        print("Demo mode - would send:")
        print(f"  POST /chat")
        print(f"  Body: {{'message': 'What is 2 + 2?'}}")
        print(f"\n  Response: {json.dumps(response, indent=2)}")
    else:
        print(f"Response: {response.get('response')}")
        print(f"Session ID: {response.get('session_id')}")
        print(f"Model: {response.get('model')}")

    print()


async def streaming_chat_example(client: ChatAPIClient):
    """Example 3: Streaming chat request."""
    print("=" * 60)
    print("Example 3: Streaming Chat Request")
    print("=" * 60)

    if not HAS_HTTPX:
        print("Demo mode - would stream:")
        print("  POST /chat/stream")
        print("  Body: {'message': 'Count to 5'}")
        print("  Response: Server-Sent Events")
        print("\n  Example SSE events:")
        print('    data: {"type": "content", "data": {"text": "1"}}')
        print('    data: {"type": "content", "data": {"text": ", 2"}}')
        print('    data: {"type": "content", "data": {"text": ", 3"}}')
        print('    data: [DONE]')
        print()
        return

    print("Streaming response:\n")
    print("Assistant: ", end="", flush=True)

    async for event in client.chat_stream("Count to 5"):
        if event.get("type") == "content":
            print(event["data"]["text"], end="", flush=True)
        elif event.get("type") == "tool_call":
            print(f"\n[Tool: {event['data']['tool']}]")

    print("\n")


async def session_management_example(client: ChatAPIClient):
    """Example 4: Session management."""
    print("=" * 60)
    print("Example 4: Session Management")
    print("=" * 60)

    # Create a session by sending a message
    session_id = None

    response1 = await client.chat("My name is Alice", session_id)
    session_id = response1.get("session_id")
    print(f"Created session: {session_id}")

    # Continue the session
    response2 = await client.chat("What's my name?", session_id)
    print(f"Follow-up response: {response2.get('response', 'N/A')[:100]}...")

    # Get session history
    history = await client.get_history(session_id)
    messages = history.get("messages", [])
    print(f"\nSession history ({len(messages)} messages):")
    for msg in messages[:4]:  # Show first 4 messages
        role = msg.get("role", "unknown")
        content = msg.get("content", "")[:50]
        print(f"  [{role}] {content}...")

    # List all sessions
    sessions = await client.list_sessions()
    print(f"\nAll sessions: {sessions.get('sessions', [])}")

    # Clear the session
    cleared = await client.clear_session(session_id)
    print(f"\nCleared session: {cleared.get('status')}")

    print()


async def multi_session_example(client: ChatAPIClient):
    """Example 5: Multiple concurrent sessions."""
    print("=" * 60)
    print("Example 5: Multiple Concurrent Sessions")
    print("=" * 60)

    # Create multiple sessions
    sessions = {}
    queries = [
        ("math-session", "What is 15 * 23?"),
        ("fact-session", "Tell me a fun fact"),
        ("code-session", "Write a Python hello world"),
    ]

    print("Creating sessions...")
    for session_name, query in queries:
        response = await client.chat(query)
        session_id = response.get("session_id", f"demo-{session_name}")
        sessions[session_name] = {
            "id": session_id,
            "query": query,
            "response": response.get("response", "Demo response")[:50]
        }
        print(f"  {session_name}: {session_id}")

    print("\nSession details:")
    for name, info in sessions.items():
        print(f"  {name}:")
        print(f"    Query: {info['query']}")
        print(f"    Response: {info['response']}...")

    print()


async def error_handling_example(client: ChatAPIClient):
    """Example 6: API error handling."""
    print("=" * 60)
    print("Example 6: API Error Handling")
    print("=" * 60)

    error_scenarios = [
        ("Empty message", {"message": ""}),
        ("Missing message field", {}),
        ("Invalid session", {"message": "Hello", "session_id": "nonexistent"}),
    ]

    for description, payload in error_scenarios:
        print(f"\nScenario: {description}")
        print(f"  Request: {json.dumps(payload)}")

        if not HAS_HTTPX:
            print("  Response: {\"demo\": true, \"error\": \"Would return HTTP 400\"}")
        else:
            try:
                response = await client.client.post("/chat", json=payload)
                print(f"  Status: {response.status_code}")
                print(f"  Response: {response.text[:200]}")
            except Exception as e:
                print(f"  Error: {e}")

    print()


async def batch_requests_example(client: ChatAPIClient):
    """Example 7: Batch processing multiple requests."""
    print("=" * 60)
    print("Example 7: Batch Request Processing")
    print("=" * 60)

    queries = [
        "What is 2 + 2?",
        "What is 3 * 3?",
        "What is 10 - 5?",
        "What is 20 / 4?",
    ]

    print(f"Processing {len(queries)} queries in parallel...\n")

    if not HAS_HTTPX:
        print("Demo mode - would send parallel requests:")
        for query in queries:
            print(f"  POST /chat - {query}")
        print()
        return

    # Process all queries concurrently
    tasks = [client.chat(q) for q in queries]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for query, result in zip(queries, results):
        if isinstance(result, Exception):
            print(f"  ✗ {query}: Error - {result}")
        else:
            response = result.get("response", "No response")[:50]
            print(f"  ✓ {query}: {response}...")

    print()


async def main():
    """Run all API examples."""
    parser = argparse.ArgumentParser(description="Chat Shell 101 API Examples")
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run in demo mode without making actual API calls"
    )
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="Base URL for the API server"
    )
    args = parser.parse_args()

    print("\n")
    print("*" * 60)
    print("Chat Shell 101 - API Server Examples")
    print("*" * 60)
    print("\n")

    if not HAS_HTTPX and not args.demo:
        print("Note: httpx not installed. Running in demo mode.\n")
        args.demo = True

    client = ChatAPIClient(base_url=args.url)

    try:
        # Check server health (if not in demo mode)
        if not args.demo:
            health = await client.health_check()
            print(f"Server health: {health}\n")

        await api_structure_demo()
        await simple_chat_example(client)
        await streaming_chat_example(client)
        await session_management_example(client)
        await multi_session_example(client)
        await error_handling_example(client)
        await batch_requests_example(client)

    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await client.close()

    print("*" * 60)
    print("All examples completed!")
    print("*" * 60)


if __name__ == "__main__":
    asyncio.run(main())
