"""
Tool registry for managing available tools.
"""

from typing import Dict, List
from .base import BaseTool
from .calculator import CalculatorTool


class ToolRegistry:
    """Registry for managing tools."""

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """Register a tool."""
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> BaseTool:
        """Get a tool by name."""
        if name not in self._tools:
            raise KeyError(f"Tool not found: {name}")
        return self._tools[name]

    def get_all_tools(self) -> List[BaseTool]:
        """Get all registered tools."""
        return list(self._tools.values())

    def get_tool_names(self) -> List[str]:
        """Get names of all registered tools."""
        return list(self._tools.keys())

    def to_langchain_tools(self):
        """Convert tools to LangChain tool format."""
        from langchain.tools import StructuredTool
        langchain_tools = []

        for tool in self._tools.values():
            # Create a wrapper function that matches LangChain's expected signature
            async def execute_wrapper(**kwargs):
                input_data = tool.input_schema(**kwargs)
                result = await tool.execute(input_data)
                if result.error:
                    raise ValueError(result.error)
                return result.result

            langchain_tool = StructuredTool.from_function(
                func=execute_wrapper,
                name=tool.name,
                description=tool.description,
                args_schema=tool.input_schema,
            )
            langchain_tools.append(langchain_tool)

        return langchain_tools


# Global tool registry instance
tool_registry = ToolRegistry()

# Register default tools
tool_registry.register(CalculatorTool())