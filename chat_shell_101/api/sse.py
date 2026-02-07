"""
Server-Sent Events streaming for chat responses.
"""

import asyncio
from typing import AsyncGenerator

from .schemas import ChatEvent
from ..agent.agent import ChatAgent


async def stream_chat_events(
    agent: ChatAgent,
    messages: list,
    session_id: str,
    subtask_id: str,
) -> AsyncGenerator[ChatEvent, None]:
    """
    Stream chat events as SSE.

    Yields ChatEvent objects for content, tool calls, and completion.
    """
    from .app import app_state

    try:
        async for event in agent.stream(messages, thread_id=session_id):
            event_type = event.get("type", "")
            data = event.get("data", {})

            yield ChatEvent(event_type=event_type, data=data)

        # Mark complete
        yield ChatEvent(event_type="complete", data={})

        # Update session status
        if subtask_id in app_state["active_sessions"]:
            app_state["active_sessions"][subtask_id]["status"] = "completed"

    except asyncio.CancelledError:
        # Handle cancellation
        if subtask_id in app_state["active_sessions"]:
            app_state["active_sessions"][subtask_id]["status"] = "cancelled"
        yield ChatEvent(event_type="cancelled", data={})
        raise
    except Exception as e:
        if subtask_id in app_state["active_sessions"]:
            app_state["active_sessions"][subtask_id]["status"] = "error"
        yield ChatEvent(event_type="error", data={"message": str(e)})
