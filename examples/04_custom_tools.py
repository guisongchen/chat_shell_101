"""
Example 04: Custom Tools - Creating Your Own Tools

This example demonstrates how to create custom tools by implementing the BaseTool
abstract class and registering them with the tool registry.

Prerequisites:
    1. Copy .env.example to .env: `cp .env.example .env`
    2. Edit .env and set your OPENAI_API_KEY
"""

import asyncio
import random
from datetime import datetime
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from pydantic import BaseModel, Field

from chat_shell_101.agent.agent import ChatAgent
from chat_shell_101.agent.config import AgentConfig
from chat_shell_101.tools.base import BaseTool, ToolInput, ToolOutput
from chat_shell_101.tools.registry import tool_registry


# ============================================================================
# Example 1: Simple Custom Tool - Dice Roller
# ============================================================================

class DiceRollerInput(ToolInput):
    """Input for dice roller tool."""
    sides: int = Field(default=6, description="Number of sides on the die")
    count: int = Field(default=1, description="Number of dice to roll")


class DiceRollerTool(BaseTool):
    """Roll dice with specified number of sides."""

    name = "dice_roller"
    description = "Roll dice with a specified number of sides. Useful for games, random decisions, or generating random numbers."
    input_schema = DiceRollerInput

    async def execute(self, input_data: DiceRollerInput) -> ToolOutput:
        """Roll the dice and return results."""
        try:
            if input_data.sides < 1:
                return ToolOutput(result="", error="Dice must have at least 1 side")
            if input_data.count < 1:
                return ToolOutput(result="", error="Must roll at least 1 die")
            if input_data.count > 100:
                return ToolOutput(result="", error="Cannot roll more than 100 dice at once")

            rolls = [random.randint(1, input_data.sides) for _ in range(input_data.count)]
            total = sum(rolls)

            if input_data.count == 1:
                result_str = f"Rolled a {input_data.sides}-sided die: **{rolls[0]}**"
            else:
                result_str = f"Rolled {input_data.count}d{input_data.sides}: {rolls} (Total: **{total}**)"

            return ToolOutput(result=result_str)

        except Exception as e:
            return ToolOutput(result="", error=str(e))


# ============================================================================
# Example 2: Tool with Complex Input - Weather Simulator
# ============================================================================

class WeatherInput(ToolInput):
    """Input for weather tool."""
    city: str = Field(..., description="City name to get weather for")
    include_forecast: bool = Field(default=False, description="Include 3-day forecast")


class WeatherSimulatorTool(BaseTool):
    """Simulate weather data for demonstration purposes."""

    name = "weather"
    description = "Get current weather and forecast for a city. (Simulated for demo purposes)"
    input_schema = WeatherInput

    # Simulated weather data
    _conditions = ["Sunny", "Partly Cloudy", "Cloudy", "Rainy", "Stormy", "Snowy"]

    async def execute(self, input_data: WeatherInput) -> ToolOutput:
        """Generate simulated weather data."""
        try:
            # Use city name to generate consistent "random" weather
            random.seed(input_data.city.lower())

            temp = random.randint(-10, 35)
            condition = random.choice(self._conditions)
            humidity = random.randint(30, 90)

            result = f"Weather in {input_data.city}:\n"
            result += f"  Temperature: {temp}°C\n"
            result += f"  Condition: {condition}\n"
            result += f"  Humidity: {humidity}%"

            if input_data.include_forecast:
                result += "\n\n3-Day Forecast:\n"
                for day in range(1, 4):
                    day_temp = temp + random.randint(-5, 5)
                    day_condition = random.choice(self._conditions)
                    result += f"  Day {day}: {day_condition}, {day_temp}°C\n"

            # Reset random seed
            random.seed()

            return ToolOutput(result=result)

        except Exception as e:
            return ToolOutput(result="", error=str(e))


# ============================================================================
# Example 3: Tool with List Output - Task Manager
# ============================================================================

class TaskManagerInput(ToolInput):
    """Input for task manager tool."""
    action: str = Field(..., description="Action: 'add', 'list', or 'clear'")
    task: str = Field(default="", description="Task description (for 'add' action)")


