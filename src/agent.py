"""
LangGraph ReAct agent for Chat Shell 101.
"""

import asyncio
from typing import Dict, List, Any, AsyncGenerator
from pydantic import BaseModel

from langchain_openai import ChatOpenAI
from langchain.tools import StructuredTool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor, ToolInvocation
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph.message import add_messages

from .config import config
from .tools.registry import tool_registry
from .utils import format_tool_call, format_tool_result, format_thinking


class AgentState(BaseModel):
    """State for the agent graph."""
    messages: List[Any] = []
    next: str = "agent"


class ChatAgent:
    """Chat agent with ReAct pattern using LangGraph."""

    def __init__(self):
        self.llm = None
        self.tools = []
        self.tool_executor = None
        self.graph = None
        self._initialized = False

    async def initialize(self):
        """Initialize the agent."""
        if self._initialized:
            return

        # Initialize LLM
        self.llm = ChatOpenAI(
            model=config.openai.model,
            api_key=config.openai.api_key,
            temperature=config.openai.temperature,
            max_tokens=config.openai.max_tokens,
            streaming=True,
        )

        # Get tools from registry
        self.tools = tool_registry.to_langchain_tools()
        self.tool_executor = ToolExecutor(self.tools)

        # Bind tools to LLM
        self.llm_with_tools = self.llm.bind_tools(self.tools)

        # Build the graph
        self.graph = self._build_graph()
        self._initialized = True

    def _build_graph(self):
        """Build the LangGraph state graph."""

        # Define nodes
        async def agent_node(state: AgentState):
            """Node that calls the agent."""
            # Get the last message
            last_message = state.messages[-1]

            # Call the LLM
            response = await self.llm_with_tools.ainvoke(state.messages)

            # Add the response to messages
            state.messages.append(response)

            # Check if the agent wants to use a tool
            if response.tool_calls:
                return {"next": "tools"}
            else:
                return {"next": END}

        async def tools_node(state: AgentState):
            """Node that executes tools."""
            last_message = state.messages[-1]

            tool_calls = last_message.tool_calls
            tool_invocations = [
                ToolInvocation(
                    tool=tool_call["name"],
                    tool_input=tool_call["args"],
                )
                for tool_call in tool_calls
            ]

            # Execute tools in parallel
            tool_outputs = await self.tool_executor.abatch(tool_invocations)

            # Create tool messages
            tool_messages = []
            for tool_call, output in zip(tool_calls, tool_outputs):
                tool_messages.append(
                    AIMessage(
                        content=f"Tool call: {tool_call['name']} with args: {tool_call['args']}. Result: {output}",
                        tool_call_id=tool_call["id"],
                    )
                )

            # Add tool messages to state
            state.messages.extend(tool_messages)

            return {"next": "agent"}

        # Build the graph
        workflow = StateGraph(AgentState)

        # Define nodes
        workflow.add_node("agent", agent_node)
        workflow.add_node("tools", tools_node)

        # Define edges
        workflow.set_entry_point("agent")
        workflow.add_conditional_edges(
            "agent",
            lambda state: "tools" if state.messages[-1].tool_calls else END,
            {"tools": "tools", END: END}
        )
        workflow.add_edge("tools", "agent")

        # Compile the graph
        return workflow.compile()

    async def stream(
        self,
        messages: List[Dict[str, str]],
        show_thinking: bool = False,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream agent responses."""
        if not self._initialized:
            await self.initialize()

        # Convert messages to LangChain format
        lc_messages = []
        for msg in messages:
            if msg["role"] == "system":
                lc_messages.append(SystemMessage(content=msg["content"]))
            elif msg["role"] == "user":
                lc_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                lc_messages.append(AIMessage(content=msg["content"]))

        # Initialize state
        initial_state = AgentState(messages=lc_messages)

        # Run the graph
        async for event in self.graph.astream(initial_state, stream_mode="values"):
            # Get the latest message
            if "messages" in event and event["messages"]:
                last_message = event["messages"][-1]

                if isinstance(last_message, AIMessage):
                    # Check if it's a tool call
                    if last_message.tool_calls:
                        for tool_call in last_message.tool_calls:
                            if show_thinking:
                                yield {
                                    "type": "thinking",
                                    "data": {
                                        "text": f"调用工具 {tool_call['name']} 参数: {tool_call['args']}"
                                    }
                                }
                            yield {
                                "type": "tool_call",
                                "data": {
                                    "tool": tool_call["name"],
                                    "input": tool_call["args"],
                                }
                            }

                            # Execute the tool
                            tool_invocation = ToolInvocation(
                                tool=tool_call["name"],
                                tool_input=tool_call["args"],
                            )
                            try:
                                result = await self.tool_executor.ainvoke(tool_invocation)
                                yield {
                                    "type": "tool_result",
                                    "data": {"result": result}
                                }
                            except Exception as e:
                                yield {
                                    "type": "error",
                                    "data": {"message": f"工具执行错误: {e}"}
                                }
                    else:
                        # It's a regular response
                        if last_message.content:
                            yield {
                                "type": "content",
                                "data": {"text": last_message.content}
                            }
                elif isinstance(last_message, HumanMessage):
                    # User message, skip
                    pass

    async def invoke(self, messages: List[Dict[str, str]]) -> str:
        """Invoke the agent and return the final response."""
        full_response = ""
        async for event in self.stream(messages):
            if event["type"] == "content":
                full_response += event["data"]["text"]
        return full_response


# Global agent instance
_agent_instance = None


async def get_agent() -> ChatAgent:
    """Get or create the global agent instance."""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = ChatAgent()
        await _agent_instance.initialize()
    return _agent_instance