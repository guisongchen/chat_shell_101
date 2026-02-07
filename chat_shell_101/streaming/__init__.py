"""
Streaming response system for Chat Shell 101.

Provides comprehensive streaming infrastructure with SSE support,
session recovery, event buffering, and robust error handling.
"""

from .events import (
    BaseStreamEvent,
    ChunkEvent,
    ToolStartEvent,
    ToolResultEvent,
    ThinkingEvent,
    StreamOffsetEvent,
    ErrorEvent,
    CompleteEvent,
    CancelledEvent,
    EventType,
)
from .state import StreamingState, StreamSession
from .buffer import EventBuffer
from .emitter import SSEEmitter, ClientConnection
from .core import StreamingCore
from .exceptions import (
    StreamingError,
    StreamNotFoundError,
    StreamAlreadyExistsError,
    StreamCompletedError,
    StreamCancelledError,
    ClientDisconnectedError,
    BufferOverflowError,
)

__all__ = [
    # Events
    "BaseStreamEvent",
    "ChunkEvent",
    "ToolStartEvent",
    "ToolResultEvent",
    "ThinkingEvent",
    "StreamOffsetEvent",
    "ErrorEvent",
    "CompleteEvent",
    "CancelledEvent",
    "EventType",
    # State
    "StreamingState",
    "StreamSession",
    # Buffer
    "EventBuffer",
    # Emitter
    "SSEEmitter",
    "ClientConnection",
    # Core
    "StreamingCore",
    # Exceptions
    "StreamingError",
    "StreamNotFoundError",
    "StreamAlreadyExistsError",
    "StreamCompletedError",
    "StreamCancelledError",
    "ClientDisconnectedError",
    "BufferOverflowError",
]