class TaskManagerTool(BaseTool):
    """Simple in-memory task manager."""

    name = "task_manager"
    description = "Manage a todo list. Actions: add (add a task), list (show all tasks), clear (remove all tasks)."
    input_schema = TaskManagerInput

    # Class-level storage (persists during session)
    _tasks: List[str] = []

    async def execute(self, input_data: TaskManagerInput) -> ToolOutput:
        """Execute task management action."""
        try:
            action = input_data.action.lower()

            if action == "add":
                if not input_data.task:
                    return ToolOutput(result="", error="Task description required for 'add' action")
                self._tasks.append(input_data.task)
                return ToolOutput(result=f"Added task: '{input_data.task}'. Total tasks: {len(self._tasks)}")

            elif action == "list":
                if not self._tasks:
                    return ToolOutput(result="No tasks in the list.")
                task_list = "\n".join([f"  {i+1}. {task}" for i, task in enumerate(self._tasks)])
                return ToolOutput(result=f"Tasks ({len(self._tasks)}):\n{task_list}")

            elif action == "clear":
                count = len(self._tasks)
                self._tasks.clear()
                return ToolOutput(result=f"Cleared {count} tasks.")

            else:
                return ToolOutput(result="", error=f"Unknown action: {action}. Use 'add', 'list', or 'clear'.")

        except Exception as e:
            return ToolOutput(result="", error=str(e))


# ============================================================================
# Example 4: Time and Date Tool
# ============================================================================

class TimeToolInput(ToolInput):
    """Input for time tool."""
    format: str = Field(default="full", description="Format: 'full', 'time', 'date', or 'iso'")


class TimeTool(BaseTool):
    """Get current time and date."""

    name = "current_time"
    description = "Get the current date and time. Useful for time-sensitive queries or scheduling."
    input_schema = TimeToolInput

    async def execute(self, input_data: TimeToolInput) -> ToolOutput:
        """Return current time in requested format."""
        try:
            now = datetime.now()
            fmt = input_data.format.lower()

            if fmt == "full":
                result = now.strftime("%A, %B %d, %Y at %I:%M:%S %p")
            elif fmt == "time":
                result = now.strftime("%I:%M:%S %p")
            elif fmt == "date":
                result = now.strftime("%A, %B %d, %Y")
            elif fmt == "iso":
                result = now.isoformat()
            else:
                result = now.strftime("%Y-%m-%d %H:%M:%S")

            return ToolOutput(result=result)

        except Exception as e:
            return ToolOutput(result="", error=str(e))


# ============================================================================
# Example Functions
# ============================================================================

async def custom_tool_direct_usage():
    """Example 1: Using custom tools directly."""
    print("=" * 60)
    print("Example 1: Direct Custom Tool Usage")
    print("=" * 60)

    # Dice roller
    dice = DiceRollerTool()
    result = await dice.execute(DiceRollerInput(sides=20, count=3))
    print(f"Dice roll (3d20): {result.result}")

    # Weather
    weather = WeatherSimulatorTool()
    result = await weather.execute(WeatherInput(city="Tokyo", include_forecast=True))
    print(f"\n{result.result}")

    # Time
    time_tool = TimeTool()
    result = await time_tool.execute(TimeToolInput(format="full"))
    print(f"\nCurrent time: {result.result}")

    print()


async def custom_tool_with_agent():
    """Example 2: Using custom tools with the agent."""
    print("=" * 60)
    print("Example 2: Custom Tools with Agent")
    print("=" * 60)

    # Register custom tools
    tool_registry.register(DiceRollerTool())
    tool_registry.register(WeatherSimulatorTool())
    tool_registry.register(TimeTool())

    config = AgentConfig(
        model="deepseek-chat",
        temperature=0.7,
    )
    agent = ChatAgent(config)
    await agent.initialize()

    queries = [
        "Roll a 6-sided die",
        "What's the weather in Paris?",
        "What time is it now?",
    ]

    for query in queries:
        print(f"\nUser: {query}")
        print("Assistant: ", end="", flush=True)

        async for event in agent.stream([{"role": "user", "content": query}], show_thinking=True):
            if event["type"] == "content":
                print(event["data"]["text"], end="", flush=True)
            elif event["type"] == "tool_call":
                print(f"\n  [Calling: {event['data']['tool']}]")
        print()

    print()


