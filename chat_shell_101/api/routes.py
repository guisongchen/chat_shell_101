"""
API routes for HTTP mode.
"""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sse_starlette.sse import EventSourceResponse

from ..agent.agent import ChatAgent
from ..config import config
from .schemas import (
    ChatRequest,
    ChatResponse,
    ChatEvent,
    SessionStatus,
    SessionHistory,
    HealthResponse,
    ErrorResponse,
)
from .dependencies import get_agent, get_session_manager
from .sse import stream_chat_events


router = APIRouter()


@router.post(
    "/response",
    response_model=ChatResponse,
    responses={500: {"model": ErrorResponse}},
)
async def start_chat(
    request: ChatRequest,
    agent: ChatAgent = Depends(get_agent),
) -> ChatResponse:
    """
    Start a new chat session.

    Creates a new subtask for processing the chat messages.
    Returns immediately with a subtask_id for polling or streaming.
    """
    subtask_id = str(uuid.uuid4())
    session_id = request.session_id or f"session-{int(datetime.now().timestamp())}"

    # Store session info
    from .app import app_state
    app_state["active_sessions"][subtask_id] = {
        "session_id": session_id,
        "status": "running",
        "created_at": datetime.now(),
        "messages": request.messages,
    }

    # If streaming requested, return SSE stream
    if request.stream:
        async def event_generator():
            async for event in stream_chat_events(
                agent=agent,
                messages=[{"role": m.role, "content": m.content} for m in request.messages],
                session_id=session_id,
                subtask_id=subtask_id,
            ):
                yield {
                    "event": event.event_type,
                    "data": event.model_dump(),
                }

        return EventSourceResponse(
            event_generator(),
            headers={"X-Subtask-ID": subtask_id},
        )

    # Non-streaming: process and return subtask_id
    return ChatResponse(
        subtask_id=subtask_id,
        session_id=session_id,
        status="created",
    )


@router.get("/response/{subtask_id}", response_model=SessionStatus)
async def get_session_status(
    subtask_id: str,
    session_manager=Depends(get_session_manager),
) -> SessionStatus:
    """
    Get status of a chat session.

    Used for polling when not using streaming.
    """
    from .app import app_state

    session = app_state["active_sessions"].get(subtask_id)
    if not session:
        raise HTTPException(status_code=404, detail="Subtask not found")

    return SessionStatus(
        subtask_id=subtask_id,
        session_id=session["session_id"],
        status=session["status"],
        created_at=session["created_at"],
        updated_at=datetime.now(),
        message_count=len(session.get("messages", [])),
    )


@router.delete("/response/{subtask_id}")
async def cancel_session(
    subtask_id: str,
    session_manager=Depends(get_session_manager),
):
    """
    Cancel a running chat session.
    """
    from .app import app_state

    if subtask_id not in app_state["active_sessions"]:
        raise HTTPException(status_code=404, detail="Subtask not found")

    # Mark as cancelled
    app_state["active_sessions"][subtask_id]["status"] = "cancelled"

    return {"status": "cancelled", "subtask_id": subtask_id}


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.
    """
    import time
    from .app import app_state

    uptime = time.time() - app_state["start_time"] if app_state["start_time"] else 0

    return HealthResponse(
        status="healthy",
        version="0.1.0",
        uptime_seconds=uptime,
        active_sessions=len(app_state["active_sessions"]),
        models_available=[config.openai.model],
    )


@router.get("/sessions/{session_id}/history", response_model=SessionHistory)
async def get_session_history(
    session_id: str,
) -> SessionHistory:
    """
    Get full message history for a session.
    """
    # Implementation would fetch from storage
    # For now, return empty history
    return SessionHistory(
        session_id=session_id,
        messages=[],
        total_messages=0,
    )
