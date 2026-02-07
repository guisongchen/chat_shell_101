"""
Example 06: Configuration Management - Environment, Files, and Runtime

This example demonstrates the various ways to configure Chat Shell 101 including
environment variables, configuration files, and runtime configuration.

Prerequisites:
    1. Copy .env.example to .env: `cp .env.example .env`
    2. Edit .env and set your OPENAI_API_KEY
"""

import asyncio
import json
import os
import tempfile
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from chat_shell_101.config import Config, OpenAIConfig, StorageConfig, load_config
from chat_shell_101.agent.agent import ChatAgent
from chat_shell_101.agent.config import AgentConfig


async def environment_variables_example():
    """Example 1: Configuration via environment variables."""
    print("=" * 60)
    print("Example 1: Environment Variables")
    print("=" * 60)

    # Environment variables are loaded from .env file at the top of this script
    # via load_dotenv(). You can also set them in your shell.
    #
    # Example .env file:
    #   OPENAI_API_KEY=sk-your-key-here
    #   CHAT_SHELL_DEFAULT_MODEL=gpt-4
    #   CHAT_SHELL_STORAGE_PATH=~/.chat_shell_101
    #   CHAT_SHELL_SHOW_THINKING=true
    #   BASE_URL=https://api.deepseek.com

    # Load config (reads from environment variables)
    config = load_config()

    print("Configuration loaded from environment (.env file or shell):")
    if config.openai.api_key:
        print(f"  API Key: {config.openai.api_key[:10]}...")
    else:
        print("  API Key: Not set!")
    print(f"  Model: {config.openai.model}")
    print(f"  Base URL: {config.openai.base_url}")
    print(f"  Storage Path: {config.storage.path}")
    print(f"  Show Thinking: {config.show_thinking}")

    # Validate API key format
    is_valid = config.validate_api_key()
    print(f"  API Key Valid Format: {is_valid}")

    print()


async def programmatic_config_example():
    """Example 2: Programmatic configuration."""
    print("=" * 60)
    print("Example 2: Programmatic Configuration")
    print("=" * 60)

    # Create config programmatically
    # Note: In production, load sensitive values from environment variables
    # rather than hardcoding them. This example shows the pattern but you
    # should use os.getenv() for the api_key in real code.
    openai_config = OpenAIConfig(
        api_key=os.getenv("OPENAI_API_KEY", ""),
        model="gpt-4-turbo",
        temperature=0.5,
        max_tokens=2048,
        base_url="https://custom-api.example.com"
    )

    storage_config = StorageConfig(
        type="json",
        path=Path("/tmp/custom_storage")
    )

    config = Config(
        openai=openai_config,
        storage=storage_config,
        show_thinking=True
    )

    print("Programmatic configuration:")
    print(f"  Model: {config.openai.model}")
    print(f"  Temperature: {config.openai.temperature}")
    print(f"  Max Tokens: {config.openai.max_tokens}")
    print(f"  Storage Type: {config.storage.type}")
    print(f"  Storage Path: {config.storage.path}")

    # Get storage path (creates if needed)
    storage_path = config.get_storage_path()
    print(f"  Resolved Storage Path: {storage_path}")
    print(f"  Path Exists: {storage_path.exists()}")

    print()


async def agent_config_example():
    """Example 3: Agent-specific configuration."""
    print("=" * 60)
    print("Example 3: Agent Configuration")
    print("=" * 60)

    # Create various agent configurations
    configs = {
        "Creative Writer": AgentConfig(
            model="gpt-4",
            temperature=1.2,  # High creativity
            max_tokens=2000,
            system_prompt="You are a creative writer who loves metaphors."
        ),
        "Code Assistant": AgentConfig(
            model="gpt-4",
            temperature=0.2,  # Low randomness for code
            max_tokens=1500,
            system_prompt="You are a precise coding assistant. Provide clean, efficient code."
        ),
        "Math Tutor": AgentConfig(
            model="gpt-4",
            temperature=0.5,
            max_tokens=1000,
            system_prompt="You are a patient math tutor who explains step by step.",
            tools=["calculator"]  # Only use calculator tool
        ),
        "Research Assistant": AgentConfig(
            model="gpt-4",
            temperature=0.7,
            max_tokens=4000,
            max_iterations=15,  # Allow more tool calls
            compress_context=True,
            max_context_tokens=6000
        ),
    }

    for name, cfg in configs.items():
        print(f"\n{name}:")
        print(f"  Model: {cfg.model}")
        print(f"  Temperature: {cfg.temperature}")
        print(f"  Max Tokens: {cfg.max_tokens}")
        print(f"  Max Iterations: {cfg.max_iterations}")
        print(f"  Tools: {cfg.tools if cfg.tools else 'All'}")
        print(f"  Context Compression: {cfg.compress_context}")

    print()


async def config_validation_example():
    """Example 4: Configuration validation."""
    print("=" * 60)
    print("Example 4: Configuration Validation")
    print("=" * 60)

    valid_configs = [
        ("Default", AgentConfig()),
        ("Low Temp", AgentConfig(temperature=0.0)),
        ("High Temp", AgentConfig(temperature=2.0)),
    ]

    print("Valid configurations:")
    for name, cfg in valid_configs:
        try:
            # Trigger validation via __post_init__
            print(f"  ✓ {name}: temperature={cfg.temperature}")
        except ValueError as e:
            print(f"  ✗ {name}: {e}")

    # Invalid configurations
    invalid_configs = [
        ("Negative temp", {"temperature": -0.5}),
        ("Too high temp", {"temperature": 2.5}),
        ("Zero iterations", {"max_iterations": 0}),
        ("Negative tokens", {"max_tokens": -100}),
        ("Bad checkpoint type", {"checkpoint_type": "invalid"}),
    ]

    print("\nInvalid configurations (should raise errors):")
    for name, kwargs in invalid_configs:
        try:
            AgentConfig(**kwargs)
            print(f"  ✗ {name}: Should have raised error!")
        except ValueError as e:
            print(f"  ✓ {name}: Caught error - {e}")

    print()