async def task_manager_demo():
    """Example 3: Task manager with state."""
    print("=" * 60)
    print("Example 3: Stateful Task Manager Tool")
    print("=" * 60)

    # Register task manager
    tool_registry.register(TaskManagerTool())

    config = AgentConfig(
        model="deepseek-chat",
        temperature=0.7,
    )
    agent = ChatAgent(config)
    await agent.initialize()

    conversation = [
        "Add a task: Buy groceries",
        "Add a task: Call mom",
        "Show me my tasks",
        "Add a task: Finish project report",
        "What tasks do I have?",
    ]

    for user_input in conversation:
        print(f"\nUser: {user_input}")
        print("Assistant: ", end="", flush=True)

        async for event in agent.stream([{"role": "user", "content": user_input}]):
            if event["type"] == "content":
                print(event["data"]["text"], end="", flush=True)
        print()

    print()


async def tool_registration_patterns():
    """Example 4: Different ways to register tools."""
    print("=" * 60)
    print("Example 4: Tool Registration Patterns")
    print("=" * 60)

    # Pattern 1: Direct registration
    tool_registry.register(DiceRollerTool())
    print("✓ Registered DiceRollerTool directly")

    # Pattern 2: Registration with replacement
    tool_registry.register(DiceRollerTool(), allow_replace=True)
    print("✓ Re-registered DiceRollerTool with allow_replace=True")

    # Pattern 3: Check before register
    if not tool_registry.has_tool("weather"):
        tool_registry.register(WeatherSimulatorTool())
        print("✓ Registered WeatherSimulatorTool (checked first)")

    # Pattern 4: Get all registered tools
    all_tools = tool_registry.get_all_tools()
    print(f"\nCurrently registered tools ({len(all_tools)}):")
    for tool in all_tools:
        print(f"  - {tool.name}: {tool.description[:50]}...")

    # Pattern 5: Unregister a tool
    if tool_registry.has_tool("dice_roller"):
        tool_registry.unregister("dice_roller")
        print("\n✓ Unregistered dice_roller")

    print(f"Tools after unregister: {tool_registry.get_tool_names()}")

    # Re-register for other examples
    tool_registry.register(DiceRollerTool())
    print()


async def error_handling_example():
    """Example 5: Tool error handling."""
    print("=" * 60)
    print("Example 5: Tool Error Handling")
    print("=" * 60)

    dice = DiceRollerTool()

    # Valid inputs
    valid_inputs = [
        DiceRollerInput(sides=6, count=1),
        DiceRollerInput(sides=20, count=2),
    ]

    # Invalid inputs
    invalid_inputs = [
        (DiceRollerInput(sides=0, count=1), "Zero sides"),
        (DiceRollerInput(sides=6, count=0), "Zero dice"),
        (DiceRollerInput(sides=6, count=200), "Too many dice"),
    ]

    print("Valid inputs:")
    for inp in valid_inputs:
        result = await dice.execute(inp)
        status = "✓" if not result.error else "✗"
        print(f"  {status} {inp.count}d{inp.sides}: {result.result or result.error}")

    print("\nInvalid inputs:")
    for inp, description in invalid_inputs:
        result = await dice.execute(inp)
        status = "✓" if result.error else "✗"
        print(f"  {status} {description}: {result.error or result.result}")

    print()


async def main():
    """Run all custom tool examples."""
    print("\n")
    print("*" * 60)
    print("Chat Shell 101 - Custom Tools Examples")
    print("*" * 60)
    print("\n")

    try:
        await custom_tool_direct_usage()
        await custom_tool_with_agent()
        await task_manager_demo()
        await tool_registration_patterns()
        await error_handling_example()

    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()
        raise

    print("*" * 60)
    print("All examples completed!")
    print("*" * 60)


if __name__ == "__main__":
    asyncio.run(main())