async def config_file_example():
    """Example 5: Loading configuration from file."""
    print("=" * 60)
    print("Example 5: Configuration File")
    print("=" * 60)

    # Create a temporary config file
    config_data = {
        "model": "gpt-4",
        "temperature": 0.8,
        "storage_type": "sqlite",
        "custom_setting": "custom_value"
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f, indent=2)
        config_file = f.name

    try:
        # Read config from file
        with open(config_file) as f:
            loaded_config = json.load(f)

        print(f"Loaded config from {config_file}:")
        for key, value in loaded_config.items():
            print(f"  {key}: {value}")

        # Apply to agent config
        agent_cfg = AgentConfig(
            model=loaded_config.get("model", "gpt-4"),
            temperature=loaded_config.get("temperature", 0.7)
        )

        print(f"\nApplied to AgentConfig:")
        print(f"  Model: {agent_cfg.model}")
        print(f"  Temperature: {agent_cfg.temperature}")

    finally:
        os.unlink(config_file)

    print()


async def runtime_config_update():
    """Example 6: Updating configuration at runtime."""
    print("=" * 60)
    print("Example 6: Runtime Configuration Updates")
    print("=" * 60)

    # Start with default config
    config = AgentConfig(
        model="gpt-4",
        temperature=0.7,
    )

    print("Initial config:")
    print(f"  Model: {config.model}, Temperature: {config.temperature}")

    # Simulate user changing settings
    print("\nUpdating configuration...")

    # Note: In practice, you'd create a new agent with new config
    # or implement a config update mechanism
    config.temperature = 0.3
    config.max_tokens = 500

    print("Updated config:")
    print(f"  Model: {config.model}, Temperature: {config.temperature}")
    print(f"  Max Tokens: {config.max_tokens}")

    # Show that dataclass fields can be modified
    print("\nDataclass fields are mutable:")
    print(f"  Fields: {list(config.__dict__.keys())}")

    print()


async def hierarchical_config_example():
    """Example 7: Hierarchical configuration (global vs agent)."""
    print("=" * 60)
    print("Example 7: Hierarchical Configuration")
    print("=" * 60)

    # Global configuration (from environment/file)
    # Note: Load API key from environment, not hardcoded
    global_config = Config(
        openai=OpenAIConfig(
            api_key=os.getenv("OPENAI_API_KEY", ""),
            model="gpt-4",
            temperature=0.7,
        ),
        show_thinking=False
    )

    print("Global config:")
    print(f"  Model: {global_config.openai.model}")
    print(f"  Temperature: {global_config.openai.temperature}")
    print(f"  Show Thinking: {global_config.show_thinking}")

    # Agent can override global settings
    agent_config = AgentConfig(
        model="gpt-3.5-turbo",  # Override global model
        temperature=0.9,         # Override global temperature
        system_prompt="Custom system prompt"
    )

    print("\nAgent config (overrides):")
    print(f"  Model: {agent_config.model}")
    print(f"  Temperature: {agent_config.temperature}")
    print(f"  System Prompt: {agent_config.system_prompt[:30]}...")

    # Effective configuration
    print("\nEffective configuration (agent overrides global):")
    print(f"  Model: {agent_config.model}")
    print(f"  Temperature: {agent_config.temperature}")
    print(f"  API Key: {global_config.openai.api_key} (from global)")
    print(f"  Show Thinking: {global_config.show_thinking} (from global)")

    print()


async def config_serialization_example():
    """Example 8: Serializing and deserializing configuration."""
    print("=" * 60)
    print("Example 8: Configuration Serialization")
    print("=" * 60)

    # Create a complex config
    original = AgentConfig(
        model="gpt-4",
        temperature=0.5,
        max_tokens=2000,
        max_iterations=5,
        system_prompt="Test prompt",
        tools=["calculator"],
        compress_context=True,
        max_context_tokens=4000
    )

    # Convert to dict
    config_dict = {
        "model": original.model,
        "temperature": original.temperature,
        "max_tokens": original.max_tokens,
        "max_iterations": original.max_iterations,
        "system_prompt": original.system_prompt,
        "tools": original.tools,
        "compress_context": original.compress_context,
        "max_context_tokens": original.max_context_tokens,
    }

    print("Serialized configuration:")
    print(json.dumps(config_dict, indent=2))

    # Recreate from dict
    restored = AgentConfig(**config_dict)

    print("\nRestored configuration:")
    print(f"  Model: {restored.model}")
    print(f"  Temperature: {restored.temperature}")
    print(f"  Tools: {restored.tools}")

    # Verify they match
    match = all(
        getattr(original, field) == getattr(restored, field)
        for field in config_dict.keys()
    )
    print(f"\nConfigurations match: {match}")

    print()


async def main():
    """Run all configuration examples."""
    print("\n")
    print("*" * 60)
    print("Chat Shell 101 - Configuration Examples")
    print("*" * 60)
    print("\n")

    try:
        await environment_variables_example()
        await programmatic_config_example()
        await agent_config_example()
        await config_validation_example()
        await config_file_example()
        await runtime_config_update()
        await hierarchical_config_example()
        await config_serialization_example()

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
